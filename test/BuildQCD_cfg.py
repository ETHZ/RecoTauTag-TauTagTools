#!/usr/bin/env cmsRun
'''
BuildQCD_cfg.py
Author: Evan K. Friis, UC Davis; evan.friis@cern.ch

Build background ROOT files to support tau neural classifier training

Sequence:
   Pythia QCD 2->2 events using user supplied "flat" pt sample
   Simulation done w/ FastSim package
   Particle Flow
   Standard HighEfficiency Tau sequence
   Tau Decay mode reconstruction 
   MC Truth Tau DecayMode production
   MC Truth Tau DecayMode <-> reco::PFTau matching
   ROOT trees of discriminant outputs applied
'''

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
options = VarParsing.VarParsing ('standard')

from files import training as files

options.register ('job',
                  0, # default value
                  VarParsing.VarParsing.multiplicity.singleton, # singleton or list
                  VarParsing.VarParsing.varType.int,          # string, int, or float
                  "Batch number.  maxEvents*job events will be skipped.")

options.register('sample',
                 '', # default
                 VarParsing.VarParsing.multiplicity.singleton,
                 VarParsing.VarParsing.varType.string,
                 "Sample name")

options.parseArguments()

process = cms.Process("TRAIN")

process.maxEvents = cms.untracked.PSet ( input = cms.untracked.int32(options.maxEvents) )

process.source = cms.Source(
    "PoolSource",
    fileNames = cms.untracked.vstring(
        # Run over one file at a time
        files[options.sample][options.job]
        #'file:/mnt/hadoop/store/mc/Summer09/QCDDiJet_Pt30to50/AODSIM/MC_31X_V3_AODSIM-v1/0000/16245B9C-E97C-DE11-B57A-001CC4BE7702.root'
       ),
    #skipEvents = cms.untracked.uint32(options.maxEvents*options.job)
    )

process.load("Configuration.StandardSequences.MagneticField_38T_cff")

# Standard Tau sequences
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")                                    

process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = "MC_31X_V3::All"

# Simulation sequence

process.load("SimGeneral.HepPDTESSource.pythiapdt_cfi")
process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")
process.load("RecoJets.Configuration.GenJetParticles_cff")

process.main = cms.Sequence(process.genParticlesForJets)

# Builds PFTauDecayMode objects from visible taus/gen jets
process.load("RecoTauTag.TauTagTools.TruthTauDecayModeProducer_cfi")            
# Matches RECO PFTaus to truth PFTauDecayModes
process.load("RecoTauTag.TauTagTools.TauRecoTruthMatchers_cfi")                 
# Builds MVA training input root trees from matching
process.load("RecoTauTag.TauTagTools.TauMVATrainer_cfi")                        

process.tauMVATrainerBackground.outputRootFileName="qcd/output_%s_%s.root" % (options.sample,options.job)

process.p1 = cms.Path(
                      process.main*
                      process.ic5PFJetTracksAssociatorAtVertex*
                      process.pfRecoTauTagInfoProducer*
                      process.produceAndDiscriminateShrinkingConePFTaus*
                      process.makeMCQCD*
                      process.matchMCQCD*
                      process.tauMVATrainerBackground)


process.MessageLogger = cms.Service("MessageLogger",
    cerr = cms.untracked.PSet(
        threshold = cms.untracked.string('ERROR'),
    ),
    destinations = cms.untracked.vstring('cerr')
)
# Make the job crash in case of missing product
process.options = cms.untracked.PSet( Rethrow = cms.untracked.vstring('ProductNotFound') )
