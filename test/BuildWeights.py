"""

BuildWeighs.py

Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

Computes the pt-eta distribution of both signal and backround training events, for each different
neural net type.  

NOTE:  In the future, this should be reimplemented, to only loop over the files created in their respective TrainDirs. 

"""

import os
import sys
# Get the list of MVAs to configure and tau algorithms to use from MVASteering.py
from RecoTauTag.TauTagTools.MVASteering_cfi import *
from MVAHelpers import *
from ROOT import TFile, TChain, TH2F, gDirectory, TGraph, gPad, gROOT, Double, EColor, TCanvas

from array import array

less = lambda x,y: x < y and x or y
more = lambda x,y: x > y and x or y

gROOT.SetBatch(True)

#Now, get the different trees into this file
# we need, for signal and background
#   -the truth trees (always)
#   -all of the desired reco trees from the different algorithms (if we have more 
#       than one in our MVASteering.py file)

#Create the training output
outputFile = TFile("weights.root", "RECREATE")

SignalChains     = dict([ (treeName, TChain(treeName)) for treeName in myTauAlgorithms ])
BackgroundChains = dict([ (treeName, TChain(treeName)) for treeName in myTauAlgorithms ])

SomeConfigurationsRequireIso = False
allDecayModes = set([])
for aModule in myModules:
   decayModeList = set(aModule.decayModeIndices.value())
   if aModule.applyIsolation.value():
      SomeConfigurationsRequireIso = True
   allDecayModes |= decayModeList

decayModePreselection = BuildCutString(list(allDecayModes))

#Add the appropriate files in
for name, chain in SignalChains.iteritems():
   #chain.Add(SignalFileTrainingGlob)
   chain.Add('finishedJobsSignal/*root')

for name, chain in BackgroundChains.iteritems():
   #chain.Add(BackgroundFileTrainingGlob)
   chain.Add('finishedJobsBackground/*root')

#Fix the chain names
for name,chain in SignalChains.iteritems():
   chain.SetName("%s_Signal" % name)
   chain.SetCacheSize(0)
for name,chain in BackgroundChains.iteritems():
   chain.SetName("%s_Background" % name)
   chain.SetCacheSize(0)

MVAImplementations = {}

PtBins = array('d', [5., 10., 20., 30., 50., 80., 120., 200., 400., 1000.])

EtaNBins = 10
EtaMax   = 2.5

TestPtNBins = 120
TestPtMax   = 120
TestCanvas  = TCanvas("testc", "testc", 2000, 500)
TestCanvas.Divide(4,1)
TestCanvas.cd(1)

#Map each decay mode - algorithm to a signal and background histogram
for anAlgo in myTauAlgorithms:  #for each algo
   for mvaCollectionName, mvaCollection in MVACollections.iteritems(): #get the set of MVAs this implementation uses
      DecayModeMap = {}
      for aModule in mvaCollection:    #different decayMode <--> MVA implentation maps
         computerName = aModule.computerName.value()
         """
         SignalName           = "SignalPtVsEta_%s_%s_%s"       %  (anAlgo , mvaCollectionName , computerName)
         BackgroundName       = "BackgroundPtVsEta_%s_%s_%s"   %  (anAlgo , mvaCollectionName , computerName)
         WeightName           = "WeightPtVsEta_%s_%s_%s"       %  (anAlgo , mvaCollectionName , computerName)
         SignalWeightName     = "SignalWeightPtVsEta_%s_%s_%s" %  (anAlgo , mvaCollectionName , computerName)
         BackgroundWeightName = "BackgroundWeightPtVsEta_%s_%s_%s" %  (anAlgo , mvaCollectionName , computerName)
         """
         SignalName           = "SignalPtVsEta_%s_%s"       %  (anAlgo ,  computerName)
         BackgroundName       = "BackgroundPtVsEta_%s_%s"   %  (anAlgo ,  computerName)
         WeightName           = "WeightPtVsEta_%s_%s"       %  (anAlgo ,  computerName)
         SignalWeightName     = "SignalWeightPtVsEta_%s_%s" %  (anAlgo ,  computerName)
         BackgroundWeightName = "BackgroundWeightPtVsEta_%s_%s" %  (anAlgo ,  computerName)

         SignalHisto           = TH2F(SignalName           , SignalName           , len(PtBins)-1 , PtBins , EtaNBins , 0 , EtaMax)
         BackgroundHisto       = TH2F(BackgroundName       , BackgroundName       , len(PtBins)-1 , PtBins , EtaNBins , 0 , EtaMax)
         WeightHisto           = TH2F(WeightName           , WeightName           , len(PtBins)-1 , PtBins , EtaNBins , 0 , EtaMax)
         SignalWeightHisto     = TH2F(SignalWeightName     , SignalWeightName     , len(PtBins)-1 , PtBins , EtaNBins , 0 , EtaMax)
         BackgroundWeightHisto = TH2F(BackgroundWeightName , BackgroundWeightName , len(PtBins)-1 , PtBins , EtaNBins , 0 , EtaMax)
         print "Linking computer %s to weight histograms." % computerName
         DecayModeMap[computerName] = (SignalHisto, BackgroundHisto, WeightHisto, SignalWeightHisto, BackgroundWeightHisto)
      MVAImplementations[anAlgo, mvaCollectionName] = DecayModeMap

summaryString = "%-40s %-20s %-30s %10i %10i %10.03f"
print "%-40s %-20s %-30s %10s %10s %10s" % ('TauType', 'Algorithm', 'Net Name', 'Nsig', 'Nbkg', 'WeightSum')
print "--------------------------------------------------------------------------------"

for name in myTauAlgorithms:
   SignalChain       = SignalChains[name]
   BackgroundChain   = BackgroundChains[name]

   print summaryString % (name, "All", "", SignalChain.GetEntries(), BackgroundChain.GetEntries(), 1)

   relevance_cut = "!__ISNULL__ && !__PREPASS__ && !__PREFAIL__ && (%s)" % decayModePreselection
   SignalChain.Draw(">>Relevant_Signal_%s" % name, relevance_cut, "entrylist")
   BackgroundChain.Draw(">>Relevant_Background_%s" % name, relevance_cut, "entrylist")
   SignalEntryList     = gDirectory.Get("Relevant_Signal_%s" % name)
   BackgroundEntryList = gDirectory.Get("Relevant_Background_%s" % name)

   print summaryString % (name, "Preselection", "", SignalEntryList.GetN(), BackgroundEntryList.GetN(), 1)

   # if desired, precompute isolation
   SignalIsoEntryList  = SignalEntryList
   BackgroundIsoEntryList  = BackgroundEntryList
   if SomeConfigurationsRequireIso:
      SignalChain.SetEntryList(SignalEntryList)
      BackgroundChain.SetEntryList(BackgroundEntryList)
      SignalChain.Draw(">>Relevant_Signal_%s_Iso" % name, IsolationCutForTraining, "entrylist")
      BackgroundChain.Draw(">>Relevant_Background_%s_Iso" % name, IsolationCutForTraining, "entrylist")
      SignalIsoEntryList = gDirectory.Get("Relevant_Signal_%s_Iso" % name)
      BackgroundIsoEntryList = gDirectory.Get("Relevant_Background_%s_Iso" % name)
      # release the original entry lists
      SignalChain.SetEntryList(0)
      BackgroundChain.SetEntryList(0)
      print summaryString % (name, "  + Iso", "", SignalIsoEntryList.GetN(), BackgroundIsoEntryList.GetN(), 1)

   SignalEntries     = SignalChain.GetEntries()
   BackgroundEntries = BackgroundChain.GetEntries()
   reportEverySignal     = SignalEntries / 10
   reportEveryBackground = BackgroundEntries / 10

   for mvaCollectionName, mvaCollection in MVACollections.iteritems():
      DecayModeMap = MVAImplementations[name, mvaCollectionName]
      for anMVA in mvaCollection:
         decayModes   = anMVA.decayModeIndices.value()
         computerName = anMVA.computerName.value()
         applyIso     = anMVA.applyIsolation.value()
         
         if applyIso:
            SignalChain.SetEntryList(SignalIsoEntryList)
            BackgroundChain.SetEntryList(BackgroundIsoEntryList)
         else:
            SignalChain.SetEntryList(SignalEntryList)
            BackgroundChain.SetEntryList(BackgroundEntryList)

         DecayModeCut = BuildCutString(decayModes)

         SignalHisto, BackgroundHisto, WeightHisto, SignalWeightHisto, BackgroundWeightHisto = DecayModeMap[computerName]

         xValue = Double(0)
         yValue = Double(0)
         # Draw the pt & eta distribution for events that will be passed to this net
         # TTree::Draw returns TGraph
         SignalTestHisto     = TH2F("SignalTest_%s_%s" % (computerName, name), "SignalTest", TestPtNBins, 0, TestPtMax, EtaNBins, 0, EtaMax)
         BackgroundTestHisto = TH2F("BackgroundTest_%s_%s" % (computerName, name), "BackgroundTest", TestPtNBins, 0, TestPtMax, EtaNBins, 0, EtaMax)

         SignalChain.Draw("Pt+Sum$(OutlierPt):abs(Eta)", DecayModeCut)
         SignalGraph      = gPad.GetPrimitive("Graph");
         SignalSubEntries = SignalGraph.GetN()
         for index in xrange(0, SignalSubEntries):
            SignalGraph.GetPoint(index, xValue, yValue)
            SignalHisto.Fill(yValue, xValue)
            SignalTestHisto.Fill(yValue, xValue)

         BackgroundChain.Draw("Pt+Sum$(OutlierPt):abs(Eta)", DecayModeCut)
         BackgroundGraph       = gPad.GetPrimitive("Graph");
         BackgroundSubEntries = BackgroundGraph.GetN()
         for index in xrange(0, BackgroundSubEntries):
            BackgroundGraph.GetPoint(index, xValue, yValue)
            BackgroundHisto.Fill(yValue, xValue)
            BackgroundTestHisto.Fill(yValue, xValue)

         WeightSum            = 0.
         SignalNormFactor     = 1.0/SignalHisto.GetEntries()
         BackgroundNormFactor = 1.0/BackgroundHisto.GetEntries()
         for xBin in range(1, SignalHisto.GetNbinsX()+1):
            for yBin in range(1, SignalHisto.GetNbinsY()+1):
               NormalizedSignal = SignalHisto.GetBinContent(xBin, yBin)*SignalNormFactor
               NormalizedBackground = BackgroundHisto.GetBinContent(xBin, yBin)*BackgroundNormFactor
               LowerWeight = less(NormalizedSignal, NormalizedBackground)
               WeightSum += LowerWeight
               WeightHisto.SetBinContent(xBin, yBin, LowerWeight)
               SignalWeight     =  NormalizedSignal > 0 and LowerWeight/NormalizedSignal or 0.0 
               BackgroundWeight =  NormalizedBackground > 0 and LowerWeight/NormalizedBackground or 0.0 
               WeightHisto.SetBinContent(xBin, yBin, LowerWeight)
               SignalWeightHisto.SetBinContent(xBin, yBin, SignalWeight)
               BackgroundWeightHisto.SetBinContent(xBin, yBin, BackgroundWeight)

         #### BEGIN TESTING CODE #####

         WeightProj = WeightHisto.ProjectionX("weightproj")
         WeightProj.SetFillColor(EColor.kGray)

         TestCanvas.cd(1)

         # pre weighted pt distributions for sig/bkg
         SignalTestHistoNormed = SignalTestHisto.ProjectionX("sig").DrawNormalized()
         SignalTestHistoNormed.SetLineColor(EColor.kRed)
         SignalTestHistoNormed.SetLineStyle(2)
         SignalTestHistoNormed.GetXaxis().SetTitle("Reco p_{T}")
         SignalTestHistoNormed.SetTitle("Signal and background versus p_{T} for %s" % computerName)

         BackgroundTestHistoNormed = BackgroundTestHisto.ProjectionX("bkg").DrawNormalized("same")
         BackgroundTestHistoNormed.SetLineColor(EColor.kBlue)
         BackgroundTestHistoNormed.SetLineStyle(2)

         upperLimit = more(SignalTestHistoNormed.GetMaximum(), BackgroundTestHistoNormed.GetMaximum())

         SignalTestHistoNormed.GetYaxis().SetRangeUser(0, upperLimit*1.1)

         # weighting pt projection
         TestCanvas.cd(2)
         WeightProj.Draw()
         WeightProj.SetTitle("Weight versus p_{T} (projection)")
         WeightProj.GetXaxis().SetTitle("Reco p_{T}")
         gPad.SetLogx(True)

         # sig/bkg projections, after weighting
         TestCanvas.cd(3)

         SignalWeightedHisto     = SignalTestHisto.Clone() 
         BackgroundWeightedHisto = BackgroundTestHisto.Clone()

         for xBin in xrange(1, SignalWeightedHisto.GetNbinsX()+1):
            xValue = SignalWeightedHisto.GetXaxis().GetBinCenter(xBin)
            for yBin in xrange(1, SignalWeightedHisto.GetNbinsY()+1):
               yValue              = SignalWeightedHisto.GetYaxis().GetBinCenter(yBin)
               theWeight           = WeightHisto.GetBinContent(WeightHisto.FindBin(xValue, yValue))
               theSignalWeight     = SignalWeightHisto.GetBinContent(WeightHisto.FindBin(xValue, yValue))
               theBackgroundWeight = BackgroundWeightHisto.GetBinContent(WeightHisto.FindBin(xValue, yValue))
               #theSignalWeight = BackgroundHisto.GetBinContent(BackgroundHisto.FindBin(xValue, yValue))*1.0/BackgroundHisto.GetEntries()
               #theBackgroundWeight = SignalHisto.GetBinContent(SignalHisto.FindBin(xValue, yValue))*1.0/SignalHisto.GetEntries()
               SignalContent = SignalWeightedHisto.GetBinContent(xBin, yBin)
               BackgroundContent = BackgroundWeightedHisto.GetBinContent(xBin, yBin)
               #print "x: ", xValue, " y: ", yValue, " w: ", theWeight, " sig: ", SignalContent, " bkg: ", BackgroundContent
               SignalWeightedHisto.SetBinContent(xBin, yBin, SignalContent*theSignalWeight)
               BackgroundWeightedHisto.SetBinContent(xBin, yBin, BackgroundContent*theBackgroundWeight)

         SignalWeightedHistoNormed = SignalWeightedHisto.ProjectionX("siggo").DrawNormalized()
         SignalWeightedHistoNormed.SetLineColor(EColor.kRed)
         SignalWeightedHistoNormed.SetLineStyle(2)
         SignalWeightedHistoNormed.GetXaxis().SetTitle("Reco p_{T}")
         SignalWeightedHistoNormed.SetTitle("Reweighted Signal and background versus p_{T} for %s" % computerName)

         BackgroundWeightedHistoNormed = BackgroundWeightedHisto.ProjectionX("biggo").DrawNormalized("same")
         BackgroundWeightedHistoNormed.SetLineColor(EColor.kBlue)
         BackgroundWeightedHistoNormed.SetLineStyle(2)

         upperLimit = more(SignalWeightedHistoNormed.GetMaximum(), BackgroundWeightedHistoNormed.GetMaximum())

         SignalWeightedHistoNormed.GetYaxis().SetRangeUser(0, upperLimit*1.1)

         TestCanvas.cd(4)

         gPad.SetLogx(True)

         WeightHisto.Draw("box")
         WeightHisto.GetXaxis().SetTitle("Pt")
         WeightHisto.GetYaxis().SetTitle("Eta")
         WeightHisto.SetTitle("Weighting Histogram")

         TestCanvas.SaveAs("%s_%s.png" % (mvaCollectionName, computerName))

         del SignalTestHisto
         del BackgroundTestHisto
         del SignalWeightedHisto
         del BackgroundWeightedHisto
         del WeightProj

         #### END TESTING CODE ######

         print summaryString % (name, mvaCollectionName, computerName, SignalSubEntries, BackgroundSubEntries, WeightSum)

      # write our histograms
      for DecayMode, (SignalHisto, BackgroundHisto, WeightHisto, SignalWeightHisto, BackgroundWeightHisto) in DecayModeMap.iteritems():
         SignalHisto.Write()
         BackgroundHisto.Write()
         WeightHisto.Write()
         SignalWeightHisto.Write()
         BackgroundWeightHisto.Write()
