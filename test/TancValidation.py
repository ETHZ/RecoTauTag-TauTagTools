import FWCore.ParameterSet.Config as cms

process = cms.Process("TEST")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/260FDDAF-F7F7-DD11-9672-001D09F2538E.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/8ED461AD-F7F7-DD11-B49F-000423D986C4.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/D05D05C6-06F8-DD11-A268-001617C3B6E2.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/F0979216-F7F7-DD11-ADF4-000423D95030.root'
)
)

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
)

'''
****************************************************
*****   Retrieve TaNC from Conditions DB   *********
****************************************************
*****   Important fields:                 **********
*****      connect string                 **********
*****      database tag                   **********
****************************************************
'''
from CondCore.DBCommon.CondDBSetup_cfi import *

process.TauMVAFromDB = cms.ESSource("PoolDBESSource",
	CondDBSetup,
	timetype = cms.untracked.string('runnumber'),
	toGet = cms.VPSet(cms.PSet(
		record = cms.string('TauTagMVAComputerRcd'),
		tag = cms.string('MyTestMVATag')
	)),
	connect = cms.string('sqlite_file:Example.db'),
	BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService')
)
# necessary to prevent conflict w/ Fake BTau conditions
process.es_prefer_TauMVA = cms.ESPrefer("PoolDBESSource", "TauMVAFromDB")

#Do Decay Mode reconstruction, just in case.  Eventually this will be a standard RECO thing
# and it won't need to be re-run 
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")                       # Standard Tau sequences
process.load("RecoTauTag.RecoTau.PFRecoTauDecayModeDeterminator_cfi")           # Reconstructs decay mode and associates (via AssociationVector) to PFTaus

process.ReRunTauID = cms.Sequence(process.PFTauHighEfficiency*process.pfTauDecayModeHighEfficiency)

# #######################################################
#       Load the TancDiscriminator 
# #######################################################

process.load("RecoTauTag.TauTagTools.TauMVADiscriminator_cfi.py")

'''
****************************************************
*****        Load validation code          *********
****************************************************
'''
process.load("Validation.RecoTau.TauTagValidationProducer_cff")
process.load("Validation.RecoTau.TauTagValidation_cfi")
process.load("Validation.RecoTau.RelValHistogramEff_cfi")

# Add our discriminator
TancDiscriminator = cms.PSet( discriminator = cms.string("pfRecoTauDiscriminationByMVAHighEfficiency"), selectionCut = cms.double(0.5) )
process.PFTausHighEfficiencyLeadingPionBothProngs.discriminators.append(TancDiscriminator)
process.PFTausHighEfficiencyBothProngs.discriminators.append(TancDiscriminator)

TauDiscriminatorPlotter             = copy.deepcopy(process.TauEfficiencies.plots.PFTauHighEfficiencyIDTrackIsolationEfficienies)
TauDiscriminatorPlotter.numerator   = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByMVAHighEfficiency/pfRecoTauDiscriminationByMVAHighEfficiency_vs_#PAR#TauVisible'),
TauDiscriminatorPlotter.denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
TauDiscriminatorPlotter.efficiency  = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByMVAHighEfficiency/TrackIsolationEff#PAR#'),
process.TauEfficiencies.plots.append(TauDiscriminatorPlotter)

process.saveTauEff = cms.EDAnalyzer("DQMSimpleFileSaver",
  outputFileName = cms.string('CMSSW_3_1_0_pre1_tauGenJets.root')
)
process.RunValidation = cms.Sequence(
    process.tauGenJetProducer +
    process.tauTagValidation +
    process.TauEfficiencies +
    process.saveTauEff)

process.p = cms.Path(
      process.ReRunTauID +
      process.pfRecoTauDiscriminationByMVAHighEfficiency +
      process.RunValidation
      )

process.schedule = cms.Schedule(process.p)
