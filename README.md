# AMR_IO_tools
Codes and scripts for reading data from AMR hydrodynamic simulations

Currenlyt, python scripts are provided. Details are described below

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
  The simulatin domain is expressed by a Numpy array with 4 components, (x_min, x_max, y_min, y_max). 
