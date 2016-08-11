#!/usr/bin/python

import json,csv,sys,gzip
import time,random,sys,string
from datetime import datetime
import signal

tableName =sys.argv[1]
fileName =sys.argv[2]
headerFileName =sys.argv[3]


fileIn = gzip.open(fileName, 'r')

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

print "-- HEADER= "+headerString
print

for thisKey, thisValue in localStoreVals.items():
  #print "-- ID="+thisKey

  if thisValue[0] == 'D':
    print "-- OLD VALUES= "+localStoreOldVals[thisKey][1:-1]
    print "DELETE FROM "+tableName+" WHERE ID="+thisKey+";"

  if thisValue[0] == 'I':
    print "-- NEW VALUES= "+thisValue[1:-1]
    print "INSERT INTO "+tableName+"\n ("+headerString+")\nVALUES\n ("+ thisValue[1:-1] +");"

  # Now the funny part...
  if thisValue[0] == 'U':
    oldValues=list(csv.reader(localStoreOldVals[thisKey][1:-1], delimiter=',', quotechar='"'))
    newValues=list(csv.reader(thisValue[1:-1], delimiter=',', quotechar='"'))

    print "-- OLD VALUES= "+localStoreOldVals[thisKey][1:-1]
    print "-- NEW VALUES= "+thisValue[1:-1]
    print "UPDATE "+tableName+" SET"

    updStr=""
    for fieldIdx in range(0,len(headerList)*2,2):
      if newValues[fieldIdx][0] != oldValues[fieldIdx][0]:
        updStr= updStr+ " "+headerList[fieldIdx/2].lower()+" = \""+ newValues[fieldIdx][0] +"\","
    print updStr[:-1]

    print " WHERE ID="+thisKey+";"

  print "\n\n"