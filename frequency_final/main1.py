import numpy as np
import utils
import os
import sys
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq, ifft

# main 1: Shifted correlation
path1 = '/Users/vivi/Documents/frequency_analysis/newdata/'
path2 = '/Users/vivi/Documents/frequency_analysis/newdata_cropped/'
output_path = 'results/'

def plot_correlation(freq_data, sp, path, patient, note, mf, cropped):
    segment = freq_data.copy()
    lags = []
    cnt = 0
    lag_thresh = 0
    if mf=='m':
        if note=='so':
            lag_thresh = int(10000*(1/98)*2)
        elif note=='do':
            lag_thresh = int(10000*(1/131)*2)
        elif note=='mi':
            lag_thresh = int(10000*(1/165)*2)
    else:
        if note=='so':
            lag_thresh = int(10000*(1/196)*2)
        elif note=='do':
            lag_thresh = int(10000*(1/262)*2)
        elif note=='mi':
            lag_thresh = int(10000*(1/330)*2)

    while True:
        corr = np.correlate(segment, segment, mode='same')
        N = len(segment)
        corr = corr[N//2:]
        xcorr = np.arange(0, len(corr))
        # find the first spot that is under 0
        corr_under0 = np.where(corr<0)[0]
        if len(corr_under0)==0:
            break
        
        corr[:corr_under0[0]] = -1
        ind = np.argpartition(corr, -2)[-2:]
        tmp_ind = ind[np.argsort(corr[ind])]
        ind_list = ind[np.argsort(corr[ind])].tolist()
        ind_list.reverse()
        lag = ind_list[0]
        lags.append(lag)
        segment = segment[lag:]
        
        """
        plt.title(patient+' '+note+' '+str(cnt))
        #plt.rcParams["figure.figsize"] = (13,7)
        plt.plot(xcorr, corr)
        plt.axvline(x=lag, color='k', linestyle='--')
        plt.savefig(path+patient+'_'+note+'_'+str(cnt)+'.png')
        plt.close()
        """
        # get the first max in lags
        # low_high = utils.get_boundaries(corr)
        
        if len(segment)<lag_thresh:
            print('if len segment < lag_thresh')
            plt.rcParams["figure.figsize"] = (10,7)
            plt.plot(freq_data)
            
            if cropped=='1':
                plt.title(patient+' '+note+ ' cropped method 1 Not long enough')
                plt.savefig(path+patient+'_1_'+note+'_cropped.png')
                plt.close()
            else:
                plt.title(patient+' '+note+ ' method Not long enough')
                plt.savefig(path+patient+'_1_'+note+'.png')
                plt.close()
            return 0, 0, 0, 0, 0, 0, 0
            break
        """
        if len(low_high)>1:
            low = low_high[1][0]
            high = low_high[1][1]
            lag = np.array(corr[low:high]).argmax()
            lags.append(lag)
            #plt.plot(segment)
            #plt.axvline(x=low, color='k', linestyle='--')
            #plt.axvline(x=high, color='k', linestyle='--')
            #plt.show()
            #plt.close()
            segment = segment[lag:]
        
        else:
            break
        """
        cnt+=1
        if cnt>40:
            break
    # draw lines
    base = 0
    plt.rcParams["figure.figsize"] = (10,7)
    plt.plot(freq_data)
    #plt.rcParams["figure.figsize"] = (13,7)
    lag_coor = []
    for lag in lags:
        base+=lag
        lag_coor.append(base)
        plt.axvline(x = base, color='k', linestyle='--')
    plt.title(patient+' '+note)
    
    if cropped=='1':
        name_tmp = path+patient+'_1_'+note+'_cropped.png'
    else:
        name_tmp = path+patient+'_1_'+note+'.png'
    #plt.savefig(path+patient+'_'+note+'_1.png')
    plt.savefig(name_tmp)
    plt.close()

    pres = []
    freq = []
    srate = 10000
    # plot frequency only
    if len(lags)>3:
        base = 0
        for lag in lags:
            period = lag/srate
            freq_tmp = 1/period
            freq.append(freq_tmp)
            pres_tmp = np.mean(sp[base:base+lag])
            pres.append(pres_tmp)
            base+=lag
        freq = freq[1:]
        pres = pres[1:]

        # plot frequency alone
        xfreq = np.arange(0, len(freq))
        coef = np.polyfit(xfreq, freq, 1)
        m = round(coef[0], 3)
        b = round(coef[1], 2)
        if b<0:
            rline = 'y = '+str(m)+'x - '+str(abs(b))
        else:
            rline = 'y = '+str(m)+'x + '+str(abs(b))
        poly1d_fn = np.poly1d(coef)
        tx = int(len(freq)/2)
        ty = poly1d_fn(tx)
        fig = plt.figure()
        ax = fig.add_subplot()
        ax.text(tx, ty, rline) 
        if cropped=='1':
            plt.title(patient+' method 1 cropped freq '+note)
        else:
            plt.title(patient+' method 1 freq '+note)
        plt.plot(freq, 'bo')
        plt.plot(xfreq, poly1d_fn(xfreq), '--k')
        name_tmp = path+patient+'_1_'+note+'_freq.png'
        if cropped=='1':
            name_tmp = path+patient+'_1_'+note+'_freq_cropped.png'
        #plt.savefig(path+patient+'_1_'+note+'_freq.png')
        plt.savefig(name_tmp)
        plt.close()

        # plot pressure alone 
        if cropped=='1':
            plt.title(patient+' method 1 cropped pres'+note)
        else:
            plt.title(patient+' method 1 pres '+note)
        plt.plot(pres, 'bo')
        name_tmp = path+patient+'_1_'+note+'_pres.png'
        if cropped=='1':
            name_tmp = path+patient+'_1_'+note+'_pres_cropped.png'
        #plt.savefig(path+patient+'_'+note+'_pres_1.png')
        plt.savefig(name_tmp)
        plt.close()

        # plot freq-pres
        coef = np.polyfit(pres, freq, 1)
        m = round(coef[0], 3)
        b = round(coef[1], 2)
        if b<0:
            rline = 'y = '+str(m)+'x - '+str(abs(b))
        else:
            rline = 'y = '+str(m)+'x + '+str(abs(b))
        poly1d_fn = np.poly1d(coef)
        tx = pres[int(len(pres)//2)]
        ty = poly1d_fn(pres[0])
        fig = plt.figure()
        ax = fig.add_subplot()
        plt.rcParams["figure.figsize"] = (10,7)
        ax.text(tx, ty, rline) 
        if cropped=='1':
            plt.title(patient+' pres_diff - freq method 1 cropped '+note)
        else:    
            plt.title(patient+' pres_diff - freq method 1'+note)
        plt.plot(pres, freq, 'bo')
        plt.plot(pres, poly1d_fn(pres), '--k')

        name_tmp = path+patient+'_1_'+note+'_result.png'
        if cropped=='1':
            name_tmp = path+patient+'_1_'+note+'_result_1_cropped.png'
        #plt.savefig(path+patient+'_'+note+'_result_1.png')
        plt.savefig(name_tmp)
        plt.close()

        return rline, m, tx, ty, poly1d_fn, freq, pres

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

    rline1, m1, tx1, ty1, fn1, freq1, pres1 = plot_correlation(f1, sp1, output_path, patient, 'so', mf, cropped)
    rline2, m2, tx2, ty2, fn2, freq2, pres2 = plot_correlation(f2, sp2, output_path, patient, 'do', mf, cropped)
    rline3, m3, tx3, ty3, fn3, freq3, pres3 = plot_correlation(f3, sp3, output_path, patient, 'mi', mf, cropped)

    if cropped=='1':
        savename = output_path+patient+'_1_all_cropped.png'
    else:
        savename = output_path+patient+'_1_all.png'
    plt.rcParams["figure.figsize"] = (10,7)
    fig = plt.figure()
    ax = fig.add_subplot()
    if rline1!=0:
        plt.plot(pres1, freq1, 'bo')
        plt.plot(pres1, fn1(pres1), '--k')
        ax.text(tx1, ty1, rline1)
    if rline2!=0:
        plt.plot(pres2, freq2, 'go')
        plt.plot(pres2, fn2(pres2), '--k')
        ax.text(tx2, ty2, rline2)
    if rline3!=0:
        plt.plot(pres3, freq3, 'ro')
        plt.plot(pres3, fn3(pres3), '--k')
        ax.text(tx3, ty3, rline3)
    
    plt.title(patient)
    plt.xlabel('Pressure Difference')
    plt.ylabel('Frequency')
    plt.savefig(savename)
    plt.rcParams["figure.figsize"] = (10,7)
    plt.close()

    # plot slope
    if cropped=='1':
        savename_slope = output_path+patient+'_1_slope_cropped.png'
    else:
        savename_slope = output_path+patient+'_1_slope.png'
   
    x_axis = []
    y_axis = []

    if rline1!=0:
        if mf=='m':
            x_axis.append(98)
        else:
            x_axis.append(196)

        y_axis.append(m1)

    if rline2!=0:
        if mf=='m':
            x_axis.append(130.81)
        else:
            x_axis.append(261.63)

        y_axis.append(m2)

    if rline3!=0:
        if mf=='m':
            x_axis.append(164.81)
        else:
            x_axis.append(329.63)

        y_axis.append(m3)

    if len(x_axis)!=0:
        plt.plot(x_axis, y_axis, 'bo')
        plt.title(patient)
        plt.xlabel('Frequency')
        plt.ylabel('Slope')
        plt.savefig(savename_slope)
        plt.close()
