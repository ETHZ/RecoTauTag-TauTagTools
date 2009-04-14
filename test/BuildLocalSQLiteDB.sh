#!/bin/sh

# Generate a local mysql database (TancLocal.db) with the correct schema for holding 
# TauMVA objects

eval `scramv1 runtime -sh`

pool_build_object_relational_mapping \
        -f $CMSSW_RELEASE_BASE/src/RecoBTau/JetTagMVALearning/test/MVAComputer-mapping-2.0.xml \
	-d CondFormatsPhysicsToolsObjects \
	-c sqlite_file:TancLocal.db \
	-u me -p mypass -info

