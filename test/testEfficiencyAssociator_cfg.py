import FWCore.ParameterSet.Config as cms

process = cms.Process("USER")

process.load("RecoTauTag.TauTagTools.PFTauEfficiencyAssociator_cfi")
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")
process.load("RecoTauTag.Configuration.RecoTauTag_EventContent_cff")
process.load("RecoTauTag.Configuration.RecoTauTag_FakeConditions_cff")

process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = 'STARTUP_V13::All'
process.load("Configuration.StandardSequences.MagneticField_cff")


process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(10) )
readFiles = cms.untracked.vstring()
secFiles = cms.untracked.vstring() 

process.source = cms.Source ("PoolSource",fileNames = readFiles, secondaryFileNames = secFiles)
readFiles.extend( [
       '/store/relval/CMSSW_2_2_10/RelValZTT/GEN-SIM-RECO/STARTUP_V11_v1/0003/FEB1EC50-033E-DE11-A238-001D09F251B8.root',
       '/store/relval/CMSSW_2_2_10/RelValZTT/GEN-SIM-RECO/STARTUP_V11_v1/0003/8641BD18-033E-DE11-AC0D-001D09F23C73.root',
       '/store/relval/CMSSW_2_2_10/RelValZTT/GEN-SIM-RECO/STARTUP_V11_v1/0003/766B5EE0-023E-DE11-86CB-001D09F251BD.root',
       '/store/relval/CMSSW_2_2_10/RelValZTT/GEN-SIM-RECO/STARTUP_V11_v1/0003/0EC91DF9-073E-DE11-BE0E-001617C3B6C6.root' ] );

process.test = cms.Path(process.PFTau*process.shrinkingConeEfficienciesProducerFromFile)

process.aod = cms.OutputModule("PoolOutputModule",
    outputCommands = cms.untracked.vstring('drop *'),
    fileName = cms.untracked.string('test.root')
)

process.aod.outputCommands.extend(process.RecoTauTagAOD.outputCommands)
process.aod.outputCommands.append('keep *_shrinkingConeEfficienciesProducerFromFile_*_*')

process.outpath = cms.EndPath(process.aod)
