from ROOT import TLegend, TPaveText, TLine, gSystem, gDirectory, gROOT, TCanvas, gPad,TF1, TPad, TChain,TH1, TTree, TEventList, TEntryList, THStack, TColor, TFile, gStyle, TH2F

import os
import time
import sys

from RecoTauTag.TauTagTools.MVASteering_cfi import *
from MVAHelpers    import *
from TaNCCutFinder import *

"""
        MVABenchmarks.py
        Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

        Create performance plots of signal efficiency versus background fake rate
        for the samples used in training.
"""

#Plot multiple different algorithms, if desired.
algosToPlot = ["shrinkingConePFTauDecayModeProducer"]
#A list of the MVAs to compare
mvasToPlot  = ["TaNC", ]#"MultiNetIso", ]

# For each combination of algosToPlot & mvasToPlot the relevant TrainDir_* must exist
# and the training must have been completed.  These directories can be prepared with the
# PrepareForTraining.py script

# Define cuts on the signal objects
KinematicCut = "%(treeName)s.Pt > 20 && %(treeName)s.Pt < 50"  #%s refers to tree name substituton

# Define fake rate benchmark points
FakeRateBenchmarks = [ (0.01, 'OnePercent'),
                       (0.005, 'HalfPercent'),
                       (0.0025, 'QuarterPercent'),
                       (0.001, 'TenthPercent') ]
#BenchmarkPoints = [ 0.01, 0.005, 0.0025, 0.001 ]
BenchmarkPoints = [ value for value, name in FakeRateBenchmarks ]

FakeRatePlotLowerBound = 0.0001  # hopefully this number shrinks!

# Cut label on the plots
CutLabel = TPaveText(0.15, 0.65, 0.4, 0.8, "brNDC")
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

BenchmarkFilePath = os.path.join(TauTagToolsWorkingDirectory, "python/BenchmarkPointCuts_cfi.py")
if os.path.exists(BenchmarkFilePath):
   stringifyTime = time.strftime("%d_%b_%H:%M", time.localtime())
   print "Backing up ../python/BenchmarkPointCuts_cfi.py to ./BenchmarkPointCuts_cfi.py.%s" % stringifyTime
   os.system("cp %s ./BenchmarkPointCuts_cfi.py.%s" % (BenchmarkFilePath, stringifyTime))

BenchmarkFile = open(BenchmarkFilePath, 'w')

#Get Truth info
SignalTruthTree     = dataFile.Get("truth_Signal")
BackgroundTruthTree = dataFile.Get("truth_Background")
SignalTruthTree.SetCacheSize(0)
BackgroundTruthTree.SetCacheSize(0)
SignalTruthTreeEntries = SignalTruthTree.GetEntries()
BackgroundTruthTreeEntries = BackgroundTruthTree.GetEntries()

colorCounter = 2

for algo in algosToPlot:
   SignalRecoTree     = dataFile.Get("%s_Signal" % algo)
   BackgroundRecoTree = dataFile.Get("%s_Background" % algo)
   SignalRecoTree.SetCacheSize(0)
   BackgroundRecoTree.SetCacheSize(0)

   #Get access to the corresponding truth data
   SignalRecoTree.AddFriend(SignalTruthTree)
   BackgroundRecoTree.AddFriend(BackgroundTruthTree)

   SignalRecoTree.AddFriend(SignalTruthTree)
   BackgroundRecoTree.AddFriend(BackgroundTruthTree)

   SignalRecoTreeEntries     = SignalRecoTree.GetEntries()
   BackgroundRecoTreeEntries = BackgroundRecoTree.GetEntries()

   #Build basic entry lists (things in the kinematic window)
   SignalRecoTree.Draw(">>KinematicWindowSignal", KinematicCut % { 'treeName' : "truth_Signal" }, "entrylist", 1000000)
   BackgroundRecoTree.Draw(">>KinematicWindowBackground", KinematicCut % { 'treeName' : "truth_Background" }, "entrylist", 1000000)
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

      SignalMVATreeEntries     = SignalMVATree.GetEntries()
      BackgroundMVATreeEntries = BackgroundMVATree.GetEntries()

      print "Checking to make sure Trees are the right size.."
      print "%-20s %15s %15s %15s" % ("", "Truth entries", "RECO entries", "MVA entries")
      checker = lambda x, y, z : x == y and (y == z and (True, "OK") or (False, "FAIL!")) or (False, "FAIL!")
      SignalCheckIt = checker(SignalTruthTreeEntries, SignalRecoTreeEntries, SignalMVATreeEntries)
      BackgroundCheckIt = checker(BackgroundTruthTreeEntries, BackgroundRecoTreeEntries, BackgroundMVATreeEntries)
      print "%-20s %15i %15s %15s %5s" % ("Signal", SignalTruthTreeEntries, SignalRecoTreeEntries, SignalMVATreeEntries, SignalCheckIt[1])
      print "%-20s %15i %15s %15s %5s" % ("Background", BackgroundTruthTreeEntries, BackgroundRecoTreeEntries, BackgroundMVATreeEntries, BackgroundCheckIt[1])
      if not SignalCheckIt[0] or not BackgroundCheckIt[0]:
         raise IOError,  ", either signal or background Truth/Reco/MVA trees are out of sync!"

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

      if not ExcludePrepassAndPrefail:
         SignalPrePassCount     = 0
         BackgroundPrePassCount = 0
         SignalPreFailCount     = 0
         BackgroundPreFailCount = 0

      NonPreFailList         = set([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14])

      # A list of MVA names, percent of total set the sample composes, and 
      # an interpolated TGraph for signal and background given eff/fakerate for
      # different MVA operating point
      MVAEfficiencyCurves    = []

      #count entries that are acted on by the MVA
      TancDecayMode.TotalPreselectedSignalEntries     = 0
      TancDecayMode.TotalPreselectedBackgroundEntries = 0

      ThrowAwayCutList = "(!__ISNULL__ && DecayMode >= 15)"  #always throw away greater than 3 prong

      # Hold a list of TaNC decay modes
      TaNCDecayModes = []
      # The TancDecayMode class needs to know (statically) how many total sig/bkg entries there are
      TancDecayMode.TotalSignalEntries     = TotalSignalEntries
      TancDecayMode.TotalBackgroundEntries = TotalBackgroundEntries
      TancDecayMode.TotalSignalPrepass     = SignalPrePassCount
      TancDecayMode.TotalBackgroundPrepass = BackgroundPrePassCount

      for aComputer in mvaCollection:
         # The 'computer' is a cms.PSET, defined originally in 
         # RecoTauTag/TauTagTools/python/TauMVAConfigurations_cfi.py
         computerName  = aComputer.computerName.value()
         DecayModeList = aComputer.decayModeIndices.value()
         DecayModeCuts = BuildCutString(DecayModeList)
         DecayModeCuts += " && %s " % LeadPionRequirementString
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
            DecayModeCuts += " && %s" % IsolationCutForTraining

         print DecayModeCuts

         # keep track of the remaining possible decay modes. At the end of the day, any decay modes
         # not removed from this list will be marked as failed
         NonPreFailList     = NonPreFailList - DecayModeSet

         # Get MVA output histogram
         SignalDrawString     = GetTTreeDrawString("%s.MVA" % SignalMVATreeName, '%s_%s' % (SignalMVATreeName, computerName))
         BackgroundDrawString = GetTTreeDrawString("%s.MVA" % BackgroundMVATreeName, '%s_%s' % (BackgroundMVATreeName, computerName))

         SignalEntries        = SignalRecoTree.Draw(SignalDrawString, DecayModeCuts, "goff")
         BackgroundEntries    = BackgroundRecoTree.Draw(BackgroundDrawString, DecayModeCuts, "goff")
         TancDecayMode.TotalPreselectedSignalEntries     += SignalEntries
         TancDecayMode.TotalPreselectedBackgroundEntries += BackgroundEntries
         SignalHist           = gDirectory.Get("%s_%s" % (SignalMVATreeName, computerName))
         BackgroundHist       = gDirectory.Get("%s_%s" % (BackgroundMVATreeName, computerName))

         DecayModeToAdd = TancDecayMode(computerName, DecayModeList, SignalHist, BackgroundHist)
         TaNCDecayModes.append(DecayModeToAdd)
         #SignalEffCurve       = MakeEfficiencyCurveFromHistogram(SignalHist)
         #BackgroundEffCurve   = MakeEfficiencyCurveFromHistogram(BackgroundHist)
         #MVAEfficiencyCurves.append( (computerName, SignalEntries, BackgroundEntries, SignalEffCurve, BackgroundEffCurve, SignalHist, BackgroundHist) )
      #Get entries that are either thrown away via decay mode or isolation
      if len(ThrowAwayCutList) > 0:
         ThrowAwayCutList += " || "
      # These decaymodes are throw away, regardless of isolation
      ThrowAwayCutList += "(" + BuildCutString(list(NonPreFailList))
      ThrowAwayCutList += ") || "
      ThrowAwayCutList += "(!(%s) && !__ISNULL__)" % LeadPionRequirementString 

      print ThrowAwayCutList

      # Catch the number of entries we throw away
      SignalThrownAway     = SignalRecoTree.Draw( "Pt",  ThrowAwayCutList, "goff")
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

      for aDecayMode in TaNCDecayModes:
         print SummaryFormatString % (aDecayMode.Name, aDecayMode.NSignal, aDecayMode.NSignal*100.0/aDecayMode.TotalSignalEntries, 
                                      aDecayMode.NBackground, aDecayMode.NBackground*100.0/aDecayMode.TotalBackgroundEntries)
      for aDecayMode in TaNCDecayModes:
         print aDecayMode.Name, aDecayMode.MinMaxTuple

      SanityCheckSignal     = SignalNULLCount     + SignalPreFailCount     + SignalPrePassCount     + SignalThrownAway     + TancDecayMode.TotalPreselectedSignalEntries
      SanityCheckBackground = BackgroundNULLCount + BackgroundPreFailCount + BackgroundPrePassCount + BackgroundThrownAway + TancDecayMode.TotalPreselectedBackgroundEntries
      print SummaryFormatString % ("Total (check):", SanityCheckSignal, SanityCheckSignal*100.0/TotalSignalEntries, SanityCheckBackground, SanityCheckBackground*100.0/TotalBackgroundEntries)
      #OpCurve = MakeOperatingPointCurveByMonteCarlo(TaNCDecayModes, 5000000)
      #OpCurve = MakeOperatingPointCurveByMonteCarlo(TaNCDecayModes,  5000000)
      #OpCurve = MakeOperatingPointCurveByMonteCarlo(TaNCDecayModes,  500000)
      OpCurve = MakeOperatingPointCurveByMonteCarlo(TaNCDecayModes,  int(sys.argv[1]))

      print "Storing cut points for %s in %s..." % (mvaName, BenchmarkFilePath) 
      print ""
      print "------BMP Cut Summary----------"
      BenchmarkPointCutSummaryString = "%15s %10s %10s"
      HeaderStringTuple = ("", "Fake Rate", "SignalEff")
      for aDM in TancSet.DecayModeList:
         BenchmarkPointCutSummaryString += " %20s"
         HeaderStringTuple += (aDM.Name,)
      print BenchmarkPointCutSummaryString % HeaderStringTuple

      for aBMP, BMPName in FakeRateBenchmarks:
         #meta python
         NewDictName = "CutSet_%s_%s" % (mvaName, BMPName)
         BenchmarkFile.write("%s = {}\n" % NewDictName)
         # Get the cuts for this point 
         CutsForThisNetThisBMP = OpCurve.GetCutForFakeRate(aBMP)

         SummaryTuple = (BMPName, "%0.3f%%" % (100*CutsForThisNetThisBMP.EstimatedFakeRate), "%0.1f%%" % (100*CutsForThisNetThisBMP.EstimatedEfficiency),)

         GetInterestingStuff = [ (aDM.Name, cut) for aDM, cut in zip(CutsForThisNetThisBMP.DecayModeList, CutsForThisNetThisBMP.TancCuts) ] 
         for NameKey, CutValue in GetInterestingStuff:
            SummaryTuple += ("%0.4f" % CutValue,)
            BenchmarkFile.write("%s['%s']\t\t = %f\n" % (NewDictName, NameKey, CutValue))
         print BenchmarkPointCutSummaryString % SummaryTuple
         BenchmarkFile.write("\n")

      Envelope, EnvelopeInverted = OpCurve.GetOpCurveTGraph()
      c1 = TCanvas()

      # Let's only use nice colors
      ColorIndexes = [2,3,4,6,7,8,9]

      CutCurveLegend = TLegend(0.2, 0.15, 0.62, 0.4)
      CutCurveLegend.SetFillColor(0)

      VeelkenVsEffCurves       = []
      StandardVsEffCurves      = []
      VeelkenVsFakeRateCurves  = []
      StandardVsFakeRateCurves = []
      VeelPointsVsFakeRateCurves = []

      for color, aDM in zip(ColorIndexes, TancSet.DecayModeList):
         more = lambda x, y: x > y and x or y 
         gPad.SetLogy(False)
         maxValue = more(aDM.SignalMVAOut.GetMaximum()*1.0/aDM.SignalMVAOut.GetEntries(), aDM.BackgroundMVAOut.GetMaximum()*1.0/aDM.BackgroundMVAOut.GetEntries())
         normedHist = aDM.SignalMVAOut.DrawNormalized()
         normedHist.GetYaxis().SetRangeUser(0, maxValue)
         aDM.BackgroundMVAOut.DrawNormalized("same")
         c1.SaveAs("Plots/%s_NN_dist_%s.pdf" % (aDM.Name, mvaName))

         NewVeelkenVsEffCurve       = TGraph(len(OpCurve.TancSets))
         NewStandardVsEffCurve      = TGraph(len(OpCurve.TancSets))
         NewVeelkenVsFakeRateCurve  = TGraph(len(OpCurve.TancSets))
         NewStandardVsFakeRateCurve = TGraph(len(OpCurve.TancSets))
         NewVeelPointsVsFakeRateCurve = TGraph(len(OpCurve.TancSets))

         NewVeelkenVsEffCurve.SetLineColor(color)
         NewStandardVsEffCurve.SetLineColor(color)
         NewVeelkenVsFakeRateCurve.SetLineColor(color)
         NewStandardVsFakeRateCurve.SetLineColor(color)
         NewVeelPointsVsFakeRateCurve.SetLineColor(color)

         CutCurveLegend.AddEntry(NewVeelkenVsEffCurve, "%20s-QCD:%0.2f%%-Sig:%0.2f%%" % (aDM.Name, aDM.GetBackgroundFractionOfPreselection()*100.0, aDM.GetSignalFractionOfPreselection()*100.0), "l")
         VeelkenVsEffCurves.append(NewVeelkenVsEffCurve)
         StandardVsEffCurves.append(NewStandardVsEffCurve)
         VeelkenVsFakeRateCurves.append(NewVeelkenVsFakeRateCurve)
         StandardVsFakeRateCurves.append(NewStandardVsFakeRateCurve)
         VeelPointsVsFakeRateCurves.append(NewVeelPointsVsFakeRateCurve)

      # parameterize NN cuts from op curve by Eff & fake rate
      for index, aSet in enumerate(OpCurve.TancSets):
         EfficiencyAtPoint = aSet.EstimatedEfficiency
         FakeRateAtPoint   = aSet.EstimatedFakeRate
#         for cutIndex, cut in enumerate(aSet.TancCuts):            #from 31X??
         for cutIndex, cut in enumerate(aSet.GetRescaledCuts()):  
            StandardVsEffCurves[cutIndex].SetPoint(index, EfficiencyAtPoint, cut)
            StandardVsFakeRateCurves[cutIndex].SetPoint(index, FakeRateAtPoint, cut)
         for cutIndex, cut in enumerate(aSet.GetVeelkenNormalization()):
            VeelkenVsEffCurves[cutIndex].SetPoint(index, EfficiencyAtPoint, cut)
            VeelkenVsFakeRateCurves[cutIndex].SetPoint(index, FakeRateAtPoint, cut)
#         for cutIndex, point in enumerate(aSet.GetVeelkenPoints()):
#            VeelPointsVsFakeRateCurves[cutIndex].SetPoint(index, FakeRateAtPoint, point)

      outputFile = TFile("MVABenchmarkOperatingCurve.root", "RECREATE")
      Envelope.SetName("%s_PerformanceCurve" % mvaName)
      Envelope.Write()

      gPad.SetLogy(False)
      gPad.SetLogx(False)
      VeelkenVsEffCurves[0].Draw("AC")
      VeelkenVsEffCurves[0].GetHistogram().GetYaxis().SetRangeUser(0.7, 1)
      VeelkenVsEffCurves[0].GetHistogram().SetTitle("Transormed cut values versus efficiency")
      VeelkenVsEffCurves[0].GetHistogram().GetYaxis().SetTitle("NNet cut")
      VeelkenVsEffCurves[0].GetHistogram().GetYaxis().CenterTitle()
      VeelkenVsEffCurves[0].GetHistogram().GetXaxis().SetTitle("SignalEfficiency")

      for i in range(1, len(VeelkenVsEffCurves)):
         VeelkenVsEffCurves[i].Draw("same")
      CutCurveLegend.Draw()
      c1.Print("Plots/VeelkenVsEff_%s.pdf" % mvaName)

      StandardVsEffCurves[0].Draw("AC")
      StandardVsEffCurves[0].GetHistogram().GetYaxis().SetRangeUser(0.7, 1)
      StandardVsEffCurves[0].GetHistogram().SetTitle("Raw cut values versus efficiency")
      StandardVsEffCurves[0].GetHistogram().GetYaxis().SetTitle("NNet cut")
      StandardVsEffCurves[0].GetHistogram().GetYaxis().CenterTitle()
      StandardVsEffCurves[0].GetHistogram().GetXaxis().SetTitle("SignalEfficiency")

      for i in range(1, len(StandardVsEffCurves)):
         StandardVsEffCurves[i].Draw("same")
      CutCurveLegend.Draw()
      c1.Print("Plots/StandardVsEff_%s.pdf" % mvaName)

      gPad.SetLogy(False)
      gPad.SetLogx(True)
      VeelkenVsFakeRateCurves[0].Draw("AC")
      VeelkenVsFakeRateCurves[0].GetHistogram().GetYaxis().SetRangeUser(0.7, 1)
      VeelkenVsFakeRateCurves[0].GetHistogram().SetBins(1, 0.0001, 0.015)
      VeelkenVsFakeRateCurves[0].GetHistogram().SetTitle("Transormed cut values versus fake rate")
      VeelkenVsFakeRateCurves[0].GetHistogram().GetYaxis().SetTitle("NNet cut")
      VeelkenVsFakeRateCurves[0].GetHistogram().GetYaxis().CenterTitle()
      VeelkenVsFakeRateCurves[0].GetHistogram().GetXaxis().SetTitle("QCD fake rate")

      for i in range(1, len(VeelkenVsFakeRateCurves)):
         VeelkenVsFakeRateCurves[i].Draw("same")
      CutCurveLegend.Draw()
      c1.Print("Plots/VeelkenVsFakeRate_%s.pdf" % mvaName)

      StandardVsFakeRateCurves[0].Draw("AC")
      StandardVsFakeRateCurves[0].GetHistogram().GetYaxis().SetRangeUser(0.7, 1)
      StandardVsFakeRateCurves[0].GetHistogram().SetBins(1, 0.0001, 0.015)
      StandardVsFakeRateCurves[0].GetHistogram().SetTitle("Raw cut values versus fake rate")
      StandardVsFakeRateCurves[0].GetHistogram().GetYaxis().SetTitle("NNet cut")
      StandardVsFakeRateCurves[0].GetHistogram().GetYaxis().CenterTitle()
      StandardVsFakeRateCurves[0].GetHistogram().GetXaxis().SetTitle("QCD fake rate")

      for i in range(1, len(StandardVsFakeRateCurves)):
         StandardVsFakeRateCurves[i].Draw("same")
      CutCurveLegend.Draw()
      c1.Print("Plots/StandardVsFakeRate_%s.pdf" % mvaName)

      VeelPointsVsFakeRateCurves[0].Draw("AC")
#      VeelPointsVsFakeRateCurves[0].GetHistogram().GetYaxis().SetRangeUser(0.4, 1)
      VeelPointsVsFakeRateCurves[0].GetHistogram().SetTitle("Transformed bin content versus fake rate")
      VeelPointsVsFakeRateCurves[0].GetHistogram().GetYaxis().SetTitle("SigBin*rhoSig/QCDBin*rhoQCD")
      VeelPointsVsFakeRateCurves[0].GetHistogram().GetYaxis().CenterTitle()
      VeelPointsVsFakeRateCurves[0].GetHistogram().GetXaxis().SetTitle("QCD fake rate")

      for i in range(1, len(VeelPointsVsFakeRateCurves)):
         VeelPointsVsFakeRateCurves[i].Draw("same")
      CutCurveLegend.Draw()
      c1.Print("Plots/VeelPointsVsFakeRate_%s.pdf" % mvaName)

      #Make histogram to hold axis, title settings, etc
      MCHisto = TH2F("%s_%s_histo" % (algo, mvaName), "%s_%s_histo" % (algo, mvaName),500, 0.0, 1.0, 1500, FakeRatePlotLowerBound, 0.1)
      MCHisto.GetXaxis().SetTitle("Signal Efficiency")
      MCHisto.GetYaxis().SetTitle("Fake Rate")
      MCHisto.GetYaxis().CenterTitle()
      algoNiceName = algo.replace("pfTauDecayMode", "")
      MCHisto.SetTitle("Efficiency. vs. Fake Rate (%s) (%s)" % (algoNiceName, mvaName))

      #Draw summary curves
      Envelope.SetLineColor(46)

      BackgroundPrePassFakeRate = BackgroundPrePassCount*1.0/TotalBackgroundEntries
      BackgroundPrePassLine = TLine(0, BackgroundPrePassFakeRate, 1, BackgroundPrePassFakeRate)
      BackgroundPrePassLine.SetLineColor(1)
      BackgroundPrePassLine.SetLineStyle(2)

      # Compare to classic cuts
      ClassicFixed = TGraph(1)
      ClassicFixed.SetPoint(0, 0.46, 0.016)
      ClassicFixed.SetMarkerStyle(29)
      ClassicFixed.SetMarkerSize(3)

      ClassicShrinking = TGraph(1)
      ClassicShrinking.SetPoint(0, 0.525, 0.04)
      ClassicShrinking.SetMarkerStyle(23)
      ClassicShrinking.SetMarkerSize(2.5)


      BenchmarksToDraw = []
      BMPColorIndex = 2
      for aBenchMark in BenchmarkPoints:
         effAtPoint = EnvelopeInverted.Eval(aBenchMark) #FindOperatingPointEfficency(MCHisto, aBenchMark)
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
      if ExcludePrepassAndPrefail:
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

      ClassicFixed.Draw("p")
      ClassicShrinking.Draw("p")
      MyLegend.AddEntry(ClassicFixed, "Classic fixed cone", "p")
      MyLegend.AddEntry(ClassicShrinking, "Classic shrinking cone", "p")

      MyLegend.Draw()
      CutLabel.Draw()

      c1.Print("Plots/%s_%s.pdf" % (algoNiceName, mvaName))

      Envelope.SetLineColor(colorCounter)
      colorCounter += 1
      SummaryGraphs.append(Envelope)
      SummaryLegend.AddEntry(Envelope,"%s" %  mvaName, "l")

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

c1.Print("Plots/Summary.pdf")


