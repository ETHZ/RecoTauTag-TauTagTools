#!/bin/sh

eval `scramv1 runtime -sh`

pool_build_object_relational_mapping \
        -f $CMSSW_RELEASE_BASE/src/CondFormats/PhysicsToolsObjects/xml/MVAComputerContainer_basic_0.xml \
	-d CondFormatsPhysicsToolsObjects \
	-c sqlite_file:Example.db \
	-u me -p mypass -info

#	-f $CMSSW_BASE/src/RecoTauTag/TauTagTools/xml/TauTagMVARecordDBBuilder.xml \
#-f $CMSSW_RELEASE_BASE/src/CondFormats/PhysicsToolsObjects/xml/MVAComputerContainer_basic_0.xml \
