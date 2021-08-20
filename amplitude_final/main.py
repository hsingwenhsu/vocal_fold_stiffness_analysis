import numpy as np
import utils
import os
import sys
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft

path1 = '/Users/vivi/Documents/frequency_analysis/newdata/'
path2 = '/Users/vivi/Documents/frequency_analysis/newdata_cropped/'
output_path = 'results/'

def find_amp(freq_data, pres_data, out_path, patient, note, cropped):
    # make all the data abs
    freq_abs = np.abs(freq_data)
    amps = []
    amps_idx = []
    
    for i in range(len(freq_abs)-2):
        p1 = freq_abs[i]
        p2 = freq_abs[i+1]
        p3 = freq_abs[i+2]
        if p1<p2 and p2>p3:
            amps.append(p2)
            amps_idx.append(i+1)

    amps_actual = []
    amps_pos = []
    pres_actual = []
    for i in range(len(amps_idx)-1):
        amp_idx1 = amps_idx[i]
        amp_idx2 = amps_idx[i+1]
        amp1 = amps[i]
        amp2 = amps[i+1]
        pres_tmp = np.mean(pres_data[amp_idx1:amp_idx2])
        amp_tmp = (amp1+amp2)/2
        i+=1
        amps_actual.append(amp_tmp)
        amps_pos.append(int((amp_idx1+amp_idx2)/2))
        pres_actual.append(pres_tmp)
        if i>len(amps_idx):
            break
    plt.rcParams["figure.figsize"] = (18,7)
    if cropped=='1':
        plt.title(patient+' '+note+' cropped')
        savename = out_path+patient+'_'+note+'_amp_cropped.png'
    else:
        plt.title(patient+' '+note)
        plt.rcParams["figure.figsize"] = (18,7)
        savename = out_path+patient+'_'+note+'_amp.png'
    
    plt.plot(freq_data)
    plt.plot(amps_idx, amps, 'bo')
    plt.plot(amps_pos, amps_actual, 'ro')
    
    for i in range(len(amps_idx)):
        plt.axvline(x=amps_idx[i], color='k', linestyle='--')
    plt.savefig(savename)
    plt.close()

    return amps_actual, pres_actual

def plot_data(out_path, patient, amps1, pres1, amps2, pres2, amps3, pres3, cropped):

    # draw points
    rline1, tx1, ty1, fn1, m1 = utils.get_regression(amps1, pres1)
    rline2, tx2, ty2, fn2, m2 = utils.get_regression(amps2, pres2)
    rline3, tx3, ty3, fn3, m3 = utils.get_regression(amps3, pres3)

    if cropped=='1':
        savename = out_path+patient+'_all_cropped.png'
    else:
        savename = out_path+patient+'_all.png'
    plt.rcParams["figure.figsize"] = (10,7)
    fig = plt.figure()
    ax = fig.add_subplot()
    if rline1!=0:
        plt.plot(pres1, amps1, 'bo')
        plt.plot(pres1, fn1(pres1), '--k')
        ax.text(tx1, ty1, rline1)
    if rline2!=0:
        plt.plot(pres2, amps2, 'go')
        plt.plot(pres2, fn2(pres2), '--k')
        ax.text(tx2, ty2, rline2)
    if rline3!=0:
        plt.plot(pres3, amps3, 'ro')
        plt.plot(pres3, fn3(pres3), '--k')
        ax.text(tx3, ty3, rline3)
    
    plt.title(patient)
    plt.xlabel('Pressure Difference')
    plt.ylabel('Amplitude')
    plt.savefig(savename)
    plt.close()

if __name__=='__main__':
    patient = sys.argv[1]
    mf = sys.argv[2]
    cropped = sys.argv[3]
    if cropped=='0':
        path = path1
    else:
        path = path2
    output_path = output_path+mf+'/'
    # read data
    f1, f2, f3, p1, p2, p3 = utils.get_all_data(path, patient)
    
    # get smoothed data
    sf1, sp1 = utils.get_smoothed_data(f1, p1, mf, 'so')
    sf2, sp2 = utils.get_smoothed_data(f2, p2, mf, 'do')
    sf3, sp3 = utils.get_smoothed_data(f3, p3, mf, 'mi')

    amps1, pres1 = find_amp(sf1, sp1, output_path, patient, 'so', cropped)
    amps2, pres2 = find_amp(sf2, sp2, output_path, patient, 'do', cropped)
    amps3, pres3 = find_amp(sf3, sp3, output_path, patient, 'mi', cropped)
    
    plot_data(output_path, patient, amps1, pres1, amps2, pres2, amps3, pres3, cropped)