import FWCore.ParameterSet.Config as cms

import copy

process = cms.Process("TEST")

process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/260FDDAF-F7F7-DD11-9672-001D09F2538E.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/8ED461AD-F7F7-DD11-B49F-000423D986C4.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/D05D05C6-06F8-DD11-A268-001617C3B6E2.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValZTT/GEN-SIM-RECO/STARTUP_30X_v1/0001/F0979216-F7F7-DD11-ADF4-000423D95030.root'
)
)

"""
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/02DFC48D-FEF7-DD11-9CD2-000423D98DB4.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/2C1C30CC-FCF7-DD11-B1D6-001617E30F56.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/32B15D35-FDF7-DD11-82EF-000423D98DB4.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/4CB750CD-FCF7-DD11-A372-000423D99658.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/785B595C-FEF7-DD11-A5ED-000423D6CA6E.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/820357D1-FCF7-DD11-9BD2-000423D98B28.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/906CE33B-FDF7-DD11-8D5C-001617C3B710.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/9680FBCD-FCF7-DD11-9229-000423D985B0.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/98B8D2DA-06F8-DD11-BFE5-000423D98DC4.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/A8BCF5D0-FCF7-DD11-9488-001617E30E2C.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/B21A8731-FDF7-DD11-837E-001617DBD5AC.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/DEDB07A6-FCF7-DD11-A70E-000423D6B48C.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/EE88D3CC-FCF7-DD11-862E-001617DBD316.root',
        '/store/relval/CMSSW_3_1_0_pre1/RelValQCD_FlatPt_15_3000/GEN-SIM-DIGI-RECO/IDEAL_30X_FastSim_v1/0001/FEAA80D9-FCF7-DD11-A08F-000423D6CA6E.root'
)
)
"""

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
#    input = cms.untracked.int32(100)
)

process.load("Configuration.StandardSequences.GeometryPilot2_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")

# Conditions: fake or frontier
#process.load("Configuration.StandardSequences.FakeConditions_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
#process.GlobalTag.globaltag = 'IDEAL_V9::All'


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
	connect = cms.string('sqlite_file:/afs/cern.ch/user/f/friis/scratch0/Example.db'),
	BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService')
)
# necessary to prevent conflict w/ Fake BTau conditions
process.es_prefer_TauMVA = cms.ESPrefer("PoolDBESSource", "TauMVAFromDB")

#Do Decay Mode reconstruction, just in case.  Eventually this will be a standard RECO thing
# and it won't need to be re-run 
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")                       # Standard Tau sequences
process.load("RecoTauTag.RecoTau.PFRecoTauDecayModeDeterminator_cfi")           # Reconstructs decay mode and associates (via AssociationVector) to PFTaus


# #######################################################
#       Load the TancDiscriminator 
# #######################################################

process.load("RecoTauTag.TauTagTools.TauMVADiscriminator_cfi")
process.load("RecoTauTag.TauTagTools.TauNeuralClassifiers_cfi")

'''
****************************************************
*****        Load validation code          *********
****************************************************
'''
process.DQMStore = cms.Service("DQMStore")
process.load("Validation.RecoTau.TauTagValidationProducer_cff")
process.load("Validation.RecoTau.TauTagValidation_cfi")
process.load("Validation.RecoTau.RelValHistogramEff_cfi")

process.saveTauEff = cms.EDAnalyzer("DQMSimpleFileSaver",
  outputFileName = cms.string('CMSSW_3_1_0_pre1_tauGenJets.root')
)


process.RunValidation = cms.Sequence(
    process.tauGenJetProducer +
    process.tauTagValidation +
    process.TauEfficiencies +
    process.saveTauEff)

process.p = cms.Path(
      process.PFTau +
      process.RunTanc +
      process.RunValidation
      )

process.schedule = cms.Schedule(process.p)
