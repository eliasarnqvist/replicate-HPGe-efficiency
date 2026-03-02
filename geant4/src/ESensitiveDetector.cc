#include "ESensitiveDetector.hh"

ESensitiveDetector::ESensitiveDetector(G4String name) : G4VSensitiveDetector(name)
{
    fTotalEnergyDeposited = 0.;
}

ESensitiveDetector::~ESensitiveDetector()
{
    
}

void ESensitiveDetector::Initialize(G4HCofThisEvent *)
{
    fTotalEnergyDeposited = 0.;
}

void ESensitiveDetector::EndOfEvent(G4HCofThisEvent *)
{
    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();
    // G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();

    if (fTotalEnergyDeposited > 0)
    {
        ERunAction* runAction = (ERunAction*)(G4RunManager::GetRunManager()->GetUserRunAction());
        G4String histogramName = runAction->GetHistogramName();
        G4int histId = analysisManager->GetH1Id(histogramName);
        analysisManager->FillH1(histId, fTotalEnergyDeposited);
    }

    // G4cout << "Deposited energy: " << fTotalEnergyDeposited_0 << G4endl;
}

G4bool ESensitiveDetector::ProcessHits(G4Step *aStep, G4TouchableHistory *)
{
    // G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();
    // G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    G4double fEnergyDeposited = aStep->GetTotalEnergyDeposit();

    // G4cout << "Copy number: " << copyNo << G4endl;

    if (fEnergyDeposited > 0)
    {
        fTotalEnergyDeposited += fEnergyDeposited;
    }
    
    return true;
}
