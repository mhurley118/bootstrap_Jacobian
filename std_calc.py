import numpy as np
from numpy import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('temp')
args = parser.parse_args()

Jac = np.loadtxt('Jac_T'+args.temp+'_01000_resamples.txt')
Jac.shape = (1001,-1,977)
x,y,z = Jac.shape

stddevs = []
for i in xrange(y):
    for j in xrange(z):
        val = std(Jac[:,i,j])
        stddevs.append(val)

sfile = open('std_T160_01000_resamples.txt','w+')
for i in xrange(len(stddevs)):
    sfile.write(str(stddevs[i]))
    sfile.write(' ')

stddevs = np.asarray(stddevs)
stddevs.shape = (-1, 977)
print stddevs.shape
fig = plt.figure()
ax = fig.add_subplot(111, title='Standard Deviations')
im = ax.pcolor(stddevs, cmap = 'Blues')
fig.colorbar(im)
fig.savefig('stddev')

