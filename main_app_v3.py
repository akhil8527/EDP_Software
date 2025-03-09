# Importing necessary libraries
import os
import sys
import csv
import json
import array
import numpy as np
import pandas as pd
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
from tkinter import Frame, Label, ttk, filedialog

configFile = "./config.json"

timestamp = array.array('f')
accSensorData_1 = array.array('f')
accSensorData_2 = array.array('f')
# peakVelocityData = array.array('f')
# peakVelocityFrequency = array.array('f')
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


class MainApp:
    
    inputFile=None

    def __init__(self, root):
        self.root = root
        self.root.title("Yantrashilpa Technologies Pvt. Ltd.")
        self.root.geometry("1400x700")

        # Top bar
        top_bar = tk.Frame(self.root, 
                           bg="#34495e", 
                           height=50)
        top_bar.pack(fill="x", side="top")

        title_label = tk.Label(top_bar, 
                               text="Energy Dissipation Performance", 
                               fg="white", 
                               bg="#34495e", 
                               font=("Calibri", 20, "normal"))
        title_label.pack(side="left", padx=20)

        # Sidebar
        sidebar = tk.Frame(self.root, 
                           bg="#2c3e50", 
                           width=250)
        sidebar.pack(fill="y", side="left")

        # Input for CSV file
        csv_file_label = tk.Label(sidebar, 
                                  text="Select CSV File", 
                                  fg="white", bg="#2c3e50", 
                                  font=("Open Sans", 12, "bold"))
        csv_file_label.pack(side="top", fill="x", pady=(10, 5))

        self.csv_file_input = tk.Entry(sidebar, 
                                       font=("Open Sans", 10))
        self.csv_file_input.pack(side="top", fill="x", pady=5, padx=10)

        # Browse button
        browse_button = tk.Button(sidebar, 
                                  text="BROWSE", 
                                  command=self.browse_file, 
                                  bg="#1abc9c", 
                                  fg="black", 
                                  font=("Open Sans", 10, "normal"))
        browse_button.pack(side="top", fill="x", pady=5, padx=10)

        # Error label
        self.error_label = tk.Label(sidebar, 
                                    text="", 
                                    fg="#FFA500", 
                                    bg="#2c3e50", 
                                    font=("Open Sans", 10, "bold"),
                                    wraplength=180,
                                    justify="left"
                                    )
        self.error_label.pack(side="top", fill="y", expand=False)

        # Central frame for plotting
        self.central_frame = tk.Frame(self.root, 
                                      bg="black", 
                                      bd=2, 
                                      relief="sunken")
        self.central_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Input for samples to plot
        input_sample_label = tk.Label(sidebar, 
                                  text="Input Samples to Plot", 
                                  fg="white", bg="#2c3e50", 
                                  font=("Open Sans", 12, "bold"))
        input_sample_label.pack(side="top", fill="x", pady=(10, 5))

        self.input_sample = tk.Entry(sidebar, font=("Open Sans", 10))
        self.input_sample.pack(side="top", fill="x", pady=5, padx=10)

        # CFC60 Filter button
        cfc60_filter_button = tk.Button(sidebar, 
                                        text="APPLY CFC60 FILTER", 
                                        fg="white", 
                                        bg="#e74c3c", 
                                        font=("Arial", 12, "normal"), 
                                        command=self.allFunctions)
        cfc60_filter_button.pack(side="top", fill="x", pady=5, padx=10)

        # CFC Filter applied label
        self.cfc_filter_label = tk.Label(sidebar, 
                                    text="", 
                                    fg="#EEC900", 
                                    bg="#2c3e50", 
                                    font=("Open Sans", 10, "bold"),
                                    wraplength=180,
                                    justify="left"
                                    )
        self.cfc_filter_label.pack(side="top", fill="y", expand=False)

        # Add button to display image
        display_button = tk.Button(sidebar, 
                                   text="Display Image", 
                                   command=self.display_image, 
                                   bg="#3498db", 
                                   fg="white", 
                                   font=("Arial", 12, "normal"))
        display_button.pack(pady=10, padx=10)

        # Button to remove image
        remove_button = tk.Button(sidebar, 
                                  text="Close Window", 
                                  command=self.clear_image, 
                                  bg="#3498db", 
                                  fg="white", 
                                  font=("Arial", 12, "normal"))
        remove_button.pack(pady=10, padx=10)
        

    def display_error(self, message):
        self.error_label.config(text=message)


    def display_cfc_filter(self, message):
        self.cfc_filter_label.config(text=message)


    def browse_file(self):
        try:
            filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if filename:
                self.csv_file_input.delete(0, tk.END)
                self.csv_file_input.insert(0, filename)
                self.inputFile = self.csv_file_input.get()
        except Exception as e:
            self.display_error(f"Error browsing file: {e}")


    def readSensorDataFromCSVFile(self):
        try: 
            # Open the CSV file
            with open(self.inputFile, mode='r') as file:
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
            
        except Exception as e:
            self.display_error(f"Error reading CSV file: {e}")


    def readConfigJSONFile(self):
        try:
            # Open JSON file
            with open(configFile, mode='r') as file:
                configData = json.load(file)

            global filter_type
            global config_order
            global samplesToPlot

            filter_type = configData['filter_type']['cfc']
            config_order = configData['filter_config']['order']
            samplesToPlot = self.input_sample.get()
            # print(samplesToPlot)
        except Exception as e:
            self.display_error(f"Error reading JSON file: {e}")


    def averageOfAccSensorData(self):
        try:
            for i in range(numberOfRows):
                averaged_accSensorData.append((accSensorData_1[i]+accSensorData_2[i])/2) 

            global avgAccSensorDataMax
            global avgAccSensorDataMin
            avgAccSensorDataMax = max(averaged_accSensorData)
            avgAccSensorDataMin = min(averaged_accSensorData)
            # print('Max Averaged Value ', avgAccSensorDataMax)
            # print('Min Averaged Value ', avgAccSensorDataMin)
        except Exception as e:
            self.display_error(f"Error averaging sensor data: {e}")
    
    
    def applyCFCFilter(self):
        try:
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

            self.display_cfc_filter("CFC Filter applied on data")
            
        except Exception as e:
            self.display_error(f"Error applying CFC filter: {e}")
            
    
    def writeProcessedDataToCSVFile(self):
        # Read the original CSV file and add the new column data
        #with open('.\\input\\'+inputFile, mode='r') as infile, open('.\\output\\Processed_'+inputFile, mode='w', newline='') as outfile:
        with open(self.inputFile, mode='r') as infile, open('.\\output\\Processed_'+self.inputFile.split('/')[-1], mode='w', newline='') as outfile:
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
            
            
    def cacheDataToPlot(self):
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
            
    
    def writeCachedDataToCSVFile(self):
        with open('.\\output\\Cached_' + self.inputFile.split('/')[-1], mode='w', newline='') as outfile:
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
    
    ### Get peak velocity from SensorTesting27444.csv input file
    # def getPeakVelocity(self):
    #     # Read the CSV file into a list of lists
    #     with open(self.inputFile, mode='r') as infile:
    #         reader = csv.reader(infile)
            
    #         # Skip the header if there is one
    #         for _ in range(9):
    #             next(reader)  # Removes first 9 lines of header

    #         global numberOfRows
    #         # Process each row in the CSV file
    #         for row in reader:
    #             # print(row)  # Each row is a list of values
    #             peakVelocityData.append(float(row[2]))
    #             peakVelocityFrequency.append(float(row[3]))
    #             numberOfRows = (numberOfRows + 1)
            
    #         # create a dictionary of peak velocity data and its corresponding frequency
    #         peakVelocityDict = dict(zip(peakVelocityFrequency, peakVelocityData))
            
    #         # get maximum peak velocity and its corresponding frequency
    #         maxPeakVelocity = max(peakVelocityDict, key=peakVelocityDict.get)
    #         print("Max Peak Velocity: ", maxPeakVelocity)
    #         maxPeakVelocityFrequency = peakVelocityDict[maxPeakVelocity]
    #         print("Max Peak Velocity Frequency: ", maxPeakVelocityFrequency)

    #         # multiply maxPeakVelocityFrequency by multiplying factor
    #         maxPeakVelocityFrequency = round(maxPeakVelocity * 0.58086, 4)

    #         print("Max Peak Velocity Frequency: ", maxPeakVelocityFrequency)
    #         return maxPeakVelocityFrequency


    def plotGraphs(self):
        # use fig whenever u want the output in a new window also specify the window size you want ans to be displayed 
        fig = plt.figure(figsize =(20, 10))

        # get the total time above 80g for both raw data and filtered data
        with open('.\\output\\Cached_' + self.inputFile.split("/")[-1], mode='r') as infile:
            
            data = pd.read_csv(infile)
            
            timestamp  = data['Time'].tolist()
            avg_raw    = data['Avg_raw'].tolist()
            avg_filter = data['Avg_filtered'].tolist()

            raw_data_sum    = dict(zip(timestamp, avg_raw))
            filter_data_sum = dict(zip(timestamp, avg_filter))

            summation_1=[]
            for key, value in raw_data_sum.items():
                if value >= 80:
                    summation_1.append(key)

            summation_2=[]
            for key, value in filter_data_sum.items():
                if value >= 80:
                    summation_2.append(key)


        # creating multiple plots in a single plot 
        sub1 = plt.subplot(3, 3, 1)   # display raw data
        sub2 = plt.subplot(3, 3, 3)   # display filtered data
        sub3 = plt.subplot(3, 3, 8)   # display overlapped data
        # sub4 = plt.subplot(3, 3, 7)   # display velocity data (in km/hr)

        sub1.plot(plot_timestamp, cache_accSensorAvgRawData, 'r--')
        sub1.set_xlabel('time(ms)')
        sub1.set_ylabel('Deceleration (g)')
        sub1.set_title('Raw Data')
        sub1.axhline(y=80, color='black', linestyle='--')
        fig.text(0.2, 0.59, f'Max Decelaration: {round(max(cache_accSensorAvgRawData), 2)}g', ha='left', va='center', fontsize=10, color='blue')
        
        if len(summation_1) == 0:
            fig.text(0.2, 0.57, f'Time above 80g: 0 ms', ha='left', va='center', fontsize=10, color='blue')
        else:
            fig.text(0.2, 0.57, f'Time above 80g: {round((max(summation_1) - min(summation_1)), 4)}ms', ha='left', va='center', fontsize=10, color='blue')


        sub2.plot(plot_timestamp, plot_avgAccSensorData, 'b--')
        sub2.set_xlabel('time(ms)')
        sub2.set_ylabel('Deceleration (g)')
        sub2.set_title('Filtered Data')
        sub2.axhline(y=80, color='black', linestyle='--')
        fig.text(0.75, 0.58, f'Max Decelaration: {round(max(plot_avgAccSensorData), 2)}g', ha='left', va='center', fontsize=10, color='blue')
        
        if len(summation_2) == 0:
            fig.text(0.75, 0.56, f'Time above 80g: 0 ms', ha='left', va='center', fontsize=10, color='blue')
        else:
            fig.text(0.75, 0.56, f'Time above 80g: {round((max(summation_2) - min(summation_2)), 4)}ms', ha='left', va='center', fontsize=10, color='blue')


        sub3.plot(plot_timestamp, cache_accSensorAvgRawData, 'r--', plot_timestamp, plot_avgAccSensorData, 'b--')
        sub3.set_xlabel('time(ms)')
        sub3.set_ylabel('Deceleration (g)')
        sub3.set_title('Overlapped')
        sub3.axhline(y=80, color='black', linestyle='--')
        
        ### display peak velocity frequency value beside sub3

        filtered_numbers = [num for num in proxySensorData if num <= 50]

        maxFrequency = round(max(filtered_numbers) * 0.58086, 4)

        fig.text(0.2, 0.35, "Peak Velocity", ha='left', va='center', fontsize=14, fontweight='normal', color='red')
        fig.text(0.19, 0.32, f"{maxFrequency} km/h", ha='left', va='center', fontsize=14, fontweight='bold', color='blue', bbox=dict(facecolor='lightyellow', alpha=0.5))


        figfile = os.path.splitext(os.path.basename(self.inputFile))[0]
        os.chdir('.\\output\\')
        plt.savefig(figfile+'.png')
        os.chdir('..')
        plt.close()
        
        
    def allFunctions(self):
        self.readSensorDataFromCSVFile()
        self.readConfigJSONFile()
        self.averageOfAccSensorData()
        self.applyCFCFilter()
        self.writeProcessedDataToCSVFile()
        self.cacheDataToPlot()
        self.writeCachedDataToCSVFile()
        self.plotGraphs()


    def display_image(self):
        try:
            if self.inputFile:
                image_path = '.\\output\\' + self.inputFile.split('/')[-1].replace('csv', 'png')
                image = Image.open(image_path)
                image = image.resize((1500, 750))
                photo_image = ImageTk.PhotoImage(image)
                # Create a label widget to hold the image
                image_label = Label(self.central_frame, image=photo_image)
                image_label.image = photo_image  # Keep a reference to avoid garbage collection
                # Place the label in the frame
                image_label.pack()
        except Exception as e:
            self.display_error(f"Error displaying image: {e}")


    def clear_image(self):
        try:
            for widget in self.central_frame.winfo_children():
                widget.destroy()
            self.csv_file_input.delete(0, tk.END)
            self.input_sample.delete(0, tk.END)
            root.quit()
        except Exception as e:
            self.display_error(f"Error clearing image: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()