import argparse
from numpy import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

parser = argparse.ArgumentParser()
parser.add_argument('file')
parser.add_argument('--path', default=None, help='if file is not in same directory')
args = parser.parse_args()

print os.getcwd()

print 'loading data'
data = np.loadtxt(args.file)
data = data.ravel()
data = data.tolist()
#print data
print max(data)

print 'binning data'
count = []
for i in xrange(200):
    list_i = []
    for k in xrange(len(data)):
        a = i
        b = i+1
        if data[k] >= a and data[k] < b:
            list_i.append(k)
    count.append(len(list_i))

bignums = []
bignumin = []
for t in xrange(len(data)):
    if data[t] >= 200:
        bignumin.append(t)
        bignums.append(data[t])
count.append(len(bignums))
f = open('NEWabove_200_index.dat','w+')
for i in xrange(len(bignumin)):
    f.write(str(bignumin[i]))
    f.write('\n')

at_100 = []
at_100in = []
for t in xrange(len(data)):
    if data[t] == 100.000:
        at_100in.append(t)
        at_100.append(data[t])
f = open('NEWat_100_index.dat','w+')
for i in xrange(len(at_100)):
    f.write(str(at_100in[i]))
    f.write('\n')

os.chdir('/dascratch/mjh9/output_files/bootJac_160_02015_Jul_13/plots')
fig = plt.figure()
ax = fig.add_subplot(111,title='NEW AVG % Diff Histogram')
for i in xrange(len(count)):
    ax.bar(i,count[i],width=1)
fig.savefig('NEWAVG_%_differences_histogram.png')

exit()
