import numpy as np
import h5py
import read_model

# specify input file here
input_file="./snap.h5"
        
if __name__=='__main__':
    #
    # file reading part
    #
    with h5py.File(input_file, mode='r') as f:
        # define and initialize the model data
        model = read_model.data(f)
        
        # the model has already initialized. 
        # you can get the properties of the models
        # for example, the epoch and the computaitional domain [x_min, x_max, y_min, y_max]
        print(model.time)
        print(model.range)
        
        # you can get the name list of variables as follows
        print(model.var.keys())
        
        # access to the data to retrieve physical values
        # in this example, you get variables "rho" "v1" "e_rad" at (r,z)
        # make sure that the coordinates are within the computational domain 
        # i.e., x_min <= r <= x_max, y_min <= z <= y_max
        r = 1.0e6
        z = 2.0e6
        print(model.get_values(f,[r,z],["rho","v1","e_rad"]))
        
        path, ix, iy = model.get_path(f,[r,z])
        print(path, ix, iy)
        
        print(f[path+"/pv"][0][ix][iy])
        
