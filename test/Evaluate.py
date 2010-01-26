'''
Evaluate.py
Author: Evan K. Friis, UC Davis; evan.friis@cern.ch

Using a local sqlite database w/ TaNC training, build a TauNtuple
containing TaNC evaluation data. This file is not complete - it only 
serves as a prototype for the specific signal/bkg cases

$Id: $ 

'''

import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing
import copy
options = VarParsing.VarParsing ('standard')

options.register (
    'job',
    0, # default value
    VarParsing.VarParsing.multiplicity.singleton, # singleton or list
    VarParsing.VarParsing.varType.int,          # string, int, or float
    "Batch number.  From the input file list, file# [job] will be selected")

options.register (
    'tags',
    '', # default value
    VarParsing.VarParsing.multiplicity.list, # singleton or list
    VarParsing.VarParsing.varType.string,          # string, int, or float
    "List of tanc tags to use")

options.register (
    'sample',
    'null', 
    VarParsing.VarParsing.multiplicity.singleton, # singleton or list
    VarParsing.VarParsing.varType.string,          # string, int, or float
    "Sample to use (in case of QCD)")

options.parseArguments()
process = cms.Process("TRAIN")

#Should in general be -1
process.maxEvents = cms.untracked.PSet ( 
    input = cms.untracked.int32(options.maxEvents) )

process.source = cms.Source(
    "PoolSource",
    # Must be updated in derived files
    fileNames = cms.untracked.vstring()
)

process.load("Configuration.StandardSequences.MagneticField_38T_cff")
# Standard Tau sequences
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")                                    
process.load("Configuration.StandardSequences.Geometry_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")
process.GlobalTag.globaltag = "MC_31X_V3::All"

# Setup the test TaNC conditions
from RecoTauTag.TauTagTools.TancConditions_cff import TauTagMVAComputerRecord
# Get the TaNC discriminator
from RecoTauTag.TauTagTools.TauMVADiscriminator_cfi import shrinkingConePFTauDiscriminationByTaNC

# Start to prepare our Ntuple defintions
from RecoTauTag.TauAnalysisTools.tools.ntupleDefinitions import \
        pftau_discriminators_extra, common_expressions, pftau_expressions,\
        pftau_discriminators

# Run standard PFTau sequence
process.runPFTau = cms.Sequence(process.PFTau)

# Add new ES sources & discriminators for each DB instance
for tag in options.tags:
    # Point in the right direction
    new_es_source = copy.deepcopy(TauTagMVAComputerRecord)
    new_es_source.connect = cms.string('sqlite_fip:RecoTauTag/TauTagTools/test/TancLocal.db')
    new_es_source.toGet[0].tag = cms.string(tag)
    new_es_source.appendToDataLabel = cms.string(tag)
    setattr(process, "es_%s" % tag, new_es_source)
    # Add a discriminator 
    new_disc = copy.deepcopy(shrinkingConePFTauDiscriminationByTaNC)
    new_disc.dbLabel = cms.string(tag)
    process_name = "shrinkingConePFTauDiscriminationBy%s" % tag
    setattr(process, process_name, new_disc)
    process.runPFTau *= new_disc
    # Add discriminator to ntuple
    setattr(pftau_discriminators_extra, "By%s" % tag, 
            cms.InputTag(process_name))
    #print pftau_discriminators_extra

# MC information
process.load("RecoTauTag.TauAnalysisTools.truthTools_cfi")

process.path = cms.Path(process.makeTruthCollections*process.runPFTau)

