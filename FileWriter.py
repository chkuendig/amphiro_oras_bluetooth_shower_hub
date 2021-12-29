import abc
import json
from datetime import datetime

from AbstractWriter import AbstractWriter

class FileWriter(AbstractWriter):

    filename = None
    fileHandle = None

    def __init__(self, Config ):
      # Call abstract base class and pass the name of this sensor and name for the sensor
      AbstractWriter.__init__(self, Config )

      if ( Config.has_option("general", "output_file") ):
        self.filename = Config.get("general", "output_file")
        self.fileHandle = open( self.filename, 'a')



    # Write data to writers target (This is abstract method that is used to write data.)
    def write(self, dataDict, rawData1, rawData2 ):
      if ( self.fileHandle != None):
           self.fileHandle.write( "--" + str(datetime.now()) + "--\n" )
           self.fileHandle.write( json.dumps(dataDict) +"\n")
           self.fileHandle.write( rawData1 +"\n")
           self.fileHandle.write( rawData2 +"\n")
           self.fileHandle.write( "" )
