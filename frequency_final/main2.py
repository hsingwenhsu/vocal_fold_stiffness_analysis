import matplotlib.pyplot as plt
import sys
import utils

path1 = '/Users/vivi/Documents/frequency_analysis/newdata/'
path2 = '/Users/vivi/Documents/frequency_analysis/newdata_cropped/'
output_path = 'results/'
def plot_data2(out_path, patient, freq1, pres1, freq2, pres2, freq3, pres3, cropped, mf):

    rline1, tx1, ty1, fn1, m1 = utils.get_regression(freq1, pres1) 
    rline2, tx2, ty2, fn2, m2 = utils.get_regression(freq2, pres2)   
    rline3, tx3, ty3, fn3, m3 = utils.get_regression(freq3, pres3)

    savename_slope = out_path+patient+'_2_slope.png'
    if cropped=='1':
        savename_slope = out_path+patient+'_2_slope_cropped.png'
    
    y_axis = [m1, m2, m3]
    if mf=='m':
        x_axis = [98, 130.81, 164.81]
    else:
        x_axis = [196, 261.63, 329.63]
    plt.plot(x_axis, y_axis, 'bo')
    plt.title(patient+ ' method 2')
    plt.xlabel('Frequency')
    plt.ylabel('Slope')
    plt.savefig(savename_slope)
    plt.close()
        
    savename = out_path+patient+'_2_all.png'
    if cropped=='1':
        savename = out_path+patient+'_2_all_cropped.png'

    fig = plt.figure()
    ax = fig.add_subplot()
    plt.plot(pres1, freq1, 'bo')
    plt.plot(pres2, freq2, 'go')
    plt.plot(pres3, freq3, 'ro')
    plt.plot(pres1, fn1(pres1), '--k')
    plt.plot(pres2, fn2(pres2), '--k')
    plt.plot(pres3, fn3(pres3), '--k')
    ax.text(tx1, ty1, rline1)
    ax.text(tx2, ty2, rline2)
    ax.text(tx3, ty3, rline3)
    if cropped=='1':
        plt.title(patient+' cropped method 2')
    else:
        plt.title(patient+' method 2')
    plt.xlabel('Pressure Difference')
    plt.ylabel('Frequency')
    plt.savefig(savename)
    plt.close()

    savename = out_path+patient+'_2_so.png'
    if cropped=='1':
        savename = out_path+patient+'_2_socropped.png'
        plt.title(patient+' so cropped method 2')
    else:
        plt.title(patient+' so method 2')
    fig = plt.figure()
    ax = fig.add_subplot()
    plt.plot(pres1, freq1, 'bo')
    plt.plot(pres1, fn1(pres1), '--k')
    ax.text(tx1, ty1, rline1)
    plt.xlabel('Pressure Difference ')
    plt.ylabel('Frequency')
    plt.savefig(savename)
    plt.close()

    savename = out_path+patient+'_2_do.png'
    if cropped=='1':
        savename = out_path+patient+'_2_do_cropped.png'
        plt.title(patient+' do cropped method 2')
    else:
        plt.title(patient+' do method 2')
    fig = plt.figure()
    ax = fig.add_subplot()
    plt.plot(pres2, freq2, 'go')
    plt.plot(pres2, fn2(pres2), '--k')
    ax.text(tx2, ty2, rline2)
    plt.xlabel('Pressure Difference')
    plt.ylabel('Frequency')
    plt.savefig(savename)
    plt.close()

    savename = out_path+patient+'_2_mi.png'
    if cropped=='1':
        savename = out_path+patient+'_2_mi_cropped.png'
        plt.title(patient+' mi cropped method 2')
    else:
        plt.title(patient+' mi method 2')
    fig = plt.figure()
    ax = fig.add_subplot()
    plt.plot(pres3, freq3, 'ro')
    plt.plot(pres3, fn3(pres3), '--k')
    ax.text(tx3, ty3, rline3)
    plt.xlabel('Pressure Difference')
    plt.ylabel('Frequency')
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
    f1, f2, f3, p1, p2, p3 = utils.get_all_data(path, patient)

    # smooth data
    sf1, sp1 = utils.get_smoothed_data(f1, p1, mf, 'so')
    sf2, sp2 = utils.get_smoothed_data(f2, p2, mf, 'do')
    sf3, sp3 = utils.get_smoothed_data(f3, p3, mf, 'mi')

    if cropped=='0':
        # crop the data
        f1, sp1 = utils.crop_data(f1, sp1)
        f2, sp2 = utils.crop_data(f2, sp2)
        f3, sp3 = utils.crop_data(f3, sp3)

    if mf=='m':
        winsize1 = int(len(f1)*2/3)
        winsize2 = int(len(f2)*3/5)
        winsize3 = int(len(f3)*3/5)
    else:
        winsize1 = int(len(f1)*2/5)
        winsize2 = int(len(f2)*2/5)
        winsize3 = int(len(f3)*2/5)

    seg_num = 10

    freq_seg1, pres_seg1 = utils.get_segments(f1, sp1, seg_num, winsize1)
    freq_seg2, pres_seg2 = utils.get_segments(f2, sp2, seg_num, winsize2)
    freq_seg3, pres_seg3 = utils.get_segments(f3, sp3, seg_num, winsize3)

    freq1, pres1 = utils.get_freq_pres(freq_seg1, pres_seg1)
    freq2, pres2 = utils.get_freq_pres(freq_seg2, pres_seg2)
    freq3, pres3 = utils.get_freq_pres(freq_seg3, pres_seg3)

    plot_data2(output_path, patient, freq1, pres1, freq2, pres2, freq3, pres3, cropped, mf)
