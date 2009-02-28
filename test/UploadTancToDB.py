import FWCore.ParameterSet.Config as cms
import RecoTauTag.TauTagTools.TauMVAConfigurations_cfi
import os

import MVASteering

# Copy TaNC training files into a local SQLite file
# Adapted from PhysicsTools/MVATrainer/test/testWriteMVAComputerCondDB_cfg.py
# Original author: Christopher Saout
# Modifications by Evan Friis

# Make sure we are only dealing w/ one algorithm...
if len(MVASteering.myTauAlgorithms) > 1:
   raise RuntimeError, "ERROR: more than one tau algorithm is defined in MVASteering.py; this feature should be used only for algorithm evaluation.  \
         Please modify it so that it only includeds the algorithm on which the TaNC is to be used."

algorithm = MVASteering.myTauAlgorithms[0]

# Unpack the TaNC neural nets into a parameter set
tempPSet   = cms.PSet()
toCopyList = cms.vstring()

for aNeuralNet in RecoTauTag.TauTagTools.TauMVAConfigurations_cfi.TaNC.value():
   # Get the name of this neural net
   neuralNetName = aNeuralNet.computerName.value()
   # Make sure we have the .mva training done
   mvaFileLocation = MVASteering.GetTrainingFile(neuralNetName, algorithm)
   if not os.path.exists(mvaFileLocation):
      raise IOError, "Expected trained .mva file at %s, it doesn't exist!" % mvaFileLocation
   # god bless you, python
   tempPSet.__setattr__(aNeuralNet.computerName.value(), cms.string(mvaFileLocation))
   toCopyList.append(neuralNetName)

process = cms.Process("TaNCCondUpload")

process.source = cms.Source("EmptySource")

process.maxEvents = cms.untracked.PSet(	input = cms.untracked.int32(1) )

process.MVAComputerESSource = cms.ESSource("TauMVAComputerESSource",
      tempPSet  # defined above, maps the Tanc NN names to their trained MVA weights files
)

process.MVAComputerSave = cms.EDAnalyzer("TauMVATrainerSave",
	toPut = cms.vstring(),
        #list of labels to add into the tag given in the PoolDBOutputService
	#toCopy = cms.vstring('ZTauTauTraining', 'ZTauTauTrainingCopy2')
	toCopy = toCopyList
)

process.PoolDBOutputService = cms.Service("PoolDBOutputService",
	BlobStreamerName = cms.untracked.string('TBufferBlobStreamingService'),
	DBParameters = cms.PSet( messageLevel = cms.untracked.int32(0) ),
	timetype = cms.untracked.string('runnumber'),
	connect = cms.string('sqlite_file:Example.db'),  #or frontier, etc
	toPut = cms.VPSet(cms.PSet(
		record = cms.string('TauTagMVAComputerRcd'),
		tag = cms.string('MyTestMVATag')                               
	))
)

process.outpath = cms.EndPath(process.MVAComputerSave)
