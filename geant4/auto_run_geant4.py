import subprocess
import time
import uuid
import json
import os
import random

# %% Settings

# The radionuclides to simulate (Z, A, name, source_position)
ZAs = [
    (55, 137, "cs137", 1.25),
    (27, 60, "co60", 2.0),
    (56, 133, "ba133", 1.25),
    (95, 241, "am241", 1.25),
    (27, 57, "co57", 1.0),
    ]

# Number of runs per setting
runs_per_radionuclide = 1e5

# Number of random settings
number_of_settings = 1

# Detector parameters to iterate over
side_dead_layer_lims = [0.7, 3] # mm
front_dead_layer_lims = [0.7, 3] # mm
front_space_lims = [3, 8] # mm
# source_position = 1.25

number_of_threads = 16
build_folder = "build/"
macro_name = "autorun.mac"
output_folder = "output/"

# %% Run
print("Starting Geant4 autorun")
print("Number of threads: " + str(number_of_threads))
print("runs per radionuclide: " + str(int(runs_per_radionuclide)))
print("Settings: ")
print("\tradionuclides: " + str(ZAs))
print("\tside_dead_layer range: " + str(side_dead_layer_lims))
print("\tfront_dead_layer range: " + str(front_dead_layer_lims))
print("\tfront_space range: " + str(front_space_lims))

start_time = time.time()
time_interval = start_time

# Iterate over radionuclides
for i_s in range(number_of_settings):
    # Select a random parameter in the ranges we specified
    side_dead_layer = random.uniform(side_dead_layer_lims[0], side_dead_layer_lims[1])
    front_dead_layer = random.uniform(front_dead_layer_lims[0], front_dead_layer_lims[1])
    front_space = random.uniform(front_space_lims[0], front_space_lims[1])

    print(f"Running setting {i_s + 1} of {number_of_settings}: ")
    print(f"\tside_dead_layer={side_dead_layer}, front_dead_layer={front_dead_layer}, front_space={front_space}")

    settings_name = "_setting_run_.root"
    file_name = output_folder + "threadoutput_" + str(i_s) + settings_name

    # Make macro file first
    macro_content = ""
    macro_content += "/run/numberOfThreads " + str(number_of_threads) + "\n"
    macro_content += "/E_run_settings/fileName " + file_name + "\n"
    macro_content += "/E_detector/sideDeadLayer " + str(side_dead_layer) + "\n"
    macro_content += "/E_detector/frontDeadLayer " + str(front_dead_layer) + "\n"
    macro_content += "/E_detector/frontSpace " + str(front_space) + "\n"

    macro_content += "/run/reinitializeGeometry" + "\n"
    macro_content += "/run/initialize" + "\n"

    macro_content += "/process/had/rdm/thresholdForVeryLongDecayTime 1.0e+60 year" + "\n"
    macro_content += "/gun/particle ion" + "\n"

    macro_content += "/E_run_settings/initialize" + "\n"

    for ZA in ZAs:
        Z = ZA[0]
        A = ZA[1]
        name = ZA[2]
        source_position = ZA[3]

        macro_content += "/E_source/sourcePosition " + str(source_position) + "\n"
        macro_content += "/E_run_settings/histogramName " + name + "\n"
        macro_content += "/gun/ion " + str(Z) + " " + str(A) + " 0 0" + "\n"
        macro_content += "/process/had/rdm/nucleusLimits "+str(A)+" "+str(A)+" "+str(Z)+" "+str(Z)+"\n"
        macro_content += "/run/printProgress " + str(int(runs_per_radionuclide/10)) + "\n"
        macro_content += "/run/beamOn " + str(int(runs_per_radionuclide)) + "\n"
    
    macro_content += "/E_run_settings/finalize" + "\n"

    print("\tWriting macro file...")

    with open(build_folder + macro_name, "w") as file:
        file.write(macro_content)

    sim_start_time = time.time()

    print("\tRunning Geant4...")
    process_geant4 = [build_folder + "sim", build_folder + macro_name]
    result = subprocess.run(process_geant4, stdout=subprocess.DEVNULL)
    # result = subprocess.run(process_geant4) # DO NOT PUT SHELL=True

    sim_stop_time = time.time()
    # the time it took to only run geant4
    simulated_minutes = (sim_stop_time - sim_start_time) / 60

    print("\tCombining ROOT files...")
    run_id = str(uuid.uuid4())
    # output_file = output_folder + "nucOutput_" + str(i_s) + settings_name
    output_file = output_folder + run_id + ".root"
    process_root = "hadd -f " + output_file + " " + output_folder + "threadoutput_" + str(i_s) + "*.root"
    result = subprocess.run(process_root, shell=True, stdout=subprocess.DEVNULL)
    # result = subprocess.run(process_root, shell=True)

    print("\tAdding metadata...")
    if not os.path.exists(output_folder + "metadata.json"):
        with open(output_folder + "metadata.json", "w") as f:
            f.write("{}")
    with open(output_folder + "metadata.json") as f:
        metadata = json.load(f)
    metadata[run_id] = {
        "filename":(run_id + ".root"),
        "file_size":os.path.getsize(output_file),
        "properties":{
            "model":"UGGLA model v1",
            "ZAs":ZAs,
            "side_dead_layer":side_dead_layer,
            "front_dead_layer":front_dead_layer,
            "front_space":front_space,
            "source_position":source_position,
            "runs":runs_per_radionuclide,
            "threads":number_of_threads,
            "time":simulated_minutes,
            },
        }
    with open(output_folder + "metadata.json", "w") as f:
         json.dump(metadata, f, indent=4)

    print("\tDeleting temporary ROOT files...")
    process_delete = "rm " + output_folder + "threadoutput_" + str(i_s) + "*.root"
    # result = subprocess.run(process_delete, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    result = subprocess.run(process_delete, shell=True)

    partial_time = time.time()
    elapsed_minutes = (partial_time - time_interval) / 60
    print(f"\tTime spent for previous run: {elapsed_minutes:.2f} minutes")
    time_interval = partial_time

print("All finished!")

end_time = time.time() # End timing
elapsed_minutes = (end_time - start_time) / 60
print(f"Total time spent: {elapsed_minutes:.2f} minutes")
