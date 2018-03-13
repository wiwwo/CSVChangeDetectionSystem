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
headerList=headerString.split(',')
headerLen=len(headerList)



################################################################################
### WRITING PART ###############################################################
################################################################################
processedRows=0
writeStr=""
for thisKey, thisValue in localStoreVals.items():

  updStr=""
  opType=""

  writeStr = writeStr + "{"
  writeStr = writeStr + rowHeader + "\"tableName\" :\""+tableName+"\""
  writeStr = writeStr + rowHeader + ",\"sourceTablePk\": "+thisKey
  writeStr = writeStr + rowHeader + ",\"headerCsv\": \""+headerString+"\""
  writeStr = writeStr + rowHeader + ",\"operationType\": \""+thisAction[thisKey]+"\""

  # updStr[:-1] to get rid of last ","

  # Old Values Part
  if thisAction[thisKey] == 'D' or thisAction[thisKey] == 'U':

    oldValues=list(localStoreOldVals[thisKey].replace('"','').split(dataFieldSeparator))

    writeStr = writeStr + rowHeader + ",\"oldValuesCsv\":["+localStoreOldVals[thisKey]+"]"

    updStr=""
    for fieldIdx in range(0,headerLen):
      updStr= updStr+  "{\""+headerList[fieldIdx].lower()+"\": \""+ oldValues[fieldIdx] +"\"},"

    writeStr = writeStr + rowHeader + ",\"oldValuesKv\": ["+ updStr[:-1]+"]"

    updStr=""
    for fieldIdx in range(0,headerLen):
      updStr= updStr+  "\""+headerList[fieldIdx].lower()+"\": \""+ oldValues[fieldIdx] +"\","
    writeStr = writeStr + rowHeader + ",\"oldValuesJson\": {"+ updStr[:-1]+"}"



  # New Values here
  if thisAction[thisKey] == 'I' or thisAction[thisKey] == 'U':

    newValues=list(thisValue.replace('"','').split(dataFieldSeparator))

    writeStr = writeStr + rowHeader + ",\"newValuesCsv\": ["+localStoreVals[thisKey]+"]"

    updStr=""
    for fieldIdx in range(0,headerLen):

      updStr= updStr+  "{\""+headerList[fieldIdx].lower()+"\": \""+ newValues[fieldIdx] +"\"},"
    writeStr = writeStr + rowHeader + ",\"newValuesKv\": ["+ updStr[:-1]+"]"

    updStr=""
    for fieldIdx in range(0,headerLen):
      updStr= updStr+  "\""+headerList[fieldIdx].lower()+"\": \""+ newValues[fieldIdx] +"\","
    writeStr = writeStr + rowHeader + ",\"newValuesJson\": {"+ updStr[:-1]+"}"


  # Just for updates
  if thisAction[thisKey] == 'U':

    updStr=""
    updStrOldNew=""

    for fieldIdx in range(0,headerLen):

      if newValues[fieldIdx] != oldValues[fieldIdx]:

        updStr= updStr+ "\""+headerList[fieldIdx].lower()+"\":\""+ newValues[fieldIdx] +"\","
        updStrOldNew= updStrOldNew+ "{\""+headerList[fieldIdx].lower()+"\": {\"is\": \""+ newValues[fieldIdx] +"\", \"was\": \""+oldValues[fieldIdx]+"\" }},"



    writeStr = writeStr + rowHeader + ",\"updateJsonNewVals\":{"+updStr[:-1]+"}"
    writeStr = writeStr + rowHeader + ",\"updateJsonOldNewVals\": ["+updStrOldNew[:-1]+"]"



  writeStr = writeStr + "\n}\n"
  processedRows = processedRows+1

  #print writeStr

  if processedRows > writeEvery:
    print writeStr
    processedRows=0
    writeStr=""


print writeStr