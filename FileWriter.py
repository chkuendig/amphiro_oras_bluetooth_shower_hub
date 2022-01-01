import abc
import json
from datetime import datetime

from AbstractWriter import AbstractWriter

class FileWriter(AbstractWriter):

    filename = None
    fileHandle = None
    rawFileHandle = None

    def __init__(self, Config ):
      # Call abstract base class and pass the name of this sensor and name for the sensor
      AbstractWriter.__init__(self, Config )

      if ( Config.has_option("file", "output_file") ):
        self.fileHandle = open( Config.get("file", "output_file"), 'a')

      if ( Config.has_option("file", "raw_output_file") ):
        self.rawFileHandle = open( Config.get("file", "raw_output_file") , 'a')

    def writeLastMessage(self, dataDict, rawData1, rawData2 ):
      self.write(dataDict, rawData1, rawData2)

    # Write data to writers target (This is abstract method that is used to write data.)
    def write(self, dataDict, rawData1, rawData2 ):
      if ( self.fileHandle != None):
           self.fileHandle.write( "--" + str(datetime.now()) + "--\n" )
           self.fileHandle.write( json.dumps(dataDict) +"\n")
           self.fileHandle.write( "" )

      if ( self.rawFileHandle != None):
           self.rawFileHandle.write( "--" + str(datetime.now()) + "--\n" )
           self.rawFileHandle.write( rawData1 +"\n")
           self.rawFileHandle.write( rawData2 +"\n")
           self.rawFileHandle.write( "" )
