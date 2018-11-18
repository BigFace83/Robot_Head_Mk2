import wx
import time
import Feature
import Interface
import Robot_Model
import OpenCV
import pickle
import PID




class MainGUI(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(MainGUI, self).__init__(*args, **kwargs)
        self.InitUI()

    def InitUI(self):
        self.MainInterface = Interface.Interface(self)
        self.MainModel = Robot_Model.Robot_Model(self)
        self.OpenCV = OpenCV.OpenCV(self)

        self.FeatureDict = {}
        self.CurrentFeature = None

        self.XPID = PID.PID(0.4, 0.015, 0.15) #PID controller for pan
        self.XPID.setPoint(self.OpenCV.CamCentreX)

        self.YPID = PID.PID(0.4, 0.015, 0.15) #PID controller for tilt
        self.YPID.setPoint(self.OpenCV.CamCentreY)

        self.AddFeature = wx.Button(self, label="Add Feature")
        self.AddFeature.Bind(wx.EVT_LEFT_DOWN, self.OnAddFeature)
        self.RemoveFeature = wx.Button(self, label="Remove Feature")
        self.RemoveFeature.Bind(wx.EVT_LEFT_DOWN, self.OnRemoveFeature)
        self.FeatName = wx.TextCtrl (self)
        self.Save = wx.Button(self, label="Save")
        self.Save.Bind(wx.EVT_LEFT_DOWN, self.SaveFeatures)
        self.Load = wx.Button(self, label="Load")
        self.Load.Bind(wx.EVT_LEFT_DOWN, self.LoadFeatures)

        self.FeatureCtrl = wx.ListCtrl(self, size=(-1,100), style=wx.LC_REPORT |wx.BORDER_SUNKEN)
        self.FeatureCtrl.InsertColumn(0, 'Name')
        self.FeatureCtrl.InsertColumn(1, 'Type')

        self.FeatureCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.FeatureChanged)

        self.XLabel = wx.StaticText(self, label="X:")
        self.XValue = wx.TextCtrl(self, size=(80, -1))
        self.YLabel = wx.StaticText(self, label="Y:")
        self.YValue = wx.TextCtrl(self, size=(80, -1))
        self.ZLabel = wx.StaticText(self, label="Z:")
        self.ZValue = wx.TextCtrl(self, size=(80, -1))

        self.PanLabel = wx.StaticText(self, label="Pan:")
        self.PanValue = wx.TextCtrl(self, size=(80, -1))
        self.TiltLabel = wx.StaticText(self, label="Tilt:")
        self.TiltValue = wx.TextCtrl(self, size=(80, -1))


        Options = ['None','Detect','Track']
        self.MatchChoice = wx.Choice(self, choices = Options) 
        self.MatchChoice.SetSelection(0)


        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer3 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer4 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer5 = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer6 = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.hsizer.Add(self.MainInterface, wx.ALL, border = 5)
        self.hsizer.Add(self.OpenCV, wx.ALL, border = 5)
        self.hsizer.Add(self.MainModel, wx.ALL, border = 5)

        self.hsizer2.Add(self.AddFeature)
        self.hsizer2.Add(self.RemoveFeature)
        self.hsizer2.Add(self.FeatName)

        self.hsizer3.Add(self.Save)
        self.hsizer3.Add(self.Load)

        self.hsizer4.Add(self.XLabel)
        self.hsizer4.Add(self.XValue)
        self.hsizer4.Add(self.YLabel)
        self.hsizer4.Add(self.YValue)
        self.hsizer4.Add(self.ZLabel)
        self.hsizer4.Add(self.ZValue)

        self.hsizer5.Add(self.FeatureCtrl)
        self.hsizer5.Add(self.MatchChoice)

        self.hsizer6.Add(self.PanLabel)
        self.hsizer6.Add(self.PanValue)
        self.hsizer6.Add(self.TiltLabel)
        self.hsizer6.Add(self.TiltValue)


        self.vsizer.Add(self.hsizer)
        self.vsizer.Add(self.hsizer2)
        self.vsizer.Add(self.hsizer3)
        self.vsizer.Add(self.hsizer5)
        self.vsizer.Add(self.hsizer4)
        self.vsizer.Add(self.hsizer6)



        self.SetSizer(self.vsizer)
        self.vsizer.SetSizeHints(self)
        self.SetTitle('Big Face Robotics - Robot Head Controller')
        self.Centre()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.timer.Start(1000/20)    # timer interval


    def OnTimer(self, event):

        pose = self.MainInterface.UpdateData()
        if pose is not None:
            X, Y, Z = self.MainModel.UpdateModel(pose[0], pose[1], pose[2])

        if self.CurrentFeature is not None:
           self.UpdateFeatureData()
        
        if self.MatchChoice.GetSelection() == 0: #No detection or tracking selected
            self.OpenCV.UpdateFromCamera(1)

        elif self.MatchChoice.GetSelection() == 1 and self.CurrentFeature is not None: #Detection of selected feature selected
            Template = self.FeatureDict[self.CurrentFeature].Data
            self.OpenCV.MatchTemplate(Template, self.CurrentFeature)

        elif self.MatchChoice.GetSelection() == 2 and self.CurrentFeature is not None: #Track selected feature
            Template = self.FeatureDict[self.CurrentFeature].Data
            centre, centred = self.OpenCV.TrackTemplate(Template, self.CurrentFeature)

            if centre is not None:
                xpid = self.XPID.update(centre[0])
                self.MainInterface.IncPan(xpid)

                ypid = self.YPID.update(centre[1])   
                self.MainInterface.IncTilt(ypid)

            if centred:
                print str(self.CurrentFeature) + ' is ' + str(pose[2]) + 'cm from robot'
                self.FeatureDict[self.CurrentFeature].Distance = pose[2]
                self.FeatureDict[self.CurrentFeature].Pan = pose[0]
                self.FeatureDict[self.CurrentFeature].Tilt = pose[1]

                self.FeatureDict[self.CurrentFeature].X = X
                self.FeatureDict[self.CurrentFeature].Y = Y
                self.FeatureDict[self.CurrentFeature].Z = Z

                self.MainInterface.SetRGBled(0,255,0)

            else:
                self.MainInterface.SetRGBled(255,0,0)

        self.timer.Start(1000/20)


    def FeatureChanged(self, event):
        #selected = self.FeatureList.GetSelection()
        #self.CurrentFeature = self.FeatureList.GetString(selected)
        #self.MainInterface.SetPan(self.FeatureDict[self.CurrentFeature].Pan)
        #self.MainInterface.SetTilt(self.FeatureDict[self.CurrentFeature].Tilt)
        self.CurrentFeature = self.FeatureCtrl.GetItemText(self.FeatureCtrl.GetFocusedItem() ,0)
        self.MainInterface.SetPan(self.FeatureDict[self.CurrentFeature].Pan)
        self.MainInterface.SetTilt(self.FeatureDict[self.CurrentFeature].Tilt)

    def OnAddFeature(self, event):
        if self.FeatName.GetLineText(0) == '': #If no Name is present in text box, do not add template
            print 'Error - Enter Object Desription'
        else:
            Name = self.FeatName.GetLineText(0)
            Template = self.OpenCV.GetROIGray()
            self.FeatureDict[Name] = Feature.Feature('Template', Template)
            self.FeatName.Clear() #Clear the Name text box
        #self.FeatureCtrl.Append(Decription)
        self.FeatureCtrl.Append((Name, str(self.FeatureDict[Name].Type)))


    def OnRemoveFeature(self, event):
        #selectedfeature = self.FeatureList.GetSelection()
        #Featforremoval = self.FeatureList.GetString(selectedfeature)
        FeatforDeletion = self.FeatureCtrl.GetItemText(self.FeatureCtrl.GetFocusedItem() ,0)
        try:
            del self.FeatureDict[FeatforDeletion]
        except KeyError:
            print("Key not found")
        #self.FeatureList.Delete(selectedfeature) #Remove deleted feature from listbox
        self.FeatureCtrl.DeleteItem(self.FeatureCtrl.GetFocusedItem())



    def SaveFeatures(self, event):
        with wx.FileDialog(self, "Save Template file",  style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # save the current contents in the file
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'wb') as file:
                    pickle.dump(self.FeatureDict, file)
            except IOError:
                wx.LogError("Cannot save current data in file '%s'." % pathname)

    def UpdateFeatureData(self):
        self.PanValue.SetValue(str(self.FeatureDict[self.CurrentFeature].Pan))
        self.TiltValue.SetValue(str(self.FeatureDict[self.CurrentFeature].Tilt))
        self.XValue.SetValue(str(self.FeatureDict[self.CurrentFeature].X))
        self.YValue.SetValue(str(self.FeatureDict[self.CurrentFeature].Y))
        self.ZValue.SetValue(str(self.FeatureDict[self.CurrentFeature].Z))



    def LoadFeatures(self, event):
        with wx.FileDialog(self, "Open Template file",  style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            pathname = fileDialog.GetPath()
            try:
                with open (pathname, 'rb') as fp:
                    self.FeatureDict = pickle.load(fp)
                    #self.FeatureList.Clear()
                    #for key in self.FeatureDict:
                    #    self.FeatureList.Append(key)
                    self.LoadFeatureCtrl()

            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def LoadFeatureCtrl(self):

        self.FeatureCtrl.DeleteAllItems()

        index = 0
        for key in self.FeatureDict:
            self.FeatureCtrl.InsertItem(index, key)
            self.FeatureCtrl.SetItem(index, 1, str(self.FeatureDict[key].Type))

            index += 1


    def OnQuit(self, e):
        self.Close()

def main():

    app = wx.App()
    ex = MainGUI(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()

