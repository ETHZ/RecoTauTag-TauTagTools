# Submit signal and background events to the condor batch system
# Author Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)

import os

'''
nEventsPerJob = 500
totalJobs     = 100
switchEvery   = 10
'''
nEventsPerJob = 10000
totalJobs     = 100 
switchEvery   = 5

signalBlock =  ( "SubmitSignal.jdl" , nEventsPerJob , 0  , 0  ) 
vlowQCD     =  ( "SubmitBkg.jdl"    , nEventsPerJob , 5  , 20 ) 
lowQCD      =  ( "SubmitBkg.jdl"    , nEventsPerJob , 20 , 30 ) 
midQCD      =  ( "SubmitBkg.jdl"    , nEventsPerJob , 30 , 50 ) 
highQCD     =  ( "SubmitBkg.jdl"    , nEventsPerJob , 50 , 80 ) 

submitters = [signalBlock, vlowQCD, lowQCD, midQCD, highQCD]
#submitters = [ lowQCD, midQCD, highQCD]
#submitters = [signalBlock,  midQCD]

eventsSubmitted = 0

while eventsSubmitted < totalJobs:
   for file, eventsPerJob, minPt, maxPt in submitters:
      os.system("cat %s | sed 's|RPL_EVENTS|%i|' | sed 's|RPL_MINPT|%i|' | sed 's|RPL_MAXPT|%i|' | sed 's|RPL_JOBS|%i|' | condor_submit" % (file, eventsPerJob, minPt, maxPt, switchEvery))
      #os.system("cat %s | sed 's|RPL_EVENTS|%i|' | sed 's|RPL_MINPT|%i|' | sed 's|RPL_MAXPT|%i|' | sed 's|RPL_JOBS|%i|'" % (file, eventsPerJob, minPt, maxPt, switchEvery))
      #print "cat %s | sed 's|RPL_EVENTS|%i|' | sed 's|RPL_MINPT|%i|' | sed 's|RPL_MAXPT|%i|' | sed 's|RPL_JOBS|%i|' | condor_submit" % (file, eventsPerJob, minPt, maxPt, switchEvery)
   eventsSubmitted += switchEvery


