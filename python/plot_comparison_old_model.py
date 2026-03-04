import matplotlib.pyplot as plt
import uproot
import numpy as np
import pandas as pd

# Experimental efficiencies
meas_csv_path = "experimental_efficiency.csv"
meas_eff_df = pd.read_csv(meas_csv_path)
# print(meas_eff_df)
E = meas_eff_df["E"].to_numpy()
meas_eff = meas_eff_df["eff"].to_numpy()
meas_eff_unc = meas_eff_df["unc_eff"].to_numpy()

# Simulated efficiencies
number_of_events_per_run = 1e5 # need to know this for the simulation!
simulation_path = "../geant4/resources/output_standard_detector_model.root"
simulation_file = uproot.open(simulation_path)
# print(simulation_file.classnames())

sim_eff = []
sim_eff_unc = []
for idx, row in meas_eff_df.iterrows():
    this_nuclide = row["nuclide"]
    this_E = row["E"]
    this_Ig = row["I_g"] / 100

    histo, ex = simulation_file[this_nuclide].to_numpy()
    ex *= 1e3 # MeV to keV
    i_bin = np.searchsorted(ex, this_E, side='right') - 1

    sim_eff.append(histo[i_bin]/(number_of_events_per_run*this_Ig))
    sim_eff_unc.append(np.sqrt(histo[i_bin])/(number_of_events_per_run*this_Ig))
sim_eff = np.array(sim_eff)
sim_eff_unc = np.array(sim_eff_unc)

# Relative difference
compare_eff = (sim_eff - meas_eff) / meas_eff
compare_eff_unc = np.sqrt((sim_eff_unc/meas_eff)**2 + (sim_eff*meas_eff_unc/meas_eff**2)**2)
chi_squared = np.sum((sim_eff - meas_eff)**2 / (sim_eff_unc**2 + meas_eff_unc**2))

# Plot
plt.close('all')
inch_to_mm = 25.4

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
ax.errorbar(E, meas_eff, meas_eff_unc, ls="", capsize=3, marker=".", label="measurement")
ax.errorbar(E, sim_eff, sim_eff_unc, ls="", capsize=3, marker=".", label="simulaion")
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Efficiency")
ax.legend(frameon=False)
plt.tight_layout(pad = 0.2)
save_name = 'comparison_old_model_efficiency'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
ax.errorbar(E, compare_eff, compare_eff_unc, ls="", capsize=3, marker=".", label="(sim-meas)/meas")
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Relative difference")
ax.legend(frameon=False, title=f"chi-squared: {chi_squared:.1f}")
plt.tight_layout(pad = 0.2)
save_name = 'comparison_old_model_rel_diff'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

plt.show()
