void trainMVA()
{
	gSystem->Load("libCintex");
	gSystem->Load("libPhysicsToolsMVAComputer");
	gSystem->Load("libPhysicsToolsMVATrainer");
	Cintex::Enable();

        using namespace PhysicsTools;

	// obtain signal and background training trees;

        TFile* signal = TFile::Open("signal.root");
	TTree *sig = (TTree*)signal->Get("train");
        
        TFile* background = TFile::Open("background.root");
	TTree *bkg = (TTree*)background->Get("train");

	cout << "Training with " << sig->GetEntries()
	     << " signal events." <<  endl;
	cout << "Training with " << bkg->GetEntries()
	     << " background events." <<  endl;

	// Note: one tree argument -> tree has to contain a branch __TARGET__
	//       two tree arguments -> signal and background tree

	TreeTrainer trainer(sig, bkg);

	Calibration::MVAComputer *calib = trainer.train("Example.xml");

	MVAComputer::writeCalibration("Example.mva", calib);

	cout << "Example.mva written." << endl;

	delete calib;
}

