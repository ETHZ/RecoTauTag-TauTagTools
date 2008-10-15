import FWCore.ParameterSet.Config as cms

process = cms.Process("TauMVA")

batchNumber=1
jobNumber=1
nEvents = 100
rootFileOutputPath="./"

#for batch running
batchNumber=RPL_BATCH #2
jobNumber=RPL_RUN #69
nEvents=RPL_EVENTS #1001

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
# Parametrized magnetic field (new mapping, 4.0 and 3.8T)
#process.load("Configuration.StandardSequences.MagneticField_40T_cff")
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
process.load("RecoTauTag.RecoTau.PFRecoTauDecayModeDeteriminator_cfi")          # Reconstructs decay mode and associates (via AssociationVector) to PFTaus
process.load("RecoTauTag.TauTagTools.TruthTauDecayModeProducer_cfi")            # Builds PFTauDecayMode objects from visible taus/gen jets
process.load("RecoTauTag.TauTagTools.TauRecoTruthMatchers_cfi")                 # Matches RECO PFTaus to truth PFTauDecayModes
process.load("RecoTauTag.TauTagTools.TauMVATrainer_cfi")                        # Builds MVA training input root trees from matching
process.load("RecoTauTag.TauTagTools.TauMVADiscriminator_cfi")

process.tauMVATrainerSignal.outputRootFileName="%s/output_%i_%i.root" % (rootFileOutputPath, batchNumber, jobNumber)


process.p1 = cms.Path(process.main*
                      process.vertexreco*
                      process.PFTauHighEfficiency*
#                      process.pfRecoTauProducerInsideOut*
#                      process.pfTauDecayModeInsideOut*
                      process.pfTauDecayModeHighEfficiency*
                      process.makeMC*
                      process.matchMCTausHighEfficiency*
                      process.tauMVATrainerSignal)

process.MessageLogger = cms.Service("MessageLogger",
    info_RPL_BATCH_RPL_RUN = cms.untracked.PSet(
        threshold = cms.untracked.string('INFO'),
    ),
    cerr = cms.untracked.PSet(
        threshold = cms.untracked.string('ERROR')
    ),
    destinations = cms.untracked.vstring('info_RPL_BATCH_RPL_RUN', 
        'cerr')
)
# Make the job crash in case of missing product
process.options = cms.untracked.PSet( Rethrow = cms.untracked.vstring('ProductNotFound') )
