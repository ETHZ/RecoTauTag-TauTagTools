#!/bin/bash

# A script for running the TauMVA examples in the condor batch framework.
# Author: Evan Friis, UC Davis

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
rm $DATALOCATION/$FILENAME

cat BuildSignal_cfg.py | sed "s|RPL_BATCH|${1}|" | sed "s|RPL_RUN|${2}|" | sed "s|RPL_EVENTS|${3}|" > $DATALOCATION/$FILENAME

cd $DATALOCATION

if [ ! -d "finishedJobs" ]
then
   mkdir finishedJobsSignal
fi

cmsRun $FILENAME

mv *_${1}_${2}.root finishedJobsSignal/
