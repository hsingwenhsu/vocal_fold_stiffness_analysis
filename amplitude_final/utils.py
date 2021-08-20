import matplotlib.pyplot as plt
import glob 
from scipy.fft import fft, fftfreq, ifft
import numpy as np
from scipy.signal import savgol_filter
from scipy.interpolate import interp1d
import math
from statistics import mean
import copy

# for reading data
def get_data(filename):
    with open(filename, 'r') as f:
        raw_data = f.read().splitlines()[1:]
    data = [float(item) for item in raw_data]
    return data

def get_freq_names(path, patient):
    name1 = path+'freq/'+patient+'_so.csv'
    name2 = path+'freq/'+patient+'_do.csv'
    name3 = path+'freq/'+patient+'_mi.csv'
    return name1, name2, name3

def get_pres_names(path, patient):
    name1 = path+'pres/'+patient+'_so.csv'
    name2 = path+'pres/'+patient+'_do.csv'
    name3 = path+'pres/'+patient+'_mi.csv'
    return name1, name2, name3

def get_all_data(path, patient):
    pname1, pname2, pname3 = get_pres_names(path, patient)
    fname1, fname2, fname3 = get_freq_names(path, patient)

    p1 = get_data(pname1)
    p2 = get_data(pname2)
    p3 = get_data(pname3)

    f1 = get_data(fname1)
    f2 = get_data(fname2)
    f3 = get_data(fname3)
    
    plen1 = len(p1)
    flen1 = len(f1)
    plen2 = len(p2)
    flen2 = len(f2)
    plen3 = len(p3)
    flen3 = len(f3)

    if plen1<flen1:
        f1 = f1[:plen1]
    elif flen1<plen1:
        p1 = p1[:flen1]
    
    if plen2<flen2:
        f2 = f2[:plen2]
    elif flen2<plen2:
        p2 = p2[:flen2]

    if plen3<flen3:
        f3 = f3[:plen3]
    elif flen3<plen3:
        p3 = p3[:flen3]

    return f1, f2, f3, p1, p2, p3

# for data smoothing
def smooth_pres(data):
    plen = len(data)
    winsize = plen
    if winsize%2==0:
        winsize = winsize-1
    smoothed_data = savgol_filter(data, winsize, 1)

    return smoothed_data

def smooth_freq(data, mf, note):
    
    sp = 10000
    if mf=='m':
        if note=='so':
            winsize = (1/98)/(1/sp)
        elif note=='do':
            winsize = (1/131)/(1/sp)
        else: # mi
            winsize = (1/165)/(1/sp)
        s = 5
        winsize = int(winsize/s)
    else:
        if note=='so':
            winsize = (1/196)/(1/sp)
        elif note=='do':
            winsize = (1/262)/(1/sp)
        else: # mi
            winsize = (1/330)/(1/sp)
        s = 2
        winsize = int(winsize/2)
        #winsize = 41
    if winsize%2==0:
        winsize = winsize+1

    try:
        smoothed_data = savgol_filter(data, winsize, 2, mode='nearest')
    except:
        smoothed_data = savgol_filter(data, 3, 2, mode='nearest')
    
    return smoothed_data

def get_smoothed_data(freq_data, pres_data, mf, note):
    smoothed_freq = smooth_freq(freq_data, mf, note)
    smoothed_pres = smooth_pres(pres_data)

    return smoothed_freq, smoothed_pres

# for result 
def get_regression(amp, p):
    coef = np.polyfit(p, amp, 1)
    m = round(coef[0], 3)
    b = round(coef[1], 2)
    if b<0:
        rline = 'y = '+str(m)+'x - '+str(abs(b))
    else:
        rline = 'y = '+str(m)+'x + '+str(abs(b))
    
    poly1d_fn = np.poly1d(coef)
    tx = p[int(len(p)//2)]
    ty = poly1d_fn(p[0])

    return rline, tx, ty, poly1d_fn, m