#include "ERunAction.hh"

ERunAction::ERunAction()
{
    fMessenger = new G4GenericMessenger(this, "/E_run_settings/", "Settings for the run");
	fMessenger->DeclareProperty("fileName", fileName, "Name of the output file");
    fMessenger->DeclareProperty("histogramName", histogramName, "Name of the histogram");
    fMessenger->DeclareMethod("initialize", &ERunAction::Initialize, "Open the output file");
    fMessenger->DeclareMethod("finalize", &ERunAction::Finalize, "Close the output file");
    
    fileName = "output_temporary.root";
    histogramName = "Edet";
}

ERunAction::~ERunAction()
{
    
}

void ERunAction::BeginOfRunAction(const G4Run *run)
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    analysisManager->CreateH1(histogramName, "Detected energy", 2048, 0, 2. * MeV);
}

void ERunAction::EndOfRunAction(const G4Run *run)
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    // analysisManager->Write();
    // analysisManager->Reset();

    analysisManager->Write();
    analysisManager->CloseFile();

    G4int runID = run->GetRunID();
    G4cout << "Finishing run " << runID << G4endl;
}

void ERunAction::Initialize()
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    // analysisManager->Reset();
    analysisManager->OpenFile(fileName);
    G4cout << "Root file opened" << G4endl;
}

void ERunAction::Finalize()
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    // analysisManager->Write();
    // analysisManager->CloseFile();
    G4cout << "Root file closed" << G4endl;
}
