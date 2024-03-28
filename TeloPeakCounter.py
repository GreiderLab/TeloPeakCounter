import statistics
import numpy as np
from scipy.spatial.distance import euclidean
import matplotlib.pyplot as plt

# Takes in TRIMMED signal 
def getPeakCount(signalIn, teloCeiling, upperCutOffOffset, lowerCutOffOffset):
    rising = True
    count = 0
    upperCutOff = teloCeiling + upperCutOffOffset
    lowerCutOff = upperCutOff + lowerCutOffOffset

    for i in range(len(signalIn)):
        if len(signalIn)-i<= 10:
            return count 
        if rising and signalIn[i] < lowerCutOff and all(values<lowerCutOff for values in signalIn[i:i+10]):
            count +=1 
            rising = False
        elif not rising and signalIn[i] > upperCutOff and signalIn[i+1] > upperCutOff:
            rising = True
    return count

# This function is meant to return an index within the telomeric region of the signal. 
# It opperates on the assumption that the end of the signal data will be telomeric, followed by the signal for any barcode or telotag. 
def getTelomereCenter(signal,stepBack = 10000):
    output = len(signal)-stepBack
    return output

def getTeloCountLength(row):
    # print(row)
    if row["isGStrand"]:
        return getTeloCountLengthFromSignal(row["signal"], isGStrand=True)
    else:
        flippedSignal =  [-x for x in reversed(row["signal"])]
        # flippedSignal =  [x for x in reversed(row["signal"])]
        return getTeloCountLengthFromSignal(flippedSignal, isGStrand=False)

def getTeloRegionFromCeilings(teloCenter, ceiling, teloCeiling, vBuffer = 30, lookAheadBuffer=-1, teloCeilingCeof=0.25, lookAheadCeof=0.5):
    start = 0
    end = 0
    # startingLookAheadBuffer = 1000
    startingLookAheadBuffer= 0

    # Get the number of values that sit within the teloCeiling range
    passingCeilingsCount = len(list(filter(lambda x: x >= teloCeiling-vBuffer and x <= teloCeiling+vBuffer, ceiling)))
    if lookAheadBuffer <= -1:
        lookAheadBuffer = int(passingCeilingsCount*lookAheadCeof)
        startingLookAheadBuffer = int(passingCeilingsCount*0.2)
        if lookAheadBuffer < 1000:
            print("Warning: lookAheadBuffer was too small, setting to 1000")
            lookAheadBuffer = 1000
        if startingLookAheadBuffer < 1000:
            print("Warning: startingLookAheadBuffer was too small, setting to 1000")
            startingLookAheadBuffer = 1000
        # print("lookAheadBuffer: "+str(lookAheadBuffer))

    for i in range(len(ceiling)):
        # If the ceiling is within the buffer, we are in the telo region
        if ceiling[i]>= teloCeiling-vBuffer and ceiling[i]<= teloCeiling+vBuffer:
            if start ==0:
                areaMed =statistics.median(ceiling[i:i+startingLookAheadBuffer])
                if areaMed>= teloCeiling-vBuffer and areaMed<= teloCeiling+vBuffer:
                    areaMed =statistics.median(ceiling[i:i+lookAheadBuffer])
                    if areaMed>= teloCeiling-vBuffer and areaMed<= teloCeiling+vBuffer:
                        print("start set")
                        start= i
            continue
        # We are not in the telo region, but we also haven't found the start yet
        elif start == 0:
            continue
        # We are not in the telo region, but we are past the start so we have to check if we should end the sequence
        elif start != 0:
            # If we are within the last 1000 values, we can just end the sequence
            if len(ceiling)-i<1000:
                end = i
                return start, end
            # print(ceiling[i:i+lookAheadBuffer])
            areaMed =statistics.median(ceiling[i:i+lookAheadBuffer])
            if areaMed>= teloCeiling-vBuffer and areaMed<= teloCeiling+vBuffer:
                continue
            else:
                print("areaMedian was: "+str(areaMed))
                end = i
                return start, end

    return start, len(ceiling)
            
def getTeloCountLengthFromSignal(signalIn, isGStrand, ceilingWindow = 500):
    stepValue =200
    ceiling= waveCeiling(signalIn, window= ceilingWindow, step=stepValue)
    teloCenter = getTelomereCenter(signalIn)
    teloCeiling =statistics.median(ceiling[max(0,int(teloCenter)-1000):int(teloCenter)+1000])
    start, end = getTeloRegionFromCeilings(teloCenter, ceiling, teloCeiling)
    
    # These values were determined by looking at the signal data and determining the best way to count the peaks
    # manually. 
    gStrandUpperCutOffOffset = -100
    gStrandLowerCutOffOffset = -50
    cStrandUpperCutOffOffset = -55
    cStrandLowerCutOffOffset = -30
    
    count = 0
    if isGStrand:
        count = getPeakCount(signalIn[start:end], teloCeiling, gStrandUpperCutOffOffset, gStrandLowerCutOffOffset)
    else:
        count = getPeakCount(signalIn[start:end], teloCeiling, cStrandUpperCutOffOffset, cStrandLowerCutOffOffset)
    return count * 6

    
def waveCeiling(signal, window = 100, step=20):
    # Go through signal and grab the highest signal value in each window
    maxValues = []
    for i in range(0,len(signal)-window, step):
        sample = signal[i:i+window]
        for i in range(step):
            maxValues.append(max(sample))
    return maxValues

def isGStrand(chrArm,strand):
    if strand == "+" and chrArm == "q":
        return True
    elif strand == "-" and chrArm == "p":
        return True
    elif strand == "+" and chrArm == "p":
        return False
    elif strand == "-" and chrArm == "q":
        return False
    else:
        print("error, could not identify strand")
        return False

def graphPeaks(dfIn, col1, col2, offset=0, opacity=1, pdfOut=None, title=None):
    x_values = dfIn[col1]
    y_values = dfIn[col2]
    # Plot the points
    plt.scatter(x_values, y_values, alpha=opacity)
    maxVal = max(max(x_values),max(y_values))
    plt.plot([0,maxVal], [0,maxVal], 'r-')
    if offset != 0:
        plt.plot([0,17500], [0+offset,17500+offset], 'b-')
        plt.plot([0,17500], [0-offset,17500-offset], 'b-')
    plt.xlabel(col1 + "Lenght(bps)")
    plt.ylabel(col2+ "Length(bps)")
    if title == None:
        plt.title(col1 + ' vs ' + col2)
    else:
        plt.title(title)
    if pdfOut != None:
        plt.savefig(pdfOut)
    # plt.grid(True)
    plt.show()


# The following was a more simplistic method of getting telomere length by measuring the amount of time the signal was 
# above a threshold. The primary issue with this approach was that we could not accurately ascertain the 
# speed at which basepairs were being read by the pore.

def getTeloLengthByTime(signal, current, nanoporeBasePerSecond, nonTeloThreshold=550):
    maxGap = 0
    lastGapIndex = 0
    for i in range(len(signal)):
        if signal[i] > nonTeloThreshold:
            currentGap = i - lastGapIndex
            if currentGap > maxGap:
                maxGap = currentGap
            lastGapIndex = i
    print(maxGap)
    length = getBPLengthByTime(maxGap, current, nanoporeBasePerSecond)
    return length

def getBPLengthByTime(distance, current, nanoporeBasePerSecond):
    seconds = distance / current
    length = seconds * nanoporeBasePerSecond
    return length