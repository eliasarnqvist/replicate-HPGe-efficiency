import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

csv_path = "experimental_efficiency.csv"
df_eff = pd.read_csv(csv_path)
# print(df_eff)

E = df_eff["E"].to_numpy()
eff = df_eff["eff"].to_numpy()
unc_eff = df_eff["unc_eff"].to_numpy()

plt.close('all')
inch_to_mm = 25.4

fig, ax = plt.subplots(figsize=(100/inch_to_mm,80/inch_to_mm))
ax.errorbar(E, eff, unc_eff, ls="", capsize=3, marker=".")
ax.set_xlabel("Energy (keV)")
ax.set_ylabel("Efficiency")
plt.tight_layout(pad = 0.2)

save_name = 'experimental_efficiency'
plt.savefig(f'figures/{save_name}.jpg', dpi=300)
plt.savefig(f'figures/{save_name}.pdf')

plt.show()
