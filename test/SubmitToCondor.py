# Submit signal and background events to the condor batch system
# Author Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

import os

nEventsPerJob = 5000
totalJobs     = 100
switchEvery   = 15

signalBlock = ( "SubmitSignal.jdl" ,2*nEventsPerJob ) 
QCD     =     ( "SubmitBkg.jdl"    , nEventsPerJob ) 

submitters = [signalBlock, QCD]

eventsSubmitted = 0

while eventsSubmitted < totalJobs:
   for file, eventsPerJob in submitters:
      os.system("cat %s | sed 's|RPL_EVENTS|%i|' |  sed 's|RPL_JOBS|%i|' | condor_submit" % (file, eventsPerJob, switchEvery))
   eventsSubmitted += switchEvery


