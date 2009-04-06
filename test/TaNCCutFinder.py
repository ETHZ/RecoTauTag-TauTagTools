#Get ROOT globals
from ROOT import gSystem, gDirectory, gROOT, gStyle, gPad
#Get TTree stuff
from ROOT import TTree, TEntryList, TChain, TFile
#Get plotting stuff
from ROOT import TGraph, TH1F, TH2F, TCanvas, TPad, TLegend, TPaveText, TLine, EColor, TF1, TGraph, TGraphAsymmErrors

import os
import random

from RecoTauTag.TauTagTools.MVASteering_cfi import *
from MVAHelpers import *

"""
        TaNCCutFinder.py
        Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

        Create performance plots of signal efficiency versus background fake rate
        for the samples. 
"""

def MakeOperatingPointCurveByMonteCarlo(TancDecayModeList, MonteCarloIterations, MaxPoints = 7000):
   ''' Takes set of N MVA Efficiency curves for for individual MVA points, and the number of tau candidates associated with them
       Throws [MonteCarloIterations] sets of N random numbers, computes the sig. eff & fake rate for that point, and adds it to the output histogram.'''

   TancSet.DecayModeList = TancDecayModeList
   OutputCurve = TancOperatingCurve()
   PointsAdded = 0
   ReportEvery = MonteCarloIterations / 35
   print "Doing %i Monte Carlo iterations on operating points" % MonteCarloIterations
   for MCIter in xrange(0, MonteCarloIterations):
      if not MCIter % ReportEvery:
         print "%0.02f%% complete - %i points added, %i in curve" % ( (MCIter*100.0/MonteCarloIterations),
                                                                      PointsAdded,
                                                                      len(OutputCurve.TancSets) )
      if len(OutputCurve.TancSets) > MaxPoints:
         break
      # Get a random cut for each decay mode
      cuts = [random.uniform(dm.MinMaxTuple[0], dm.MinMaxTuple[1]) for dm in TancSet.DecayModeList]
      # The TancSet takes care of determing the efficiency, etc
      NewSet = TancSet(cuts)
      PointsAdded += OutputCurve.InsertOperatingPoint(NewSet)
   print "Filling out low end."
   for MCIter in xrange(0, MonteCarloIterations):
      # Get on of the best 50 points
      if not MCIter % ReportEvery:
         print "%0.02f%% complete - %i points added, %i in curve" % ( (MCIter*100.0/MonteCarloIterations),
                                                                      PointsAdded,
                                                                      len(OutputCurve.TancSets) )
      if len(OutputCurve.TancSets) > MaxPoints:
         break
      less = lambda x, y: x < y and x or y
      # Pick a random point in the curve, and throw points around it's point in ND space
      TempTancSet = OutputCurve.TancSets[random.randint(0, len(OutputCurve.TancSets)-1)]
      cuts = [random.gauss(OldCut, less(abs(OldCut - dm.MinMaxTuple[0]), abs(OldCut - dm.MinMaxTuple[1]))/10.0) for OldCut, dm in zip(TempTancSet.TancCuts, TempTancSet.DecayModeList)]
      NewSet = TancSet(cuts)
      PointsAdded += OutputCurve.InsertOperatingPoint(NewSet)
   return OutputCurve

