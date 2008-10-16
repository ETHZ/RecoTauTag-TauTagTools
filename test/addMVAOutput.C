void addMVAOutput()
{
   gSystem->Load("libCintex");
   gSystem->Load("libPhysicsToolsMVAComputer");
   gSystem->Load("libPhysicsToolsMVATrainer");
   Cintex::Enable();

   using namespace PhysicsTools;

   cout << "Adding MVA computer..." << endl;
   MVAComputer mva("./Example.mva");

   cout << "Loading ROOT chains..." << endl;
   TFile* chainInfo = TFile::Open("chainInfo.root", "UPDATE");

   TTree* SignalChain = chainInfo->Get("SignalReco");
   TTree* BackgroundChain = chainInfo->Get("BackgroundReco");

   cout << "Building Signal reader" << endl;
   TreeReader SignalReader(SignalChain);

   cout << "Building Background reader" << endl;
   TreeReader BackgroundReader(BackgroundChain);

   TTree* SignalOutput = new TTree("SignalOutput", "SignalOutput");
   TTree* BackgroundOutput = new TTree("BackgroundOutput", "BackgroundOutput");
   double mvaOutput;
   SignalOutput->Branch("MVAOut", &mvaOutput, "MVAOut/D");
   BackgroundOutput->Branch("MVAOut", &mvaOutput, "MVAOut/D");

   Bool_t isNull;
   BackgroundChain->SetBranchAddress("__ISNULL__", &isNull);

   int nSignalEntries = SignalChain->GetEntries();
   //Filling signal
   for (int i = 0; i < nSignalEntries; i++)
   {
      if (i % 1000 == 0)
         cout << "Filling event " << i << " for signal." << endl;
      SignalChain->SetBranchAddress("__ISNULL__", &isNull);
      SignalChain->LoadTree(i);
      SignalChain->GetEntry(i, 1);
      if (!isNull)
      {
         SignalReader.update();
         mvaOutput = SignalReader.fill(&mva);
      } else
         mvaOutput = -100;
      SignalOutput->Fill();
   }

   int nBackgroundEntries = BackgroundChain->GetEntries();
   for (int i = 0; i < nBackgroundEntries; i++)
   {
      if (i % 1000 == 0)
         cout << "Filling event " << i << " for background." << endl;
      BackgroundChain->SetBranchAddress("__ISNULL__", &isNull);
      BackgroundChain->LoadTree(i);
      BackgroundChain->GetEntry(i, 1);
      if(!isNull)
      {
         BackgroundReader.update();
         mvaOutput = BackgroundReader.fill(&mva);
      } else
         mvaOutput = -100;
      BackgroundOutput->Fill();
   }
   SignalOutput->Write();
   BackgroundOutput->Write();
   

}



