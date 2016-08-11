#!/usr/bin/python

import json,csv,sys,gzip,time,random

tableName =sys.argv[1]
fileName =sys.argv[2]
headerFileName =sys.argv[3]


localStoreId={}
thisAction={}
localStoreVals={}
localStoreOldVals={}
writeEvery=5
#rowHeader="\n   "
rowHeader="   "


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
  thisId=thisLine.split(',')[0]
  localStoreId[thisId]=thisId

  # New Id, default action
  if not localStoreVals.has_key(thisId):

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

  localStoreVals[thisId]=thisLine


fileIn.close()

# Header, write once execute everywhere :-D
headerFile = open(headerFileName, 'r')
headerString=headerFile.readline().rstrip('\n')
headerFile.close()
headerList=headerString.split(',')




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

  # Old Values Part
  if thisAction[thisKey] == 'D' or thisAction[thisKey] == 'U':

    oldValues=list(csv.reader(localStoreOldVals[thisKey], delimiter=',', quotechar='"'))

    writeStr = writeStr + rowHeader + ",\"oldValuesCsv\":["+localStoreOldVals[thisKey][:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "{\""+headerList[fieldIdx].lower()+"\": \""+ oldValues[fieldIdx*2][0] +"\"},"
    writeStr = writeStr + rowHeader + ",\"oldValuesKv\": ["+ updStr[:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "\""+headerList[fieldIdx].lower()+"\": \""+ oldValues[fieldIdx*2][0] +"\","
    writeStr = writeStr + rowHeader + ",\"oldValuesJson\": {"+ updStr[:-1]+"}"



  # New Values here
  if thisAction[thisKey] == 'I' or thisAction[thisKey] == 'U':

    newValues=list(csv.reader(thisValue[:-1], delimiter=',', quotechar='"'))

    writeStr = writeStr + rowHeader + ",\"newValuesCsv\": ["+localStoreVals[thisKey][:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "{\""+headerList[fieldIdx].lower()+"\": \""+ newValues[fieldIdx*2][0] +"\"},"
    writeStr = writeStr + rowHeader + ",\"newValuesKv\": ["+ updStr[:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "\""+headerList[fieldIdx].lower()+"\": \""+ newValues[fieldIdx*2][0] +"\","
    writeStr = writeStr + rowHeader + ",\"newValuesJson\": {"+ updStr[:-1]+"}"


  # Just for updates
  if thisAction[thisKey] == 'U':

    updStr=""
    updStrOldNew=""

    for fieldIdx in range(0,len(headerList)*2,2):

      if newValues[fieldIdx][0] != oldValues[fieldIdx][0]:

        updStr= updStr+ "\""+headerList[fieldIdx/2].lower()+"\":\""+ newValues[fieldIdx][0] +"\","
        updStrOldNew= updStrOldNew+ "{\""+headerList[fieldIdx/2].lower()+"\": {\"is\": \""+ newValues[fieldIdx][0] +"\", \"was\": \""+oldValues[fieldIdx][0]+"\" }},"

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