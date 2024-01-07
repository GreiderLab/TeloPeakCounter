# names: fast5Telo, TeloSignal, fast5TeloSignal
# Nanopore Signal Telomere Extractor (NSTE)
# Fast5 to Telomere (FTT)
# Telomere Region From NP (TRN)
# IDK maybe the name of nemo's dad cause he was looking for Nemo and here we are looking 
# for the telomere and it would be in keeping with the fish theme of the basecallers
# Maybe the name of the dumb fish from nemo because this program is kind of stupid lol





import statistics
import numpy as np
from scipy.spatial.distance import euclidean





def getTeloLength(signal, current, nanoporeBasePerSecond, nonTeloThreshold=550):
    maxGap = 0
    lastGapIndex = 0
    for i in range(len(signal)):
        if signal[i] > nonTeloThreshold:
            currentGap = i - lastGapIndex
            if currentGap > maxGap:
                maxGap = currentGap
            lastGapIndex = i
    print(maxGap)
    seconds = maxGap / current
    length = seconds * nanoporeBasePerSecond
    return length

def getTeloLengthByTime(distance, current, nanoporeBasePerSecond):
    seconds = distance / current
    length = seconds * nanoporeBasePerSecond
    return length

def getTeloStartEndGStrand(signal, nonTeloThreshold=550, lookAheadWindow = 100):
    maxGap = 0
    maxGapStartIndex = 0
    maxGapEndIndex = 0
    lastGapStartIndex = 0
    for i in range(len(signal)):
        if signal[i] > nonTeloThreshold:
            if len(signal) - lookAheadWindow > i and lookAheadContainsNTPeakGStrand(signal[i:i+lookAheadWindow], nonTeloThreshold, lookAheadWindow):
                
                currentGap = i - lastGapStartIndex
                if currentGap > maxGap:
                    maxGap = currentGap
                    maxGapStartIndex = lastGapStartIndex
                    maxGapEndIndex = i
                lastGapStartIndex = i
    
    
    print(maxGap)
    print("start Index: "+str(maxGapStartIndex))
    print("End Index: " + str(maxGapEndIndex))
    # seconds = maxGap / current
    # length = seconds * nanoporeBasePerSecond
    return maxGapStartIndex, maxGapEndIndex

# This function will look ahead, see if after coming back down past the threshold, the signal goes back over 
def lookAheadContainsNTPeakGStrand(signalIn, nonTeloThreshold, lookAheadWindow):
    pastStart = False
    for i in range(len(signalIn)):
        if not pastStart:
            if signalIn[i]>nonTeloThreshold:
                continue
            else:
                pastStart = True
        if pastStart:
            if signalIn[i]>nonTeloThreshold:
                return True
    return False


# def getTeloStartEndWithCeilingGStrand(signalIn, lookAheadWindow = 100){

# }

# Takes in SMOOTHED and TRIMMED signal 
def getPeakCountGStrand(signalIn, teloCeiling):
    # 100 is abitrary here
    rising = True

    count = 0
    upperCutOff = teloCeiling - 100
    lowerCutOff = upperCutOff - 50


# # *************** This is for testing purposes
#     # stepValue =200
#     # ceiling= waveCeiling(signalIn, window= 850, step=stepValue)
#     # start, end = getTeloRegionFromCeilings(ceiling, teloCeilingCeof=0.15)
#     plt.plot(signalIn)
#     # plt.axvline(x=start, color="red")
#     # plt.axvline(x=end, color="red")
#     plt.axhline(y=teloCeiling, color="red")
#     plt.axhline(y=upperCutOff, color="green")
#     plt.axhline(y=lowerCutOff, color="purple")
# # ***************

    for i in range(len(signalIn)):
        # if rising and signalIn[i] < upperCutOff and signalIn[i+1] < upperCutOff:
        if len(signalIn)-i<= 10:
            return count 
        if rising and signalIn[i] < lowerCutOff and all(values<lowerCutOff for values in signalIn[i:i+10]):
            count +=1 
            # # *************** This is for testing purposes
            # plt.axvline(x=i, color="red")
            # # ***************
            # print("count +1")
            # print(i)
            rising = False
        elif not rising and signalIn[i] > upperCutOff and signalIn[i+1] > upperCutOff:
            rising = True
            # # *************** This is for testing purposes
            # plt.axvline(x=i, color="orange")
            # # ***************
    

    return count

def getPeakCountCStrand(signalIn, teloCeiling):
    # 100 is abitrary here
    rising = True

    count = 0
    upperCutOff = teloCeiling - 55
    lowerCutOff = upperCutOff - 30

# # *************** This is for testing purposes
    # import matplotlib.pyplot as plt
    # # stepValue =200
    # # ceiling= waveCeiling(signalIn, window= 850, step=stepValue)
    # # start, end = getTeloRegionFromCeilings(ceiling, teloCeilingCeof=0.15)
    # plt.plot(signalIn)
    # # plt.axvline(x=start, color="red")
    # # plt.axvline(x=end, color="red")
    # plt.axhline(y=teloCeiling, color="red")
    # plt.axhline(y=upperCutOff, color="green")
    # plt.axhline(y=lowerCutOff, color="purple")
# # ***************

    for i in range(len(signalIn)):
        # if rising and signalIn[i] < upperCutOff and signalIn[i+1] < upperCutOff:
        if len(signalIn)-i<= 10:
            return count 
        if rising and signalIn[i] < lowerCutOff and all(values<lowerCutOff for values in signalIn[i:i+10]):
            count +=1 
            # # *************** This is for testing purposes
            # plt.axvline(x=i, color="red")
            # # ***************
            # print("count +1")
            # print(i)
            rising = False
        elif not rising and signalIn[i] > upperCutOff and signalIn[i+1] > upperCutOff:
            rising = True
    return count



def getTelomereCenter(signal,isGStrand, window_size=20000, window_step=1000):

    output = len(signal)-10000
    # grab median
    # output = statistics.median(signal[output-500:output+500])
    return output

    # # Normalize the signal
    # signal = normalize(signal[:,np.newaxis], axis=0).ravel()
    # if signal in is not np.array
    if type(signal) is not np.ndarray:
        signal = np.array(signal)
    
    # Create a sliding window
    windows = [signal[i:i+window_size] for i in range(0,len(signal)-window_size+1,window_step)]
    
    # Calculate the Euclidean distance between each pair of windows
    distances = [[euclidean(w1, w2) for w2 in windows] for w1 in windows]
    
    # Average the distances
    avg_distances = np.mean(distances, axis=0)
    
    # Repeat each value in avg_distances by window_step times
    avg_distances = np.repeat(avg_distances, window_step)
    
    telomereCenter = 0
    
    if isGStrand:
        # Find the window with the smallest average distance
        # telomereCenter = np.argmax(avg_distances)
        telomereCenter = np.argmin(avg_distances)
    else:
        # Find the window with the smallest average distance
        telomereCenter = np.argmin(avg_distances)
    
    # return telomereCenter + window_size
    return telomereCenter 


def getTeloRegionFromCeilings(teloCenter, ceiling, teloCeiling, vBuffer = 30, lookAheadBuffer=-1, teloCeilingCeof=0.25, lookAheadCeof=0.5):
    # sortedCeiling = sorted(ceiling)
    # teloCeiling =sortedCeiling[int(teloCeilingCeof*len(ceiling))]

    # window_size = 20000
    # window_step=1000
    # teloCenter = getTelomereCenter(signalIn,isGStrand)
    print(f"teloCenter: {teloCenter}")
    # take the area 500 before and after the center and get the median
    # if ceiling[max(0,teloCenter-500):teloCenter+500] == []:
    #     print("Error: teloCenter is too close to the end of the signal")
    #     return 0, len(ceiling)
    # areaMed =statistics.median(ceiling[max(0,teloCenter-500):teloCenter+500])
    # teloCeiling = areaMed

    # teloCeiling = ceiling[int(teloCenter)]

    start = 0
    end = 0

    # startingLookAheadBuffer = 1000
    startingLookAheadBuffer= 0

    # print("heLLOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOV2")
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



            # if len(ceiling)-i<1000:
            #     end = i
            #     return start, end
            # if len(ceiling)-i<10000:
            #     lookAheadBuffer = len(ceiling)-i
            # else:
            #     # lookAheadBuffer = 10000
            #     lookAheadBuffer = int(passingCeilingsCount*0.25)
            # areaMed =statistics.median(ceiling[i:i+lookAheadBuffer])
            # if areaMed>= teloCeiling-vBuffer and areaMed<= teloCeiling+vBuffer:
            #     continue
            # else:
            #     print("areaMedian was: "+str(areaMed))
            #     end = i
            #     return start, end
    return start, len(ceiling)
            

    


# print(getTeloLength(signal, 4000,400))


# ********
# def isGStrand(row):
#     if row["strand"] == "+" and row["chr"][-1] == "q":
#         return True
#     elif row["strand"] == "-" and row["chr"][-1] == "p":
#         return True
#     if row["strand"] == "+" and row["chr"][-1] == "p":
#         return False
#     elif row["strand"] == "-" and row["chr"][-1] == "q":
#         return False
#     else:
#         print("error, could not identify strand")
#         return False
    
# def isGStrand(row, strandCol="strand", chrCol="chr"):
#     strand =row[strandCol]
#     chr = row[chrCol][-1]
#     if strand == "+" and chr == "q":
#         return True
#     elif strand == "-" and chr == "p":
#         return True
#     elif strand == "+" and chr == "p":
#         return False
#     elif strand == "-" and chr == "q":
#         return False
#     else:
#         print("error, could not identify strand")
#         return False

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
import matplotlib.pyplot as plt
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

ceilingWindow = 500
    
def getTeloCountLengthGStrand(signalIn):
    stepValue =200
    ceiling= waveCeiling(signalIn, window= ceilingWindow, step=stepValue)
    # sortedCeiling = sorted(ceiling)
    # teloCeiling =sortedCeiling[int(0.25*len(ceiling))]
    teloCenter = getTelomereCenter(signalIn,True)
    teloCeiling =statistics.median(ceiling[max(0,int(teloCenter)-1000):int(teloCenter)+1000])
    start, end = getTeloRegionFromCeilings(teloCenter, ceiling, teloCeiling)
    count = getPeakCountGStrand(signalIn[start:end], teloCeiling)
    return count * 6

def getTeloCountLengthCStrand(signalIn):
    stepValue =200
    ceiling= waveCeiling(signalIn, window= ceilingWindow, step=stepValue)
    # sortedCeiling = sorted(ceiling)
    # teloCeiling =sortedCeiling[int(0.15*len(ceiling))]
    teloCenter = getTelomereCenter(signalIn,False)
    print(f"teloCenter within teloCountLength Helloooo: {teloCenter}")
    teloCeiling =statistics.median(ceiling[max(0,int(teloCenter)-1000):int(teloCenter)+1000])
    print(f"teloCeiling within teloCountLength Helloooo: {teloCeiling}")
    start, end = getTeloRegionFromCeilings(teloCenter, ceiling,teloCeiling)
    # start, end = getTeloRegionFromCeilings(teloCenter, ceiling,teloCeiling, teloCeilingCeof=0.15)
    count = getPeakCountCStrand(signalIn[start:end], teloCeiling)
    return count * 6

def getTeloCountLength(row):
    # print(row)
    if row["isGStrand"]:
        return getTeloCountLengthGStrand(row["signal"])
    else:
        flippedSignal =  [-x for x in reversed(row["signal"])]
        # flippedSignal =  [x for x in reversed(row["signal"])]
        return getTeloCountLengthCStrand(flippedSignal)
    
def waveCeiling(signal, window = 100, step=20):
    # Go through signal and grab the highest signal value in each window
    maxValues = []
    for i in range(0,len(signal)-window, step):
        sample = signal[i:i+window]
        for i in range(step):
            maxValues.append(max(sample))
    return maxValues