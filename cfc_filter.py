import os
import sys
import csv
import json
import array
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter

inputFile = sys.argv[1]
# outputFile = sys.argv[2]
# cachedDataFile = sys.argv[3]
configFile = "./config.json"

timestamp = array.array('f')
accSensorData_1 = array.array('f')
accSensorData_2 = array.array('f')
proxySensorData = array.array('f')
numberOfRows = 0

config_order = 0
config_cutoff = 0
config_sampling_rate = 0
samplesToPlot = 0

accSensorDataMax_1 = 0
accSensorDataMax_2 = 0
accSensorDataMin_1 = 0
accSensorDataMin_2 = 0
avgAccSensorDataMax = 0
avgAccSensorDataMin = 0

averaged_accSensorData = array.array('f')
filtered_accSensorData_1 = array.array('f')
filtered_accSensorData_2 = array.array('f')
filtered_avgAccSensorData = array.array('f')

plot_timestamp = array.array('f')
cache_accSensorRawData_1 = array.array('f')
cache_accSensorRawData_2 = array.array('f')
cache_accSensorAvgRawData = array.array('f')
plot_accSensorData_1 = array.array('f')
plot_accSensorData_2 = array.array('f')
plot_avgAccSensorData = array.array('f')

def readSensorDataFromCSVFile():
    # Open the CSV file
    with open('.\\input\\'+inputFile, mode='r') as file:
        # Create a CSV reader
        csv_reader = csv.reader(file)

        # Skip the header if there is one
        for _ in range(9):
            next(csv_reader)  # Removes first 9 lines of header 
        
        global numberOfRows
        # Process each row in the CSV file
        for row in csv_reader:
            # print(row)  # Each row is a list of values
            timestamp.append(float(row[0]))
            accSensorData_1.append(float(row[1]))
            accSensorData_2.append(float(row[2]))
            proxySensorData.append(float(row[3]))
            numberOfRows = (numberOfRows + 1)

        # print(timestamp[1])
        # print(accSensorData_1[1])
        # print(accSensorData_2[1])
        # print(proxySensorData[1])
        # print(numberOfRows)

def readConfigJSONFile():
    # Open JSON file
    with open(configFile, mode='r') as file:
        configData = json.load(file)

    global filter_type
    global config_order
    global samplesToPlot

    filter_type = configData['filter_type']['cfc']
    config_order = configData['filter_config']['order']
    samplesToPlot = configData['graph_config']['samples_to_plot']
    # print(configData)
    # print('Filter order ', config_order, 'Filter type ', filter_type)

def averageOfAccSensorData():
    for i in range(numberOfRows):
        averaged_accSensorData.append((accSensorData_1[i]+accSensorData_2[i])/2) 

    global avgAccSensorDataMax
    global avgAccSensorDataMin
    avgAccSensorDataMax = max(averaged_accSensorData)
    avgAccSensorDataMin = min(averaged_accSensorData)
    # print('Max Averaged Value ', avgAccSensorDataMax)
    # print('Min Averaged Value ', avgAccSensorDataMin)

def applyCFCFilter():
        # Define your filter specifications based on CFC60 characteristics
    order = int(config_order)  # Example order

    if filter_type == 60:
        cutoff = 100.0
        fs = 600.0
    elif filter_type == 180:
        cutoff = 300.0
        fs = 1800.0
    elif filter_type == 600:
        cutoff = 1000.0
        fs = 6000.0
    elif filter_type == 1000:
        cutoff = 1650.0
        fs = 10000.0
    
    # print(cutoff)
    # print(fs)
    # Get the filter coefficients
    b, a = butter(order, cutoff/(0.5*fs), btype='low', analog=False)

    # Apply the filter to your data (replace 'data' with your actual data array)
    output = lfilter(b, a, accSensorData_1 )
    for i in range(len(output)):
        filtered_accSensorData_1.append(output[i])
        # print(filtered_accSensorData_1[i])   

    # Apply the filter to your data (replace 'data' with your actual data array)
    output = lfilter(b, a, accSensorData_2 )
    for i in range(len(output)):
        filtered_accSensorData_2.append(output[i])
        # print(filtered_accSensorData_2[i])   

    # Apply the filter to your data (replace 'data' with your actual data array)
    output = lfilter(b, a, averaged_accSensorData )
    for i in range(len(output)):
        filtered_avgAccSensorData.append(output[i])
        # print(filtered_avgAccSensorData[i])   
    
def writeProcessedDataToCSVFile():
    # Read the original CSV file and add the new column data
    with open('.\\input\\'+inputFile, mode='r') as infile, open('.\\output\\Processed_'+inputFile, mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Skip the header if there is one
        for _ in range(9):
            next(reader)  # Removes first 9 lines of header 

        # Write the rest of the rows with the new column data added
        for i, row in enumerate(reader):
            row.append(filtered_accSensorData_1[i])
            row.append(filtered_accSensorData_2[i])
            row.append(averaged_accSensorData[i])
            row.append(filtered_avgAccSensorData[i])
            writer.writerow(row)

        infile.close()
        outfile.close()

def cacheDataToPlot():
    index = averaged_accSensorData.index(avgAccSensorDataMax)
    data_points = int(samplesToPlot)
    # arr_idx = (index - 100)
    # for i in range(arr_idx, arr_idx + 200):
    arr_idx = (index - int(data_points/2))
    for i in range(arr_idx, arr_idx + data_points):
        # print(filtered_accSensorData_1[i])
        cache_accSensorRawData_1.append(accSensorData_1[i])
        cache_accSensorRawData_2.append(accSensorData_2[i])
        cache_accSensorAvgRawData.append(averaged_accSensorData[i])
        plot_accSensorData_1.append(filtered_accSensorData_1[i])
        plot_accSensorData_2.append(filtered_accSensorData_2[i])
        plot_avgAccSensorData.append(filtered_avgAccSensorData[i])
        plot_timestamp.append(timestamp[i])

def writeCachedDataToCSVFile():
    with open('.\\output\\Cached_'+inputFile, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)

        header = ['Time', 'S1_raw', 'S2_raw', 'Avg_raw', 'S1_filtered', 'S2_filtered', 'Avg_filtered']
        writer.writerow(header)

        for i in range(len(plot_timestamp)):
            data = []
            data.append(plot_timestamp[i])
            data.append(cache_accSensorRawData_1[i])
            data.append(cache_accSensorRawData_2[i])
            data.append(cache_accSensorAvgRawData[i])
            data.append(plot_accSensorData_1[i])
            data.append(plot_accSensorData_2[i])
            data.append(plot_avgAccSensorData[i])
            writer.writerow(data)

        outfile.close()

def plotGraphs():
    # use fig whenever u want the  
    # output in a new window also  
    # specify the window size you 
    # want ans to be displayed 

    fig = plt.figure(figsize =(20, 10)) 

    # creating multiple plots in a  
    # single plot 
    sub1 = plt.subplot(3, 3, 1) 
    sub2 = plt.subplot(3, 3, 3) 
    sub3 = plt.subplot(3, 3, 5) 
    # sub4 = plt.subplot(3, 3, 7) 

    sub1.plot(plot_timestamp, cache_accSensorAvgRawData, 'r--')
    sub1.set_xlabel('time(ms)')
    sub1.set_ylabel('Sensor Data')
    sub1.set_title('Raw Data')

    sub2.plot(plot_timestamp, plot_avgAccSensorData, 'b--')
    sub2.set_xlabel('time(ms)')
    sub2.set_ylabel('Sensor Data')
    sub2.set_title('Filtered Data')

    sub3.plot(plot_timestamp, cache_accSensorAvgRawData, 'r--', plot_timestamp, plot_avgAccSensorData, 'b--')
    sub3.set_xlabel('time(ms)')
    sub3.set_ylabel('Sensor Data')
    sub3.set_title('Overlapped')

    figfile = os.path.splitext(os.path.basename(inputFile))[0]
    os.chdir('.\\output\\')
    plt.savefig(figfile+'.png')
    os.chdir('..')
    # plt.show()

def main():
    readSensorDataFromCSVFile()
    readConfigJSONFile()
    averageOfAccSensorData()
    applyCFCFilter()
    writeProcessedDataToCSVFile()
    cacheDataToPlot()
    writeCachedDataToCSVFile()
    plotGraphs()

if __name__ == "__main__":
    main()