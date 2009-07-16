// -*- C++ -*-
//
// Package:    PFTauDecayModeCVTransformation
// Class:      PFTauDecayModeCVTransformation
// 
/*
 *
 * The Tau Neural Classifier (TaNC) and friends apply a different 
 * neural net to the distinct decay modes of the tau.  Therefore;
 * for N decay modes considered there are N different MVA which 
 * require N different cuts to set an operating point.  In general,
 * these cuts are chosen by MonteCarlo - 
 *      see RecoTauTag/TauTagTools/test/MVABenchmarks.py
 *
 * The Veelken transformation maps the set of N cuts into a single
 * number, based on the relative percentage of signal/background in 
 * each separate decay mode.
 *
 * the transformation is:
 *                            Ps[dm]
 * CV(x, dm) =    --------------------------- 
 *                 Ps[dm] + ( 1/x - 1 )Pb[dm]
 *
 * where x is the cut chosen for decay mode dm, and Ps[dm] and Pb[dm] are the 
 * probability for a tau candidate to be classified as decay mode dm for signal
 * and background, respectively. 
 *
*/
//
// Original Author:  Evan K. Friis, UC Davis (friis@physics.ucdavis.edu)
//         Created:  Thurs, April 25, 2009
// $Id: PFTauDecayModeCVTransformation.cc,v 1.0 2009/04/16 14:16:24 friis Exp $
//
//

// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/TauReco/interface/PFTau.h"
#include "DataFormats/TauReco/interface/PFTauDiscriminator.h"

//
// class decleration
//
using namespace std;
using namespace edm;
using namespace reco;

class PFTauDecayModeCVTransformation : public edm::EDProducer {
   public:
      explicit PFTauDecayModeCVTransformation(const edm::ParameterSet&);
      ~PFTauDecayModeCVTransformation();

      struct  ComputerAndCut {
         string                                 computerName;
         double                                 signalFraction;
         double                                 backgroundFraction;
      };

      typedef vector<ComputerAndCut>    CutList;
      typedef map<int, CutList::iterator> DecayModeToCutMap;

   private:
      typedef vector<Handle<PFTauDiscriminator> > DiscriminantHandleList;
      typedef vector<Handle<PFTauDiscriminator> >::const_iterator DiscriminantHandleIterator;

      virtual void beginRun( const edm::Run& run, const edm::EventSetup& );
      virtual void beginJob(const edm::EventSetup&) ;
      virtual void produce(edm::Event&, const edm::EventSetup&);
      virtual void endJob();
      InputTag                  pfTauDecayModeIndexSrc_;
      InputTag                  discriminantToTransform_;
      std::vector<InputTag>     preDiscriminants_; //These must pass for the MVA value to be computed
      DecayModeToCutMap         computerMap_;      //Maps decay mode to MVA implementation
      CutList                   computers_;
};

float VeelkenTransformation(float cut, float signalFraction, float backgroundFraction)
{
   if (cut >= 1.)
      return 1.;
   if (cut <= 0.)
      return 0.;

   if (signalFraction <= 0.)
      return 0;
   if (backgroundFraction <= 0.)
      return 1;

   double transformed = signalFraction/(signalFraction + ( (1./cut) - 1 )*backgroundFraction);
   return transformed;
}

PFTauDecayModeCVTransformation::PFTauDecayModeCVTransformation(const edm::ParameterSet& iConfig):
                   pfTauDecayModeIndexSrc_(iConfig.getParameter<InputTag>("PFTauDecayModeSrc")),
                   discriminantToTransform_(iConfig.getParameter<InputTag>("PFTauDiscriminantToTransform")),
                   preDiscriminants_(iConfig.getParameter<std::vector<InputTag> >("preDiscriminants"))
{
   produces<PFTauDiscriminator>(); //define product

   //get the computer/decay mode map
   vector<ParameterSet> decayModeMap = iConfig.getParameter<vector<ParameterSet> >("computers");
   computers_.reserve(decayModeMap.size());
   double signalFractionTotal     = 0.;
   double backgroundFractionTotal = 0;
   for(vector<ParameterSet>::const_iterator iComputer  = decayModeMap.begin();
                                            iComputer != decayModeMap.end();
                                          ++iComputer)
   {
      ComputerAndCut toInsert;
      toInsert.computerName       =  iComputer->getParameter<string>("computerName");
      toInsert.signalFraction     =  iComputer->getParameter<double>("signalFraction");
      toInsert.backgroundFraction =  iComputer->getParameter<double>("backgroundFraction");
      signalFractionTotal         += toInsert.signalFraction;
      backgroundFractionTotal     += toInsert.backgroundFraction;
      CutList::iterator computerJustAdded = computers_.insert(computers_.end(), toInsert); //add this computer to the end of the list

      //populate the map
      vector<int> associatedDecayModes = iComputer->getParameter<vector<int> >("decayModeIndices");
      for(vector<int>::const_iterator iDecayMode  = associatedDecayModes.begin();
                                      iDecayMode != associatedDecayModes.end();
                                    ++iDecayMode)
      {
         //map this integer specifying the decay mode to the MVA comptuer we just added to the list
         pair<DecayModeToCutMap::iterator, bool> insertResult = computerMap_.insert(make_pair(*iDecayMode, computerJustAdded));

         //make sure we aren't double mapping a decay mode
         if(insertResult.second == false) { //indicates that the current key (decaymode) has already been entered!
            throw cms::Exception("PFTauDecayModeCVTransformation::ctor") << "A tau decay mode: " << *iDecayMode << " has been mapped to two different MVA implementations, "
                                                              << insertResult.first->second->computerName << " and " << toInsert.computerName 
                                                              << ". Please check the appropriate cfi file." << std::endl;
         }
      }
   }
   if (signalFractionTotal && backgroundFractionTotal)
   {
      // normalize signal/background fractions
      for(CutList::iterator iComputer  = computers_.begin(); 
                            iComputer != computers_.end();
                          ++iComputer)
      {
         iComputer->signalFraction /= signalFractionTotal;
         iComputer->backgroundFraction /= backgroundFractionTotal;
      }
   }
}

PFTauDecayModeCVTransformation::~PFTauDecayModeCVTransformation()
{
   //do nothing
}

// ------------ method called to produce the data  ------------
void
PFTauDecayModeCVTransformation::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   using namespace std;
   using namespace reco;

   Handle<PFTauDiscriminator> pfTauDecayModeIndices;
   iEvent.getByLabel(pfTauDecayModeIndexSrc_, pfTauDecayModeIndices);

   Handle<PFTauDiscriminator> targetDiscriminant;
   iEvent.getByLabel(discriminantToTransform_, targetDiscriminant);

   //initialize discriminant vector w/ the RefProd of the tau collection
   auto_ptr<PFTauDiscriminator> outputProduct(new PFTauDiscriminator(pfTauDecayModeIndices->keyProduct()));

   // Get the prediscriminants that must always be satisfied
   DiscriminantHandleList                    otherDiscriminants;
   for(std::vector<InputTag>::const_iterator iDiscriminant  = preDiscriminants_.begin();
                                             iDiscriminant != preDiscriminants_.end();
                                           ++iDiscriminant)
   {
      Handle<PFTauDiscriminator> tempDiscriminantHandle;
      iEvent.getByLabel(*iDiscriminant, tempDiscriminantHandle);
      otherDiscriminants.push_back(tempDiscriminantHandle);
   }
                                             
   size_t numberOfTaus = pfTauDecayModeIndices->size();
   for(size_t iDecayMode = 0; iDecayMode < numberOfTaus; ++iDecayMode)
   {
      double output = 0.;

      // Check if this tau fails one of the specified discriminants
      // This is needed as applying these discriminants on a tau w/o a 
      // lead track doesn't do much good
      bool passesPreDiscriminant = true;

      for(DiscriminantHandleIterator iDiscriminant  = otherDiscriminants.begin();
                                     iDiscriminant != otherDiscriminants.end();
                                   ++iDiscriminant)
      {
         float thisDiscriminant = (*iDiscriminant)->value(iDecayMode);
         if (thisDiscriminant < 0.5)
         {
            passesPreDiscriminant = false;
            break;
         }
      }

      if (passesPreDiscriminant)
      {
         int decayMode          = lrint(pfTauDecayModeIndices->value(iDecayMode)); //convert to int
         float cutToTransform   = targetDiscriminant->value(iDecayMode);
         // Get correct cut
         DecayModeToCutMap::iterator iterToComputer = computerMap_.find(decayMode);
         if(iterToComputer != computerMap_.end()) //if we don't have a MVA mapped to this decay mode, skip it, it fails.
         {
            CutList::const_iterator myComputer = iterToComputer->second;
            output = VeelkenTransformation(cutToTransform, myComputer->signalFraction, myComputer->backgroundFraction);
         }
      }

      outputProduct->setValue(iDecayMode, output);
   }
   iEvent.put(outputProduct);
}
void 
PFTauDecayModeCVTransformation::beginRun( const edm::Run& run, const edm::EventSetup& iSetup)
{
}

// ------------ method called once each job just before starting event loop  ------------
void 
PFTauDecayModeCVTransformation::beginJob(const edm::EventSetup& iSetup)
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
PFTauDecayModeCVTransformation::endJob() {
}

//define this as a plug-in
DEFINE_FWK_MODULE(PFTauDecayModeCVTransformation);
