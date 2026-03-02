#include "ERunAction.hh"

ERunAction::ERunAction()
{
    fMessenger = new G4GenericMessenger(this, "/E_run_settings/", "Settings for the run");
	fMessenger->DeclareProperty("fileName", fileName, "Name of the output file");
    fMessenger->DeclareProperty("histogramName", histogramName, "Name of the histogram");
    fMessenger->DeclareMethod("finalize", &ERunAction::Finalize, "Close the output file");
    
    fileName = "output_temporary.root";
    histogramName = "Edet";

    fFileOpen = false;

    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    analysisManager->CreateH1(histogramName, "Detected energy", 2048, 0, 2. * MeV);
}

ERunAction::~ERunAction()
{
    
}

void ERunAction::BeginOfRunAction(const G4Run *run)
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    // Open file only once
    if (!fFileOpen)
    {
        analysisManager->OpenFile(fileName);
        fFileOpen = true;
    }
}

void ERunAction::EndOfRunAction(const G4Run *run)
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    // Write data to our output root file and then close the file
    analysisManager->Write();

    G4int runID = run->GetRunID();
    G4cout << "Finishing run " << runID << G4endl;
}

void ERunAction::Finalize()
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    if (fFileOpen)
    {
        analysisManager->CloseFile();
        fFileOpen = false;
        G4cout << "Root file closed" << G4endl;
    }
}
