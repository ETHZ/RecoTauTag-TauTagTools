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
less = lambda x, y: x < y and x or y

def LoopAndAddNewCuts(nIterations, OutputCurve, CutFunction):
   ''' 
   Do nIterations and add points to supplied TancCurve.  The CutFunction
   is method that determines how to randomly generate the candidate cuts
   '''
   ReportEvery = nIterations / 5
   for MCIter in xrange(0, nIterations):
      if not MCIter % ReportEvery:
         print "%0.02f%% complete - %i points added, %i in curve" % ( (MCIter*100.0/(nIterations)),
                                                                      OutputCurve.PointsAdded,
                                                                      len(OutputCurve.TancSets) )
      # Get a random cut for each decay mode
      #cuts = [random.uniform(dm.MinMaxTuple[0], dm.MinMaxTuple[1]) for dm in TancSet.DecayModeList]
      cuts = CutFunction(OutputCurve, TancSet.DecayModeList)
      # The TancSet takes care of determing the efficiency, etc
      NewSet = TancSet(cuts)
      OutputCurve.InsertOperatingPoint(NewSet)

# Monte Carlo functions to generate sets of cuts

def RandomCuts(aCurve, ListOfDecayModes):
   """ 
   Cut function to uniformaly generate cuts over the entire MVA output space.  Used to 
   initially rough out the TaNC performance curve
   """
   cuts = [random.uniform(decayMode.MinMaxTuple[0], decayMode.MinMaxTuple[1]) for decayMode in ListOfDecayModes]
   return cuts

def CutsAroundCurve(aCurve, ListOfDecayModes):
   """
   Cut function to throw cuts around already existing cuts along the entire length of
   the Tanc performance cuts.  The new cut candidates are distributed normally about the 
   previous ones with a width that is 1/5 of the distance to the nearest boundary (ie -1, 1)
   """
   randomIndex = int(random.uniform(0, len(aCurve.TancSets)-1))
   if randomIndex > len(aCurve.TancSets)-1:
      randomIndex = len(aCurve.TancSets)-1
   TancSetToThrowAround = aCurve.TancSets[randomIndex]
   cuts = [random.gauss(OldCut, less(abs(OldCut - dm.MinMaxTuple[0]), abs(OldCut - dm.MinMaxTuple[1]))/5) for OldCut, dm in zip(TancSetToThrowAround.TancCuts, TancSetToThrowAround.DecayModeList)]
   return cuts

def CutsAroundLowEnd(aCurve, ListOfDecayModes):
   """
   Similary to cuts around curve, but the width is 1/10 of the distance to the boundaries,
   and the existing points selected are chosen w/ a triangular distribution, favoring the low 
   fake rate end of the curve.
   """

   # Pick a random point in the curve, weighted triangularly (suboptimally) towards the low end, 
   # and throw points around it's point in ND space
   myrandom1 = random.uniform(0, len(aCurve.TancSets)-1) # xaxis
   myrandom2 = random.uniform(0, len(aCurve.TancSets)-1) # yaxis
   while myrandom1 > myrandom2:  # repeat until we are in the lower triangular portion
      myrandom1 = random.uniform(0, len(aCurve.TancSets)-1)
      myrandom2 = random.uniform(0, len(aCurve.TancSets)-1)
   #myrandom1 is now distributed triangularly
   randomIndex = int(myrandom1)
   if randomIndex > len(aCurve.TancSets)-1:
      randomIndex = len(aCurve.TancSets)-1
   TancSetToThrowAround = aCurve.TancSets[randomIndex]
   cuts = [random.gauss(OldCut, less(abs(OldCut - dm.MinMaxTuple[0]), abs(OldCut - dm.MinMaxTuple[1]))/10) for OldCut, dm in zip(TancSetToThrowAround.TancCuts, TancSetToThrowAround.DecayModeList)]
   return cuts

def MakeOperatingPointCurveByMonteCarlo(TancDecayModeList, MonteCarloIterations, MaxPoints = 7000):
   ''' Takes set of N MVA Efficiency curves for for individual MVA points, and the number of tau candidates associated with them
       Throws [MonteCarloIterations] sets of N random numbers, computes the sig. eff & fake rate for that point, and adds it to the output histogram.'''

   TancSet.DecayModeList = TancDecayModeList
   OutputCurve = TancOperatingCurve()
   Done = False
   ConvergenceLevel = 0
   PointsAddedAtLastIteration = 0
   ConvergenceTarget = 0.005 
   print "Roughing out curve..."
   LoopAndAddNewCuts(MonteCarloIterations, OutputCurve, RandomCuts)
   while not Done:
      PointsAddedAtLastIteration = OutputCurve.PointsAdded
      print "Filling out middle."
      LoopAndAddNewCuts(MonteCarloIterations, OutputCurve, CutsAroundCurve)
      print "Filling out low end."
      LoopAndAddNewCuts(MonteCarloIterations, OutputCurve, CutsAroundLowEnd)
      ConvergenceLevel = (OutputCurve.PointsAdded-PointsAddedAtLastIteration)*1.0/OutputCurve.PointsAdded
      print "Convergence level: %f Target: %f" % (ConvergenceLevel, ConvergenceTarget)
      if ConvergenceTarget > ConvergenceLevel:
         Done = True
   print "Done"
   return OutputCurve

