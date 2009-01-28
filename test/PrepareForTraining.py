"""
        PrepareForTraining.py

        Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

        Creates subdirectories for each MVA needing training, and builds 
        the appropriate training data set.

        Note that in each subdirectory, one must still execute 'root -b -q trainMVA.C'
        This step is left to the user as it is preferable it be done on a cluser
"""


import os
import sys
# Get CMSSW base
try:
   Project_Area = os.environ["CMSSW_BASE"]
except KeyError:
   print "$CMSSW_BASE enviroment variable not set!  Please run eval `scramv1 ru -[c]sh`"
   sys.exit(1)

from ROOT import TTree, TChain, TFile, gDirectory, TEntryList
import FWCore.ParameterSet.Config as cms

# Get the list of MVAs to configure and tau algorithms to use from MVASteering.py
from MVASteering import *
from MVAHelpers  import *

#Keep track of the number of events we have
summaryInformation = []

for aTauAlgorithm in myTauAlgorithms:
   print "Creating training directories for the %s algorithm." % aTauAlgorithm
   # Create TChains (need to use internal root glob..)
   SignalChain     = TChain(aTauAlgorithm)
   BackgroundChain = TChain(aTauAlgorithm)

   print "Chained %i signal files." % SignalChain.Add(SignalFileTrainingGlob)
   print "Chained %i background files." % BackgroundChain.Add(BackgroundFileTrainingGlob)

   print "Pruning non-relevant entries."
   #Relevance cuts - dont' train on null entries (obviously), isolated single prong entries, or ones marked w/ prefail
   relevance_cut = "!__ISNULL__ && !__PREPASS__ && !__PREFAIL__"
   SignalChain.Draw(">>Relevant_Signal_%s" % aTauAlgorithm, relevance_cut, "entrylist")
   BackgroundChain.Draw(">>Relevant_Background_%s" % aTauAlgorithm, relevance_cut, "entrylist")
   SignalEntryList     = gDirectory.Get("Relevant_Signal_%s" % aTauAlgorithm)
   BackgroundEntryList = gDirectory.Get("Relevant_Background_%s" % aTauAlgorithm)

   SignalChain.SetEntryList(SignalEntryList)
   BackgroundChain.SetEntryList(BackgroundEntryList)

   print "Looping over different MVA types..."
   for aModule in myModules:
      computerName = aModule.computerName.value() #convert to python string
      #build decay mode cut string
      decayModeList = aModule.decayModeIndices.value()
      decayModeCuts = BuildCutString(decayModeList)

      if aModule.applyIsolation.value():
         decayModeCuts += " && %s" % IsolationCutForTraining

      print "Building %s training set. Cut: %s" % (computerName, decayModeCuts)
      workingDir = os.path.join(TauTagToolsWorkingDirectory, "test", "TrainDir_%s_%s" % (computerName, aTauAlgorithm))
      if not os.path.exists(workingDir):
         os.mkdir(workingDir)
      outputSignalFile = TFile(os.path.join(workingDir, "signal.root"), "RECREATE")
      outputSignalTree = SignalChain.CopyTree(decayModeCuts)
      outputSignalTree.SetName("train")
      SignalEntries = outputSignalTree.GetEntries()
      outputSignalTree.Write()
      outputSignalFile.Write()
      outputSignalFile.Close()

      outputBackgroundFile = TFile(os.path.join(workingDir, "background.root"), "RECREATE")
      outputBackgroundTree = BackgroundChain.CopyTree(decayModeCuts)
      outputBackgroundTree.SetName("train")
      BackgroundEntries = outputBackgroundTree.GetEntries()
      outputBackgroundTree.Write()
      outputBackgroundFile.Write()
      outputBackgroundFile.Close()

      #copy the appropriate training file
      xmlFileLoc   = os.path.join(TauTagToolsWorkingDirectory, "xml", "%s.xml" % computerName)
      #xmlFileDest  = os.path.join(workingDir, "%s.xml" % computerName)
      #os.system("cp %s %s" % (xmlFileLoc, xmlFileDest))
      os.system("cat trainMVA_template.C | sed 's|RPL_MVA_OUTPUT|%s|' | sed 's|REPLACE_XML_FILE_ABS_PATH|%s|' > %s/trainMVA.C" % (computerName, xmlFileLoc, workingDir))

      summary = (aTauAlgorithm, computerName, SignalEntries, BackgroundEntries)
      summaryInformation.append(summary)

#print summary
print "*******  Summary **********"

for aDatum in summaryInformation:
   print "%20s %20s: Signal:\t%i\t\tBackground:%i" % aDatum


