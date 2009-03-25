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

from ROOT import TTree, TChain, TFile, gDirectory, TEntryList, Long
import FWCore.ParameterSet.Config as cms

# Get the list of MVAs to configure and tau algorithms to use from MVASteering.py
from MVASteering import *
from MVAHelpers  import *

#sys.stdout = open("TancPrepare.log","w")
#sys.stderr = open("TancPrepare.err","w")

#Keep track of the number of events we have
summaryInformation = []

#Get the list of decay modes we use
allDecayModes = set([])
for aModule in myModules:
   decayModeList = set(aModule.decayModeIndices.value())
   allDecayModes |= decayModeList

decayModePreselection = BuildCutString(list(allDecayModes))

for aTauAlgorithm in myTauAlgorithms:
   print "Creating training directories for the %s algorithm." % aTauAlgorithm
   # Create TChains (need to use internal root glob..)
   tempFile = TFile("tempFile.root", "RECREATE")
   tempFile.cd()
   SignalChain     = TChain(aTauAlgorithm)
   BackgroundChain = TChain(aTauAlgorithm)

   print "Chained %i signal files."     % SignalChain.Add(SignalFileTrainingGlob,0)
   print "Chained %i background files." % BackgroundChain.Add(BackgroundFileTrainingGlob,0)

   SignalChain.Write()
   BackgroundChain.Write()

   print "Total signal entries: %i"     % SignalChain.GetEntries()
   print "Total background entries: %i" % BackgroundChain.GetEntries()

   SignalChain.GetEntry(0)
   BackgroundChain.GetEntry(0)

   print "Pruning non-relevant entries."

   #Relevance cuts - dont' train on null entries (obviously), isolated single prong entries, or ones marked w/ prefail
   relevance_cut = "!__ISNULL__ && !__PREPASS__ && !__PREFAIL__ && (%s)" % decayModePreselection
   SignalChain.Draw(">>Relevant_Signal_%s" % aTauAlgorithm, relevance_cut, "entrylist")
   BackgroundChain.Draw(">>Relevant_Background_%s" % aTauAlgorithm, relevance_cut, "entrylist")
   SignalEntryList     = gDirectory.Get("Relevant_Signal_%s" % aTauAlgorithm)
   BackgroundEntryList = gDirectory.Get("Relevant_Background_%s" % aTauAlgorithm)

   print "After pruning, %i signal and %i background entries remain." % (SignalEntryList.GetN(), BackgroundEntryList.GetN())

   SignalChain.SetEntryList(SignalEntryList)
   BackgroundChain.SetEntryList(BackgroundEntryList)


   print "Looping over different MVA types..."
   for aModule in myModules:
      computerName = aModule.computerName.value() #convert to python string
      #build decay mode cut string
      decayModeList = aModule.decayModeIndices.value()
#      decayModeCuts = "!__ISNULL__ && "
      decayModeCuts = ""
      decayModeCuts += BuildCutString(decayModeList)

      if aModule.applyIsolation.value():
         decayModeCuts += " && %s" % IsolationCutForTraining

      print "Building %s training set. Cut: %s" % (computerName, decayModeList)
      workingDir = os.path.join(TauTagToolsWorkingDirectory, "test", "TrainDir_%s_%s" % (computerName, aTauAlgorithm))
      if not os.path.exists(workingDir):
         os.mkdir(workingDir)
      outputSignalFile = TFile(os.path.join(workingDir, "signal.root"), "RECREATE")
      SignalChain.GetEntry(0)
      outputSignalFile.cd()
      # Make a new tree for the subset
      # Copy the headers w/ branches, etc.
      outputSignalTree = SignalChain.CloneTree(0)
      outputSignalTree.SetName("train")
      # Get the entries from this chain that we want
      SignalChain.SetEntryList(SignalEntryList)
      SignalChain.Draw(">>Temp_SignalList", decayModeCuts, "entrylist")
      SignalEntryList = SignalChain.GetEntryList()
      TempEntryListSignal = gDirectory.Get("Temp_SignalList")
      print "Got %i entries from Signal for cut: %s" % (TempEntryListSignal.GetN(), decayModeList)
      print "Building subset tree..."
      SignalEntriesToCopy = TempEntryListSignal.GetN()
      SignalChain.SetEntryList(TempEntryListSignal)
      for x in xrange(0, SignalEntriesToCopy):
         globalnumber = SignalChain.GetEntryNumber(x)
         doot         = SignalChain.LoadTree(globalnumber)
         nb           = SignalChain.GetEntry(globalnumber)
         if nb <= 0:
            print "ERROR!!!", number, doot, nb
         else:
            outputSignalTree.Fill()

      SignalChain.SetEntryList(0)

      SignalEntries = outputSignalTree.GetEntries()
      outputSignalTree.Write()
      outputSignalFile.Write()
      outputSignalFile.Close()
      gDirectory.Delete("train")
      gDirectory.Delete("Temp_SignalList")

      outputBackgroundFile = TFile(os.path.join(workingDir, "background.root"), "RECREATE")
      BackgroundChain.GetEntry(0)
      outputBackgroundFile.cd()
      # Make a new tree for the subset
      # Copy the headers w/ branches, etc.
      outputBackgroundTree = BackgroundChain.CloneTree(0)
      print outputBackgroundTree
      outputBackgroundTree.SetName("train")
      # Get the entries from this chain that we want
      BackgroundChain.SetEntryList(BackgroundEntryList)
      BackgroundChain.Draw(">>Temp_BackgroundList", decayModeCuts, "entrylist")
      BackgroundEntryList = BackgroundChain.GetEntryList()
      TempEntryListBackground = gDirectory.Get("Temp_BackgroundList")

      print "Got %i entries from Background for cut: %s" % (TempEntryListBackground.GetN(), decayModeList)
      print "Building subset tree..."
      BackgroundEntriesToCopy = TempEntryListBackground.GetN()
      BackgroundChain.SetEntryList(TempEntryListBackground)
      for x in xrange(0, BackgroundEntriesToCopy):
         globalnumber = BackgroundChain.GetEntryNumber(x)
         doot         = BackgroundChain.LoadTree(globalnumber)
         BytesRead    = BackgroundChain.GetEntry(globalnumber)
         if BytesRead <= 0:
            print "ERROR!!!", globalnumber, doot, BytesRead
         else:
            outputBackgroundTree.Fill()

      BackgroundChain.SetEntryList(0)
      BackgroundEntries = outputBackgroundTree.GetEntries()
      outputBackgroundTree.Write()
      outputBackgroundFile.Write()
      outputBackgroundFile.Close()
      gDirectory.Delete("train")
      gDirectory.Delete("Temp_BackgroundList")

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


