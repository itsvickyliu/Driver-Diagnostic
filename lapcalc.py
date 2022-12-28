from numpy.lib.function_base import average
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

def importData(filePath):
    df = pd.read_csv(filePath)
    #Remove NaN values
    df.dropna(subset=['Power [W]'], inplace=True)
    # print (len(df))
    return df
    
def findTrackStart(newTime, newPos):
    #Smoothen the position curve
    n = 1
    b = [1.0 / n] * n
    a = 1
    smoothPos = savgol_filter(newPos, 301, 2)
    # plt.plot(newTime, smoothPos, 'b')
    # plt.show()

    slope = np.diff(smoothPos)/np.diff(newTime)
   
    hasStarted = False 
    startIndexArray = []
    endIndexArray = []

    for i in range(0, len(smoothPos)-120):
        #Find track start time
        if not hasStarted:
            if abs(smoothPos[i+120] - smoothPos[i]) >= 0.000005:
                startIndexArray.append(i+60)
                hasStarted = True
        
        #Find track end time
        if hasStarted:
            if abs(smoothPos[i+120] - smoothPos[i]) <= 0.000005 and slope[i+120] * slope [i] >= 0 :
                endIndexArray.append(i+60)
                hasStarted = False
    
    #Eliminate erroneous track start and end times
    deleteStartArray = []
    deleteEndArray = []
    for i in range(0, len(startIndexArray)-1):
        if startIndexArray[i+1]-endIndexArray[i] < 800:
            deleteStartArray.append(i+1)  
            deleteEndArray.append(i)
    
    startIndexArray = np.delete(startIndexArray, deleteStartArray)
    endIndexArray = np.delete(endIndexArray, deleteEndArray)

    # print ("Start Index:", startIndexArray)
    # print ("End Index:", endIndexArray)
    
    return (startIndexArray, endIndexArray)

def combineData(longStartIndexArray, latStartIndexArray, longEndIndexArray, latEndIndexArray):
    startIndexArray = []
    endIndexArray = []
    if len(longStartIndexArray) == len(latStartIndexArray):
        for i in range(0, len(longStartIndexArray)):
            startIndexArray.append(round((longStartIndexArray[i]+latStartIndexArray[i])/2))
            endIndexArray.append(round((longEndIndexArray[i]+latEndIndexArray[i])/2))

    print ("Start Index:", startIndexArray)
    print ("End Index:", endIndexArray)

    return (startIndexArray, endIndexArray)

def seperateData(startIndexArray, endIndexArray):
    dataframeDict = {}
    for i in range(0, len(startIndexArray)):
        trackData = (data.iloc[startIndexArray[i]:endIndexArray[i]])
        dataframeDict[i+1] = [trackData]
    return(dataframeDict)

def findLapStart(dataframe):
    dataframe = dataframe[0]
    initialTime = dataframe.iloc[0,0]
    initialLong = dataframe.iloc[0,8]
    initialLat = dataframe.iloc[0,9]

    print ("Initial Time:", initialTime)
    print ("Initial Longitude:", initialLong)
    print ("Initial Latitude:", initialLat)

    lapStartArray = []
    tempTime = []

    for i in range(0, len(dataframe)):
        if abs(dataframe.iloc[i,8] - initialLong) < 0.00005 and abs(dataframe.iloc[i,9] - initialLat) < 0.00005:
            tempTime.append(dataframe.iloc[i,0])
        
    #Cluster time values and return the averaged value
    groups = [[tempTime[0]]]

    for i in tempTime[1:]:
        if i - groups[-1][-1] < 3:
            groups[-1].append(i)
        else:
            groups.append([i])

    for i in range(len(groups)):
        lapStartArray.append(sum(groups[i][:])/len(groups[i]))

    print ("Lap Start Time:", lapStartArray)

    return lapStartArray

def calLapTime(lapStartArray):
    lapTime = []
    #Calculate the lap time
    for i in range(0, len(lapStartArray)-1):
        lapTime.append(lapStartArray[i+1]-lapStartArray[i])

    print("Lap Time:", lapTime)

data = importData('./track-data.csv')
longIndexArray = findTrackStart(data.iloc[:,0], data.iloc[:,8])
latIndexArray = findTrackStart(data.iloc[:,0], data.iloc[:,9])
trackStartIndexArray = combineData(longIndexArray[0], latIndexArray[0], longIndexArray[1], latIndexArray[1])
dataframeDict = seperateData(trackStartIndexArray[0], trackStartIndexArray[1])
for key in dataframeDict.keys():
     print (key)
     lapStartTime = findLapStart(dataframeDict[key])
     calLapTime(lapStartTime)
