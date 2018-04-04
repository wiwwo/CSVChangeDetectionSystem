#!/usr/bin/python

import sys,gzip,zlib
import hashlib
import datetime

dataFieldSeparator='\t'

tableName =sys.argv[1]
oldFileName =sys.argv[2]
newFileName =sys.argv[3]
headerFileName =sys.argv[4]


eventAction={}
oldContentHash={}
oldContentData={}
newContentData={}

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
  #newContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )
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
      del oldContentHash[thisId]
      #del newContentData[thisId]
      continue

    else:
      # UPDATE
      eventAction[thisId]='U'
      #newContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )
      del oldContentHash[thisId]

  else:
    # new
    eventAction[thisId]='I'
    #newContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )

fileIn.close()

del oldContentHash
#print eventAction




# Header, write once execute everywhere :-D
headerFile = open(headerFileName, 'r')
headerString=headerFile.readline().rstrip('\n')
headerFile.close()
headerList=headerString.split(',')
headerLen=len(headerList)

for thisKey,thisAction in eventAction.items():
  print thisAction,
  print thisKey
  #if eventAction[thisId] != 'D':
  #  updData = zlib.decompress (  newContentData[thisKey]  ).split(dataFieldSeparator)
  #  for fieldIdx in range(0,len(headerList)):
  #    print headerList[fieldIdx]+"="+updData[fieldIdx]+'\t',
  #
  print

#print
#print datetime.datetime.now()
