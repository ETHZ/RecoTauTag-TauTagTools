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

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1)
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

process.load("RecoTauTag.TauTagTools.TauMVADiscriminator_cfi")

'''
****************************************************
*****        Load validation code          *********
****************************************************
'''
process.DQMStore = cms.Service("DQMStore")
process.load("Validation.RecoTau.TauTagValidationProducer_cff")
process.load("Validation.RecoTau.TauTagValidation_cfi")
process.load("Validation.RecoTau.RelValHistogramEff_cfi")

# Add our discriminator
TancDiscriminator = cms.PSet( discriminator = cms.string("pfRecoTauDiscriminationByMVAHighEfficiency"), selectionCut = cms.double(0.5) )

TancValidation = copy.deepcopy(process.PFTausHighEfficiencyLeadingPionBothProngs)
TancValidation.ExtensionName = 'Tanc'
#get rid of normal isolation
if TancValidation.discriminators[1].discriminator == 'pfRecoTauDiscriminationByTrackIsolationUsingLeadingPionHighEfficiency':
   del TancValidation.discriminators[1] #track iso
else:
   raise RuntimeError, " trying to replace isolation discriminators with TaNC, name has changed!"
if TancValidation.discriminators[1].discriminator == 'pfRecoTauDiscriminationByECALIsolationUsingLeadingPionHighEfficiency':
   del TancValidation.discriminators[1] #ecal iso
else:
   raise RuntimeError, " trying to replace isolation discriminators with TaNC, name has changed!"

# insert the Tanc before the e/mu discriminants
TancValidation.discriminators.insert(1, TancValidation)

TauDiscriminatorPlotter             = copy.deepcopy(process.TauEfficiencies.plots.PFTauHighEfficiencyIDTrackIsolationEfficienies)
TauDiscriminatorPlotter.numerator   = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByMVAHighEfficiency/pfRecoTauDiscriminationByMVAHighEfficiency_vs_#PAR#TauVisible')
TauDiscriminatorPlotter.denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible')
TauDiscriminatorPlotter.efficiency  = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByMVAHighEfficiency/TaNCEff#PAR#')
process.TauEfficiencies.plots.TauDiscriminatorPlotter = TauDiscriminatorPlotter

process.saveTauEff = cms.EDAnalyzer("DQMSimpleFileSaver",
  outputFileName = cms.string('CMSSW_3_1_0_pre1_tauGenJets.root')
)

EvansTauEfficiences = cms.EDAnalyzer("DQMHistEffProducer",
    plots = cms.PSet(
# REGULAR PFTAU EFFICIENCIES CALCULATION
      PFTauIDMatchingEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_Matched/pfRecoTauProducerMatched_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_Matched/PFJetMatchingEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauIDLeadingTrackFindEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByLeadingTrackFinding/pfRecoTauDiscriminationByLeadingTrackFinding_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByLeadingTrackFinding/LeadingTrackFindingEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauIDLeadingTrackPtCutEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByLeadingTrackPtCut/pfRecoTauDiscriminationByLeadingTrackPtCut_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByLeadingTrackPtCut/LeadingTrackPtCutEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauIDTrackIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByTrackIsolation/pfRecoTauDiscriminationByTrackIsolation_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByTrackIsolation/TrackIsolationEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauIDECALIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByECALIsolation/pfRecoTauDiscriminationByECALIsolation_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationByECALIsolation/ECALIsolationEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauIDMuonRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationAgainstElectron/pfRecoTauDiscriminationAgainstElectron_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationAgainstElectron/AgainstElectronEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauIDElectronRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationAgainstMuon/pfRecoTauDiscriminationAgainstMuon_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducer_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducer_pfRecoTauDiscriminationAgainstMuon/AgainstMuonEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
# PFTAUHIGHEFFICIENCY EFFICIENCY CALCULATION
      PFTauHighEfficiencyIDMatchingEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_Matched/pfRecoTauProducerHighEfficiencyMatched_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_Matched/PFJetMatchingEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyIDLeadingTrackFindEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByLeadingTrackFindingHighEfficiency/pfRecoTauDiscriminationByLeadingTrackFindingHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByLeadingTrackFindingHighEfficiency/LeadingTrackFindingEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyIDLeadingTrackPtCutEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByLeadingTrackPtCutHighEfficiency/pfRecoTauDiscriminationByLeadingTrackPtCutHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByLeadingTrackPtCutHighEfficiency/LeadingTrackPtCutEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyIDTrackIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByTrackIsolationHighEfficiency/pfRecoTauDiscriminationByTrackIsolationHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByTrackIsolationHighEfficiency/TrackIsolationEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyIDECALIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByECALIsolationHighEfficiency/pfRecoTauDiscriminationByECALIsolationHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationByECALIsolationHighEfficiency/ECALIsolationEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyIDMuonRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationAgainstElectronHighEfficiency/pfRecoTauDiscriminationAgainstElectronHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationAgainstElectronHighEfficiency/AgainstElectronEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyIDElectronRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationAgainstMuonHighEfficiency/pfRecoTauDiscriminationAgainstMuonHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiency_pfRecoTauDiscriminationAgainstMuonHighEfficiency/AgainstMuonEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
# PFTAUHIGHEFFICIENCY_LEADING_PION EFFICIENCY CALCULATION
      PFTauHighEfficiencyLeadingPionIDMatchingEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_Matched/pfRecoTauProducerHighEfficiencyMatched_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_Matched/PFJetMatchingEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyLeadingPionIDLeadingPionPtCutEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationByLeadingPionPtCutHighEfficiency/pfRecoTauDiscriminationByLeadingPionPtCutHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationByLeadingPionPtCutHighEfficiency/LeadingPionPtCutEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyLeadingPionIDTrackIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationByTrackIsolationUsingLeadingPionHighEfficiency/pfRecoTauDiscriminationByTrackIsolationUsingLeadingPionHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationByTrackIsolationUsingLeadingPionHighEfficiency/TrackIsolationEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyLeadingPionIDECALIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationByECALIsolationUsingLeadingPionHighEfficiency/pfRecoTauDiscriminationByECALIsolationUsingLeadingPionHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationByECALIsolationUsingLeadingPionHighEfficiency/ECALIsolationEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyLeadingPionIDMuonRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationAgainstElectronHighEfficiency/pfRecoTauDiscriminationAgainstElectronHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationAgainstElectronHighEfficiency/AgainstElectronEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyLeadingPionIDElectronRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationAgainstMuonHighEfficiency/pfRecoTauDiscriminationAgainstMuonHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyLeadingPion_pfRecoTauDiscriminationAgainstMuonHighEfficiency/AgainstMuonEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),      

# TANC PLOTS
      PFTauHighEfficiencyTancIDMatchingEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_Matched/pfRecoTauProducerHighEfficiencyMatched_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_Matched/PFJetMatchingEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyTancIDLeadingPionPtCutEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationByLeadingPionPtCutHighEfficiency/pfRecoTauDiscriminationByLeadingPionPtCutHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationByLeadingPionPtCutHighEfficiency/LeadingPionPtCutEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyTancIDTrackIsolationEfficienies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationByMVAHighEfficiency/pfRecoTauDiscriminationByMVAHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationByMVAHighEfficiency/TancEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyTancIDMuonRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationAgainstElectronHighEfficiency/pfRecoTauDiscriminationAgainstElectronHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationAgainstElectronHighEfficiency/AgainstElectronEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),
      PFTauHighEfficiencyTancIDElectronRejectionEfficiencies = cms.PSet(
        numerator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationAgainstMuonHighEfficiency/pfRecoTauDiscriminationAgainstMuonHighEfficiency_vs_#PAR#TauVisible'),
        denominator = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_ReferenceCollection/nRef_Taus_vs_#PAR#TauVisible'),
        efficiency = cms.string('RecoTauV/pfRecoTauProducerHighEfficiencyTanc_pfRecoTauDiscriminationAgainstMuonHighEfficiency/AgainstMuonEff#PAR#'),
        parameter = cms.vstring('pt', 'eta', 'phi', 'energy')
      ),      
      )

process.RunValidation = cms.Sequence(
    process.tauGenJetProducer +
    process.tauTagValidation +
    process.EvansTauEfficiences +
    process.saveTauEff)

process.p = cms.Path(
      process.ReRunTauID +
      process.pfRecoTauDiscriminationByMVAHighEfficiency +
      process.RunValidation
      )

process.schedule = cms.Schedule(process.p)
