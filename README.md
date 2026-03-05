# Replicate-HPGe-efficiency

High purity germanium (HPGe) gamma spectrometers are useful in many areas of nuclear science. They can, for instance, be used to determine the activity of a sample $A$, based on a measured peak count rate $c$, a gamma-ray intensity $I_\gamma$, and the detection efficiency $\varepsilon$ according to 

$$
A = \frac{c}{I_\gamma \varepsilon} .
$$

The detection efficiency $\varepsilon$ is heavily affected by the detector design, source geometry, and the measured radionuclide (for example through true coincidence summing). A flexible way of determining $\varepsilon$ is through simulations. In such simulations, it is crucial that the response of the modeled detector matches the response of the real detector as closely as possible. 

In this repository, there is code that: 
1. Plots experimentall measured efficiencies for a detecor. 
2. Simulates the resonse of the detector model. 
3. Compares the measured and simulated efficiency. 
4. Simulates the resonse of the detector model, but randomly varies design parameters withing user-specified ranges. For instance, randomly selects a dead layer between two values. 
5. Plots the efficiency of the randomly generated detector that best agrees with experimental data. 

In this case, the UGGLA HPGe detector is modeled. The parameters that are randomly varied are the front dead layer, side dead layer, and distance between the Ge crystal and the Al can. 

## Short instructions

Very short and limited instructions are supplied here. Inside a micromamba environment with the configuration specified in micromamba_env.yaml (or any other environment with root and python). 

To run Geant4:

    cd geant4

    mkdir build

    mkdir output

    cd build

    cmake ..

    make -j4

    cd ..

    python3 auto_run_geant4.py

Data analysis is handled in a different directory (you need uproot, matplotlib, pandas, numpy):

    cd python

    python3 plot_comparison_old_model.py

## Example of results

Before: 

![Efficiency before](/python/figures/comparison_old_model_efficiency.jpg)

After: 

![Efficiency after](/python/figures/comparison_new_model_efficiency.jpg)

## Limitations

The best-fitting result is still not perfect, so some additional tweaking is needed. Perhaps, to increase the thickness of the Al. 
