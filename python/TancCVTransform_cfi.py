import FWCore.ParameterSet.Config as cms
import copy

# Get MVA configuration defintions (edit MVAs here)
from RecoTauTag.TauTagTools.TauMVAConfigurations_cfi import *
from RecoTauTag.TauTagTools.BenchmarkPointCuts_cfi import *

def UpdateTransform(TheProducer, TheSigBkgFractions):
   for aComputer in TheProducer.computers:
      SigOccupancy, BackgroundOccupancy = TheSigBkgFractions[aComputer.computerName.value()]
      # By default TMVA produces an output from [-1, 1].  The benchmark points are computed using this range.
      #  if the user has specified to remap the output to [0, 1] (usual case), remap the benchmark point used 
      #  to produce the binary decision
      aComputer.signalFraction = cms.double(SigOccupancy)
      aComputer.backgroundFraction = cms.double(BackgroundOccupancy)

TauCVTransformPrototype = cms.EDProducer("PFTauDecayModeCVTransformation",
      PFTauDecayModeSrc            = cms.InputTag("shrinkingConePFTauDecayModeIndexProducer"),
      PFTauDiscriminantToTransform = cms.InputTag('shrinkingConePFTauDiscriminationByTaNC'),
      preDiscriminants             = cms.VInputTag("shrinkingConePFTauDiscriminationByLeadingPionPtCut"),
      computers                    = TaNC
)

shrinkingConePFTauTancCVTransform = copy.deepcopy(TauCVTransformPrototype)
UpdateTransform(shrinkingConePFTauTancCVTransform, TaNC_DecayModeOccupancy)
