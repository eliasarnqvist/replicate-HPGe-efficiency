#include "EDetectorConstruction.hh"

EDetectorConstruction::EDetectorConstruction()
{
    fMessenger = new G4GenericMessenger(this, "/E_detector/", "Settings for the detector");

    fMessenger->DeclareProperty("frontDeadLayer", frontDeadLayerR, "Front dead layer (mm)");
    fMessenger->DeclareProperty("sideDeadLayer", sideDeadLayerR, "Side dead layer (mm)");
    fMessenger->DeclareProperty("frontSpace", frontSpaceR, "Front space between crystal and can (mm)");

    frontDeadLayerR = 0.7;
    sideDeadLayerR = 0.7;
    frontSpaceR = 3.0;
}

EDetectorConstruction::~EDetectorConstruction()
{
    
}

G4VPhysicalVolume *EDetectorConstruction::Construct()
{
    G4double frontDeadLayer = frontDeadLayerR * mm;
    G4double sideDeadLayer = sideDeadLayerR * mm;
    G4double frontSpace = frontSpaceR * mm;

    G4bool checkOverlaps = true;

    // Define materials
    G4NistManager *nist = G4NistManager::Instance();
    G4Material *MatWorld = nist->FindOrBuildMaterial("G4_AIR");
    G4Material *MatGe = nist->FindOrBuildMaterial("G4_Ge");
    G4Material *MatAl = nist->FindOrBuildMaterial("G4_Al");
    // G4Material *MatCu = nist->FindOrBuildMaterial("G4_Cu");
    // G4Material *MatVac = nist->FindOrBuildMaterial("G4_Galactic");

    // World
    G4double xWorld = 1. * m;
    G4double yWorld = 1. * m;
    G4double zWorld = 1. * m;
    G4Box *solidWorld = new G4Box("solidWorld", 0.5 * xWorld, 0.5 * yWorld, 0.5 * zWorld);
    G4LogicalVolume *logicWorld = new G4LogicalVolume(solidWorld, MatWorld, "logicWorld");
    G4VPhysicalVolume *physWorld = new G4PVPlacement(0, G4ThreeVector(0., 0., 0.), logicWorld, "physWorld", 0, false, 0, checkOverlaps);

    G4double detectorInternalHoleDiameter = 13 * mm;
    G4double detectorInternalHoleDepth = 40 * mm;
    G4double detectorDiameter = 60.9 * mm;
    G4double detectorLength = 54.6 * mm;
    G4double detectorSensitiveDiameter = detectorDiameter - 2 * sideDeadLayer;
    G4double detectorSensitiveLength = detectorLength - frontDeadLayer;

    G4double capThickness = 1 * mm;
    G4double capOuterDiameter = 81 * mm;
    G4double capInnerDiamter = capOuterDiameter - 2 * capThickness;
    G4double capOuterLength = capThickness + frontSpace + detectorLength;
    
    G4double sliceAngle = 360. * deg;

    // Cap
    G4Tubs *solidCapSides = new G4Tubs("solidCapSides", 0.5 * capInnerDiamter, 0.5 * capOuterDiameter, 0.5 * (capOuterLength - capThickness), 0. * deg, sliceAngle);
    G4LogicalVolume *logicCapSides = new G4LogicalVolume(solidCapSides, MatAl, "logicCapSides");
    G4VPhysicalVolume *physCapSides = new G4PVPlacement(0, G4ThreeVector(0., 0., -0.5 * (capOuterLength - capThickness) - capThickness), logicCapSides, "physCapSides", logicWorld, false, 0, checkOverlaps);
    G4Tubs *solidCapFront = new G4Tubs("solidCapFront", 0., 0.5 * capOuterDiameter, 0.5 * capThickness, 0. * deg, sliceAngle);
    G4LogicalVolume *logicCapFront = new G4LogicalVolume(solidCapFront, MatAl, "logicCapFront");
    G4VPhysicalVolume *physCapFront = new G4PVPlacement(0, G4ThreeVector(0., 0., -0.5 * capThickness), logicCapFront, "physCapFront", logicWorld, false, 0, checkOverlaps);

    // Crystal dead layer
    G4Tubs *solidDeadLayerSides = new G4Tubs("solidDeadLayerSides", 0.5 * detectorSensitiveDiameter, 0.5 * detectorDiameter, 0.5 * detectorSensitiveLength, 0. * deg, sliceAngle);
    G4LogicalVolume *logicDeadLayerSides = new G4LogicalVolume(solidDeadLayerSides, MatGe, "logicDeadLayerSides");
    G4VPhysicalVolume *physDeadLayerSides = new G4PVPlacement(0, G4ThreeVector(0., 0., -capThickness -frontSpace -0.5 * detectorSensitiveLength - frontDeadLayer), logicDeadLayerSides, "physDeadLayerSides", logicWorld, false, 0, checkOverlaps);
    G4Tubs *solidDeadLayerFront = new G4Tubs("solidDeadLayerFront", 0., 0.5 * detectorDiameter, 0.5 * frontDeadLayer, 0. * deg, sliceAngle);
    G4LogicalVolume *logicDeadLayerFront = new G4LogicalVolume(solidDeadLayerFront, MatGe, "logicDeadLayerFront");
    G4VPhysicalVolume *physDeadLayerFront = new G4PVPlacement(0, G4ThreeVector(0., 0., -capThickness -frontSpace -0.5 * frontDeadLayer), logicDeadLayerFront, "physDeadLayerFront", logicWorld, false, 0, checkOverlaps);

    // Crystal
    G4Tubs *solidDetector1 = new G4Tubs("solidDetector1", 0.5 * detectorInternalHoleDiameter, 0.5 * detectorSensitiveDiameter, 0.5 * detectorInternalHoleDepth, 0. * deg, sliceAngle);
    G4Tubs *solidDetector2 = new G4Tubs("solidDetector2", 0, 0.5 * detectorSensitiveDiameter, 0.5 * (detectorSensitiveLength - detectorInternalHoleDepth), 0. * deg, sliceAngle);
    G4MultiUnion* munionDetector = new G4MultiUnion("munionDetector");
    munionDetector->AddNode(*solidDetector1, G4Transform3D(G4RotationMatrix(), G4ThreeVector(0., 0., - 0.5 * (detectorSensitiveLength - detectorInternalHoleDepth))));
    munionDetector->AddNode(*solidDetector2, G4Transform3D(G4RotationMatrix(), G4ThreeVector(0., 0., 0.5 * detectorInternalHoleDepth)));
    munionDetector->Voxelize();
    logicDetector = new G4LogicalVolume(munionDetector, MatGe, "logicDetector");
    G4VPhysicalVolume *physDetector = new G4PVPlacement(0, G4ThreeVector(0., 0., -capThickness -frontSpace -frontDeadLayer -0.5 * detectorSensitiveLength), logicDetector, "physDetector", logicWorld, false, 0, checkOverlaps);

    // Show pretty colors in the visualization
    G4VisAttributes *capVisAtt = new G4VisAttributes(G4Color(0.0, 0.0, 1.0, 0.5));
    capVisAtt->SetForceSolid(true);
    logicCapSides->SetVisAttributes(capVisAtt);
    logicCapFront->SetVisAttributes(capVisAtt);
    G4VisAttributes *dLVisAtt = new G4VisAttributes(G4Color(1.0, 0.0, 0.0, 0.5));
    dLVisAtt->SetForceSolid(true);
    logicDeadLayerSides->SetVisAttributes(dLVisAtt);
    logicDeadLayerFront->SetVisAttributes(dLVisAtt);
    G4VisAttributes *detVisAtt = new G4VisAttributes(G4Color(1.0, 1.0, 0.0, 0.5));
    detVisAtt->SetForceSolid(true);
    logicDetector->SetVisAttributes(detVisAtt);

    return physWorld;
}

void EDetectorConstruction::ConstructSDandField()
{
    ESensitiveDetector *sensDet = new ESensitiveDetector("ESensitiveDetector");
    logicDetector->SetSensitiveDetector(sensDet);
    G4SDManager::GetSDMpointer()->AddNewDetector(sensDet);
}
