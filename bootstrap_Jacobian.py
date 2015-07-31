from numpy import *
import numpy as np
import numpy.random as npr
import os
import time
import argparse
import mdtraj as md
import model_builder as mdb
import project_tools.parameter_fitting.util.util as util
import project_tools.parameter_fitting.FRET.compute_Jacobian as compute
import scipy.stats as stats

model, fitopts = mdb.inputs.load_model('1PB7', dry_run = True)

parser = argparse.ArgumentParser()
parser.add_argument('--trajfile',default='1PB7/iteration_0/160_0/traj.xtc')
parser.add_argument('--topfile',default='1PB7/iteration_0/160_0/Native.pdb')
parser.add_argument('tempfile')
parser.add_argument('--brs',type=int,default=1000)
args = parser.parse_args()

global GAS_CONSTANT_KJ_MOL
GAS_CONSTANT_KJ_MOL = 0.0083144621
def_FRET_pairs = [[114,192]]
defspacing = 0.1 ## in nm
cwd = os.getcwd()
brs = args.brs

if 'fret_pairs' in fitopts:
    fret_pairs = fitopts['fret_pairs']
    FRET_pairs = np.asarray(fret_pairs)-1
    print FRET_pairs

t = md.load(args.trajfile, top = args.topfile)
oFRETr = md.compute_distances(t, FRET_pairs, periodic=False)
shape = oFRETr.shape
matrix_to_list = []
originalJac = []

os.chdir('/dascratch/mjh9/output_files')
from time import strftime
date = strftime('%Y_%b_%d')
print date
try:
    os.mkdir('bootJac_'+args.tempfile+date)
except OSError:
    pass
os.chdir(cwd)

savelocation = '/dascratch/mjh9/output_files/bootJac_'+args.tempfile+date

###############COMPUTE_JACOBIAN###############
def find_sim_bins(savelocation, FRETr, fit_temp, residues=def_FRET_pairs, spacing=defspacing, weights=None):
    """find_sim_bins calculates and writes the simulation files """
    ##assumes nothing about where you are, but assumes the savelocation is specified correctly
    print "Calculating Simulation FRET bins"
    #savelocation should be in "cwd/subdir/iteration_number/fitting_number
    
    ##debugging
    print "save location is in:"
    print savelocation
    print "FRETr is:"
    print FRETr
    print "shape of FRETr is:"
    print np.shape(FRETr)
    print "fit temp is:"
    print fit_temp
    print "residues are:"
    print residues
    print "spacing is:"
    print spacing
    print "weights is"
    print weights
    ##debugging
    
    cwd = os.getcwd()
    
    if not os.path.isdir(savelocation):
        os.mkdir(savelocation)
     
    os.chdir(savelocation)
    FRETmax = 4.4
    FRETmin = 1.9
    maxvalue = int(FRETmax/spacing)
    minvalue = int(FRETmin/spacing)
    num_bins = maxvalue - minvalue
    ran_size = (minvalue*spacing,maxvalue*spacing)
    
    #if not weighted, set weights to ones
    if weights == None:
        weights = np.ones(np.shape(FRETr)[0])
    
    #actually histogram it
    print "***************************"
    print np.shape(FRETr)
    print "***************************"
    hist, edges, slices = stats.binned_statistic(FRETr, weights, statistic="sum", range=[ran_size], bins=num_bins)
    hist = hist/(np.sum(hist)*spacing)
    bincenters = 0.5 * (edges[1:] + edges[:-1])
    
    print "Saving the bincenters:"
    #actually save it
    np.savetxt("simf_valuesT%d.dat"%fit_temp,hist)
    np.savetxt("simf_centers%d.dat"%fit_temp,bincenters)
    np.savetxt("simf-params%d.dat"%fit_temp,np.array([num_bins,minvalue*spacing,maxvalue*spacing,spacing]))
    
    os.chdir(cwd)
    print "Calculated bins for simulation data at a spacing of %.4f" % spacing
    
    return hist, slices
    
def calculate_average_Jacobian(model,fitopts,FRET_pairs=def_FRET_pairs,spacing=defspacing):
    print "Working on calculating model's trajectory and contact info"
    if "t_fit" in fitopts:
        fit_temp = fitopts["t_fit"]
    else:
        raise IOError("Missing the fit_temperature, please specify in .ini file")
    
    if "fret_pairs" in fitopts:
        fret_pairs = fitopts["fret_pairs"]
        FRET_pairs = np.array(fret_pairs) - 1
        print "The FRET pairs are:"
        print FRET_pairs
    
    if "y_shift" in fitopts:
        y_shift = fitopts["y_shift"]   
    else:
        y_shift = 0.0
        fitopts["y_shift"] = 0.0        
 
    if "spacing" in fitopts:
        spacing = fitopts["spacing"]

    cwd = os.getcwd()
    subdir = model.name
    iteration = fitopts["iteration"]
    sub = "%s/%s/iteration_%d" % (cwd,subdir,iteration)
    traj_location = "%s/%d_0" % (sub, fit_temp)
    sim_location = "%s/fitting_%d" % (sub,iteration)
    ##define location of logical files
    os.chdir(traj_location)
    traj,rij,qij = util.get_rij_Vp(model)

    sim_feature, sim_slices = find_sim_bins(sim_location, FRETr[:,0], fit_temp, residues=FRET_pairs, spacing=spacing, weights=None)
    
    beta = 1.0 / (GAS_CONSTANT_KJ_MOL*float(fit_temp))
    os.chdir(cwd)
    
    print "Computing Jacobian and Simparams for the temperature %d, with spacing %f" % (fit_temp, spacing)
    Jacobian = compute.compute_Jacobian_basic(qij,sim_feature*spacing, sim_slices, beta)
    Jacobian /= spacing        
    sim_feature_err = sim_feature ** 0.5
    Jacobian_err = np.zeros(np.shape(Jacobian))
    
    return sim_feature, sim_feature_err, Jacobian, Jacobian_err
###############COMPUTE_JACOBIAN###############

###############BOOTSTRAPPING###############
for i in xrange(brs+1):
    FRETr = oFRETr
    if i < 1:
        sf, sfe, j, je = calculate_average_Jacobian(model,fitopts,FRET_pairs=def_FRET_pairs,spacing=defspacing)
        (num_bins, num) = j.shape
        j = j.ravel()
        j = j.tolist()
        for t in xrange(len(j)):
            matrix_to_list.append(j[t])
            originalJac.append(j[t])
        print 'NUMBER OF SAMPLES'
        print i+1
    elif i >= 1:
        FRETr = FRETr.ravel()
        FRETr = FRETr.tolist()
        FRETr = npr.choice(FRETr, len(FRETr))
        FRETr.shape = shape
        sf, sfe, j, je = calculate_average_Jacobian(model,fitopts, FRET_pairs=def_FRET_pairs, spacing=defspacing)
        j = j.ravel()
        j = j.tolist()
        for t in xrange(len(j)):
            matrix_to_list.append(j[t])
        print 'NUMBER OF SAMPLES:'
        print i+1
        
print 'Analysis Complete'
print 'Reverting list of data into a matrix'
list_to_matrix = np.asarray(matrix_to_list)
# list_to_matrix.shape = (brs+1,-1,977)
# print list_to_matrix.shape
###############BOOTSTRAPPING###############

###############SAVING###############
print 'Creating directory for  data in output_files dir'
os.chdir(savelocation)

print 'Arranging the Jacobians into a list'
np.savetxt('Jac_T'+args.tempfile+str(brs)+'_resamples.dat', list_to_matrix)
# convert data into an array of dimensinos (brs+1, num_bins, 977)

print 'Savings the original Jacobian'
originalJac = np.asarray(originalJac)
originalJac.shape = (-1,977)
np.savetxt('originalJac_T'+args.tempfile+str(brs)+'_resamples.dat', originalJac)

print 'COMPELETE'
exit()
