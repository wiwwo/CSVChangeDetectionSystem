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

  # Get rid of non ID lines
  if not thisLine[1].isdigit():
    #print 'SKIP'+thisLine[1]
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
headerList=headerString.split(',')
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
    print "DEL ID "+thisKey+";\t -- OLD VALUES="+localStoreOldVals[thisKey]

  if thisAction[thisKey] == 'I':
    #print "INS ID "+thisKey+";\t -- NEW VALUES="+thisValue
    newValues=list(thisValue.replace('"','').split(dataFieldSeparator))
    print "INS ID "+thisKey+";\t",
    for fieldIdx in range(0,len(headerList)):
      print headerList[fieldIdx]+"="+newValues[fieldIdx]+'\t',
    print

  # Now the funny part...
  if thisAction[thisKey] == 'U':
    oldValues=list(localStoreOldVals[thisKey].replace('"','').split(dataFieldSeparator))
    newValues=list(thisValue.replace('"','').split(dataFieldSeparator))

    #print "UPD ID "+thisKey+";\t -- NEW VALUES="+thisValue+"\t -- OLD VALUES="+localStoreOldVals[thisKey]
    print "UPD ID "+thisKey+";\t",
    for fieldIdx in range(0,len(headerList)):
      if newValues[fieldIdx] != oldValues[fieldIdx]:
        print headerList[fieldIdx]+" HAS CHANGED -- OLD VALUE="+oldValues[fieldIdx]+" -- NEW VALUE="+newValues[fieldIdx]+"\t",
    print
