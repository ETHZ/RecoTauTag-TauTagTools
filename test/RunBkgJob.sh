#!/bin/bash

# A script for running the TauMVA examples in the condor batch framework.
# Author: Evan Friis, UC Davis

if [ ! -n "$5" ]
then
  echo "Produce background (QCD 2->2) MVA training data for the Tau MVA framework - the CMS job as specified in BuildQCD.py"
  echo "Usage: `basename $0` JobNumber BatchNumber MaxEvents MinPtHat MaxPtHat "
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

cat BuildQCD_cfg.py | sed "s|RPL_BATCH|${1}|" | sed "s|RPL_RUN|${2}|" | sed "s|RPL_EVENTS|${3}|" | sed "s|RPL_MINPT|${4}|" | sed "s|RPL_MAXPT|${5}|" > $DATALOCATION/run_${1}_${2}.py

cd $DATALOCATION

if [ ! -d "finishedJobs" ]
then
   mkdir finishedJobsBackground
fi

cmsRun run_${1}_${2}.py 

mv *_${1}_${2}.root finishedJobsBackground/
