"""

EvaluateTraining.py

Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

Takes the MVA input, (as in PrepareTraining.py) and creates MVAOutput.root
MVAOutput.root is a TChain containing all the signal/background reco & truth information
from finishedJobsSignal/Background and adds the MVA output from the training session.
The MVA output is stored as a friend tree.  The entry nubmer in the MVA output tree corresponds to
the entry number in the associated reconstruction tree.  

The MVA configuration (which Decaymodes go to which MVA, which reconstruction algorithms to use)
are again taken from MVASteering.py.

"""

import os
import sys
from array import array
# Get the list of MVAs to configure and tau algorithms to use from MVASteering.py
from RecoTauTag.TauTagTools.MVASteering_cfi import *

#PyRoot madness to get the MVA support classes
import PyCintex
from ROOT import gROOT, gSystem, TFile, TChain, gDirectory, TTree
gSystem.Load("libPhysicsToolsMVAComputer")
gSystem.Load("libPhysicsToolsMVATrainer")
PyCintex.Cintex.Enable()
# Get the namespace 
PhysicsTools = PyCintex.Namespace("PhysicsTools")

#Make sure we have the trained MVA files
for anAlgo in myTauAlgorithms:
   for aModule in myModules:
      computerName = aModule.computerName.value()
      mvaFile = GetTrainingFile(computerName, anAlgo)
      if not os.path.exists(mvaFile):
         print "Expected %s to exits, but it doesn't! Have you completed the training?" % mvaFile
         raise MVAError

#Now, get the different trees into this file
# we need, for signal and background
#   -the truth trees (always)
#   -all of the desired reco trees from the different algorithms (if we have more 
#       than one in our MVASteering.py file)
#   -for each reco tree, and addtional friend tree that stores the appropriate MVA output (we add this later)

#Create the training output
outputFile = TFile("MVAOutput.root", "RECREATE")

SignalChains = dict([ (treeName, TChain(treeName)) for treeName in myTauAlgorithms ])
SignalChains['truth'] = TChain('truth')
BackgroundChains = dict([ (treeName, TChain(treeName)) for treeName in myTauAlgorithms ])
BackgroundChains['truth'] = TChain('truth')

#Add the appropriate files in
for name, chain in SignalChains.iteritems():
   chain.Add(SignalFileTestingGlob)

for name, chain in BackgroundChains.iteritems():
   chain.Add(BackgroundFileTestingGlob)

#Fix the chain names
for name,chain in SignalChains.iteritems():
   chain.SetName("%s_Signal" % name)
   chain.SetCacheSize(0)
for name,chain in BackgroundChains.iteritems():
   chain.SetName("%s_Background" % name)
   chain.SetCacheSize(0)

#Always speak the truth
SignalChains['truth'].Write()
BackgroundChains['truth'].Write()

MVAImplementations = {}

#Load the trained MVAs
for anAlgo in myTauAlgorithms:  #for each algo
   for mvaCollectionName, mvaCollection in MVACollections.iteritems(): #get the set of MVAs this implementation uses
      DecayModeMap = {}
      for aModule in mvaCollection:    #different decayMode <--> MVA implentation maps
         computerName = aModule.computerName.value()
         theTrainedMVA = PhysicsTools.MVAComputer(GetTrainingFile(computerName, anAlgo))
         for aDecayMode in aModule.decayModeIndices.value():
            print "Linking decay mode %i to MVA: %s for algorithm %s, MVA collection: %s" % (aDecayMode, computerName, anAlgo, mvaCollectionName)
            DecayModeMap[aDecayMode] = theTrainedMVA
      MVAImplementations[anAlgo, mvaCollectionName] = DecayModeMap

#Build the reader class (from the MVA framework) for the signal and background chains
SignalReaders = dict([ (name, PhysicsTools.TreeReader(chain, True, True)) for name, chain in SignalChains.iteritems() ])
BackgroundReaders = dict([ (name, PhysicsTools.TreeReader(chain, True, True)) for name, chain in BackgroundChains.iteritems() ])

# Variable for TTree branch w/ MVA output 
mvaout = array( 'f', [0.] )

reportEvery = 10000

for name in myTauAlgorithms:
   for mvaCollectionName, mvaCollection in MVACollections.iteritems():
      #Get DecayMode map, this should all be a tuple but whatever
      DecayModeMap = MVAImplementations[name, mvaCollectionName]
      #At this point, we ignore the isolation requirement.  This should be applied in MVABenchmarks
      #or in the actual analysis chain.  
      #Do signal
      SignalReader = SignalReaders[name]
      SignalChain  = SignalChains[name]
      SignalOutput = TTree("%s_Signal_MVAOutput_%s" % (name, mvaCollectionName), "%s_Signal_MVAOutput_%s" % (name, mvaCollectionName))
      #print SignalOutput
      SignalOutput.Branch("MVA", mvaout, "MVA/F")
      SignalEntries = SignalChain.GetEntries()
#      SignalEntries = 1500
      print "Filling signal %s data: %i total events" % (name, SignalEntries)
      for entry in xrange(0, SignalEntries):
         if entry % reportEvery == 0:
            percentDone = (100.0*entry)/SignalEntries
            print "%00.0f%% done" % percentDone
         ientry = SignalChain.LoadTree(entry)
         if ientry < 0:
            break
         nb = SignalChain.GetEntry(entry)
         if nb <= 0:
            print "Root read error!"
            mvaout[0] = -2.5
         else:
            #Try and get the computer for this decay mode.  If it doesn't exist,
            #then we mark it automatically as fail (it is either NULL, or it is some non-usable decay mode, like 50 charged tracks)
            try:
               mvaComputer = DecayModeMap[SignalChain.DecayMode]
               SignalReader.update()
               mvaout[0] = SignalReader.fill(mvaComputer)
            except KeyError:
               mvaout[0] = -2.0
         SignalOutput.Fill()
      #Close the stuff we are done with
      SignalChain.AddFriend(SignalOutput)
      SignalOutput.Write()
      SignalChain.Write()

      #Do background
      BackgroundReader = BackgroundReaders[name]
      BackgroundChain  = BackgroundChains[name]
      BackgroundOutput = TTree("%s_Background_MVAOutput_%s" % (name, mvaCollectionName), "%s_Background_MVAOutput_%s" % (name, mvaCollectionName))
      #print BackgroundOutput
      BackgroundOutput.Branch("MVA", mvaout, "MVA/F")
      BackgroundEntries = BackgroundChain.GetEntries()
#      BackgroundEntries = 1500
      print "Filling background %s data: %i total events" % (name, BackgroundEntries)
      for entry in xrange(0, BackgroundEntries):
         if entry % reportEvery == 0:
            percentDone = (100.0*entry)/BackgroundEntries
            print "%00.0f%% done" % percentDone
         ientry = BackgroundChain.LoadTree(entry)
         if ientry < 0:
            break
         nb = BackgroundChain.GetEntry(entry)
         if nb <= 0:
            print "Root read error!"
            mvaout[0] = 2.5
         else:
            #Try and get the computer for this decay mode.  If it doesn't exist,
            #then we mark it automatically as fail
            try:
               mvaComputer = DecayModeMap[BackgroundChain.DecayMode]
               BackgroundReader.update()
               mvaout[0] = BackgroundReader.fill(mvaComputer)
            except KeyError:
               mvaout[0] = 2.0
         BackgroundOutput.Fill()
      #Close the stuff we are done with
      BackgroundChain.AddFriend(BackgroundOutput)
      BackgroundOutput.Write()
      BackgroundChain.Write()

