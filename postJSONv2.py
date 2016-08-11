#!/usr/bin/python

import json,csv,sys,gzip,time,random,sys,string
from datetime import datetime
import signal

tableName =sys.argv[1]
fileName =sys.argv[2]
headerFileName =sys.argv[3]


fileIn = open(fileName, 'r')

localStoreId={}
localStoreVals={}
localStoreOldVals={}

for thisLine in fileIn:

  thisSign=thisLine[0]
  thisId=thisLine[1:].split(',')[0]
  localStoreId[thisId] = thisId

  # If i already have this id, it means this needs to be updated
  # (example:
  #     -"123","bla bla bla OLD","22"
  #     +"123","bla bla bla NEW","22"
  #  )
  if localStoreVals.has_key(thisId):

    if thisSign == '-':
      # I save the old value, to produce a more specific update statement
      localStoreVals[thisId]='U'+thisLine[1:]
      localStoreOldVals[thisId]='U'+thisLine[1:]

    if thisSign == '+':
      localStoreVals[thisId]='U'+thisLine[1:]

  # New Id, default action
  else:
    if thisSign == '-':
      localStoreVals[thisId]='D'+thisLine[1:]

      # This might get into a UPDATE, so i save old values
      localStoreOldVals[thisId]='U'+thisLine[1:]

    if thisSign == '+':
      localStoreVals[thisId]='I'+thisLine[1:]

fileIn.close()


headerFile = open(headerFileName, 'r')
headerString=headerFile.readline()
headerFile.close()
headerList=headerString.split(',')





for thisKey, thisValue in localStoreVals.items():

  writeStr=""
  updStr=""

  writeStr = writeStr + "{"
  writeStr = writeStr + "\n \"tableName\" :\""+tableName+"\""
  writeStr = writeStr + "\n ,\"sourceTablePk\": "+thisKey
  writeStr = writeStr + "\n ,\"headerCsv\": \""+headerString+"\""
  if thisValue[0] == 'D': writeStr = writeStr + "\n ,\"operationType\": \"D\""
  if thisValue[0] == 'I': writeStr = writeStr + "\n ,\"operationType\": \"I\""
  if thisValue[0] == 'U': writeStr = writeStr + "\n ,\"operationType\": \"U\""


  # Old Values Part
  if thisValue[0] == 'D' or thisValue[0] == 'U':
    oldValues=list(csv.reader(localStoreOldVals[thisKey][1:-1], delimiter=',', quotechar='"'))

    writeStr = writeStr + "\n ,\"oldValuesCsv\":["+localStoreOldVals[thisKey][1:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "{\""+headerList[fieldIdx].lower()+"\": \""+ oldValues[fieldIdx*2][0] +"\"},"
    writeStr = writeStr + "\n ,\"oldValuesKv\": ["+ updStr[:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "\""+headerList[fieldIdx].lower()+"\": \""+ oldValues[fieldIdx*2][0] +"\","
    writeStr = writeStr + "\n ,\"oldValuesJson\": {"+ updStr[:-1]+"}"




  # New Values Part
  if thisValue[0] == 'I' or thisValue[0] == 'U':
    newValues=newValues=list(csv.reader(thisValue[1:-1], delimiter=',', quotechar='"'))

    writeStr = writeStr + "\n ,\"newValuesCsv\": ["+localStoreVals[thisKey][1:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "{\""+headerList[fieldIdx].lower()+"\": \""+ newValues[fieldIdx*2][0] +"\"},"
    writeStr = writeStr + "\n ,\"newValuesKv\": ["+ updStr[:-1]+"]"

    updStr=""
    for fieldIdx in range(0,len(headerList)):
      updStr= updStr+  "\""+headerList[fieldIdx].lower()+"\": \""+ newValues[fieldIdx*2][0] +"\","
    writeStr = writeStr + "\n ,\"newValuesJson\": {"+ updStr[:-1]+"}"


  # Just for updates
  if thisValue[0] == 'U':
    updStr=""
    updStrOldNew=""
    for fieldIdx in range(0,len(headerList)*2,2):
      if newValues[fieldIdx][0] != oldValues[fieldIdx][0]:
        updStr= updStr+ "\""+headerList[fieldIdx/2].lower()+"\":\""+ newValues[fieldIdx][0] +"\","
        updStrOldNew= updStrOldNew+ "{\""+headerList[fieldIdx/2].lower()+"\": {\"is\": \""+ newValues[fieldIdx][0] +"\", \"was\": \""+oldValues[fieldIdx][0]+"\" }},"
    writeStr = writeStr + "\n ,\"updateJsonNewVals\":{"+updStr[:-1]+"}"
    writeStr = writeStr + "\n ,\"updateJsonOldNewVals\": ["+updStrOldNew[:-1]+"]"

  writeStr = writeStr + "\n}\n"
  print writeStr