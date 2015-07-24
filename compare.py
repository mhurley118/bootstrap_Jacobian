from numpy import *
import numpy as np
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

cwd = os.getcwd()
print 'loading files'
original = np.loadtxt('originalJac_T160_01000_resamples.txt')
average = np.loadtxt('NEWavgJac_T160_01000_resamples.txt')
os.chdir('%s/new_output_data'%(cwd))
at_100_in = np.loadtxt('NEWat_100_index.dat')
above_200_in = np.loadtxt('NEWabove_200_index.dat')

original = original.tolist()
average = average.tolist()
at_100_in = at_100_in.tolist()
above_200_in = above_200_in.tolist()

print 'determining numbers that present 100% difference'
f = open('NEWat_100_values.dat','w+')
f.write('index (original, average)\n')
for i in xrange(len(original)):
    for k in xrange(len(at_100_in)):
        if i == at_100_in[k]:
            f.write('%s (%s, %s)\n'%(i,original[i],average[i]))

print 'determining numbers that present greater than 200% difference'
f = open('NEWabove_200_values.dat','w+')
f.write('index (original, average)\n')
for i in xrange(len(original)):
    for k in xrange(len(above_200_in)):
        if i == above_200_in[k]:
            f.write('%s (%s, %s)\n'%(i,original[i],average[i]))

originalzeros = open('NEWoriginalzeroes.dat','w+')
for i in xrange(len(original)):
    if original[i] == 0:
        originalzeros.write('%s\n'%i)

print 'creating array of indices > 200'
original = np.asarray(original)
original.shape = (-1,977)
(a,b) = original.shape
pattern = zeros(a*b)
for i in xrange(len(above_200_in)):
    for k in xrange(pattern.size):
        if above_200_in[i] == k:
            pattern[k] = 1
pattern.shape = (a,b) 

print 'plotting'
os.chdir('%s/plots'%(cwd))
fig = plt.figure()
px = fig.add_subplot(111,title='Indices Above 200% Diff')
im = px.pcolor(pattern,cmap='Blues')
fig.colorbar(im)
fig.savefig('indices_above_200.png')
print 'COMPLETE'
exit()
