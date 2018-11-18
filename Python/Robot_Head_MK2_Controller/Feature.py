# This file is part of Big Face Robotics Robot Head Controller
# 
#
# (C) Peter Neal (2018)

class Feature:
	"""
	Class to contain environment feature data
	"""
	def __init__(self, Type=0, Data=0, Distance = 0, X=0, Y=0, Z=0, Pan=0, Tilt=0):

                self.Type = Type #Feature type (Template, colour etc)
		self.Data = Data #Data to detect feature, for templates it's the template image
                self.Distance = Distance #Distance to feature as measured by sonar sensor
                self.X = X #X coordinate of object
                self.Y = Y #Y coordinate of object
                self.Z = Z #Z coordinate of object
                self.Pan = Pan #Pan angle when object is centred in view
                self.Tilt = Tilt #Tilt angle when object is centred in view

