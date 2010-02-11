#!/usr/bin/env cmsRun

import FWCore.ParameterSet.Config as cms
from Evaluate import process, options, ntupleVars

from files import testing as files 
process.source.fileNames = cms.untracked.vstring(
    files['Ztautau'][options.job])

# Setup ntuple production
from RecoTauTag.TauAnalysisTools.tools.ntupleTools import makeTauNtuple
makeTauNtuple(
    process,
    expressions = cms.PSet(ntupleVars.common_expressions, 
                           ntupleVars.pftau_expressions),
    discriminators=cms.PSet(ntupleVars.pftau_discriminators_extra, 
                            ntupleVars.pftau_discriminators),
    matchingOption = "matched", # These two values must be changed!
    matchingCollection = "trueHadronicTaus")

process.path += process.buildTauNtuple

process.out = cms.OutputModule("PoolOutputModule",                                                                                                                                                        
      outputCommands = cms.untracked.vstring("drop *", "keep *_*NtupleProducer_*_*" ),
      verbose = cms.untracked.bool(False),
      fileName = cms.untracked.string("evaluate/ztt/output_%i.root" % options.job)      
      )

process.end = cms.EndPath(process.out)
