from numpy import *
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import argparse
import os

cwd = os.getcwd()

parser = argparse.ArgumentParser()
parser.add_argument('temp')
parser.add_argument('--plots',default='False',action='store_true',help='running initial plots of Jacobians')
parser.add_argument('--tests',default='False',action='store_true',help='testing new plots')
args = parser.parse_args()

print 'loading files'
avgJac = np.loadtxt('NEWavgJac_T'+args.temp+'_01000_resamples.txt')
stddev = np.loadtxt('std_T'+args.temp+'_01000_resamples.txt')
# Jac = np.loadtxt('Jac_T'+args.temp+'_01000_resamples.txt')

print 'altering shape'
avgJac.shape = (-1,977)
stddev.shape = (-1,977)
# Jac.shape = (1001,-1,977)

print 'acquiring original Jacobian'
originalJac = np.loadtxt('originalJac_T160_01000_resamples.txt')
originalJac.shape = (-1,977)

def plots():
    os.chdir('%s/plots'%(cwd))
    afig = plt.figure()
    ax = afig.add_subplot(111,title='NEW Avgerage Jacobian')
    print 'plotting avgJac'
    im_a=ax.pcolormesh(avgJac,cmap='Blues')
    afig.colorbar(im_a)
    print 'saving'
    afig.savefig('NEWaverage_Jacobian_T'+args.temp+'.png')
    
    Jfig = plt.figure()
    Jx = Jfig.add_subplot(111,title='Original Jacobian')
    print 'plotting original Jacobian'
    im_J=Jx.pcolormesh(originalJac,cmap='Blues')
    Jfig.colorbar(im_J)
    print 'saving'
    Jfig.savefig('original_Jacobian_T'+args.temp+'.png')


    (r, c) = avgJac.shape
    diff = []
    print 'Calculating Difference Between Jacobians'
    for i in xrange(r):
        for j in xrange(c):
            value = avgJac[i,j] - originalJac[i,j]
            diff.append(abs(value))
    diff = np.asarray(diff)
    diff.shape = (r,c)
    print 'Creating figure'
    dfig = plt.figure()
    dx = dfig.add_subplot(111, title='NEW Difference')
    im_d = dx.pcolormesh(diff, cmap = 'Blues')
    dfig.colorbar(im_d)
    dfig.savefig('NEWdiff_avgJac_v_originalJac.png')
    print np.amax(diff)

    print 'Calculating Percent Difference Between Jacobians'
    perdiff = []
    for i in xrange(r):
        for j in xrange(c):
            value = avgJac[i,j] - originalJac[i,j]
            if originalJac[i,j] != 0:
                 percent = abs((value/originalJac[i,j])*100)
            else:
                 percent = abs(value)*100
            perdiff.append(percent)
    perdiff = np.asarray(perdiff)
    perdiff.shape = (r,c)
    print np.amax(perdiff)
    print 'Creating figure'
    pfig = plt.figure()
    px = pfig.add_subplot(111, title='NEW % Difference')
    im_p = px.pcolormesh(perdiff, cmap = 'Blues')
    pfig.colorbar(im_p)
    pfig.savefig('NEW%_difference_avgJac_v_originalJac.png')

    print 'filtering out high values'
    os.chdir('%s/new_output_data'%(cwd))
    f = open('NEWhigh_values.dat', 'w+')
    t = open('NEW%_differences_AVG.dat', 'w+')
    for i in xrange(43):
        for j in xrange(977):
            t.write('%s '%perdiff[i,j])
            if perdiff[i,j] > 10:
                f.write('(%s,%s)'%(i,j))
                f.write(' ')
                f.write(str(perdiff[i,j]))
                f.write('\n')
                perdiff[i,j]=0
    os.chdir('%s/plots'%(cwd))
    ffig = plt.figure()
    fx = ffig.add_subplot(111,title='NEW Filtered % Difference')
    im_f = fx.pcolormesh(perdiff, cmap='Blues')
    ffig.colorbar(im_f)
    ffig.savefig('NEW%_diff_filtered10.png')

def tests():
    os.chdir('%s/plots'%(cwd))
    print 'Calculating Percent Difference Between Jacobian and Std'
    (r, c) = avgJac.shape
    print stddev.shape
    print avgJac.shape
    perdiff = []
    for i in xrange(r):
        for j in xrange(c):
            value = stddev[i,j] - avgJac[i,j]
            if avgJac[i,j] != 0:
                 percent = abs((value/avgJac[i,j])*100)
            else:
                 percent = 0
            perdiff.append(percent)
    perdiff = np.asarray(perdiff)
    perdiff.shape = (r,c)
    print np.amax(perdiff)
    print 'Creating figure'
    psfig = plt.figure()
    psx = psfig.add_subplot(111, title='NEW % Difference Between AvgJac and Std')
    im_ps = psx.pcolormesh(perdiff, cmap = 'Blues')
    psfig.colorbar(im_ps)
    psfig.savefig('NEW%_difference_avgJac_v_stddev.png')
    psfig = plt.figure()

    print 'filtering out high values'
    os.chdir('%s/new_output_data'%(cwd))
    s = open('NEWhigh_stdvalues.dat', 'w+')
    fperdiff = perdiff
    for i in xrange(43):
        for j in xrange(977):
            if fperdiff[i,j] > 10:
                s.write('(%s,%s) '%(i,j))
                s.write(str(fperdiff[i,j]))
                s.write('\n')
                fperdiff[i,j]=0
    os.chdir('%s/plots'%(cwd))
    sfig = plt.figure()
    sx = sfig.add_subplot(111,title='NEW Filtered STD % Difference')
    im_s = sx.pcolormesh(fperdiff, cmap='Blues')
    sfig.colorbar(im_s)
    sfig.savefig('NEWSTD_%_diff_filtered10.png')

if args.plots==True:
    plots()
elif args.tests==True:
    tests()
elif args.tests==True and args.plots==True:
    plots()
    tests()

print 'COMPLETE'
