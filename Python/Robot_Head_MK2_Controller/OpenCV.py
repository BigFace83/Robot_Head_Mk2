# This file is part of Big Face Robotics Robot Head Controller
# 
#
# (C) Peter Neal (2018)

import cv2
import numpy as np
import math
import wx

class OpenCV(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(OpenCV, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):

        self.capture = cv2.VideoCapture(0)
        self.CaptureWidth = 640
        self.CaptureHeight = 480

        self.capture.set(3,self.CaptureWidth) #1024 640 1280 800 384
        self.capture.set(4,self.CaptureHeight) #600 480 960 600 288

        self.CamCentreX = self.CaptureWidth/2
        self.CamCentreY = self.CaptureHeight/2

        self.Screen1Width = 320
        self.Screen1Height = 240

        self.Screen23Width = (self.Screen1Width/2) - 5
        self.Screen23Height = (self.Screen1Height/2) - 5

        self.Selectedbox = [0,0,0,0]

        self.LatestImage = 0
        self.ROIimage = 0


        #Create objects

        self.CVstaticbox = wx.StaticBox(self, -1, 'OpenCV Images')
        self.Screen1 = wx.StaticBitmap(self, size = (self.Screen1Width, self.Screen1Height)) # Static bitmaps for OpenCV images
        self.Screen2 = wx.StaticBitmap(self, size = (self.Screen23Width, self.Screen23Height))
        self.Screen3 = wx.StaticBitmap(self, size = (self.Screen23Width, self.Screen23Height))

        self.Screen1.Bind(wx.EVT_LEFT_DOWN, self.Screen1Click)
        self.Screen1.Bind(wx.EVT_MOTION, self.Screen1Motion)
        self.Screen1.Bind(wx.EVT_LEFT_UP, self.Screen1Release)

        # Create sizers

        self.CVstaticboxsizer = wx.StaticBoxSizer(self.CVstaticbox, wx.VERTICAL)
        self.Screen23Sizer = wx.BoxSizer(wx.HORIZONTAL)

        # Add objects to sizers
        self.Screen23Sizer.Add(self.Screen2, 0 , wx.EXPAND|wx.LEFT|wx.RIGHT, 10)
        self.Screen23Sizer.Add(self.Screen3, 0 , wx.EXPAND)

        self.CVstaticboxsizer.Add(self.Screen1, 0, wx.EXPAND | wx.ALL, 10)
        self.CVstaticboxsizer.Add(self.Screen23Sizer)

        self.SetSizer(self.CVstaticboxsizer)
        self.CVstaticboxsizer.SetSizeHints(self)
        self.Centre()

        return self.CamCentreX, self.CamCentreY


    def UpdateFromCamera(self, Screen = 1):

        ret,img = self.capture.read()
        ret,img = self.capture.read()
        ret,img = self.capture.read() #get a bunch of frames to make sure current frame is the most recent

        self.LatestImage = img
        cv2.rectangle(img,(self.Selectedbox[0],self.Selectedbox[1]),(self.Selectedbox[2],self.Selectedbox[3]),(0,0,255),2) #Draw on selected rectangle
        self.OutputToScreen(img, Screen)


    def OutputToScreen(self, img, Screen = 1):

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Convert to RGB ready to display to screen
              
        if Screen is 1: #Display img to Screen1 window only
            img = cv2.resize(img, (self.Screen1Width, self.Screen1Height), interpolation = cv2.INTER_AREA) #Return a 320x240 RGB image
            h, w = img.shape[:2] # get the height and width of the source image for buffer construction
            wxbmp = wx.Bitmap.FromBuffer(w, h, img) # make a wx style bitmap using the buffer converter
            self.Screen1.SetBitmap(wxbmp)

        elif Screen is 2: #Display img to Screen2 window only
            img = cv2.resize(img, (self.Screen23Width, self.Screen23Height), interpolation = cv2.INTER_AREA) #Return a 320x240 RGB image
            h, w = img.shape[:2] # get the height and width of the source image for buffer construction
            wxbmp = wx.Bitmap.FromBuffer(w, h, img) # make a wx style bitmap using the buffer converter
            self.Screen2.SetBitmap(wxbmp)

        elif Screen is 3: #Display img to Screen3 window only
            img = cv2.resize(img, (self.Screen23Width, self.Screen23Height), interpolation = cv2.INTER_AREA) #Return a 320x240 RGB image
            h, w = img.shape[:2] # get the height and width of the source image for buffer construction
            wxbmp = wx.Bitmap.FromBuffer(w, h, img) # make a wx style bitmap using the buffer converter
            self.Screen3.SetBitmap(wxbmp)

        elif Screen is 4: #Display img to Screen1, Screen2 and Screen3 windows
            img1 = cv2.resize(img, (self.Screen1Width, self.Screen1Height), interpolation = cv2.INTER_AREA) #Return a 320x240 RGB image
            h, w = img1.shape[:2] # get the height and width of the source image for buffer construction
            wxbmp = wx.Bitmap.FromBuffer(w, h, img1) # make a wx style bitmap using the buffer converter
            self.Screen1.SetBitmap(wxbmp)
            img2 = cv2.resize(img, (self.Screen23Width, self.Screen23Height), interpolation = cv2.INTER_AREA) #Return a 320x240 RGB image
            h, w = img2.shape[:2] # get the height and width of the source image for buffer construction
            wxbmp = wx.Bitmap.FromBuffer(w, h, img2) # make a wx style bitmap using the buffer converter
            self.Screen2.SetBitmap(wxbmp)
            self.Screen3.SetBitmap(wxbmp)
   

    def MatchTemplate(self, Template, Description = None):

        ret,img = self.capture.read()
        ret,img = self.capture.read()
        ret,img = self.capture.read() #get a bunch of frames to make sure current frame is the most recent

        self.LatestImage = img

        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        w, h = Template.shape[::-1]
        res = cv2.matchTemplate(img_gray, Template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        centre = None

        if max_val > 0.85:
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            centre = (top_left[0] + w/2, top_left[1] + h/2)
            cv2.rectangle(img,top_left, bottom_right, (0,0,255), 2)
            cv2.circle(img, centre, 5, (0,0,255),-1) #draw a circle at centre point of object
            cv2.putText(img, Description, (top_left[0], top_left[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255))
            
        self.OutputToScreen(img, 1)
        

    def TrackTemplate(self, Template, Description = None, detthresh = 10):

        ret,img = self.capture.read()
        ret,img = self.capture.read()
        ret,img = self.capture.read() #get a bunch of frames to make sure current frame is the most recent

        self.LatestImage = img

        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        w, h = Template.shape[::-1]
        res = cv2.matchTemplate(img_gray, Template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        centre = None
        Centred = False

        cv2.circle(img, (self.CamCentreX, self.CamCentreY), 8, (255,0,0),-1) #draw a circle at centre point of screen

        if max_val > 0.85:
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            centre = (top_left[0] + w/2, top_left[1] + h/2)

            if centre[0]>self.CamCentreX-detthresh and centre[0]<self.CamCentreX+detthresh and centre[1]>self.CamCentreY-detthresh and centre[1]<self.CamCentreY+detthresh:
                colour = (0,255,0)
                Centred = True
            else:
                colour = (0,0,255)

            cv2.rectangle(img,top_left, bottom_right, colour, 2)
            cv2.circle(img, centre, 5, colour,-1) #draw a circle at centre point of object
            cv2.putText(img, Description, (top_left[0], top_left[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colour)
            


        self.OutputToScreen(img, 1)
        
        return centre, Centred

   
    ################################################################################
    #Handling of events for dragging a box on Screen1 to select a region of interest
    ################################################################################
    def Screen1Click(self, event): 
        self.pt = event.GetPosition()  # position tuple
        self.Selectedbox[0] = self.pt[0]*self.CaptureWidth/self.Screen1Width
        self.Selectedbox[1] = self.pt[1]*self.CaptureHeight/self.Screen1Height
        self.Selectedbox[2] = self.pt[0]*self.CaptureWidth/self.Screen1Width
        self.Selectedbox[3] = self.pt[1]*self.CaptureHeight/self.Screen1Height

    def Screen1Motion(self, event):
        if event.LeftIsDown():
            self.pt = event.GetPosition()  # position tuple
            self.Selectedbox[2] = self.pt[0]*self.CaptureWidth/self.Screen1Width
            self.Selectedbox[3] = self.pt[1]*self.CaptureHeight/self.Screen1Height

    def Screen1Release(self, event):
        print self.Selectedbox
        self.ROIimg = self.LatestImage[self.Selectedbox[1]+2:self.Selectedbox[3]-2, self.Selectedbox[0]+2:self.Selectedbox[2]-2]
        self.OutputToScreen(self.ROIimg, 2)
        self.OutputToScreen(self.ROIimg, 3)
        self.Selectedbox = [0,0,0,0]




    def GetROIGray(self):
        self.ROIimg = cv2.cvtColor(self.ROIimg, cv2.COLOR_BGR2GRAY) #Convert to RGB ready to display to screen
        return self.ROIimg


