#!/bin/bash

# A script for running the TauMVA examples in the condor batch framework.
# Author: Evan Friis, UC Davis

# Edit for your local machine setup....
export SCRAM_ARCH='slc4_ia32_gcc345'
export VO_CMS_SW_DIR='/raid1/cmssw'
source $VO_CMS_SW_DIR/cmsset_default.sh

if [ ! -n "$3" ]
then
  echo "Produce signal (Z->tautau) MVA training data for the Tau MVA framework - the CMS job as specified in BuildSignal.py"
  echo "Usage: `basename $0` JobNumber BatchNumber MaxEvents"
  exit 65
fi  

echo "Scramming..."
eval `scramv1 runtime -sh`

if [ -z "$DATALOCATION" ] ## Succeeds if DATALOCATION is unset or empty
then
#DATALOCATION=/home/friis/data/TauClass/ZTT/
DATALOCATION="./"
echo "Setting default working directory as ${DATALOCATION}"
fi

echo "Working directory is ${DATALOCATION}"

FILENAME=run_${1}_${2}.py
if [ -f $DATALOCATION/$FILENAME ] 
then
   rm $DATALOCATION/$FILENAME
fi

cat BuildSignal_cfg.py | sed "s|RPL_BATCH|${1}|" | sed "s|RPL_RUN|${2}|" | sed "s|RPL_EVENTS|${3}|" > $DATALOCATION/$FILENAME

cd $DATALOCATION

if [ ! -d "finishedJobsSignal" ]
then
   mkdir finishedJobsSignal
fi

cmsRun $FILENAME

mv *_${1}_${2}.root finishedJobsSignal/

#cleanup
if [ ! -d "logfiles" ]
then
   mkdir logfiles
fi

mv $DATALOCATION/$FILENAME logfiles/
mv info_$1_$2.log logfiles/

