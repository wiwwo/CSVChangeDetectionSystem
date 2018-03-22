#!/usr/bin/python

import sys,gzip,zlib
import hashlib
import datetime

dataFieldSeparator='\t'
headerSeparator=','

tableName =sys.argv[1]
oldFileName =sys.argv[2]
newFileName =sys.argv[3]
headerFileName =sys.argv[4]


eventAction={}
oldContentHash={}
oldContentData={}
updContentData={}

################################################################################
### READING PART ###############################################################
################################################################################

#print datetime.datetime.now()

fileIn = gzip.open(oldFileName, 'r')
for thisLine in fileIn:
  # Get rid of non ID lines
  if not thisLine[0].isdigit():
    continue

  thisId=thisLine.split(dataFieldSeparator)[0]

  oldContentHash[thisId]=hashlib.md5(thisLine).hexdigest()
  oldContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )
  eventAction[thisId]='D'
fileIn.close()
#print eventAction

#print "new"
#print datetime.datetime.now()
fileIn = gzip.open(newFileName, 'r')
for thisLine in fileIn:
  # Get rid of non ID lines
  if not thisLine[0].isdigit():
    continue

  thisId=thisLine.split(dataFieldSeparator)[0]

  # Check if exists
  if eventAction.has_key(thisId):
    # if so, same data?
    if oldContentHash[thisId] == hashlib.md5(thisLine).hexdigest():
      del eventAction[thisId]
      #del oldContentHash[thisId]
      del oldContentData[thisId]
      continue

    else:
      # UPDATE
      eventAction[thisId]='U'
      updContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )

  else:
    # new
    eventAction[thisId]='I'
    oldContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )

fileIn.close()

#print eventAction




# Header, write once execute everywhere :-D
headerFile = open(headerFileName, 'r')
headerString=headerFile.readline().rstrip('\n')
headerFile.close()
headerList=headerString.split(headerSeparator)
headerLen=len(headerList)

for thisKey,thisAction in eventAction.items():
  print thisAction,
  print thisKey,
  if thisAction != 'D':
    print '\t',
    if thisAction == 'I':
      print 'NEW ',
    else:
      print 'OLD ',
    newData = zlib.decompress (  oldContentData[thisKey]  ).split(dataFieldSeparator)
    for fieldIdx in range(0,len(headerList)):
      print headerList[fieldIdx]+"="+newData[fieldIdx]+'\t',
    if thisAction == 'U':
       print '\t',
       print 'NEW ',
       updData = zlib.decompress (  updContentData[thisKey]  ).split(dataFieldSeparator)
       for fieldIdx in range(0,len(headerList)):
         print headerList[fieldIdx]+"="+updData[fieldIdx]+'\t',
       del updContentData[thisKey]
  del oldContentData[thisKey]
  print

#print
#print datetime.datetime.now()
