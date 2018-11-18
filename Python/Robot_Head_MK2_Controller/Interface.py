# This file is part of Big Face Robotics Robot Head Controller
# 
#
# (C) Peter Neal (2018)


import wx
import serial
import time


class Interface(wx.Panel):

    def __init__(self, *args, **kwargs):
        super(Interface, self).__init__(*args, **kwargs)
        self.InitUI()
        self.Bind(wx.EVT_PAINT, self.OnPaint)

    def InitUI(self):

        self.SerialConnection = serial.Serial()
        self.SerialConnected = False
        
        self.ConnectButton = wx.Button(self, label="Connect")
        self.ConnectButton.Bind(wx.EVT_LEFT_DOWN, self.SerialConnect)

        self.ControlsWidth = 300
        self.ControlsHeight = 200
        self.pt = (self.ControlsWidth/2,self.ControlsHeight/3)
        self.PanScreen = self.ControlsWidth/2
        self.TiltScreen = self.ControlsHeight/3
        self._2DControls = wx.Panel(self, size = (self.ControlsWidth, self.ControlsHeight))
        self._2DControls.Bind(wx.EVT_LEFT_DOWN, self.On2DControlsClick)
        self._2DControls.Bind(wx.EVT_RIGHT_DOWN, self.On2DControlsHome)

        self.SpeedSlider = wx.Slider(self, value = 5, minValue = 1, maxValue = 10, style = wx.SL_LABELS, size = (self.ControlsWidth,60))
        self.SpeedSlider.Bind(wx.EVT_SCROLL_THUMBRELEASE, self.OnSpeedSliderScroll)

        self.ZeroText = wx.StaticText(self, wx.ID_ANY, label="0%")
        self.FullText = wx.StaticText(self, wx.ID_ANY, label="100%")
        self.BatteryGauge = wx.Gauge(self, range = 100, style = wx.GA_HORIZONTAL)

        self.PanText = wx.StaticText(self, wx.ID_ANY, label="Pan")
        self.PanData = wx.TextCtrl (self, value = "0",style = wx.TE_READONLY)
        self.TiltText = wx.StaticText(self, wx.ID_ANY, label="Tilt")
        self.TiltData = wx.TextCtrl (self, value = "0",style = wx.TE_READONLY)
        self.SonarText = wx.StaticText(self, wx.ID_ANY, label="Sonar")
        self.SonarData = wx.TextCtrl (self, value = "0",style = wx.TE_READONLY)
        self.SpeedText = wx.StaticText(self, wx.ID_ANY, label="Speed")
        self.SpeedData = wx.TextCtrl (self, value = "0",style = wx.TE_READONLY)


        # Create sizers

        self.Batterysizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Batterysizer.Add(self.ZeroText, wx.ALIGN_LEFT, border = 3)
        self.Batterysizer.Add(self.BatteryGauge, wx.ALIGN_CENTRE, border = 3)
        self.Batterysizer.Add(self.FullText, wx.ALIGN_RIGHT, border = 3)

        self.Datasizer = wx.GridSizer(2, 4, 5, 5)
        self.Datasizer.Add(self.PanText)
        self.Datasizer.Add(self.PanData)
        self.Datasizer.Add(self.TiltText)
        self.Datasizer.Add(self.TiltData)
        self.Datasizer.Add(self.SonarText)
        self.Datasizer.Add(self.SonarData)
        self.Datasizer.Add(self.SpeedText)
        self.Datasizer.Add(self.SpeedData)

        self.Topstaticbox = wx.StaticBox(self, -1, 'Robot Interface') 
        self.Topstaticboxsizer = wx.StaticBoxSizer(self.Topstaticbox, wx.VERTICAL)

        self.Topstaticboxsizer.Add(self.ConnectButton) 
        self.Topstaticboxsizer.Add(self._2DControls)
        self.Topstaticboxsizer.Add(self.SpeedSlider)
        self.Topstaticboxsizer.Add(self.Batterysizer)
        self.Topstaticboxsizer.Add(self.Datasizer)

   
        self.SetSizer(self.Topstaticboxsizer)
        self.Topstaticboxsizer.SetSizeHints(self)
        self.Centre()


    def OnSpeedSliderScroll(self, event):
        self.SetSpeed(self.SpeedSlider.GetValue())

    def On2DControlsClick(self, event): #Update set-point positions

        self.pt = event.GetPosition()  # position tuple
        Pan, Tilt = self.ScreenToAngle(self.pt[0], self.pt[1])
        self.SetPanTilt(Pan, Tilt)

    def On2DControlsHome(self, event): #Update set-point positions
        self.pt = (self.ControlsWidth/2,self.ControlsHeight/3)
        Pan = 0
        Tilt = 0
        self.SetPanTilt(Pan, Tilt)

    def UpdateData(self):
        '''Reads all data from the robot and updates screen'''
        if self.SerialConnected:
            #Update 2d control panel with pan/tilt positions
            self.SendCommand('G0')
            Pan = int(self.ReadSerial())
            self.SendCommand('G1')
            Tilt = int(self.ReadSerial())
            self.SendCommand('G2')
            Sonar = int(self.ReadSerial())
            self.SendCommand('G3')
            Battery = int(self.ReadSerial())
            self.SendCommand('G4')
            Speed = int(self.ReadSerial())

            #Update head angles on 2D Control panel
            self.PanScreen, self.TiltScreen = self.AngleToScreen(Pan, Tilt)
            self.Refresh()

            #Update battery gauge
            if Battery > 100:
                self.BatteryGauge.SetValue(100)
            else:
                self.BatteryGauge.SetValue(float(Battery))
            #Update data boxes
            self.PanData.SetValue(str(float(Pan)/10))
            self.TiltData.SetValue(str(float(Tilt)/10))
            self.SonarData.SetValue(str(Sonar))
            self.SpeedData.SetValue(str(Speed))

            return float(Pan)/10, float(Tilt)/10, Sonar
        else:
            return None


    def OnPaint(self, event=None):
        dc = wx.ClientDC(self._2DControls)
        dc.Clear()
        dc.SetBrush(wx.Brush(wx.Colour(0,110,160), 1))
        dc.DrawRectangle(0, 0, self.ControlsWidth, self.ControlsHeight) #Draw Home marker       
        dc.SetBrush(wx.Brush(wx.Colour(255,0,0), 1))
        dc.DrawCircle(self.ControlsWidth/2, self.ControlsHeight/3,10) #Draw Home marker
        dc.SetBrush(wx.Brush(wx.Colour(0,0,255), 1))
        dc.DrawCircle(self.pt[0], self.pt[1], 8) #Draw set-point marker

        dc.SetBrush(wx.Brush(wx.Colour(0,255,0), 1))
        dc.DrawCircle(self.PanScreen, self.TiltScreen, 8) #Draw actual position marker


    def SerialConnect(self, event):
        if not self.SerialConnected:
            self.SerialConnection.baudrate = 115200
            self.SerialConnection.port = '/dev/ttyUSB0'
            self.SerialConnection.timeout = 10
            self.SerialConnection.open()
            time.sleep(1) # wait here a bit, let arduino boot up fully before sending data
            print ("Port open:  " + self.SerialConnection.portstr)       # check which port was really used
            self.SerialConnection.flushInput()
            time.sleep(1)
            self.SerialConnected = True
            self.ConnectButton.Disable()
        else:
            print 'Serial port already connected'


    def ReadSerial(self):
        if self.SerialConnected:
            while True:
                if self.SerialConnection.inWaiting()>0:
                    line = self.SerialConnection.readline()
                    return line.rstrip('\r\n')
        else:
            print 'No connection to Robot'


    def SendCommand(self, serialdata):
        if self.SerialConnected:
            self.SerialConnection.write(serialdata + '\n') #Write data string, newline terminated
        else:
            print 'No connection to Robot'
     

    def closeserial():
        if self.SerialConnected:
            self.SerialConnection.close()
            self.SerialConnection = None
        else:
            print 'No connection to Robot'

    def SetSpeed(self, speed):
        self.SendCommand('S7V' + str(speed))

    def SetPan(self, pan):
        self.SendCommand('S3V' + str(pan*10))

    def SetTilt(self, tilt):
        self.SendCommand('S4V' + str(tilt*10))

    def SetPanTilt(self, pan, tilt):
        self.SendCommand('S3V' + str(pan))
        self.SendCommand('S4V' + str(tilt))

    def SetRGBled(self, R, G, B):
        self.SendCommand('S0V' + str(R))
        self.SendCommand('S1V' + str(G))
        self.SendCommand('S2V' + str(B))


    def IncPan(self, delta):
        self.SendCommand('S5V' + str(delta))

    def IncTilt(self, delta):
        self.SendCommand('S6V' + str(delta))

    def ScreenToAngle(self, x, y):
        #map function is (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

        Pan = (x - 0) * (900 - -900) / (self.ControlsWidth - 0) + -900
        Tilt = (y - 0) * (-900 - 450) / (self.ControlsHeight - 0) + 450

        return Pan, Tilt

    def AngleToScreen(self, pan, tilt):

        x = (pan - -900) * (self.ControlsWidth - 0) / (900 - -900) + 0
        y = (tilt - 450) * (self.ControlsHeight - 0) / (-900 - 450) + 0
        return x ,y

            
