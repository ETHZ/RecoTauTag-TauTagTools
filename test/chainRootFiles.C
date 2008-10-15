{
   /* chainRootFiles.C
    * 
    * ***************************************************************************************************************
    *
    * Concatenates many seperate signal and background ROOT trees into one filtered TTree for use in the MVA training
    *
    * ***************************************************************************************************************
    * 
    */

   /*
    * specifiy the names of the input reco trees - matchings producer label of appropriate PFTauDecayMode producer`
    */

   string SignalRecoTreeName = "pfTauDecayModeHighEfficiency";
   string BackgroundRecoTreeName = "pfTauDecayModeHighEfficiency";

   string SignalDataLocation = "finishedJobsSignal/*.root";
   string BackgroundDataLocation = "finishedJobsBackground/*.root";
    
   /* specifies types of events to use for training
    * description:
    * __ISNULL__ : do not train on reco taus that did not exist - required, obviously.  (This exists so that you can probe the truth information about un reco'd taus)
    * __PREPASS__ and __PREFAIL__:  Prepass events are isolated single pions (don't train on these), prefail have 4 or more prongs or 5 neutral pions
    * __TrackPt@.size() !=1 : Kill 2 prong taus.  (TrackPt is a vector of the track pt's that starts after the lead track)
    * __DecayMode < 13 : Removes 3 prongs w/ 3 or more pi zeros
    *
    * The next two parameters apply the 'standard' isolation requirement
    * Alt$(NeutralOutlierPt[0], 0) < 1  Don't train on non-gamma isolated taus.  (Taus that have very low Pt isolation activity will still be used for training)
    * Alt$(ChargedOutlierPt[0], 0) < 1.5  Don't train on non-charge isolated taus.  (Taus that have very low Pt isolation activity will still be used for training)
    */

   string cut = "!__ISNULL__ && !__PREPASS__ && !__PREFAIL__ && TrackPt@.size() != 1 && DecayMode < 13 && Alt$(NeutralOutlierPt[0], 0) < 1.5 && Alt$(ChargedOutlierPt[0], 0) < 1";


   TChain* signalChain = new TChain(SignalRecoTreeName.c_str());
   int signalFilesAdded = signalChain->Add(SignalDataLocation.c_str(), 0);

   int signalEvents = signalChain->GetEntries();
   cout << "Added " << signalFilesAdded << " signal root files with " << signalEvents << " events " << endl;

   TFile* outputSignalFile = new TFile("signal.root", "RECREATE");
   TTree* sigTree = signalChain->CopyTree(cut.c_str());
   cout << "After cut application " << sigTree->GetEntries() << " signal entries remain." << endl;
   sigTree->SetName("train");

   sigTree->Write();
   outputSignalFile->Write();
   outputSignalFile->Close();

   TChain* BackgroundChain = new TChain(BackgroundRecoTreeName.c_str());
   int bkgFilesAdded = BackgroundChain->Add(BackgroundDataLocation.c_str());

   int bkgEvents = BackgroundChain->GetEntries();
   cout << "Added " << bkgFilesAdded << " bkg root files with " << bkgEvents << " events " << endl;

   TFile* outputBackgroundFile = new TFile("background.root", "RECREATE");
   TTree* bkgTree = BackgroundChain->CopyTree(cut.c_str());
   cout << "after cut: " << bkgTree->GetEntries() << endl;
   bkgTree->SetName("train");

   bkgTree->Write();
   outputBackgroundFile->Write();
   outputBackgroundFile->Close();
   
}




