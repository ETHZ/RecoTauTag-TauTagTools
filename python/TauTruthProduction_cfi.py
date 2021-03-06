import FWCore.ParameterSet.Config as cms

from PhysicsTools.JetMCAlgos.TauGenJets_cfi import tauGenJets
from PhysicsTools.HepMCCandAlgos.genParticles_cfi import genParticles
from RecoJets.JetProducers.ak5GenJets_cfi import ak5GenJets
from RecoJets.Configuration.GenJetParticles_cff import genParticlesForJets

trueHadronicTaus = cms.EDFilter(
    "TauGenJetDecayModeSelector",
    src = cms.InputTag("tauGenJets"),
    select = cms.vstring(
        'oneProng0Pi0', 'oneProng1Pi0', 'oneProng2Pi0', 'oneProngOther',
        'threeProng0Pi0', 'threeProng1Pi0', 'threeProngOther', 'rare'),
    filter = cms.bool(False)
)

trueCommonHadronicTaus = cms.EDFilter(
    "TauGenJetDecayModeSelector",
    src = cms.InputTag("tauGenJets"),
    select = cms.vstring(
        'oneProng0Pi0', 'oneProng1Pi0', 'oneProng2Pi0',
        'threeProng0Pi0', 'threeProng1Pi0'),
    filter = cms.bool(False)
)

trueMuonicTaus = cms.EDFilter(
    "TauGenJetDecayModeSelector",
    src = cms.InputTag("tauGenJets"),
    select = cms.vstring('muon'),
    filter = cms.bool(False)
)

trueElecronicTaus = cms.EDFilter(
    "TauGenJetDecayModeSelector",
    src = cms.InputTag("tauGenJets"),
    select = cms.vstring('electron'),
    filter = cms.bool(False)
)

tauTruthSequence = cms.Sequence(
    #genParticles *
    genParticlesForJets *
    ak5GenJets *
    tauGenJets *
    trueHadronicTaus *
    trueMuonicTaus *
    trueElecronicTaus)
