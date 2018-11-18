# This file is part of Big Face Robotics Robot Head Controller
# 
#
# (C) Peter Neal (2018)

import wx
import numpy as np
import math

import matplotlib
matplotlib.use('WXAgg')
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

class Robot_Model(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(Robot_Model, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):


        # Matplotlib window #######################################################################################
        # Create items
        self.ModelFig = Figure(figsize=(3,3), dpi=100)
        self.ModelCanvas = FigureCanvas(self, -1, self.ModelFig)

        self.a = self.ModelFig.add_subplot(111, projection='3d')

        # Create sizer
        self.Topstaticbox = wx.StaticBox(self, -1, 'Robot Model') 
        self.Topstaticboxsizer = wx.StaticBoxSizer(self.Topstaticbox, wx.VERTICAL)

        # Add canvas to static box sizer
        self.Topstaticboxsizer.Add(self.ModelCanvas, 0, wx.EXPAND)

        self.SetSizer(self.Topstaticboxsizer)
        self.Topstaticboxsizer.SetSizeHints(self)
        self.Centre()
 

    def UpdateModel(self, PanValue, TiltValue, SonarValue): 

        ReturnArray, XYZSonar = self.DHGetHeadJointPositions(PanValue, TiltValue, (SonarValue*10)) #Convert sonar to mm

        X =  ReturnArray[:,0]
        Y = ReturnArray[:,1]
        Z = ReturnArray[:,2]

        XSonar =  XYZSonar[0]
        YSonar =  XYZSonar[1]
        ZSonar =  XYZSonar[2]

        self.a.clear()
 
        self.a.set_xlim3d(-50, 2000)
        self.a.set_ylim3d(-2000,2000)
        self.a.set_zlim3d(0,1000)
        self.a.set_autoscale_on(False)
        self.ModelFig.tight_layout()

        self.a.plot(X,Y,Z, color="red", linewidth=4)
        self.a.scatter(X,Y,Z, s = 20,  marker = "_")



        self.a.plot((ReturnArray.item(2,0), XYZSonar.item(0)),(ReturnArray.item(2,1), XYZSonar.item(1)),(ReturnArray.item(2,2), XYZSonar.item(2)), color="green", linewidth=1)
        self.ModelCanvas.draw()

        return XSonar, YSonar, ZSonar



    def DHMatrix(self, a, alpha, d, theta):
        cos_theta = math.cos(math.radians(theta))
        sin_theta = math.sin(math.radians(theta))
        cos_alpha = math.cos(math.radians(alpha))
        sin_alpha = math.sin(math.radians(alpha))

        return np.array([
            [cos_theta, -sin_theta*cos_alpha, sin_theta*sin_alpha, a*cos_theta],
            [sin_theta, cos_theta*cos_alpha, -cos_theta*sin_alpha, a*sin_theta],
            [0, sin_alpha, cos_alpha, d],
            [0, 0, 0, 1],])


    def DHGetHeadJointPositions(self, thetaPan, thetaTilt, Sonar):

        XYZ0 = np.array([0,0,0,1])
        T1 = self.DHMatrix(0, 90, 88, thetaPan) 
        T2 = self.DHMatrix(114, 0, 0, thetaTilt+90) 
        TS = self.DHMatrix(Sonar, 0, 0, -90) #XYZ of sonar end point

        XYZ1 = np.dot(T1,XYZ0)
        XYZ2 = np.dot(T1,np.dot(T2,XYZ0))
        XYZSonar = np.dot(T1,np.dot(T2,np.dot(TS,XYZ0)))

        #Form return array
        ReturnArray = np.array([XYZ0,XYZ1,XYZ2])
        return ReturnArray, XYZSonar




