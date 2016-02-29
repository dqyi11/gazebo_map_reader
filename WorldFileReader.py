'''
Created on Apr 24, 2014

@author: walter
'''

from xml.dom import minidom
from PyQt4 import QtGui, QtCore
import math
import numpy as np
from shapely.geometry import Polygon, Point


class modelObject(object):
    
    def __init__(self, name):
        self.name = name
        self.pos = []
        self.size = []

        
class WorldFileReader(QtGui.QWidget):

    def __init__(self, file, scale=5):
        
        self.worldSize = []
        
        self.models = []  
        
        self.parseFile(file)
        self.filename = file
        self.scale = scale
        super(WorldFileReader, self).__init__()
        self.initWorld()
        self.initUI()
        
        
    def initUI(self):
        if len(self.worldSize) != 0:
            width = int(self.scale*self.worldSize[0])
            height = int(self.scale*self.worldSize[1])
            self.setGeometry(300, 300, width, height)
        self.show()
        
    def findModel(self, name):
        
        for model in self.models:
            if model.name == name:
                return model
        return None
        
    def parseBit(self, data):
        data_array =  data.split(' ')
        float_array = []
        for d in data_array:
            float_array.append(float(d))
        return float_array
    
    def dump(self, outfile):
        width = self.scale * self.worldSize[0]
        height = self.scale * self.worldSize[1] 
        img = QtGui.QImage(QtCore.QSize(width, height), QtGui.QImage.Format_ARGB32_Premultiplied)
        img.fill(QtCore.Qt.white)
        qp = QtGui.QPainter(img)
        qp.begin(self)
        color = QtGui.QColor(0,0,0)
        qp.setPen(color)
        qp.setBrush(color)
        
        for model in self.models:
            qp.drawPolygon(QtCore.QPointF(model.points[0][0],model.points[0][1]), 
                           QtCore.QPointF(model.points[1][0],model.points[1][1]),
                           QtCore.QPointF(model.points[2][0],model.points[2][1]),
                           QtCore.QPointF(model.points[3][0],model.points[3][1]))
            
        img.save(outfile, 'PNG')
    
    def paintEvent(self, e):

        if len(self.models)==0:
            return
        
        qp = QtGui.QPainter()
        qp.begin(self)
        
        color = QtGui.QColor(0,0,0)
        qp.setPen(color)
        qp.setBrush(color)
        
        for model in self.models:
            qp.drawPolygon(QtCore.QPointF(model.points[0][0],model.points[0][1]), 
                           QtCore.QPointF(model.points[1][0],model.points[1][1]),
                           QtCore.QPointF(model.points[2][0],model.points[2][1]),
                           QtCore.QPointF(model.points[3][0],model.points[3][1]))
                    
        qp.end()
        
        
    def parseFile(self, filename):
        
        self.models = []
        xmldoc = minidom.parse(filename)
        models = xmldoc.getElementsByTagName('model')
        
        for model in models:
            statics = model.getElementsByTagName("static")
            if len(statics)==0:
                continue
            
            if model.getAttribute("name") != "ground_plane_0" and model.getAttribute("name") != "mobile_base":
                mod_obj = modelObject(model.getAttribute("name"))
                model_pos = model.getElementsByTagName("pose")[0]
                mod_obj.pos = self.parseBit(model_pos.firstChild.data)
                collision = model.getElementsByTagName("collision")[0]
                col_size = collision.getElementsByTagName("size")[0]
                mod_obj.size = self.parseBit(col_size.firstChild.data)
                self.models.append(mod_obj)
                
            elif model.getAttribute("name") == "ground_plane_0":
                for collision in model.getElementsByTagName("collision"):
                    coll_size = collision.getElementsByTagName("size")[0]
                    self.worldSize = self.parseBit(coll_size.firstChild.data)
                    
        for model in models:
            if model.getAttribute("name") != "ground_plane_0" and model.getAttribute("name") != "mobile_base":
                statics = model.getElementsByTagName("static")
                if len(statics)==0:
                    mod_obj = self.findModel(model.getAttribute("name"))
                    model_pos = model.getElementsByTagName("pose")[0]
                    mod_obj.map_pos = self.parseBit(model_pos.firstChild.data)
            

    def initWorld(self):

        for model in self.models:

            posX = model.map_pos[0] + model.pos[0] + self.worldSize[0]/2.0 
            posY = model.map_pos[1] + model.pos[1] + self.worldSize[0]/2.0
            rot = model.map_pos[5] + model.pos[5]
  
            ULx = posX+(model.size[0]*math.cos(rot)/2.0)-(model.size[1]*math.sin(rot)/2.0)
            ULy = posY+(model.size[1]*math.cos(rot)/2.0)+(model.size[0]*math.sin(rot)/2.0)
            URx = posX-(model.size[0]*math.cos(rot)/2.0)-(model.size[1]*math.sin(rot)/2.0)
            URy = posY+(model.size[1]*math.cos(rot)/2.0)-(model.size[0]*math.sin(rot)/2.0)
            BLx = posX+(model.size[0]*math.cos(rot)/2.0)+(model.size[1]*math.sin(rot)/2.0)
            BLy = posY-(model.size[1]*math.cos(rot)/2.0)+(model.size[0]*math.sin(rot)/2.0)
            BRx = posX-(model.size[0]*math.cos(rot)/2.0)+(model.size[1]*math.sin(rot)/2.0)
            BRy = posY-(model.size[1]*math.cos(rot)/2.0)-(model.size[0]*math.sin(rot)/2.0)    
                
            ULx = ULx*self.scale
            ULy = ULy*self.scale
            URx = URx*self.scale
            URy = URy*self.scale
            BLx = BLx*self.scale
            BLy = BLy*self.scale
            BRx = BRx*self.scale
            BRy = BRy*self.scale
            model.points = [(ULx, ULy),(URx, URy),(BRx, BRy), (BLx, BLy)]
            model.polygon = Polygon(model.points)        
                
    def save_to_xml(self, filename):
        
        #print "dumping.."        
        
        doc = minidom.Document()
        root = doc.createElement("World")
        doc.appendChild(root)
        
        root.setAttribute( "width", str(int(self.worldSize[0])) );
        root.setAttribute( "height", str(int(self.worldSize[1])) );
        root.setAttribute( "scale", str(int(self.scale)) );

        for model in self.models:
            mod_node = doc.createElement("model")
            mod_node.setAttribute("name", model.name)
            mod_node.setAttribute("pos", str(model.pos))
            mod_node.setAttribute("size", str(model.size))
            mod_node.setAttribute("map_pos", str(model.map_pos))
            for p in model.points:
                p_node = doc.createElement("point")
                p_node.setAttribute("x", p[0])
                p_node.setAttribute("y", p[1])
                mod_node.appendChild(p_node)
            root.appendChild(mod_node)
        
        doc.writexml( open(filename, 'w'), indent="", addindent="", newl='')
        
        #doc.unlink()
    
    def mousePressEvent(self, e):
        if e.button() == QtCore.Qt.LeftButton:
            x_pos = e.pos().x()
            y_pos = e.pos().y()
            for model in self.models:
                if model.polygon.contains( Point(x_pos, y_pos) ):
                    print model.name
        
