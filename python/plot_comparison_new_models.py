import matplotlib.pyplot as plt
import uproot
import numpy as np
import pandas as pd
import json

# Experimental efficiencies
meas_csv_path = "experimental_efficiency.csv"
meas_eff_df = pd.read_csv(meas_csv_path)
# print(meas_eff_df)
E = meas_eff_df["E"].to_numpy()
meas_eff = meas_eff_df["eff"].to_numpy()
meas_eff_unc = meas_eff_df["unc_eff"].to_numpy()

# Simulated efficiencies
metadata_path = "../geant4/output/metadata.json"
with open(metadata_path) as f:
    metadata = json.load(f)

for run_id, run_info in metadata.items():
    filename = run_info["filename"]
    simulation_path = "../geant4/output/"
    simulation_file = uproot.open(simulation_path + filename)

    number_of_events_per_run = run_info["properties"]["runs"]

    sim_eff = []
    sim_eff_unc = []
    sim_eff_E = []
    for idx, row in meas_eff_df.iterrows():
        this_nuclide = row["nuclide"]
        this_E = row["E"]
        this_Ig = row["I_g"] / 100

        histo, ex = simulation_file[this_nuclide].to_numpy()
        ex *= 1e3 # MeV to keV
        i_bin = np.searchsorted(ex, this_E, side='right') - 1

        # subtract continuum ("background")
        peak_counts = histo[i_bin] - (histo[i_bin-1] + histo[i_bin+1])/2
        peak_counts_unc = np.sqrt(np.sqrt(histo[i_bin])**2 + (0.5*np.sqrt(histo[i_bin-1]))**2 + (0.5*np.sqrt(histo[i_bin+1]))**2)

        sim_eff.append(peak_counts/(number_of_events_per_run*this_Ig))
        sim_eff_unc.append(peak_counts_unc/(number_of_events_per_run*this_Ig))
        sim_eff_E.append(this_E)

    metadata[run_id]["sim_eff"] = sim_eff
    metadata[run_id]["sim_eff_unc"] = sim_eff_unc
    metadata[run_id]["sim_eff_E"] = sim_eff_E

    sim_eff = np.array(sim_eff)
    sim_eff_unc = np.array(sim_eff_unc)

    # Relative difference
    compare_eff = (sim_eff - meas_eff) / meas_eff
    compare_eff_unc = np.sqrt((sim_eff_unc/meas_eff)**2 + (sim_eff*meas_eff_unc/meas_eff**2)**2)
    chi_squared = np.sum((sim_eff - meas_eff)**2 / (sim_eff_unc**2 + meas_eff_unc**2))

    compare_eff = list(compare_eff)
    compare_eff_unc = list(compare_eff_unc)
    chi_squared = float(chi_squared)

    metadata[run_id]["compare_eff"] = compare_eff
    metadata[run_id]["compare_eff_unc"] = compare_eff_unc
    metadata[run_id]["chi_squared"] = chi_squared

save_name = "metadata_updated.json"
with open("metadata_updated.json", "w") as f:
    json.dump(metadata, f, indent=4)



# Plot
plt.close('all')
inch_to_mm = 25.4
color = plt.cm.tab10

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
ax.errorbar(E, meas_eff, meas_eff_unc, ls="", capsize=3, marker=".", label="measurement", color=color(0), zorder=2)
i = 0
for run_id, run_info in metadata.items():
    run_E = run_info["sim_eff_E"]
    run_sim_eff = run_info["sim_eff"]
    run_sim_eff_unc = run_info["sim_eff_unc"]
    if i == 0:
        ax.errorbar(run_E, run_sim_eff, run_sim_eff_unc, ls="", capsize=3, marker=".", label="simulaion(s)", color=color(1), zorder=1)
    else:
        ax.errorbar(run_E, run_sim_eff, run_sim_eff_unc, ls="", capsize=3, marker=".", color=color(1), zorder=1)
    i += 1
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Efficiency")
ax.legend(frameon=False)
plt.tight_layout(pad = 0.2)
save_name = 'comparison_new_models_efficiency'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
for run_id, run_info in metadata.items():
    run_E = run_info["sim_eff_E"]
    run_compare_eff = run_info["compare_eff"]
    run_compare_eff_unc = run_info["compare_eff_unc"]
    ax.errorbar(run_E, run_compare_eff, run_compare_eff_unc, ls="", capsize=3, marker=".", color=color(0), zorder=1)
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Relative difference")
plt.tight_layout(pad = 1)
save_name = 'comparison_new_models_rel_diff'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
for run_id, run_info in metadata.items():
    x = run_info["properties"]["side_dead_layer"]
    y = run_info["chi_squared"]
    ax.errorbar(x, y, None, ls="", capsize=3, marker=".", color=color(0))
ax.set_xlabel("side_dead_layer (mm)")
ax.set_ylabel("Chi-squared")
ax.set_yscale("log")
plt.tight_layout(pad = 0.2)
save_name = 'new_models_chi_vs_sdl'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
for run_id, run_info in metadata.items():
    x = run_info["properties"]["front_dead_layer"]
    y = run_info["chi_squared"]
    ax.errorbar(x, y, None, ls="", capsize=3, marker=".", color=color(0))
ax.set_xlabel("front_dead_layer (mm)")
ax.set_ylabel("Chi-squared")
ax.set_yscale("log")
plt.tight_layout(pad = 0.2)
save_name = 'new_models_chi_vs_fdl'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
for run_id, run_info in metadata.items():
    x = run_info["properties"]["front_space"]
    y = run_info["chi_squared"]
    ax.errorbar(x, y, None, ls="", capsize=3, marker=".", color=color(0))
ax.set_xlabel("front_space (mm)")
ax.set_ylabel("Chi-squared")
ax.set_yscale("log")
plt.tight_layout(pad = 0.2)
save_name = 'new_models_chi_vs_fs'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
for run_id, run_info in metadata.items():
    x = run_info["properties"]["cap_thickness"]
    y = run_info["chi_squared"]
    ax.errorbar(x, y, None, ls="", capsize=3, marker=".", color=color(0))
ax.set_xlabel("cap_thickness (mm)")
ax.set_ylabel("Chi-squared")
ax.set_yscale("log")
plt.tight_layout(pad = 0.2)
save_name = 'new_models_chi_vs_ct'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')



best_run_ids = []
for run_id, run_info in metadata.items():
    chi2 = run_info["chi_squared"]
    sdl = run_info["properties"]["side_dead_layer"]
    fdl = run_info["properties"]["front_dead_layer"]
    fs = run_info["properties"]["front_space"]
    ct = run_info["properties"]["cap_thickness"]
    if chi2 < 10:
        print(sdl, fdl, fs, ct, run_id)
        best_run_ids.append(run_id)

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
ax.errorbar(E, meas_eff, meas_eff_unc, ls="", capsize=3, marker=".", label="measurement")
for i, best_run_id in enumerate(best_run_ids):
    best_sim_eff_E = metadata[best_run_id]["sim_eff_E"]
    best_sim_eff = metadata[best_run_id]["sim_eff"]
    best_sim_eff_unc = metadata[best_run_id]["sim_eff_unc"]
    ax.errorbar(best_sim_eff_E, best_sim_eff, best_sim_eff_unc, ls="", capsize=3, marker=".", label=f"best simulaion {i}", color=color(i+1))
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Efficiency")
ax.legend(frameon=False)
plt.tight_layout(pad = 1)
save_name = 'comparison_best_model_efficiency'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
for i, best_run_id in enumerate(best_run_ids):
    best_sim_compare_E = metadata[best_run_id]["sim_eff_E"]
    best_sim_compare = metadata[best_run_id]["compare_eff"]
    best_sim_compare_unc = metadata[best_run_id]["compare_eff_unc"]
    ax.errorbar(best_sim_compare_E, best_sim_compare, best_sim_compare_unc, ls="", capsize=3, marker=".", label=f"best simulaion {i}", color=color(i+1))
ax.plot([0, 1400], [0, 0], ls="--", color="black")
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Relative difference")
ax.legend(frameon=False)
plt.tight_layout(pad = 0.2)
save_name = 'comparison_best_model_rel_diff'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

plt.show()
