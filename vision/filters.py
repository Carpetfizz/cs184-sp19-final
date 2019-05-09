import numpy as np
import numpy.fft as fft
from scipy.signal import savgol_filter

def lowpassFilter(inputSig, bw=10):
    sig = fft.fft(inputSig)
    filteredSig = np.array([sig[i] if abs(i - len(sig)//2) > (len(sig)//2 - bw) else 0 for i in range(len(sig))])
    # freq = fft.fftfreq(len(filteredSig))
    return fft.ifft(filteredSig)    

def manualFilter(sig, w=50, t=0.01, dampen=10, shiftDown=.5):
    lastDiff = shiftDown
    ret = []
    i = 0
    while i < (len(sig) - w):
        slopes = [(sig[i+j] - sig[i]) / j for j in range(1,w)]
        maxSlope = max(slopes)
        minSlope = min(slopes)
        maxIdx = np.argmax(slopes)
        minIdx = np.argmin(slopes)
        if maxSlope > t:
            # spike up
            lastDiff = sig[i] - ret[i-1] if i > 0 and i < len(sig) else lastDiff
            j = maxIdx+1
            while (i+j < len(sig)) and ((sig[i+j] - sig[i]) / j) > t:
                j += 1
            shift = min(sig[i:i+j])
            for k in range(i, i+j):
                ret.append(((sig[k] - shift) / dampen) + shift - lastDiff)
            i += j
            lastDiff = sig[i] - ret[i-1] if i > 0 and i < len(sig) else lastDiff
        elif minSlope < -t:
            # spike down
            lastDiff = sig[i] - ret[i-1] if i > 0 and i < len(sig) else lastDiff
            j = minIdx+1
            while (i+j < len(sig)) and ((sig[i+j] - sig[i]) / j) < -t:
                j += 1
            shift = max(sig[i:i+j])
            for k in range(i, i+j):
                ret.append(((sig[k] - shift) / dampen) + shift - lastDiff)
            i += j
            lastDiff = sig[i] - ret[i-1] if i > 0 and i < len(sig) else lastDiff
        else:
            ret.append(sig[i] - lastDiff)
            i += 1
    return np.array(ret)

def fullFilter(sig, hFilterWidth, threshold, dampen, shiftDown, bandwidth):
    filtered = manualFilter(sig, hFilterWidth, threshold, dampen, shiftDown)
    return lowpassFilter(filtered, bandwidth)

def simpleFilter(sig, threshold):
    ret = [sig[0]]
    for i in range(1, len(sig)):
        if (abs(sig[i] - ret[i-1]) > threshold):
            ret.append(ret[i-1])
        else:
            ret.append(sig[i])
    return np.array(ret)

def movAvgFilter(sig, window=50):
    ret = []
    for i in range(len(sig) - window):
        ret.append(np.mean())
        if (abs(sig[i] - sig[i-1] > threshold)):
            ret.append(sig[i-1])
        else:
            ret.append(sig[i])
    return np.array(ret)

def smoothenSavGol(sig3, window=[101, 101, 101], deg=[2, 2, 2]):
    if type(window) != list and type(window) != np.ndarray:
        window = [window, window, window]
    if type(deg) != list and type(deg) != np.ndarray:
        deg = [deg, deg, deg]
    ret = np.zeros(sig3.shape)
    ret[:, 0] = savgol_filter(sig3[:, 0], window[0], deg[0])
    ret[:, 1] = savgol_filter(sig3[:, 1], window[1], deg[1])
    ret[:, 2] = savgol_filter(sig3[:, 2], window[2], deg[2])
    return ret

def simpleFilter3(sig3, threshold):
    if type(threshold) != list and type(threshold) != np.ndarray:
        threshold = [threshold, threshold, threshold]
    ret = np.zeros(sig3.shape)
    ret[:, 0] = simpleFilter(sig3[:, 0], threshold[0])
    ret[:, 1] = simpleFilter(sig3[:, 1], threshold[1])
    ret[:, 2] = simpleFilter(sig3[:, 2], threshold[2])
    return ret

def smoothenSimpleFilter3(sig3, threshold=[20, 20, 20], window=[51, 51, 51], deg=[2, 2, 2]):
    return smoothenSavGol(simpleFilter3(sig3, threshold), window, deg)

def VO_Filter(pathArr, rotArr):
    return (smoothenSavGol(pathArr), smoothenSimpleFilter3(rotArr))
