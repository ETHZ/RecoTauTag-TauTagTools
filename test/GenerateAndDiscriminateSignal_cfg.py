'''
GenerateAndDiscriminateSignal_cfg.py.py
Author: Evan K. Friis, UC Davis; evan.friis@cern.ch

Test trained MVA file on signal sample

Sequence:
   Pythia Z->tautau (both taus decay hadronically) events
   Simulation done w/ FastSim package
   Particle Flow
   Standard HighEfficiency Tau sequence
   Tau Decay mode reconstruction 
   MC Truth Tau DecayMode production                   (not required but helpful for studies) 
   MC Truth Tau DecayMode <-> reco::PFTau matching     (not required but helpful for studies) 
   Production of PFTauDiscriminator matching MVA output to PFTaus
'''
import FWCore.ParameterSet.Config as cms
process = cms.Process("TauMVA")

batchNumber=1
jobNumber=1
nEvents = 200
rootFileOutputPath="./"

#uncomment for batch running on condor (see shell script examples)
'''
batchNumber=RPL_BATCH
jobNumber=RPL_RUN
nEvents=RPL_EVENTS
'''

#get a random number from the batch/job number for reproducibility (not robust)
import random
random.seed(batchNumber)
rand1=random.randint(0, 10000)
random.seed(jobNumber)
rand2=random.randint(0, 10000)
baseSeed=rand1+rand2

print "Seed is %i" % baseSeed

process.maxEvents = cms.untracked.PSet ( input = cms.untracked.int32(nEvents) )

process.RandomNumberGeneratorService = cms.Service("RandomNumberGeneratorService",
    # This is to initialize the random engines of Famos
    moduleSeeds = cms.PSet(
        l1ParamMuons = cms.untracked.uint32(baseSeed+54525),
        caloRecHits = cms.untracked.uint32(baseSeed+654321),
        MuonSimHits = cms.untracked.uint32(baseSeed+97531),
        muonCSCDigis = cms.untracked.uint32(baseSeed+525432),
        muonDTDigis = cms.untracked.uint32(baseSeed+67673876),
        famosSimHits = cms.untracked.uint32(baseSeed+13579),
        paramMuons = cms.untracked.uint32(baseSeed+54525),
        famosPileUp = cms.untracked.uint32(baseSeed+918273),
        VtxSmeared = cms.untracked.uint32(baseSeed+123456789),
        muonRPCDigis = cms.untracked.uint32(baseSeed+524964),
        siTrackerGaussianSmearingRecHits = cms.untracked.uint32(baseSeed+24680)
    ),
    # This is to initialize the random engine of the source
    sourceSeed = cms.untracked.uint32(baseSeed+123456789)
)

#Z to tau tau hadronic only pythia source
process.load("RecoTauTag/TauTagTools/ZtoTauHadronic_cfi")

# Common inputs, with fake conditions
process.load("FastSimulation.Configuration.CommonInputsFake_cff")
# Famos sequences
process.load("FastSimulation.Configuration.FamosSequences_cff")
process.load("Configuration.StandardSequences.MagneticField_38T_cff")
process.VolumeBasedMagneticFieldESProducer.useParametrizedTrackerField = True

process.famosPileUp.PileUpSimulator.averageNumber = 0.0    
# You may not want to simulate everything for your study
process.famosSimHits.SimulateCalorimetry = True
process.famosSimHits.SimulateTracking = True

# Simulation sequence
process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")

process.main = cms.Sequence(process.genParticles*process.famosWithParticleFlow)

process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")                       # Standard Tau sequences
process.load("RecoTauTag.Configuration.RecoTauTag_FakeConditions_cff")
# necessary to prevent conflict w/ Fake BTau conditions
process.es_prefer_TauMVA = cms.ESPrefer("PoolDBESSource", "TauTagMVAComputerRecord")
#print process.BTauMVAJetTagComputerRecord.toGet
#process.BTauMVAJetTagComputerRecord.toGet[0].tag = 'TauNeuralClassifier22X'
#process.BTauMVAJetTagComputerRecord.connect = 'oracle://cms_orcoff_prep/CMS_COND_BTAU'
#process.BTauMVAJetTagComputerRecord.DBParameters.authenticationPath = '/afs/cern.ch/cms/DB/conddb'


process.p1 = cms.Path(process.main*
                      process.vertexreco*
                      process.PFTau
                      )

#keeps/drops
from RecoTauTag.Configuration.RecoTauTag_EventContent_cff import *
from RecoParticleFlow.Configuration.RecoParticleFlow_EventContent_cff import *

myOutputCommands = cms.untracked.vstring(
   'drop *'
   ,'keep *_genParticles*_*_*'
   ,'keep *_matchMCTau*_*_*'
   ,'keep *_matchMCQCD*_*_*'
   ,'keep *_makeMCTau*_*_*'
   ,'keep *_makeMCQCD*_*_*'
   ) 

myOutputCommands.extend(RecoTauTagFEVT.outputCommands)
myOutputCommands.extend(RecoParticleFlowFEVT.outputCommands)

process.o1 = cms.OutputModule(
    "PoolOutputModule",
    fileName = cms.untracked.string("Signal_Discriminated_%i_%i.root" % (batchNumber, jobNumber)),
    outputCommands = myOutputCommands
    )

process.outpath = cms.EndPath(process.o1)

process.MessageLogger = cms.Service("MessageLogger",
    info_RPL_BATCH_RPL_RUN = cms.untracked.PSet(
        threshold = cms.untracked.string('INFO'),
        limit = cms.untracked.int32(100)
    ),
    cerr = cms.untracked.PSet(
        threshold = cms.untracked.string('ERROR')
    ),
    destinations = cms.untracked.vstring('info_RPL_BATCH_RPL_RUN', 
        'cerr')
)
# Make the job crash in case of missing product
process.options = cms.untracked.PSet( Rethrow = cms.untracked.vstring('ProductNotFound') )
