"""

WeightTrainingByPtAndEta.py

Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

Computes the pt-eta distribution of both signal and backround events.  
Sets event weights such that events in kinematic regions that are 100% signal
or 100% background are not trained on.

"""

import os
import sys
from array import array
# Get the list of MVAs to configure and tau algorithms to use from MVASteering.py
from MVASteering import *

#Now, get the different trees into this file
# we need, for signal and background
#   -the truth trees (always)
#   -all of the desired reco trees from the different algorithms (if we have more 
#       than one in our MVASteering.py file)

#Create the training output
outputFile = TFile("weights.root", "RECREATE")

SignalChains     = dict([ (treeName, TChain(treeName)) for treeName in myTauAlgorithms ])
BackgroundChains = dict([ (treeName, TChain(treeName)) for treeName in myTauAlgorithms ])

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

MVAImplementations = {}

#Map each decay mode - algorithm to a signal and background histogram
for anAlgo in myTauAlgorithms:  #for each algo
   for mvaCollectionName, mvaCollection in MVACollections.iteritems(): #get the set of MVAs this implementation uses
      DecayModeMap = {}
      for aModule in mvaCollection:    #different decayMode <--> MVA implentation maps
         computerName = aModule.computerName.value()
         SignalName          = "SignalPtVsEta_%s_%s_%s" % (anAlgo, mvaCollectionName, computerName)
         BackgroundName      = "BackgroundPtVsEta_%s_%s_%s" % (anAlgo, mvaCollectionName, computerName)
         SignalHisto     = TH2F(SignalName, SignalName, 500, 0, 500, 100, 0, 2.5)
         BackgroundHisto = TH2F(BackgroundName, BackgroundName, 500, 0, 500, 100, 0, 2.5)
         for aDecayMode in aModule.decayModeIndices.value():
            print "Linking decay mode %i to signal/bkg histograms: %s for algorithm %s, MVA collection: %s" % (aDecayMode, computerName, anAlgo, mvaCollectionName)
            DecayModeMap[aDecayMode] = (SignalHisto, BackgroundHisto)
      MVAImplementations[anAlgo, mvaCollectionName] = DecayModeMap


for name in myTauAlgorithms:
   SignalChain       = SignalChains[name]
   BackgroundChain   = BackgroundChains[name]

   SignalChain.SetBranchStatus('*', 0)
   SignalChain.SetBranchStatus('DecayMode', 1)
   SignalChain.SetBranchStatus('Pt', 1)
   SignalChain.SetBranchStatus('Eta', 1)

   BackgroundChain.SetBranchStatus('*', 0)
   BackgroundChain.SetBranchStatus('DecayMode', 1)
   BackgroundChain.SetBranchStatus('Pt', 1)
   BackgroundChain.SetBranchStatus('Eta', 1)

   SignalEntries     = SignalChain.GetEntries()
   BackgroundEntries = BackgroundChain.GetEntries()
   reportEverySignal     = SignalEntries / 10
   reportEveryBackground = BackgroundEntries / 10

   for mvaCollectionName, mvaCollection in MVACollections.iteritems():
      #Get DecayMode map, this should all be a tuple but whatever
      DecayModeMap = MVAImplementations[name, mvaCollectionName]
      print "Filling signal %s data for config %s: %i total events" % (name, mvaCollectionName, SignalEntries)
      for entry in xrange(0, SignalEntries):
         if entry % reportEverySignal == 0:
            percentDone = (100.0*entry)/SignalEntries
            print "%00.0f%% done" % percentDone
         ientry = SignalChain.LoadTree(entry)
         if ientry < 0:
            break
         nb = SignalChain.GetEntry(entry)
         if nb <= 0:
            raise IOError, "Root read error!"
         else:
            #Try and get the computer for this decay mode.  If it doesn't exist,
            #then we mark it automatically as fail (it is either NULL, or it is some non-usable decay mode, like 50 charged tracks)
            try:
               SignalHisto, BackgroundHisto = DecayModeMap[SignalChain.DecayMode]
               SignalHisto.Fill(SignalChain.Pt, abs(SignalChain.Eta))
            except KeyError:
               pass

      #Do background
      print "Filling background %s data for config: %i total events" % (name, BackgroundEntries)
      for entry in xrange(0, BackgroundEntries):
         if entry % reportEveryBackground == 0:
            percentDone = (100.0*entry)/BackgroundEntries
            print "%00.0f%% done" % percentDone
         ientry = BackgroundChain.LoadTree(entry)
         if ientry < 0:
            break
         nb = BackgroundChain.GetEntry(entry)
         if nb <= 0:
            raise IOError, "Root read error!"
         else:
            #Try and get the computer for this decay mode.  If it doesn't exist,
            #then we mark it automatically as fail
            try:
               SignalHisto, BackgroundHisto = DecayModeMap[BackgroundChain.DecayMode]
               BackgroundHisto.Fill(BackgroundChain.Pt, abs(BackgroundChain.Eta))
            except KeyError:
               pass

      # write our histograms
      for DecayMode, (SignalHisto, BackgroundHisto) in DecayModeMap.iteritems():
         SignalHisto.Write()
         BackgroundHisto.Write()
