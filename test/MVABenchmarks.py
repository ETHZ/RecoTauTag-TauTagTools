from ROOT import TLegend, TPaveText, TLine, gSystem, gDirectory, gROOT, TCanvas, gPad,TF1, TPad, TChain,TH1, TTree, TEventList, TEntryList, THStack, TColor, TFile, gStyle, TH2F

import os

from MVASteering import *
import MVASteering
from MVAHelpers  import *

"""
        MVABenchmarks.py
        Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

        Create performance plots of signal efficiency versus background fake rate
        for the samples used in training.
"""

#Plot multiple different algorithms, if desired.
algosToPlot = ["pfTauDecayModeHighEfficiency"]
mvasToPlot  = ["SingleNetIso", "SingleNet", "MultiNet", "MultiNetIso"]

# For each combination of algosToPlot & mvasToPlot the relevant TrainDir_* must exist
# and the training must have been completed

# Define cuts on the signal objects
KinematicCut = "%(treeName)s.Pt > 20 && %(treeName)s.Pt < 50"  #%s refers to tree name substituton

# Define fake rate benchmark points
BenchmarkPoints = [ 0.01, 0.005, 0.0025, 0.001 ]
FakeRatePlotLowerBound = 0.0005  # hopefully this number shrinks!

# Cut label on the plots
CutLabel = TPaveText(0.2, 0.7, 0.4, 0.8, "brNDC")
CutLabel.AddText("20 GeV/c < True p_{T} < 50 GeV/c")


CutLabel.SetFillStyle(0)
CutLabel.SetBorderSize(0)

gROOT.SetBatch(True)
gROOT.SetStyle("Plain")
gStyle.SetOptStat(0)
gStyle.SetPalette(1)
gStyle.SetTitleBorderSize(0)

dataFile = TFile("MVAOutput.root", "READ")

SummaryGraphs = []
SummaryLegend = TLegend(0.7, 0.15, 0.92, 0.5)
SummaryLegend.SetFillColor(0)
SummaryBackground = 0

if not os.path.exists("Plots"):
   os.mkdir("Plots")

#Get Truth info
SignalTruthTree     = dataFile.Get("truth_Signal")
BackgroundTruthTree = dataFile.Get("truth_Background")

colorCounter = 2

for algo in algosToPlot:
   SignalRecoTree     = dataFile.Get("%s_Signal" % algo)
   BackgroundRecoTree = dataFile.Get("%s_Background" % algo)
   #Get access to the corresponding truth data
   SignalRecoTree.AddFriend(SignalTruthTree)
   BackgroundRecoTree.AddFriend(BackgroundTruthTree)

   #Build basic entry lists (things in the kinematic window)
   SignalRecoTree.Draw(">>KinematicWindowSignal", KinematicCut % { 'treeName' : "truth_Signal" }, "entrylist")
   BackgroundRecoTree.Draw(">>KinematicWindowBackground", KinematicCut % { 'treeName' : "truth_Background" }, "entrylist")
   SignalEntryList     = gDirectory.Get("KinematicWindowSignal")
   BackgroundEntryList = gDirectory.Get("KinematicWindowBackground")

   TotalSignalEntries     = SignalEntryList.GetN();
   TotalBackgroundEntries = BackgroundEntryList.GetN();
   print "Found %i signal and %i background truth objects in the kinematic window." % (TotalSignalEntries, TotalBackgroundEntries)

   #only use the kinematic window entries
   SignalRecoTree.SetEntryList(SignalEntryList)
   BackgroundRecoTree.SetEntryList(BackgroundEntryList)

   for mvaName in mvasToPlot:
      #Get the MVA
      mvaCollection         = MVACollections[mvaName]
      SignalMVATreeName     = "%s_Signal_MVAOutput_%s"     % (algo, mvaName)
      BackgroundMVATreeName = "%s_Background_MVAOutput_%s" % (algo, mvaName)
      SignalMVATree         = gDirectory.Get(SignalMVATreeName)
      BackgroundMVATree     = gDirectory.Get(BackgroundMVATreeName)
      SignalRecoTree.AddFriend(SignalMVATree)
      BackgroundRecoTree.AddFriend(BackgroundMVATree)
      """
      Get the MVA distributions for the appropriate decay modes
      The goal is to find an operating point (multi dimensional for multinet)
      Split the samples into the following sets:
        -NULL     (ie, lead track finding failed, or nothing at all was reconstructed)
        -PrePass  (Single, completely isolated pions.  These are set to pass, as there is no
                  discriminating information)
        -Prefail  (Fails initial multiplicity cuts)
        -A set for each MVA used
        -The remaining decay modes not associated w/ an MVA (2-prongs, etc)
      """

      SignalNULLCount        = SignalRecoTree.Draw(     "Pt" , "__ISNULL__"  , "goff" )
      BackgroundNULLCount    = BackgroundRecoTree.Draw( "Pt" , "__ISNULL__"  , "goff" )
      SignalPrePassCount     = SignalRecoTree.Draw(     "Pt" , "__PREPASS__" , "goff" )
      BackgroundPrePassCount = BackgroundRecoTree.Draw( "Pt" , "__PREPASS__" , "goff" )
      SignalPreFailCount     = SignalRecoTree.Draw(     "Pt" , "__PREFAIL__" , "goff" )
      BackgroundPreFailCount = BackgroundRecoTree.Draw( "Pt" , "__PREFAIL__" , "goff" )

      NonPreFailList         = set([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])

      # A list of MVA names, percent of total set the sample composes, and 
      # an interpolated TGraph for signal and background given eff/fakerate for
      # different MVA operating point
      MVAEfficiencyCurves    = []

      #count entries that are acted on by the MVA
      SignalMVAEntries     = 0
      BackgroundMVAEntries = 0

      ThrowAwayCutList = ""

      for aComputer in mvaCollection:
         # The 'computer' is a cms.PSET, defined originally in 
         # RecoTauTag/TauTagTools/python/TauMVAConfigurations_cfi.py
         computerName  = aComputer.computerName.value()
         DecayModeList = aComputer.decayModeIndices.value()
         DecayModeCuts = BuildCutString(DecayModeList)
         DecayModeSet = set(DecayModeList)

         if aComputer.applyIsolation.value():
            #Add non-isolated instances of one of these decay modes to the throw away cuts
            if len(ThrowAwayCutList) > 0:
               ThrowAwayCutList += " || "
            ThrowAwayCutList += "(("
            ThrowAwayCutList += DecayModeCuts 
            ThrowAwayCutList += ")"
            ThrowAwayCutList += " && !(%s))" % IsolationCutForTraining
            #Add the isolation requirement to the cuts string for determining MVA performace
            DecayModeCuts += " && %s" % MVASteering.IsolationCutForTraining

         # keep track of the remaining possible decay modes. At the end of the day, any decay modes
         # not removed from this list will be marked as failed
         NonPreFailList     = NonPreFailList - DecayModeSet

         # Get MVA output histogram
         SignalDrawString     = GetTTreeDrawString("%s.MVA" % SignalMVATreeName, '%s_%s' % (SignalMVATreeName, computerName))
         BackgroundDrawString = GetTTreeDrawString("%s.MVA" % BackgroundMVATreeName, '%s_%s' % (BackgroundMVATreeName, computerName))

         SignalEntries        = SignalRecoTree.Draw(SignalDrawString, DecayModeCuts, "goff")
         BackgroundEntries    = BackgroundRecoTree.Draw(BackgroundDrawString, DecayModeCuts, "goff")
         SignalMVAEntries     += SignalEntries
         BackgroundMVAEntries += BackgroundEntries
         SignalHist           = gDirectory.Get("%s_%s" % (SignalMVATreeName, computerName))
         BackgroundHist       = gDirectory.Get("%s_%s" % (BackgroundMVATreeName, computerName))
         SignalEffCurve       = MakeEfficiencyCurveFromHistogram(SignalHist)
         BackgroundEffCurve   = MakeEfficiencyCurveFromHistogram(BackgroundHist)
         MVAEfficiencyCurves.append( (computerName, SignalEntries, BackgroundEntries, SignalEffCurve, BackgroundEffCurve, SignalHist, BackgroundHist) )

      #Get entries that are either thrown away via decay mode or isolation
      if len(ThrowAwayCutList) > 0:
         ThrowAwayCutList += " || "

      # These decaymodes are throw away, regardless of isolation
      ThrowAwayCutList += BuildCutString(list(NonPreFailList))

      SignalThrownAway = SignalRecoTree.Draw( "Pt",  ThrowAwayCutList, "goff")
      BackgroundThrownAway = BackgroundRecoTree.Draw( "Pt", ThrowAwayCutList, "goff")

      SummaryHeaderString    = "%-20s %10s %10s %10s %10s"
      SummaryFormatString    = "%-20s %10i %10.02f%% %10i %10.02f%%"

      print "Summary:  MVA Config: %s Algorithm: %s" % (mvaName, algo)
      print "----------------------------------------------------------------------"
      print SummaryHeaderString % ("Type:", "Signal", "Signal%", "Bckgrnd", "Bkg%")
      print "----------------------------------------------------------------------"
      print SummaryFormatString % ("Total"     , TotalSignalEntries , 100.00                                      , TotalBackgroundEntries , 100.00)
      print SummaryFormatString % ("Null"      , SignalNULLCount    , SignalNULLCount*100.0/TotalSignalEntries    , BackgroundNULLCount    , BackgroundNULLCount*100.0/TotalBackgroundEntries)
      print SummaryFormatString % ("PreFail"   , SignalPreFailCount , SignalPreFailCount*100.0/TotalSignalEntries , BackgroundPreFailCount , BackgroundPreFailCount*100.0/TotalBackgroundEntries)
      print SummaryFormatString % ("ThrowAway" , SignalThrownAway   , SignalThrownAway*100.0/TotalSignalEntries   , BackgroundThrownAway   , BackgroundThrownAway*100.0/TotalBackgroundEntries)
      print SummaryFormatString % ("PrePass"   , SignalPrePassCount , SignalPrePassCount*100.0/TotalSignalEntries , BackgroundPrePassCount , BackgroundPrePassCount*100.0/TotalBackgroundEntries)

      for ComputerName, SignalEntries, BackgroundEntries, SignalEffCurve, BackgroundEffCurve, SignalHist, BackgroundHist in MVAEfficiencyCurves:
         print SummaryFormatString % (ComputerName, SignalEntries, SignalEntries*100.0/TotalSignalEntries, BackgroundEntries, BackgroundEntries*100.0/TotalBackgroundEntries)

      SanityCheckSignal     = SignalNULLCount     + SignalPreFailCount     + SignalPrePassCount     + SignalThrownAway     + SignalMVAEntries
      SanityCheckBackground = BackgroundNULLCount + BackgroundPreFailCount + BackgroundPrePassCount + BackgroundThrownAway + BackgroundMVAEntries
      print SummaryFormatString % ("Total (check):", SanityCheckSignal, SanityCheckSignal*100.0/TotalSignalEntries, SanityCheckBackground, SanityCheckBackground*100.0/TotalBackgroundEntries)

      #Make histogram to store Monte Carlo'd operating points
      MCHisto = TH2F("%s_%s_histo" % (algo, mvaName), "%s_%s_histo" % (algo, mvaName),500, 0.0, 1.0, 1500, FakeRatePlotLowerBound, 0.03)
      MCHisto.GetXaxis().SetTitle("Signal Efficiency")
      MCHisto.GetYaxis().SetTitle("Fake Rate")
      MCHisto.GetYaxis().CenterTitle()
      algoNiceName = algo.replace("pfTauDecayMode", "")
      MCHisto.SetTitle("Efficiency. vs. Fake Rate (%s) (%s)" % (algoNiceName, mvaName))

      FindOperatingPointsByMonteCarlo(MVAEfficiencyCurves, TotalSignalEntries, SignalPrePassCount, TotalBackgroundEntries, BackgroundPrePassCount, MCHisto, 5000000)

      Envelope, EnvelopeInverted = MakeEnvelopeGraph(MCHisto)
      Envelope.SetLineColor(46)

      BackgroundPrePassFakeRate = BackgroundPrePassCount*1.0/TotalBackgroundEntries
      BackgroundPrePassLine = TLine(0, BackgroundPrePassFakeRate, 1, BackgroundPrePassFakeRate)
      BackgroundPrePassLine.SetLineColor(1)
      BackgroundPrePassLine.SetLineStyle(2)


      BenchmarksToDraw = []
      BMPColorIndex = 2
      for aBenchMark in BenchmarkPoints:
         effAtPoint = FindOperatingPointEfficency(MCHisto, aBenchMark)
         HorizontalLine = TLine(0, aBenchMark, effAtPoint, aBenchMark)
         VertLine       = TLine(effAtPoint, FakeRatePlotLowerBound, effAtPoint, aBenchMark)
         HorizontalLine.SetLineColor(BMPColorIndex)
         VertLine.SetLineColor(BMPColorIndex)
         HorizontalLine.SetLineStyle(2)
         VertLine.SetLineStyle(2)
         LegendString = "%0.03f%% BMP" % (aBenchMark*100.0)
         BMPColorIndex += 1
         BenchmarksToDraw.append( (LegendString, HorizontalLine, VertLine) )

      MyLegend = TLegend(0.7, 0.15, 0.92, 0.4)
      MyLegend.SetFillColor(0)
      MyLegend.AddEntry(BackgroundPrePassLine, "Prepass fake rate", "l")

      c1 = TCanvas()
      gPad.SetLogy()
      MCHisto.Reset()
      MCHisto.Draw()
      Envelope.Draw("L,same")
      BackgroundPrePassLine.Draw()
      for LegendString, HorizontalLine, VertLine in BenchmarksToDraw:
         HorizontalLine.Draw()
         VertLine.Draw()
         MyLegend.AddEntry(HorizontalLine, LegendString, "l")
      MyLegend.Draw()
      CutLabel.Draw()

      c1.Print("%s_%s.pdf" % (algoNiceName, mvaName))

      Envelope.SetLineColor(colorCounter)
      colorCounter += 1
      SummaryGraphs.append(Envelope)
      SummaryLegend.AddEntry(Envelope,"%s-%s" % (algoNiceName, mvaName), "l")

      #Build the axis titles, etc, if it doesn't a
      if SummaryBackground == 0:
         SummaryBackground = MCHisto
         SummaryBackground.SetTitle("MVA Performance Summary")

#Print the summary
SummaryBackground.Draw()
for aSummaryCurve in SummaryGraphs:
   aSummaryCurve.Draw("L,same")
SummaryLegend.Draw()
CutLabel.Draw()

c1.Print("Summary.pdf")


