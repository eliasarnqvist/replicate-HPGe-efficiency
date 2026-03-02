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

    G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();

    if (fTotalEnergyDeposited > 0)
    {
        analysisManager->FillH1(0, fTotalEnergyDeposited);
    }

    // G4cout << "Deposited energy: " << fTotalEnergyDeposited_0 << G4endl;
}

G4bool ESensitiveDetector::ProcessHits(G4Step *aStep, G4TouchableHistory *)
{
    G4int eventID = G4RunManager::GetRunManager()->GetCurrentEvent()->GetEventID();

    G4AnalysisManager *analysisManager = G4AnalysisManager::Instance();

    G4double fEnergyDeposited = aStep->GetTotalEnergyDeposit();

    // G4StepPoint *preStepPoint = aStep->GetPreStepPoint();
    // const G4VTouchable *touchable = aStep->GetPreStepPoint()->GetTouchable();
    // G4int copyNo = touchable->GetCopyNumber(1);

    // G4cout << "Copy number: " << copyNo << G4endl;

    if (fEnergyDeposited > 0)
    {
        fTotalEnergyDeposited += fEnergyDeposited;
    }
    
    return true;
}
