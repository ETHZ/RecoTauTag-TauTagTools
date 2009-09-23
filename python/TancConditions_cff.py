import FWCore.ParameterSet.Config as cms
from CondCore.DBCommon.CondDBCommon_cfi import *

TauTagMVAComputerRecord = cms.ESSource("PoolDBESSource",
	CondDBCommon,
        appendToDataLabel = cms.string("TauMVASpecific"),
	timetype = cms.string('runnumber'),
	toGet = cms.VPSet(cms.PSet(
		record = cms.string('BTauGenericMVAJetTagComputerRcd'),
		tag = cms.string('TauNeuralClassifier22X')
	)),
	#connect = cms.string('sqlite_file:/afs/cern.ch/user/f/friis/scratch0/TancLocal22X.db'),
        connect = cms.string('frontier://FrontierProd/CMS_COND_21X_BTAU'),
	BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService')
)
