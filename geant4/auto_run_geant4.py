import subprocess
import numpy as np
import time

# %% Settings

# Choose what to do
simulate_radionuclides = True
simulate_background = True

# The radionuclides to simulate (Z, A)
ZAs = [(57, 140)]
# ZAs = [(57, 140), (56, 140)]
# Detector parameters to iterate over
detector_distances = [0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0] # mm
detector_angles = [180.0] # degrees
detector_diameters = [70.0] # mm
detector_lengths = [70.0] # mm

# Number of runs per setting
runs_per_radionuclide = 1e7
# 1e7 is about 6 min per ZA
runs_per_background = 2e8
# 1e8 is about 12 min
# 5e8 is about 65 min

build_folder = "build/"
macro_name = "autorun.mac"
output_folder = "output/"
number_of_threads = 18

# %% Prepare background source

# True by default
automatic_source_radius = True
standard_source_radius = 0

resource_folder = "resources/"
background_filenames = ["source_flux_avg.csv"]

# %% Run
print("Starting geant4 autorun")
print("Number of threads: " + str(number_of_threads))
print("Settings: ")
print("\tradionuclides: " + str(ZAs))
print("\tdetector distances: " + str(detector_distances))
print("\tdetector angles: " + str(detector_angles))
print("\tdetector diameters: " + str(detector_diameters))
print("\tdetector lengths: " + str(detector_lengths))
print("\tbackground files: " + str(background_filenames))
print("\truns per radionuclide: " + str(int(runs_per_radionuclide)))
print("\truns per background: " + str(int(runs_per_background)))

start_time = time.time()
time_interval = start_time

settings = [(ZA, dis, ang, dia, len) 
            for ZA in ZAs
            for dis in detector_distances 
            for ang in detector_angles
            for dia in detector_diameters 
            for len in detector_lengths]

# Iterate over radionuclides
if simulate_radionuclides:
    for i_s, (ZA, distance, angle, diameter, length) in enumerate(settings):
        print(f"Running setting {i_s + 1} of {len(settings)}: ")
        print(f"\tZA={ZA}, distance={distance}, angle={angle}, diameter={diameter}, length={length}")

        Z = int(ZA[0])
        A = int(ZA[1])

        settings_name = "_Z_" + str(Z) + "_A_" + str(A)
        settings_name += "_dis_" + str(distance) + "_ang_" + str(angle)
        settings_name += "_dia_" + str(diameter) + "_len_" + str(length)
        settings_name += "_runs_" + f"{runs_per_radionuclide:.1e}"
        settings_name += "_.root"

        # Make macro file first
        macro_content = ""
        macro_content += "/run/numberOfThreads " + str(number_of_threads) + "\n"
        file_name = output_folder + "threadoutput_" + str(i_s) + settings_name
        macro_content += "/E_file_settings/fileName " + file_name + "\n"
        macro_content += "/E_detector/detectorAngle " + str(angle) + "\n"
        macro_content += "/E_detector/detectorDistance " + str(distance) + "\n"
        macro_content += "/E_detector/detectorDiameter " + str(diameter) + "\n"
        macro_content += "/E_detector/detectorLength " + str(length) + "\n"
        macro_content += "/run/reinitializeGeometry" + "\n"
        macro_content += "/run/initialize" + "\n"
        macro_content += "/process/had/rdm/thresholdForVeryLongDecayTime 1.0e+60 year" + "\n"
        macro_content += "/gun/particle ion" + "\n"
        macro_content += "/gun/ion " + str(Z) + " " + str(A) + " 0 0" + "\n"
        macro_content += "/process/had/rdm/nucleusLimits "+str(A)+" "+str(A)+" "+str(Z)+" "+str(Z)+"\n"
        macro_content += "/E_source/selectBackground false" + "\n"
        macro_content += "/run/printProgress " + str(int(runs_per_radionuclide/10)) + "\n"
        macro_content += "/run/beamOn " + str(int(runs_per_radionuclide))

        print("\tWriting macro file...")

        with open(build_folder + macro_name, "w") as file:
            file.write(macro_content)

        print("\tRunning Geant4...")
        process_geant4 = [build_folder + "sim", build_folder + macro_name]
        result = subprocess.run(process_geant4, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # result = subprocess.run(process_geant4) # DO NOT PUT SHELL=True

        print("\tCombining ROOT files...")
        output_file = output_folder + "nucOutput_" + str(i_s) + settings_name
        process_root = "hadd -f " + output_file + " " + output_folder + "threadoutput_" + str(i_s) + "*.root"
        result = subprocess.run(process_root, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # result = subprocess.run(process_root, shell=True)

        print("\tDeleting temporary ROOT files...")
        process_delete = "rm " + output_folder + "threadoutput_" + str(i_s) + "*.root"
        # result = subprocess.run(process_delete, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(process_delete, shell=True)

        partial_time = time.time()
        elapsed_minutes = (partial_time - time_interval) / 60
        print(f"\tTime spent for previous run: {elapsed_minutes:.2f} minutes")
        time_interval = partial_time

    print("\tFinsihed radionuclide setting!")

settings = [(bac, dis, ang, dia, len) 
            for bac in background_filenames
            for dis in detector_distances 
            for ang in detector_angles
            for dia in detector_diameters 
            for len in detector_lengths]

# Iterate over background
if simulate_background:
    for i_b, (background_filename, distance, angle, diameter, length) in enumerate(settings):
        print(f"Running setting {i_b + 1} of {len(settings)}: ")
        print(f"\tfile={background_filename}, distance={distance}, angle={angle}, diameter={diameter}, length={length}")

        flux_data = np.genfromtxt(resource_folder + background_filename, delimiter=",")
        E = flux_data[:, 0]
        flux = flux_data[:, 1:]
        background_total_flux = flux.sum()
        # Make cumulative distribution function
        flux_cdf = np.cumsum(flux) / background_total_flux
        np.savetxt("resources/flux_cdf.dat", np.column_stack((E, flux_cdf)), fmt="%.9f\t%.9f")

        if automatic_source_radius:
            source_radius = np.sqrt((diameter/2 + 1)**2 + (distance/2 + length + 2)**2)
        else:
            source_radius = standard_source_radius
        
        pseudo_time = runs_per_background / (source_radius**2 * np.pi * background_total_flux)

        settings_name = "_dis_" + str(distance) + "_ang_" + str(angle)
        settings_name += "_dia_" + str(diameter) + "_len_" + str(length)
        settings_name += "_runs_" + f"{runs_per_background:.1e}"
        settings_name += "_pt_" + f"{pseudo_time:.6e}"
        settings_name += "_rad_" + f"{source_radius:.4e}"
        settings_name += "_.root"

        # Make macro file first
        macro_content = ""
        macro_content += "/run/numberOfThreads " + str(number_of_threads) + "\n"
        file_name = output_folder + "threadoutput_" + str(i_b) + settings_name
        macro_content += "/E_file_settings/fileName " + file_name + "\n"
        macro_content += "/E_detector/detectorAngle " + str(angle) + "\n"
        macro_content += "/E_detector/detectorDistance " + str(distance) + "\n"
        macro_content += "/E_detector/detectorDiameter " + str(diameter) + "\n"
        macro_content += "/E_detector/detectorLength " + str(length) + "\n"
        macro_content += "/run/reinitializeGeometry" + "\n"
        macro_content += "/run/initialize" + "\n"
        macro_content += "/E_source/sourceRadius " + str(source_radius) + "\n"
        macro_content += "/E_source/selectBackground true" + "\n"
        macro_content += "/run/printProgress " + str(int(runs_per_background/10)) + "\n"
        macro_content += "/run/beamOn " + str(int(runs_per_background))

        print("\tWriting macro file...")

        with open(build_folder + macro_name, "w") as file:
            file.write(macro_content)

        print("\tRunning Geant4...")
        process_geant4 = [build_folder + "sim", build_folder + macro_name]
        result = subprocess.run(process_geant4, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # result = subprocess.run(process_geant4) # DO NOT PUT SHELL=True

        print("\tCombining ROOT files...")
        output_file = output_folder + "backOutput_" + str(i_b) + settings_name
        process_root = "hadd -f " + output_file + " " + output_folder + "threadoutput_" + str(i_b) + "*.root"
        result = subprocess.run(process_root, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # result = subprocess.run(process_root, shell=True)

        print("\tDeleting temporary ROOT files...")
        process_delete = "rm " + output_folder + "threadoutput_" + str(i_b) + "*.root"
        # result = subprocess.run(process_delete, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        result = subprocess.run(process_delete, shell=True)

        partial_time = time.time()
        elapsed_minutes = (partial_time - time_interval) / 60
        print(f"\tTime spent for previous run: {elapsed_minutes:.2f} minutes")
        time_interval = partial_time

        print("\tFinsihed background setting!")

print("All finished!")

end_time = time.time() # End timing
elapsed_minutes = (end_time - start_time) / 60
print(f"Total time spent: {elapsed_minutes:.2f} minutes")


