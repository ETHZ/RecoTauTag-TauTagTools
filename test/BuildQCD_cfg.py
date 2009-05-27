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

process = cms.Process("TaNC")

batchNumber=1
jobNumber=1
#minPtHat = 30
#maxPtHat = 50
nEvents = 100
rootFileOutputPath="./"

#for batch running on condor (see shell scripts)
batchNumber=RPL_BATCH
jobNumber=RPL_RUN
#minPtHat=RPL_MINPT
#maxPtHat=RPL_MAXPT
nEvents=RPL_EVENTS

#get a random number from the batch/job number for reproducibility (not robust)
import random
random.seed(batchNumber)
rand1=random.randint(0, 10000)
random.seed(jobNumber)
rand2=random.randint(0, 10000)
baseSeed=rand1+rand2

print "Seed is %i" % baseSeed

process.maxEvents = cms.untracked.PSet ( input = cms.untracked.int32(nEvents) )


process.load("Configuration.Generator.QCDForPF_cfi")

# lower maximum cut
process.source.processParameters = cms.vstring(
      'MSEL=1                ! QCD hight pT processes', 
      'CKIN(3)=15.           ! minimum pt hat for hard interactions', 
      'CKIN(4)=300.         ! maximum pt hat for hard interactions',
      'MSTP(142)=2           ! Turns on the PYWEVT Pt reweighting routine' 
      )

#Random number gen
process.load("FastSimulation.Configuration.RandomServiceInitialization_cff")
newSeed = process.RandomNumberGeneratorService.theSource.initialSeed.value() + baseSeed
process.RandomNumberGeneratorService.theSource.initialSeed = cms.untracked.uint32(newSeed)
process.RandomNumberGeneratorService.generator.initialSeed = cms.untracked.uint32(newSeed)

# Common inputs, with fake conditions
#process.load("FastSimulation.Configuration.CommonInputsFake_cff")
# Common inputs
process.load("FastSimulation.Configuration.CommonInputs_cff")
# Famos sequences
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")                                    # Standard Tau sequences
process.load("FastSimulation.Configuration.FamosSequences_cff")
# Parametrized magnetic field (new mapping, 4.0 and 3.8T)
#process.load("Configuration.StandardSequences.MagneticField_40T_cff")
process.load("Configuration.StandardSequences.MagneticField_38T_cff")
process.VolumeBasedMagneticFieldESProducer.useParametrizedTrackerField = True

process.famosPileUp.PileUpSimulator.averageNumber = 0.0    
# You may not want to simulate everything for your study
process.famosSimHits.SimulateCalorimetry = True
process.famosSimHits.SimulateTracking = True

#material effects
#process.famosSimHits.PairProduction     = cms.bool(False)
#process.famosSimHits.Bremsstrahlung     = cms.bool(False)
#process.famosSimHits.EnergyLoss         = cms.bool(False)
#process.famosSimHits.NuclearInteraction = cms.bool(False)

#process.Timing = cms.Service("Timing")

# Simulation sequence
process.load("PhysicsTools.HepMCCandAlgos.genParticles_cfi")

process.main = cms.Sequence(process.ProductionFilterSequence*process.genParticles*process.genParticlesForJets*process.famosWithElectrons*process.famosWithCaloTowersAndParticleFlow)
process.load("RecoTauTag.TauTagTools.TruthTauDecayModeProducer_cfi")            # Builds PFTauDecayMode objects from visible taus/gen jets
process.load("RecoTauTag.TauTagTools.TauRecoTruthMatchers_cfi")                 # Matches RECO PFTaus to truth PFTauDecayModes
process.load("RecoTauTag.TauTagTools.TauMVATrainer_cfi")                        # Builds MVA training input root trees from matching
process.tauMVATrainerBackground.outputRootFileName="%s/output_%i_%i.root" % (rootFileOutputPath, batchNumber, jobNumber)


process.p1 = cms.Path(process.main*
                      process.ic5PFJetTracksAssociatorAtVertex*
                      process.pfRecoTauTagInfoProducer*
                      process.produceAndDiscriminateShrinkingConePFTaus*
                      process.makeMCQCD*
                      process.matchMCQCD*
                      process.tauMVATrainerBackground)


process.MessageLogger = cms.Service("MessageLogger",
    info_RPL_BATCH_RPL_RUN = cms.untracked.PSet(
        threshold = cms.untracked.string('ERROR'),
    ),
    destinations = cms.untracked.vstring('info_RPL_BATCH_RPL_RUN')
)
# Make the job crash in case of missing product
process.options = cms.untracked.PSet( Rethrow = cms.untracked.vstring('ProductNotFound') )
