# AMR_IO_tools
Codes and scripts for reading data from AMR hydrodynamic simulations
Currenlyt, python scripts are provided. Details are described below

# Dataset description
A single simulation data (e.g., snap.h5) is a snapshot of radiation-hydrodynamic simulation in 2D cylindrical coordinate (r,z). 
Since the original simulations employ adaptive-mesh-refinement (AMR), the grid structure and resolution can be different from a domain to another. 
Variables on specific numerical cells (e.g, density, velocity, and so on) are therefore kept in a hierarchical way, which is complicated. 
Ths following codes help users to extract values at specific points on the simulation domain, output them in ASCII format, and make plots. 


# HDF5 setting
Simulation data are stored in HDF5 (Hierarchical Data Fromat version 5; https://www.hdfgroup.org/solutions/hdf5/).
In order to read HDF5 files, you need to install h5py module (https://docs.h5py.org/). 
Installation can be completed by following the instruction given by https://docs.h5py.org/en/stable/build.html.


# How to use
The current version of repository contains a Python script, `read_model.py`, and three examples, `read_snapshot.py`, `make_1d_plot.py`, and `make_2d_plot.py`. 
The script `read_model.py` contains some basic functions to explore the data. 
Users are not supposed to directly modify this script. 
The three example codes show how to read and analyze a sample data file `snap.h5`, which should be located in the same directory. 
`snap.h5` is a sample data of spherical supernova ejecta (10 Msun) with spherical circumstellar material (2 Msun). 


## read_snapshot.py
This example explains basic usage of the functions provided by `read_mdoel.py`
The code reads the data file and extracts some values. 
- First of all, the code starts with iimporting necessary modules:
  ```
  import matplotlib.pyplot as plt
  import matplotlib.gridspec as gridspec
  import numpy as np
  import h5py
  import read_model
  ```
- Next, input filename is specified:
  ```
  input_file="./snap.h5"
  ```
- The main part starts with:
  ```
  with h5py.File(input_file, mode='r') as f:
  ```
  , which opens the file as f and initialize the model data
  ```
  model = read_model.data(f)
  ```
  Now, you can use functions provided by `read_model` for the dataset.
- After data loading, the code botains and prints the epoch and the domain of the simulation.
  ```
  print(model.time)
  print(model.range)
  ``` 
  In this example, the corresponding output on the terminal should look like:
  ```
  10367926.400037047
  [       0.          4269620.41853635 -4269620.41853635  4269620.41853635]
  ```
  The units of the time and coordinates are seconds and light-seconds (~ 3.0e10 cm).
  The first line means the simulation epoch is t = 10367926.400037047 ~ 120 days.
  The simulatin domain is expressed by a Numpy array with 4 components, (r_min, r_max, z_min, z_max).
- Users can check the physical variables contained in the data:
  ```
  print(model.var.keys())
  ``` 
  The corresponding output would look like:
  ```
  dict_keys(['rho', 'v1', 'v2', 'v3', 'e_gas', 'e_rad', 'f1', 'f2', 'f3', 'e_rad_nt', 'f1_nt', 'f2_nt', 'f3_nt', 'Xej', 'Xcsm', 'Xrad', 'Xel', 'Xh', 'Xhe', 'Xc', 'Xn', 'Xo', 'Xne', 'Xmg', 'Xsi', 'Xs', 'Xar', 'Xca', 'Xfe'])
  ```
  Each label stands for density (rho), 3 components of velocity (v1, v2, v3), gas energy density (e_gas), thermal radiation energy density (e_rad), thermal radiation flux (f1, f2, f3), non-thermal radiation (e_rad_nt, f1_nt, f2_nt, f3_nt), ejecta mass fraction (Xej), CSM+ejecta mass fraction (Xcsm), mass fraction of radioactive nickel (Xrad), electron mass fraction (Xel) and mass fractions of 12 elements (Xh to Xfe).

- Here, we retrieve density (rho), velocity (v1), and the radiation energy density (e_rad) by using the function `getvalues()`:
   ```
   r = 1.0e6
   z = 2.0e6
   print(model.get_values(f,[r,z],["rho","v1","e_rad"]))
   ```
  Users give file f, the coordinate r and z, and the name list of variables (rho, v1, e_rad) for `getvalues()`.
  In this example, we access vriables at r = 1e6 and z = 2e6, which is inside the numerical domain range.
  The corresponding terminal output should be
  ```
  [1.1166868116161294e-22, 2.6709488609033433e-09, 8.661066136634234e-24]
  ```

## make_1d_plot.py
