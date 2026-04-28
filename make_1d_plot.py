import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import h5py
import read_model

# specify input file here
input_file="./snap.h5"
# specify output file here
output_file="./test.txt"

if __name__=='__main__':
    #
    # file reading part
    #
    with h5py.File(input_file, mode='r') as f:
        # define and initialize the model data
        model = read_model.data(f)
        
        # radial coordinate and variables
        rad_list = []
        var_list = []
        for n in range(2000):
            r = 1.0
            z = 0.0 + 30.0e1 * n
            rad_list.append(np.sqrt(r**2 + z**2))
            var_list.append(model.get_values(f,[r,z],["rho","v1","v2","f1","f2","Xej","Xcsm"]))
            
        # nor var_list[0:2000] contains 2000 lists of physical variables 
        # as is specified in get_values() rho -> 0, v1 -> 1, v2 -> 2 and so on
        # check the first 10 items in the unit
        print(rad_list[:10])
        print(var_list[:10])
    #
    # saving the 1D prpfile to an output text file in the same directory
    #
    with open(output_file, mode="w") as fout:
        for n in range(len(rad_list)):
            fout.write(str(rad_list[n])+" ")
            for var in var_list[n]:
                fout.write(str(var)+" ")
            fout.write("\n")
    #
    # plotting part
    #
    fig=plt.figure()
    ax1 = fig.add_subplot(311)
    ax2 = fig.add_subplot(312)
    ax3 = fig.add_subplot(313)
    
    # plotting density profile
    ax1.plot(np.array(rad_list)*model.units["r"], 
             np.array(var_list).T[0]*model.units["rho"],   # rho is 0-th compoennt
             label="rho",color="black")
    ax1.fill_between(np.array(rad_list)*model.units["r"], 
                     np.array(var_list).T[0]*model.units["rho"]*(np.array(var_list).T[5]), 
                     color="blue",alpha=0.3)
    ax1.fill_between(np.array(rad_list)*model.units["r"], 
                     np.array(var_list).T[0]*model.units["rho"]*(np.array(var_list).T[6]), 
                     color="gray",alpha=0.3)
    
    # plotting velocity profile
    # velocity norm is computed by v_r = (v1^2 + v2^2)^1/2
    velocity = np.sqrt( np.array(var_list).T[1]**2 + np.array(var_list).T[2]**2 )
    ax2.plot(np.array(rad_list)*model.units["r"], 
             velocity*model.units["v1"], 
             label="vr",color="black")
    
    # you may compute and plot outgoing luminosity from flux and radius: 4*pi*r^2*|F|
    flux = np.sqrt( np.array(var_list).T[3]**2 + np.array(var_list).T[4]**2 )
    luminosity = flux*model.units["f1"] * 4.0*np.pi*(np.array(rad_list)*model.units["r"])**2
    ax3.plot(np.array(rad_list)*model.units["r"], 
             luminosity, 
             label="e_rad",color="black")
    
    # axis settings
    ax1.set_yscale("log")
    ax1.set_ylim([1.0e-22,1.0e-9])
    ax2.set_yscale("log")
    ax2.set_ylim([1.0e6,1.0e9])
    ax3.set_yscale("log")
    ax3.set_ylim([1.0e40,1.0e45])
    plt.show()
