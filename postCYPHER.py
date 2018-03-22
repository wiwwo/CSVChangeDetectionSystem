#!/usr/bin/python

import sys,gzip

tableName =sys.argv[1]
fileName =sys.argv[2]
headerFileName =sys.argv[3]


localStoreId={}
thisAction={}
localStoreVals={}
localStoreOldVals={}
writeEvery=5
rowHeader="\n   "
#rowHeader="   "

dataFieldSeparator=','
headerSeparator=','


################################################################################
### READING PART ###############################################################
################################################################################

# Delta file example:
#     -"123","bla bla bla OLD","22"
#     +"123","bla bla bla NEW","22"

fileIn = gzip.open(fileName, 'r')
for thisLine in fileIn:

  thisSign=thisLine[0]
  # Get rid of leading [+-] sign
  thisLine=thisLine[1:]

  # Get rid of first two lines (+++ and ---, resulting from diff)
  if thisLine[0] == '-' or thisLine[0]=='+':
    continue

  # Get rid of non-ID lines
  if not thisLine[1].isdigit():
    continue

  thisLine=thisLine.rstrip('\n')

  thisId=thisLine.split(dataFieldSeparator)[0]

  # New Id, default action
  if not localStoreId.has_key(thisId):

    if thisSign == '-':
      thisAction[thisId]='D'

    if thisSign == '+':
      thisAction[thisId]='I'

  # If i already have this id, it is an updated
  else:

    thisAction[thisId]='U'


  # If minus sign, i save old values
  if thisSign == '-':
      localStoreOldVals[thisId]=thisLine

  localStoreId[thisId]=thisId
  localStoreVals[thisId]=thisLine


fileIn.close()

# Header, write once execute everywhere :-D
headerFile = open(headerFileName, 'r')
headerString=headerFile.readline().rstrip('\n')
headerFile.close()
headerList=headerString.split(headerSeparator)
headerLen=len(headerList)



################################################################################
### WRITING PART ###############################################################
################################################################################
print "-- HEADER= "+headerString
print

processedRows=0
writeStr=""
for thisKey, thisValue in localStoreVals.items():

  updStr=""
  opType=""


  if thisAction[thisKey] == 'D':
    print "-- OLD VALUES= "+localStoreOldVals[thisKey]
    print "MATCH (x:"+tableName+" {id: '"+thisKey+"'} )"
    print " DELETE x;"


  if thisAction[thisKey] == 'I':
    print "-- NEW VALUES= "+thisValue[1:-1]
    print "CREATE (x:"+tableName
    print "{ "

    newValues=list(thisValue.replace('"','').split(dataFieldSeparator))
    insStr=""
    for fieldIdx in range(0,len(headerList)):
      insStr=insStr+ " "+ headerList[fieldIdx]+": '"+newValues[fieldIdx]+"',\n"
    print insStr[:-1]
    print "} );"


  # Now the funny part...
  if thisAction[thisKey] == 'U':
    oldValues=list(localStoreOldVals[thisKey].replace('"','').split(dataFieldSeparator))
    newValues=list(thisValue.replace('"','').split(dataFieldSeparator))

    print "-- OLD VALUES= "+localStoreOldVals[thisKey]
    print "-- NEW VALUES= "+thisValue
    print "MATCH (x:"+tableName+" {id: '"+thisKey+"'} )"
    print " SET "

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      if newValues[fieldIdx] != oldValues[fieldIdx]:
        updStr= updStr+ "   "+ headerList[fieldIdx]+": '"+newValues[fieldIdx]+"',\n"
    print updStr[:-1]

    print " WHERE ID="+thisKey+";"

  print "\n\n"
