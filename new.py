###################################################################
###    Category                : Automation                     ###
###    Created by              : Naseredin aramnejad            ###
###    Tested Environment      : Python 3.9.4                   ###
###    Last Modification Date  : 29/08/2023                     ###
###    Contact Information     : naseredin.aramnejad@gmail.com  ###
###    Requirements            : "pip3 install matplotlib"      ###
###################################################################

import json
from datetime import datetime
import matplotlib.pyplot as plt
import re
from pprint import pprint as pp
import sys
from textwrap import wrap
import struct
import plotly.tools as tls # Import this for make_subplots
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


__author__ = "Naseredin Aramnejad"

class sorReader:
    def __init__(self,filename):
        self.filename = filename
        self.jsonoutput = {}
        self.c = 299.79181901
        try:
            with open(filename,"rb") as rawdata:
                self.rawdecodedfile = rawdata.read()
        except FileNotFoundError:
            print("file {} not found!".format(filename))
            sys.exit()
        self.hexdata = self.rawdecodedfile.hex()
        self.decodedfile = "".join(list(map(chr,self.rawdecodedfile)))
        self.SecLocs = self.GetOrder()
        self.jsonoutput.update(self.fixedParams())
        self.dataPts()

    def GetNext(self,key):
        if key in self.SecLocs:
            index = self.SecLocs[key][0]
            next = index + 9999999999999
            for k,v in self.SecLocs.items():
                if k == key or len(v) == 0:
                    continue
                if v[0] > index and v[0] < next:
                    next = v[0]
            for k,v in self.SecLocs.items():
                if len(v) == 0:
                    continue
                if v[0] == next:
                    return k
        return None

    def GetOrder(self):
        sections = [
                        "SupParams",
                        "Map",
                        "FxdParams",
                        "DataPts",
                        "NokiaParams",
                        "KeyEvents",
                        "WaveMTSParams",
                        "GenParams",
                        "WavetekTwoMTS",
                        "WavetekThreeMTS",
                        "BlocOtdrPrivate",
                        "ActernaConfig",
                        "ActernaMiniCurve",
                        "JDSUEvenementsMTS"
                        ]
        SectionLocations = {}
        for word in sections:
            SectionLocations[word] = [m.start() for m in re.finditer(word,self.decodedfile)]
        

        return SectionLocations

    def ploter(self):
        df = pd.DataFrame(self.dataset.items(), columns=['Length', 'Reflection']) 

        # Reflection differences
        df['Diff'] = df['Reflection'].rolling(window=5).mean().diff()  

        # Rolling average (window size of 5 for example)
        df['Rolling_Avg'] = df['Reflection'].rolling(5).mean()

        # Gradient (approximate)
        df['Gradient'] = df['Diff'] / df['Length'].diff() 

        # # df['Event'] = np.where(df['Diff'].abs() > 0.1, 'Potential Connector', 'Normal')
        
        # threshold = 0.002  # Adjust this based on your data
        # consecutive_increases = 10  # How many consecutive increases to look for

        # potential_events = []
        # start_index = None

        # for i, diff in enumerate(df['Diff']):
        #     if diff > threshold:
        #         if start_index is None:
        #             start_index = i
        #         elif i - start_index >= consecutive_increases:  
        #             end_index = i + 10  # Account for 100 point change span
        #             potential_events.append((start_index, end_index))
        #             start_index = None
        #     else:
        #         start_index = None

        # # Update the DataFrame
        # df['Event'] = 'Normal'  # Set to normal by default
        # for start, end in potential_events:
        #     df.loc[start:end, 'Event'] = 'Potential Connector'

        # df['Event'] = np.where((df['Diff'].abs() > 3) & (df['Diff'].abs() < 8), 'Check', 'Normal') 
            
############################
        # df = pd.DataFrame(self.dataset.items(), columns=['Length', 'Reflection']) 
        # df['Diff'] = df['Reflection'].diff()
        # df['Gradient'] = df['Diff'] / df['Length'].diff()  # Assuming 'Length' is a column

        # threshold_diff = 5  
        # min_consecutive_low = 20  

        # potential_connectors = []
        # fiber_end = None

        # for i, row in df.iterrows():
        #     if row['Diff'] > threshold_diff:
        #         # Potential connector start
        #         start_index = i
        #     elif row['Diff'] < -threshold_diff:  
        #         if fiber_end is None:
        #             # Check if preceded by high reflection
        #             if start_index is not None and df.loc[start_index]['Diff'] > threshold_diff:
        #                 # Likely end of connector:
        #                 end_index = i - 1
        #                 window_size = 10 
        #                 potential_connectors.append((start_index - window_size, end_index))
        #                 start_index = None
        #             else:
        #                 # Potentially fiber end
        #                 consecutive_low = 1  # Initialize here
        #             fiber_end = i
        #         else:
        #             consecutive_low += 1  # Only increment if initialized 
        #             if consecutive_low >= min_consecutive_low:
        #                 break  

        # # Update DataFrame to mark events (replace 'Event' with your column name)
        # df['Event'] = 'Normal'
        # for start, end in potential_connectors:
        #     df.loc[start:end, 'Event'] = 'Connector'
        # if fiber_end is not None:
        #     df.loc[fiber_end:, 'Event'] = 'End of Fiber'

#####################################################
        # plt.figure(figsize=(10, 6)) # Adjust figure size if needed
        # plt.plot(df['Length'], df['Reflection'], label='Reflection')
        # plt.plot(df['Length'], df['Diff'], label='Difference')
        # plt.plot(df['Length'], df['Rolling_Avg'], label='Rolling Average')
        # plt.plot(df['Length'], df['Gradient'], label='Gradient')
        # plt.xlabel('Length')
        # plt.ylabel('Reflection')
        # plt.title('OTDR Data Analysis')
        # plt.legend()
        # plt.grid(True) 
        # plt.show()
###################################################################
        # fig = px.line(df, x='Length', y=['Reflection', 'Diff', 'Rolling_Avg', 'Gradient'], title='OTDR Data Analysis')
        # fig.show()
######################################################
        # fig = go.Figure()
        # fig.add_trace(go.Scatter(x=df['Length'], y=df['Reflection'], name='Reflection'))
        # for i, event in enumerate(df['Event']):
        #     if event == 'Potential Connector':
        #         start_length = df.iloc[i]['Length']
        #         end_length = df.iloc[i + 1]['Length']
        #         fig.add_shape(type='rect',
        #             x0=start_length, y0=-50,  # Adjust y0, y1 for visual positioning 
        #             x1=end_length, y1=-40, 
        #             line=dict(color='RoyalBlue'),
        #             fillcolor='LightSalmon',
        #             opacity=0.5
        # )

        # fig.update_layout(title='OTDR Data with Potential Connectors',
        #                 xaxis_title='Length',
        #                 yaxis_title='Reflection')
        # fig.show()
####################################################
        fig = tls.make_subplots(rows=2, cols=1, shared_xaxes=True)
        fig2 = px.line(df, x='Length', y=['Reflection', 'Diff', 'Rolling_Avg', 'Gradient'], title='OTDR Data Analysis')

        # Main subplot
        fig.add_trace(go.Scatter(
            x=df['Length'], y=df['Reflection'], 
            mode='lines', name='Reflection'
        ), row=1, col=1)

        # Event subplot
        fig.add_trace(go.Scatter(
            x=df[df['Event'] == 'Potential Connector']['Length'], 
            y=df[df['Event'] == 'Potential Connector']['Reflection'],
            mode='markers', name='Potential Connectors'
        ), row=2, col=1) 

        fig.update_layout(title='OTDR Data with Event Visualization',
                        height=600) 
        fig.show()
        fig2.show()
#################################################################
        # plt.plot(df['Length'], df['Reflection'])
        # plt.xlabel('Length')
        # plt.ylabel('Reflection')
        # plt.title('OTDR Data')
        # plt.show()

    def hexparser(self,cleanhex,mode=""):
        if mode == "schmutzig":
            return int("0x" + "".join(list(map(hex,list(map(ord,cleanhex))))[::-1]).replace("0x",""),0)
        elif mode == "schreiben":
            return bytes.fromhex(cleanhex).decode()
        elif mode== "loss":
            return int(struct.unpack('h', bytes.fromhex(cleanhex))[0])
        else:
            return int("0x"+"".join([cleanhex[i:i+2] for i in range(0,len(cleanhex),2)][::-1]),0)   

    def jsondump(self):
        with open(self.filename.replace("sor","json"),"w") as output:
            json.dump(self.jsonoutput,output)
        # print("json file generated!")

    def bellcore_version(self):
        return self.hexparser((self.hexdata[(self.SecLocs["Map"][0]+4)*2:(self.SecLocs["Map"][0]+5)*2]))/ 100

    def totalloss(self):
        totallossinfo = self.hexdata[(self.SecLocs["WaveMTSParams"][1]-22)*2:(self.SecLocs["WaveMTSParams"][1]-18)*2]
        return str(round(self.hexparser(totallossinfo)*0.001,3))

    def fiberlength(self):
        length = self.hexparser(self.hexdata[(self.SecLocs["WaveMTSParams"][1]-14)*2:(self.SecLocs["WaveMTSParams"][1]-10)*2])
        return round(length * (10 ** -4) * self.c / self.jsonoutput['refractionIndex'],3)

    def SupParams(self):
        supInfos = {}
        supInfo = self.decodedfile[self.SecLocs["SupParams"][1]+10:self.SecLocs[self.GetNext("SupParams")][1]].split("\x00")[:-1]
        supInfos["otdrSupplier"] = supInfo[0].strip()
        supInfos["otdrName"] = supInfo[1].strip()
        supInfos["otdrSN"] = supInfo[2].strip()
        supInfos["otdrModuleName"] = supInfo[3].strip()
        supInfos["otdrModuleSN"] = supInfo[4].strip()
        supInfos["otdrSwVersion"] = supInfo[5].strip()
        supInfos["otdrOtherInfo"] = supInfo[6].strip()
        return supInfos

    def genParams(self):
        buildInfo = {"BC": "as-built","CC": "as-current","RC": "as-repaired","OT": "other"}
        genInfos = {}
        genInfo = self.decodedfile[self.SecLocs["GenParams"][1]+10:self.SecLocs[self.GetNext("GenParams")][1]].split("\x00")[:-1]
        genInfos["lang"] = genInfo[0][:2].strip()
        genInfos["cableId"] = genInfo[0][2:].strip()
        genInfos["fiberId"] = genInfo[1].strip()
        genInfos["locationA"] = genInfo[2][4:].strip()
        genInfos["locationB"] = genInfo[3].strip()
        genInfos["buildCondition"] = buildInfo[genInfo[5].strip()]
        genInfos["comment"] = genInfo[14].strip()
        genInfos["cableCode"] = genInfo[4].strip()
        genInfos["operator"] = genInfo[13].strip()
        genInfos["fiberType"] = f'G.{self.hexparser(genInfo[2][:2],"schmutzig")}'
        genInfos["otdrWavelength"] = f'{self.hexparser(genInfo[2][2:4],"schmutzig")} nm'
        return genInfos

    def fixedParams(self):
        fixInfos = {}
        fixInfo = self.hexdata[(self.SecLocs["FxdParams"][1]+10)*2:(self.SecLocs[self.GetNext("FxdParams")][1]*2)]
        fixInfos["dateTime"] = datetime.fromtimestamp(self.hexparser(fixInfo[:8])).strftime('%Y-%m-%d %H:%M:%S')
        fixInfos["unit"] = self.hexparser(fixInfo[8:12],"schreiben")
        fixInfos["actualWavelength_nm"] = self.hexparser(fixInfo[12:16]) / 10
        fixInfos["pulseWidthNo"] = self.hexparser(fixInfo[32:36])
        fixInfos["pulseWidth_ns"] = self.hexparser(fixInfo[36:40])
        fixInfos["sampleQty"] = self.hexparser(fixInfo[48:56])
        fixInfos['ior'] = self.hexparser(fixInfo[56:64])
        fixInfos["refractionIndex"] = fixInfos['ior']* (10 ** -5)
        fixInfos["fiberLightSpeed_km/ms"] = self.c / fixInfos['refractionIndex']
        fixInfos["resolution_m"] = self.hexparser(fixInfo[40:48]) * (10 ** -8) * fixInfos["fiberLightSpeed_km/ms"]
        fixInfos["backscatteringCo_dB"] = self.hexparser(fixInfo[64:68]) * -0.1
        fixInfos["averaging"] = self.hexparser(fixInfo[68:76])
        fixInfos["averagingTime_M"] = round(self.hexparser(fixInfo[76:80])/600,3)
        fixInfos["range_m"] = round(fixInfos["sampleQty"] * fixInfos["resolution_m"],3)
        return fixInfos

    def dataPts(self):    
        dtpoints = self.hexdata[self.SecLocs["DataPts"][1]*2:self.SecLocs[self.GetNext("DataPts")][1]*2][40:]
        self.dataset = {}
        for length in range(self.jsonoutput['sampleQty']):
            passedlen = round(length * self.jsonoutput['resolution_m'],3)
            self.dataset[passedlen]=self.hexparser(dtpoints[length*4:length*4 + 4]) * -1000 * (10 ** -6)

    def keyEvents(self):
        keyevents = {}
        events = self.hexdata[self.SecLocs["KeyEvents"][1]*2:self.SecLocs[self.GetNext("KeyEvents")][1]*2]
        evnumbers= self.hexparser(events[20:24])
        pure_events = events[24:-44]
        eventhex = wrap(pure_events, width=int(len(pure_events)/evnumbers))
        for e in eventhex:
            eNum = self.hexparser(e[:4])
            keyevents[eNum] = {}
            keyevents[eNum]["eventPoint_m"] = self.hexparser(e[4:12]) * (10 ** -4) * self.jsonoutput["fiberLightSpeed_km/ms"]
            stValue = keyevents[eNum]["eventPoint_m"] % self.jsonoutput["resolution_m"]
            if stValue >= self.jsonoutput["resolution_m"] / 2:
                keyevents[eNum]["eventPoint_m"] = round(keyevents[eNum]["eventPoint_m"] +(self.jsonoutput["resolution_m"] - stValue),3)
            else:
                keyevents[eNum]["eventPoint_m"] = round(keyevents[eNum]["eventPoint_m"] - stValue , 3)

            keyevents[eNum]["slope"] = round(self.hexparser(e[12:16]) * 0.001,3)
            keyevents[eNum]["spliceLoss_dB"] = round(self.hexparser(e[16:20],"loss") * 0.001,3)
            keyevents[eNum]["reflectionLoss_dB"] = round((self.hexparser(e[20:28]) - (2**32)) * \
                0.001 if self.hexparser(e[20:28]) > 0 else self.hexparser(e[20:28]),3)
            keyevents[eNum]["eventType"] = self.hexparser(e[28:44],"schreiben")
            keyevents[eNum]["endOfPreviousEvent"] = self.hexparser(e[44:52])
            keyevents[eNum]["beginningOfCurrentEvent"] = self.hexparser(e[52:60])
            keyevents[eNum]["endOfCurrentEvent"] = self.hexparser(e[60:68])
            keyevents[eNum]["beginningOfNextEvent"] = self.hexparser(e[68:76])
            keyevents[eNum]["peakpointInCurrentEvent"] = self.hexparser(e[76:84])

        return keyevents



def find_end_of_fiber(otdr_data, drop_threshold=3, stability_window=10):


    distances = list(otdr_data.keys())
    reflections = list(otdr_data.values())

    for i in range(len(reflections) - 1):
        if reflections[i + 1] - reflections[i] <= -drop_threshold:  # Detect sharp drop
            # Check for stability
            if all(abs(reflections[j] - reflections[i + 1]) < 1 
                   for j in range(i + 2, i + stability_window + 2)):
                return distances[i]  

    return None  # No end-of-fiber event found






if __name__ == "__main__":
    # r1 = sorReader(u"/Users/aramneja/Library/CloudStorage/OneDrive-Nokia/UDM/MyData/MacData/Projects/Belgium/Elia/OTDR Issue/otdrs/orig/TS-auvel150d1-OTDR-1-10-P3-OTS_DW067_auvel150d1-achen380d1-PROFILE2-11288-20231204_17-02-50.sor")
    # r2 = sorReader(u"/Users/aramneja/Downloads/forj2_01_04_LO_20240321_11-38-03.sor")
    # r1.ploter()

    otdr_data = {0: 10, 10: 8, 20: 5, 30: 10, 40: -20, 45: -40, 50: -50}  

    end_of_fiber_distance = find_end_of_fiber(otdr_data, drop_threshold=5, stability_window=1) 

    if end_of_fiber_distance:
        print("End of fiber found at approximately:", end_of_fiber_distance)
    else:
        print("End of fiber not detected within the data.")

    plt.plot(list(otdr_data.keys()), list(otdr_data.values()))
    plt.xlabel("Distance (m)")
    plt.ylabel("Power (dB)")
    plt.title("OTDR Trace")
    plt.show()