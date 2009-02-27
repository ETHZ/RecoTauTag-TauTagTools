import sys
import os
# Get CMSSW base
try:
   Project_Area = os.environ["CMSSW_BASE"]
except KeyError:
   print "$CMSSW_BASE enviroment variable not set!  Please run eval `scramv1 ru -[c]sh`"
   sys.exit(1)

import FWCore.ParameterSet.Config as cms
import glob

# Get defintions (w/ decay mode mapping) from the python defintion file
from RecoTauTag.TauTagTools.TauMVAConfigurations_cfi import *

"""
        MVASteering.py
        Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

        Define the MVA configurations to be used in training/testing
                - which neural net xml descriptors
                - which algorithms (pfTauHighEfficiency, etc)
        Define locations of train/test ROOT files
"""
#######  USER PARAMETERS  #######################################
#################################################################

# Define lists of neural nets corresponding to a total configuration
# The Neural net objects used here (SingleNet, OneProngNoPiZero, etc) must be defined in
# the TauMVAConfigurations_cfi.py found in ../python
MVACollections = {}


# Use the Tau neural classifier configuration
MVACollections['TaNC'] = [OneProngNoPiZero,
                          OneProngOnePiZero,
                          OneProngTwoPiZero,
                          ThreeProngNoPiZero,
                          ThreeProngOnePiZero]

# non isolated, single net only
# MVACollections['SingleNet'] = [SingleNet]       

# isolation applied, neural net for each decay mode
MVACollections['MultiNetIso'] = [OneProngNoPiZeroIso,
                                 OneProngOnePiZeroIso,
                                 OneProngTwoPiZeroIso,
                                 ThreeProngNoPiZeroIso,
                                 ThreeProngOnePiZeroIso]

# isolation applied, single neural net 
#MVACollections['SingleNetIso'] = [SingleNetIso]


# For training/evaluating on an isolated sample, define the isolated criteria here
IsolationCutForTraining = "Alt$(ChargedOutlierPt[0], 0) < 1.0 && Alt$(NeutralOutlierPt[0], 0) < 1.5" #no tracks above 1 GeV, no gammas above 1.5  GeV

#Define the PFRecoTauDecayMode source to use (in the case of more than one separate directories will be created for each training sample)
myTauAlgorithms = ["pfTauDecayModeHighEfficiency"]

"""
Example of multiple algorithms
myTauAlgorithms = ["pfTauDecayModeHighEfficiency",
                   "pfTauDecayModeInsideOut"]
"""

# define locations of signal/background root files
TauTagToolsWorkingDirectory = os.path.join(Project_Area, "src/RecoTauTag/TauTagTools")
SignalRootDir               = os.path.join(TauTagToolsWorkingDirectory, "test", "finishedJobsSignal")
BackgroundRootDir           = os.path.join(TauTagToolsWorkingDirectory, "test", "finishedJobsBackground")

#Globs to get files for training and evaluation.  If you want to ensure different sets, you can do something like
# add a requirement such as *[0123].root for training and *[4].root.  (files not ending in four used for trianing, ending in four used for testing)
SignalFileTrainingGlob     = "%s/*[0123].root" % SignalRootDir
#BackgroundFileTrainingGlob = "%s/*82953*0.root" % BackgroundRootDir
BackgroundFileTrainingGlob = "%s/*[0123].root" % BackgroundRootDir

SignalFileTestingGlob     = "%s/*4.root" % SignalRootDir
BackgroundFileTestingGlob = "%s/*4.root" % BackgroundRootDir


#################################################################
#####  DO NOT MODIFY BELOW THIS LINE (experts only) #############
#################################################################


#Find the unique mva types to train
listOfMVANames = {}
for name, mvaCollection in MVACollections.iteritems():
   for mva in mvaCollection:
      name = mva.computerName.value()
      if not name in listOfMVANames:
         listOfMVANames[name] = mva

myModules = []
for name, mva in listOfMVANames.iteritems():
   myModules.append(mva)

# Catch dumb errors before we begin

if not os.path.exists(SignalRootDir):
   print "Signal root file directory (%s) does not exist! Have you created the MVA raw training data?" % SignalRootDir
   sys.exit(1)
if not os.path.exists(BackgroundRootDir):
   print "Background root file directory (%s) does not exist! Have you created the MVA raw training data?" % BackgroundRootDir
   sys.exit(1)

SignalTrainFiles         = glob.glob(SignalFileTrainingGlob)
BackgroundTrainFiles     = glob.glob(BackgroundFileTrainingGlob)

SignalTestingFiles         = glob.glob(SignalFileTestingGlob)
BackgroundTestingFiles     = glob.glob(BackgroundFileTestingGlob)

if not len(SignalTrainFiles) or not len(BackgroundTrainFiles) or not len(SignalTestingFiles) or not len(BackgroundTestingFiles):
   print "The signal/background root file training/testing file list is empty! Check the SignalFileTrainingGlob etc. in MVASteering.py"
   sys.exit(1)

# Ensure that we have all the necessary XML files 
for aModule in myModules:
   computerName = aModule.computerName.value() #conver to python string
   xmlFileLoc   = os.path.join(TauTagToolsWorkingDirectory, "xml", "%s.xml" % computerName)
   if not os.path.exists(xmlFileLoc):
      print "Can't find xml configuration file for %s - please check that %s exists!" % (computerName, xmlFileLoc)
      sys.exit(1)
