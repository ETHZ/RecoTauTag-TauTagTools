from ROOT import TGraph, TH1F
import random

"""
        MVAHelpers.py
        Author: Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

        Helper functions used in various TauTagTools::MVA training scripts
"""

def BuildCutString(decayModeList):
   ''' Format a cut string (for use in TTree::Draw) to select all decay modes given in the input decayModeList'''
   output = "!__PREFAIL__ && ("
   for index, aDecayMode in enumerate(decayModeList):
      if aDecayMode == 0:
         output += "(!__PREPASS__ && DecayMode == 0)"  #exclude isolated one prong taus from training, as there is no info
      else:
         output += "DecayMode == %i" % aDecayMode
      if index != len(decayModeList)-1:
         output += " || "
   output += ")"
   return output

def ComputeSeparation(SignalHistogram, BackgroundHistogram):
   ''' Computes statistical seperation between two histograms.  Output will be zero for identically shaped distributions
   and one for distributions with no overlap.'''
   output = 0.0
   nPoints = SignalHistogram.GetNBinsX()
   if nPoints != BackgroundHistogram.GetNBinsX():
      print "Signal and background histograms don't have the same number of points!"
      sys.exit(1)
   SignalEntries     = SignalHistogram.GetEntries()
   BackgroundEntries = BackgroundHistogram.GetEntries()
   for bin in range(1, nPoints+1):
      normalizedSignal = SignalHistogram.GetBinContent(bin)*1.0/SignalEntries
      normalizedBackground = BackgroundHistogram.GetBinContent(bin)*1.0/BackgroundEntries
      output += (normalizedSignal - normalizedBackground)*(normalizedSignal - normalizedBackground)/(normalizedSignal + normalizedBackground)
   return output/2.0

def BuildSingleEfficiencyCurve(SignalHistogram, SignalTotal, BackgroundHistogram, BackgroundTotal, colorIndex):
   ''' Return a TGraph mapping background efficiency to signal efficiencies of a cut applied on two distributions'''
   nPoints = SignalHistogram.GetNBinsX()
   if nPoints != BackgroundHistogram.GetNBinsX():
      print "Signal and background histograms don't have the same number of points!"
      sys.exit(1)
   output = TGraph(nPoints)
   SignalSum = 0.
   BackgroundSum = 0.
   for bin in range(1, nPoints+1):
      SignalSum     += SignalHistogram.GetBinContent(bin)
      BackgroundSum += BackgroundHistogram.GetBinContent(bin)
      SignalEff     =  (1.0*SignalSum)/SignalTotal
      BackgroundEff =  (1.0*BackgroundSum)/BackgroundTotal
      output.SetPoint(bin-1, SignalEff, BackgroundEff)
   return output

# Binning of all efficiency curves.  nBins must be large to accurately build the eff-fake rate curve
EfficiencyCurveBinning = { 'nBins' : 1000, 'xlow' : -2.0, 'xhigh' : 2.0 }

def GetTTreeDrawString(varexp, histoName, nBins = EfficiencyCurveBinning['nBins'], xlow = EfficiencyCurveBinning['xlow'], xhigh = EfficiencyCurveBinning['xhigh']):
   '''Format a TTree Draw->stored histo string.  ROOT is a mess!'''
   return "%(varexp)s>>%(histoName)s(%(nBins)i, %(xlow)f, %(xhigh)f)" % { 'varexp' : varexp, 'histoName' : histoName, 'nBins' : nBins, 'xlow' : xlow, 'xhigh' : xhigh }

def MakeEfficiencyCurveFromHistogram(histogram):
   '''Returns a graph of f(x), where f is percentage of entries in the histogram above x'''
   output = TGraph(histogram.GetNbinsX())
   normalization = histogram.GetEntries()
   integralSoFar = 0.
   for x in xrange(0, histogram.GetNbinsX()):
      integralSoFar += histogram.GetBinContent(x+1)*1.0/normalization
      output.SetPoint(x, histogram.GetBinCenter(x+1), 1.0-integralSoFar)
   return output

def FindOperatingPointsByMonteCarlo(MVAEfficiencyCurves, TotalSignalEntries, SignalPrepass, TotalBackgroundEntries, BackgroundPrepass, OutputHistogram, MonteCaroloIterations):
   ''' Takes set of N MVA Efficiency curves for for individual MVA points, and the number of tau candidates associated with them
       Throws [MonteCarloIterations] sets of N random numbers, computes the sig. eff & fake rate for that point, and adds it to the output histogram.'''
   maxFakeRate = 0.50
   computers = []
   for ComputerName, SignalEntries, BackgroundEntries, SignalEffCurve, BackgroundEffCurve, SignalHistogram, BackgroundHistogram in MVAEfficiencyCurves: 
      upperLimitOnMVAPoint = -10000
      lowerLimitOnMVAPoint = 10000
      for bin in range(1,SignalHistogram.GetNbinsX()+1):
         if SignalHistogram.GetBinContent(bin) + BackgroundHistogram.GetBinContent(bin) > 0:
            upperLimitOnMVAPoint = SignalHistogram.GetBinCenter(bin)
         if BackgroundEffCurve.Eval(BackgroundHistogram.GetBinCenter(bin)) > maxFakeRate:
            lowerLimitOnMVAPoint = BackgroundHistogram.GetBinCenter(bin)
      #repack
      ComputerInfo = (SignalEntries, SignalEffCurve, BackgroundEntries, BackgroundEffCurve, upperLimitOnMVAPoint, lowerLimitOnMVAPoint)
      computers.append(ComputerInfo)
   print "Doing %i Monte Carlo iterations on operating points" % MonteCaroloIterations
   reportEvery = MonteCaroloIterations/35;
   for iIter in xrange(0,MonteCaroloIterations):
      if iIter % reportEvery == 0:
         print "%0.02f%% complete" % (iIter*100.0/MonteCaroloIterations)
      SignalPassing     = SignalPrepass
      BackgroundPassing = BackgroundPrepass
      for SignalEntries, SignalEffCurve, BackgroundEntries, BackgroundEffCurve, upperLimit, lowerLimit in computers:
         #throw random cut
         randomCut         =  random.uniform(lowerLimit, upperLimit)
         SignalPassing     += SignalEntries*SignalEffCurve.Eval(randomCut)
         BackgroundPassing += BackgroundEntries*BackgroundEffCurve.Eval(randomCut)

      SignalEfficiency     = SignalPassing*1.0/TotalSignalEntries
      BackgroundEfficiency = BackgroundPassing*1.0/TotalBackgroundEntries
      OutputHistogram.Fill(SignalEfficiency, BackgroundEfficiency)

def MakeConvex(xyPointsList):
   '''takes a list of xy points, and makes it into a 1-to-1, increasing function'''
   #slow but whatever
   outputCopy = []
   for index1 in range(0, len(xyPointsList)):
      eff1, fakeRate1 = xyPointsList[index1]
      #make sure there are no lower fake rates for higher efficiencies
      keepThisPoint = True
      for index2 in range(index1+1, len(xyPointsList)):
         eff2, fakeRate2 = xyPointsList[index2]
         if fakeRate2 < fakeRate1 and eff2 > eff1:
            keepThisPoint = False
            break
      if keepThisPoint:
         outputCopy.append( (eff1, fakeRate1) )
   return outputCopy

def FindOperatingPointEfficency(InputHisto, DesiredBackground):
   ''' find the best bin whose upper edge is under the background rate '''
   highestXBinWithNonZeroContent = 0
   for ybin in range(1,InputHisto.GetNbinsY()+1):
      if InputHisto.GetYaxis().GetBinUpEdge(ybin) > DesiredBackground:
         break
      for xbin in range(highestXBinWithNonZeroContent, InputHisto.GetNbinsX()+1):
         if InputHisto.GetBinContent(xbin, ybin) > 0:
            highestXBinWithNonZeroContent = xbin
   return InputHisto.GetXaxis().GetBinLowEdge(highestXBinWithNonZeroContent)

def MakeEnvelopeGraph(OperatingPointsHistogram):
   """
   Return a TGraph function that envelopes the monte-carlo generated output histogram
   Note, the Y axis must be the fake rate, and the X axis must be the signal efficiency
   """
   points = []
   #find the minimum fake rate @ each signal efficiency
   for xbin in range(1, OperatingPointsHistogram.GetNbinsX()+1):
      # always take the most conservative bin corner
      efficiency = OperatingPointsHistogram.GetXaxis().GetBinLowEdge(xbin)
      for ybin in range(1, OperatingPointsHistogram.GetNbinsY()+1):
         if OperatingPointsHistogram.GetBinContent(xbin, ybin) > 0:
            FakeRate = OperatingPointsHistogram.GetYaxis().GetBinUpEdge(ybin)
            points.append( (efficiency, FakeRate) )
            break
#   points         = MakeConvex(points)
   output         = TGraph(len(points))
   outputInverted = TGraph(len(points))
   for i,(x,y) in enumerate(points):
      output.SetPoint(i, x, y)
      outputInverted.SetPoint(i, y, x)
   return (output, outputInverted)


