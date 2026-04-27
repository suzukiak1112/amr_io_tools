import numpy as np
import h5py

DEBUG = False

#######
#  class for reading a single block from a hdf5 file
#######
class block2d():
    
    def __init__(self):
        super().__init__()

        self.Nnode = 0         # number of nodes
        self.Nval = 0          # number of variables
        self.Nx = 0            # number of x-grid
        self.Ny = 0            # number of y-grid
        self.time = 0.0        # epoch of the simulation
        self.Nblk = []         # list of block numbers
        self.var=[]            # containor for physical variables
        self.plot_var=[]       # container for plot variables
        self.grid_x = None     # grid in x-direction
        self.grid_y = None     # grid in y-direction
        
        self.loaded_node = None
        self.loaded_block = None
        

    def info(self,file_in):
        #
        # read block info
        #
        self.Nnode = file_in["./number_of_processes"][0]
        self.Nval = file_in["./block_size"][0]
        self.Nx = file_in["./block_size"][1]
        self.Ny = file_in["./block_size"][3]
        self.time = file_in["./time"][0]
        if not self.Nblk:
            for n in range(self.Nnode):
                self.Nblk.append(file_in["./"+str(n)+"/number_of_blocks"][0])
        else:
            for n in range(self.Nnode):
                self.Nblk[n]=file_in["./"+str(n)+"/number_of_blocks"][0]
        #
        # mesh generation
        #
        self.grid_x = np.zeros(self.Nx+1)
        self.grid_y = np.zeros(self.Ny+1)
        self.var = [np.zeros((self.Nx, self.Ny)) for _ in range(self.Nval)]
        self.plot_var = [np.zeros((self.Nx, self.Ny)) for _ in range(4)]

        #for iv in range(self.Nval):
        #    self.var.append(np.zeros((self.Nx,self.Ny)))
        #for iv in range(4):
        #    self.plot_var.append(np.zeros((self.Nx,self.Ny)))  
            

    def read_block(self,file_in,node_id,blk_id):
        # 
        # read physical variables in a single AMR block
        #
        if self.loaded_node == node_id and self.loaded_block == blk_id:
            return  # already loaded
        else:
            # read grid_x
            group = file_in[str(node_id)][str(blk_id)]
            self.grid_x[:self.Nx] = group["grid_x"][0][:]
            self.grid_x[self.Nx] = group["grid_x"][2][self.Nx-1]
            # read grid_y
            self.grid_y[:self.Ny] = group["grid_y"][0][:]
            self.grid_y[self.Ny] = group["grid_y"][2][self.Ny-1]
            # read variables
            for iv in range(self.Nval):
                self.var[iv]= group["pv"][iv][:]

            # update loaded node and block
            self.loaded_node = node_id
            self.loaded_block = blk_id
                   
            
    def search(self,file_in,node_id,blk_id,x_in,y_in):
        # 
        # search 
        #
        self.read_block(file_in,node_id,blk_id)
        idx_x = np.searchsorted(self.grid_x, x_in) -1
        idx_y = np.searchsorted(self.grid_y, y_in) -1
        
        if DEBUG == True:
            print(self.grid_x, x_in, self.grid_x[idx_x], self.grid_x[idx_x+1])
            print(self.grid_y, y_in, self.grid_y[idx_y], self.grid_y[idx_y+1])
            
        return idx_x, idx_y
 

#######
#  class for reading the block structure from a hdf5 file
#######
class block_structure():
    def __init__(self, file_in):
        super().__init__()
        
        # information on the base blocks
        self.number_of_base_blocks = file_in["block_structure/base/number_of_base_blocks"][0]
        
        # list "base" contains (rank,id) of the base blocks
        self.base = []
        for n in range(self.number_of_base_blocks):        
            self.base.append([])
            self.base[-1].append(file_in["block_structure/base"][str(n)]["rank"][0])
            self.base[-1].append(file_in["block_structure/base"][str(n)]["id"][0])


    def test(self, file_in):
        # this loop access the base blocks one by one
        for n in range(self.number_of_base_blocks):
            node_blk = str(self.base[n][0])+"/"+str(self.base[n][1])
            for item in file_in["block_structure/"+node_blk]: 
                print(item)
            print(file_in["block_structure/"+node_blk]["block_range"][:])


    def search_base(self, file_in, x_in, y_in):
        # search x and y ranges in base blocks
        # this loop access the base blocks one by one
        for n in range(self.number_of_base_blocks):
            node_blk = str(self.base[n][0])+"/"+str(self.base[n][1])
            lims = file_in["block_structure/"+node_blk]["block_range"][:]
            if lims[0] <= x_in and x_in < lims[1] and lims[2] <= y_in and y_in < lims[3]:
                return self.base[n][0],self.base[n][1]
            
        # in cases of (x,y) not in the domain coverrd by the base blocks
        print("input (x,y) not in the simulation domain")
        return -1,-1
    
    
    def recursive_access(self, file_in, x_in, y_in, node_in, blk_in):
        node_blk = str(node_in)+"/"+str(blk_in)

        if file_in["block_structure/"+node_blk]["child_rank"][0] < 0:
            # no child block. directly return rank and id
            block_no = file_in["block_structure/"+node_blk]["block_number"][0]
            return node_in,block_no
        else:
            # this block (rank,id) has child blocks. 
            order = 0
            lims = file_in["block_structure/"+node_blk]["block_range"][:]
            if 0.5*(lims[0]+lims[1]) < x_in:
                order = order + 1
            if 0.5*(lims[2]+lims[3]) < y_in:
                order = order + 2
                
            # rankd and id for the corresponding child block
            child_node = file_in["block_structure/"+node_blk]["child_rank"][order]
            child_blk = file_in["block_structure/"+node_blk]["child_id"][order]
            
            # recurssively access to the child block
            return self.recursive_access(file_in,x_in,y_in,child_node,child_blk)
    
    
    def search(self,file_in,x_in,y_in):
        node_id,blk_id = self.search_base(file_in,x_in,y_in)
        if node_id > -1:
            return self.recursive_access(file_in,x_in,y_in,node_id,blk_id)
        else:
            print("input (x,y) not in the simulation domain")
            return -1,-1
         
            
#######
#  class for a container of model data
#######
class data():  
    def __init__(self, file_in):
        super().__init__()
        
        self.structure = block_structure(file_in)
        self.block = block2d()
        self.block.info(file_in)

        # model properties
        self.Nnode = file_in["./number_of_processes"][0]
        self.Nval = file_in["./block_size"][0]
        self.Nx = file_in["./block_size"][1]
        self.Ny = file_in["./block_size"][3]
        self.time = file_in["./time"][0]
        
        # computational domain x in [x_min,x_max] and y in [y_min,y_max]
        self.x_min = None
        self.x_max = None
        self.y_min = None
        self.y_max = None
        for n in range(self.structure.number_of_base_blocks):        
            path = "block_structure/"+str(self.structure.base[n][0])+"/"+str(self.structure.base[n][1])
            if self.x_min == None:
                self.x_min = file_in[path]["block_range"][0]
                self.x_max = file_in[path]["block_range"][1]
                self.y_min = file_in[path]["block_range"][2]
                self.y_max = file_in[path]["block_range"][3]
            else:
                if self.x_min > file_in[path]["block_range"][0]:
                    self.x_min = file_in[path]["block_range"][0]
                if self.x_max < file_in[path]["block_range"][1]:
                    self.x_max = file_in[path]["block_range"][1]
                if self.y_min > file_in[path]["block_range"][2]:
                    self.y_min = file_in[path]["block_range"][2]
                if self.y_max < file_in[path]["block_range"][3]:
                    self.y_max = file_in[path]["block_range"][3]
        self.range = np.array([self.x_min, self.x_max, self.y_min, self.y_max])
        
        self.node_id = -1
        self.block_no = -1
        self.idx_x = -1
        self.idx_y = -1
        
        # list of variables and the corrsponding indices
        self.var = {"rho": 0,       # mass density
                    "v1": 1,        # velocity in x1-direction
                    "v2": 2,        # velocity in x2-direction
                    "v3": 3,        # velocity in x3-direction
                    "e_gas": 4,     # gas energy density
                    "e_rad": 5,     # thermal photon energy density
                    "f1": 6,        # thermal photon flux in x1-direction
                    "f2": 7,        # thermal photon flux in x2-direction
                    "f3": 8,        # thermal photon flux in x3-direction
                    "e_rad_nt": 9,  # non-thermal photon energy density
                    "f1_nt": 10,    # non-thermal photon flux in x1-direction
                    "f2_nt": 11,    # non-thermal photon flux in x2-direction
                    "f3_nt": 12,    # non-thermal photon flux in x3direction
                    "Xej": 13,      # ejecta mass fraction
                    "Xcsm": 14,     # eecta+CSM mass fraction
                    "Xrad": 15,     # radioactive element mass fraction
                    "Xel": 16,      # electron mass fraction
                    "Xh": 17,       # hydrogen mass fraction
                    "Xhe": 18,      # helium mass fraction
                    "Xc": 19,       # carbon mass fraction
                    "Xn": 20,       # nitrogen mass fraction
                    "Xo": 21,       # oxygen mass fraction
                    "Xne": 22,      # neon mass fraction
                    "Xmg": 23,      # magnesium mass fraction
                    "Xsi": 24,      # silicon mass fraction
                    "Xs": 25,       # sulfer mass fraction
                    "Xar": 26,      # argon mass fraction
                    "Xca": 27,      # calsium mass fraction
                    "Xfe": 28,      # iron mass fraction
                    }
        
        # units for variables
        self.units = {"r": 29979245800.0,
                      "z": 29979245800.0,
                      "rho": 1.0,
                      "v1": 29979245800.0,
                      "v2": 29979245800.0,
                      "v3": 29979245800.0,
                      "e_gas": 8.9875518e+20,
                      "e_rad": 8.9875518e+20,
                      "f1": 2.6944002e+31,
                      "f2": 2.6944002e+31,
                      "f3": 2.6944002e+31,
                      "e_rad_nt": 8.9875518e+20,
                      "f1_nt": 2.6944002e+31,
                      "f2_nt": 2.6944002e+31,
                      "f3_nt": 2.6944002e+31}
        
        
    def get_indices(self,file_in, x_in, y_in):
        # get node ID and block Number
        self.node_id, self.block_no = self.structure.search(file_in,x_in,y_in)
        
        # given (x,y) inside the computational domain
        if self.node_id > -1: 
            self.idx_x, self.idx_y = self.block.search(file_in,self.node_id,self.block_no,x_in,y_in)
        # given (x,y) ouside the computational domain
        else:
            self.idx_x = -1
            self.idx_y = -1
        
        if DEBUG == True:
            print(self.node_id, self.block_no, self.idx_x, self.idx_y)
            print(self.block.grid_y)
            print(self.block.var[0].shape)
            
        return self.node_id, self.block_no, self.idx_x, self.idx_y
    
    
    def get_indices_test(self,file_in, xy_list):
        node_blk_list=[]
        for xy in xy_list:
            # get node ID and block Number
            node_id, block_no = self.structure.search(file_in,xy[0],xy[1])
            node_blk_list.append( [node_id, block_no] )
            
            if DEBUG == True:
                if len(node_blk_list)%200 == 0:
                    print(len(node_blk_list)/200,xy)


    def get_values(self, file_in, pos, var_list):
        self.get_indices(file_in, pos[0], pos[1])
        result = []
        for varname in var_list:
            result.append(self.block.var[self.var[varname]][self.idx_x][self.idx_y])
        return result
    
        
    def get_path(self, file_in, pos):
        self.get_indices(file_in, pos[0], pos[1])
        return str(self.node_id)+"/"+str(self.block_no), self.idx_x, self.idx_y