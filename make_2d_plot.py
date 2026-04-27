import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import h5py
import read_model

# specify input file here
input_file="../result/snap.h5"

# specify output file here
figure_file="./test.png"

        
if __name__=='__main__':
    #
    # file reading part
    #
    with h5py.File(input_file, mode='r') as f:
        # define and initialize the model data
        model = read_model.data(f)
        
        # mapping the density distribution [0,2000]x[0,2000] into 200 x 200 regular grid
        Nr = 200
        Nz = 400
        r_range = 5.0e5
        z_range = 10.0e5
        dr = r_range/Nr
        dz = z_range/Nz
        mesh_r = np.zeros([Nr+1, Nz+1])
        mesh_z = np.zeros([Nr+1, Nz+1])
        var = np.zeros([Nr, Nz])
        for i in range(Nr):
            r = 0.0 + dr * (i + 0.5)
            for j in range(Nz):
                z = -z_range*0.5 + dz * (j + 0.5)
                mesh_r[i][j]   = mesh_r[i][j+1]   = 0.0 + dr * i
                mesh_r[i+1][j] = mesh_r[i+1][j+1] = 0.0 + dr * (i+1)
                mesh_z[i][j]   = mesh_z[i][j+1]   = -z_range*0.5 + dz * j
                mesh_z[i+1][j] = mesh_z[i+1][j+1] = -z_range*0.5 + dz * (j+1)
                var[i][j] = model.get_values(f,[r, z],["rho"])[0]
    #
    # plotting part
    #
    fig=plt.figure()
    ax1 = fig.add_subplot(111,aspect='equal')
    ax1.pcolor(mesh_r, mesh_z, np.log10(var), vmin=-20, vmax=-12)
    plt.savefig(figure_file,format='png',dpi=300)
    plt.show()
 