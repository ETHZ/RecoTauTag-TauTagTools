import FWCore.ParameterSet.Config as cms

# Copy example MVA training into a local SQLite file
# Adapted from PhysicsTools/MVATrainer/test/testWriteMVAComputerCondDB_cfg.py
# Original author: Christopher Saout
# Modifications by Evan Friis

process = cms.Process("TauMVACondUpload")

process.load("FWCore.MessageLogger.MessageLogger_cfi")

process.source = cms.Source("EmptySource")

process.maxEvents = cms.untracked.PSet(	input = cms.untracked.int32(1) )

process.MVAComputerESSource = cms.ESSource("TauMVAComputerESSource",
	MyTestMVATag = cms.string('Example.mva')
)

process.PoolDBOutputService = cms.Service("PoolDBOutputService",
	BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService'),
	DBParameters = cms.PSet( messageLevel = cms.untracked.int32(0) ),
	timetype = cms.untracked.string('runnumber'),
	connect = cms.string('sqlite_file:Example.db'),  #or frontier, etc
	toPut = cms.VPSet(cms.PSet(
		record = cms.string('BTauGenericMVAJetTagComputerRcd'),
		tag = cms.string('MyTestMVATag')
	))
)

process.MVAComputerSave = cms.EDProducer("TauMVATrainerSave",
	toPut = cms.vstring(),
	toCopy = cms.vstring('MyTestMVATag')
)

process.outpath = cms.EndPath(process.MVAComputerSave)
