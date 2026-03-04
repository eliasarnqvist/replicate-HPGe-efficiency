# replicate-HPGe-efficiency
Trying to replicate the efficiency of the UGGLA HPGe detector by varying parameters of the detector 

## short instructions

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
