'''
Created on Apr 24, 2014

@author: walter
'''

from WorldFileReader import *

import sys 

if __name__ == '__main__':
    
    #file = 'world_wall2.world'
    file = 'world02.world'
    app = QtGui.QApplication(sys.argv)
    reader = WorldFileReader(file,40)
    reader.dump('world02.png')
    #reader.save_to_xml('world02.xml')
    sys.exit(app.exec_())
