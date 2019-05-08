import numpy as np
import numpy.fft as fft

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
    return(np.array(ret))

def fullFilter(sig, hFilterWidth, threshold, dampen, shiftDown, bandwidth):
    filtered = manualFilter(sig, hFilterWidth, threshold, dampen, shiftDown)
    return lowpassFilter(filtered, bandwidth)
