#include "EPrimaryGenerator.hh"

EPrimaryGenerator::EPrimaryGenerator()
{
    fMessenger = new G4GenericMessenger(this, "/E_source/", "Settings for the source");
    fMessenger->DeclareProperty("sourcePosition", sourcePositionR, "Position of point source");
    
    sourcePositionR = 1.25;

    G4int n_particle = 1;
    fParticleGun  = new G4ParticleGun(n_particle);

    fParticleGun->SetParticleEnergy(0*eV);
    fParticleGun->SetParticlePosition(G4ThreeVector(0.,0.,0.));
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(1.,0.,0.));
}

EPrimaryGenerator::~EPrimaryGenerator()
{
    delete fParticleGun;
}

void EPrimaryGenerator::GeneratePrimaries(G4Event *anEvent)
{
    // If the particle has not bee assigned yet, assign it as an ion
    if (fParticleGun->GetParticleDefinition() == G4Geantino::Geantino())
    {
        G4double sourcePosition = sourcePositionR * mm;
        G4int Z = 55, A = 137;
        G4double excitEnergy = 0. * keV;
        G4IonTable *ionTable = G4IonTable::GetIonTable();
        G4ParticleDefinition *ion = ionTable->GetIon(Z, A, excitEnergy);

        fParticleGun->SetParticleDefinition(ion);
        fParticleGun->SetParticleCharge(0. * eplus);
        fParticleGun->SetParticleEnergy(0 * eV);
        fParticleGun->SetParticlePosition(G4ThreeVector(0.,0.,sourcePosition));
    }

    // Create vertex
    fParticleGun->GeneratePrimaryVertex(anEvent);
}
