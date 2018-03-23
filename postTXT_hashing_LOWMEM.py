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
updContentHeader={}

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


# Header, write once execute everywhere :-D
headerFile = open(headerFileName, 'r')
headerString=headerFile.readline().rstrip('\n')
headerFile.close()
headerList=headerString.split(headerSeparator)
headerLen=len(headerList)


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
      #updContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )

      # Just save modified fields
      oldData = zlib.decompress (  oldContentData[thisId] ).split(dataFieldSeparator)
      thisData=thisLine.rstrip('\n').split(dataFieldSeparator)
      thisOldData=''
      thisNewData=''
      thisHeader=''

      for fieldIdx in range(len(oldData)):
        if oldData[fieldIdx] != thisData[fieldIdx]:
          thisOldData = thisOldData + oldData[fieldIdx]  + dataFieldSeparator
          thisNewData = thisNewData + thisData[fieldIdx] + dataFieldSeparator
          thisHeader  = thisHeader  + headerList[fieldIdx]   + headerSeparator
        oldContentData[thisId]=zlib.compress( thisOldData.rstrip(dataFieldSeparator) )
        updContentData[thisId]=zlib.compress( thisNewData.rstrip(dataFieldSeparator) )
        updContentHeader[thisId] = thisHeader.rstrip(headerSeparator)


  else:
    # new
    eventAction[thisId]='I'
    oldContentData[thisId]=zlib.compress( thisLine.rstrip('\n') )


del oldContentHash
fileIn.close()

#print eventAction


for thisId,thisAction in eventAction.items():
  print thisAction,
  print thisId,
  if thisAction == 'D':
    print '\t',
    print 'OLD ',
    newData = zlib.decompress (  oldContentData[thisId]  ).split(dataFieldSeparator)
    for fieldIdx in range(0,len(headerList)):
      print headerList[fieldIdx]+"="+newData[fieldIdx]+'\t',

  if thisAction == 'I':
    print 'NEW ',
    newData = zlib.decompress (  oldContentData[thisId]  ).split(dataFieldSeparator)
    for fieldIdx in range(0,len(headerList)):
      print headerList[fieldIdx]+"="+newData[fieldIdx]+'\t',

  if thisAction == 'U':
    oldData = zlib.decompress (  oldContentData[thisId]  ).split(dataFieldSeparator)
    updData = zlib.decompress (  updContentData[thisId]  ).split(dataFieldSeparator)
    thisHeader=updContentHeader[thisId].split(headerSeparator)
    for fieldIdx in range(0,len(thisHeader)):
      print thisHeader[fieldIdx]+" OLD VAL="+oldData[fieldIdx]+" NEW VAL="+updData[fieldIdx]+"\t",
    del updContentData[thisId]

  del oldContentData[thisId]


  print

#print
#print datetime.datetime.now()
