###################################################################
###    Category                : Automation                     ###
###    Created by              : Naseredin aramnejad            ###
###    Tested Environment      : Python 3.12                    ###
###    Last Modification Date  : 08/07/2024                     ###
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
from pprint import pprint as pp
import itertools
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go  # For annotations

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
        self.jsonoutput["bellcoreVersion"] = self.bellcore_version()
        if "2.1" not in str(self.jsonoutput["bellcoreVersion"]):
            print("This script works best with bellcore Version 2.1 and may not be completely compatible with this file: {}.".format(self.jsonoutput["bellcoreVersion"]))
        self.jsonoutput["totalLoss_dB"] = self.totalloss()
        self.jsonoutput["vacuumSpeed_m/us"] = self.c
        self.jsonoutput.update(self.SupParams())
        self.jsonoutput.update(self.genParams())
        self.jsonoutput.update(self.fixedParams())
        self.jsonoutput["fiberLength_m"] = self.fiberlength()
        self.dataPts()
        self.jsonoutput["events"] = self.keyEvents()
        self.jsondump()

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
                        "JDSUEvenementsMTS",
                        "Cksum"
                        ]
        SectionLocations = {}
        for word in sections:
            SectionLocations[word] = [m.start() for m in re.finditer(word,self.decodedfile)]
        
        return SectionLocations

    def plotly(self,draw="line"):

        # Data Preparation
        df = pd.DataFrame({'Fiber Length (m)':[t[0] for t in self.dataset],
                        'Optical Power(dB)': [t[1] for t in self.dataset]})

        # Base Plotly Express Graph
        if draw == "line":
            fig = px.line(df, x='Fiber Length (m)', y='Optical Power(dB)', color_discrete_sequence=['darkgreen'],title='OTDR Graph')
        else:
            fig = px.scatter(df, x='Fiber Length (m)', y='Optical Power(dB)', color_discrete_sequence=['darkgreen'],title='OTDR Graph')

        fig.update_layout(xaxis_title='Fiber Length (m)', yaxis_title='Optical Power(dB)')

        # Grid and Tick Styling
        fig.update_layout(
            xaxis=dict(gridcolor='gray', gridwidth=0.5, linecolor='dimgray'),
            yaxis=dict(gridcolor='gray', gridwidth=0.5, linecolor='dimgray'),
            paper_bgcolor='white',
            plot_bgcolor='white'
        )

        # Annotations
        for ev in self.jsonoutput["events"]:
            tmp1 = self.jsonoutput["events"][ev]['eventPoint_m']
            tmp2 = self.jsonoutput['events'][ev]

            # Event Type Logic
            if "E9999" in tmp2['eventType']:
                eventType = "EOF"
            elif float(tmp2['reflectionLoss_dB']) == 0:
                eventType = "Splice"
                refQ = " - OK"
            else:
                eventType = "Connector"
                if float(tmp2['reflectionLoss_dB']) <= -40:
                    refQ = " - OK"
                else:
                    refQ = " - !"

            # Loss Logic
            if float(tmp2['spliceLoss_dB']) == 0:
                lossQ = " - Ghost!"
            elif float(tmp2['spliceLoss_dB']) <= 1:
                lossQ = " - OK"
            else:
                lossQ = " - !" 

            # Arrow Annotation
            fig.add_annotation(
                x=tmp1, y=df.loc[df['Fiber Length (m)'] == tmp1, 'Optical Power(dB)'].iloc[0] + 1,
                xref='x', yref='y', 
                ax=tmp1, ay=df.loc[df['Fiber Length (m)'] == tmp1, 'Optical Power(dB)'].iloc[0] - 1,
                axref='x', ayref='y',
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='red'
            )

            # Text Annotation
            fig.add_annotation(
                x=tmp1, y=df.loc[df['Fiber Length (m)'] == tmp1, 'Optical Power(dB)'].iloc[0] - 1,
                xref='x', yref='y',
                text=f"  Event:{ev}<br>EventType:  {tmp2['eventType']}<br>Type:  {eventType}<br>Len:   {round(tmp1,1)}m<br>RefLoss: {tmp2['reflectionLoss_dB']}dB{refQ}<br>Loss:  {tmp2['spliceLoss_dB']}dB{lossQ}",
                showarrow=False,
                font=dict(size=8)
            )

        # Display the Plot
        fig.show()

    def return_index(self,data,v):
        for i in data:
            if i[0] == v:
                return i[1]
             
    def ploter(self):

        c = plt.subplots(figsize=(15,10))[1]
        c.set_facecolor('white')
        c.plot([t[0] for t in self.dataset],[z[1] for z in self.dataset],color='darkgreen',lw=1.3)

        c.grid(True, color='gray', linestyle='--', linewidth=0.5) 
        c.tick_params(color='dimgray', labelcolor='dimgray')  
        for ev in self.jsonoutput["events"]:
            refQ = ""
            lossQ = ""
            ev_location = self.jsonoutput["events"][ev]['eventPoint_m']

            ev_no = self.jsonoutput['events'][ev]
            if "E9999" in ev_no['eventType']:
                eventType = "EOF"
            elif float(ev_no['reflectionLoss_dB']) == 0:
                eventType = "Splice"
                refQ = " - OK"
            else:
                eventType = "Connector"
                if float(ev_no['reflectionLoss_dB']) <= -40:
                    refQ = " - OK"
                else:
                    refQ = " - !"
            
            if float(ev_no['spliceLoss_dB']) == 0:
                lossQ = " - Ghost!"
            elif float(ev_no['spliceLoss_dB']) <= 1:
                lossQ = " - OK"
            else:
                lossQ = " - !" 

            c.annotate("",xy=(ev_location,self.return_index(self.dataset,ev_location) + 1),
                       xytext=(ev_location,self.return_index(self.dataset,ev_location) - 1),
                        arrowprops=dict(arrowstyle="<->",color="red",connectionstyle= "bar,fraction=0"))

            c.annotate(f"  Event:{ev}\n  EventType:  {ev_no['eventType']}\n  EventRef:  {self.return_index(self.dataset,ev_no['eventPoint_m'])}\n  Type:  {eventType}\n  Len:   {round(ev_location,1)}m\n  RefLoss:   {ev_no['reflectionLoss_dB']}dB{refQ}\n  Loss:  {ev_no['spliceLoss_dB']}dB{lossQ}",
                      xy=(ev_location,self.return_index(self.dataset,ev_location)),
                          xytext=(ev_location,self.return_index(self.dataset,ev_location)-1),fontsize=8)

        c.set(xlabel='Fiber Length (m)', ylabel='Optical Power(dB)',title='OTDR Graph')
        plt.show()

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
        if self.SecLocs["WaveMTSParams"] != []:
            totallossinfo = self.hexdata[(self.SecLocs["WaveMTSParams"][1]-22)*2:(self.SecLocs["WaveMTSParams"][1]-18)*2]
            return str(round(self.hexparser(totallossinfo)*0.001,3))
        else:
            print("WaveMTSParams section not found in the sor file!")
            return 0

    def fiberlength(self):
        if self.SecLocs["WaveMTSParams"] != []:
            length = self.hexparser(self.hexdata[(self.SecLocs["WaveMTSParams"][1]-14)*2:(self.SecLocs["WaveMTSParams"][1]-10)*2])
            return round(length * (10 ** -4) * self.c / self.jsonoutput['refractionIndex'],3)
        else:
            return 0

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
        fixInfo = self.hexdata[(self.SecLocs["FxdParams"][1]+10)*2:(self.SecLocs[self.GetNext("FxdParams")][1]*2)];p=8
        fixInfos["dateTime"] = datetime.fromtimestamp(self.hexparser(fixInfo[:p])).strftime('%Y-%m-%d %H:%M:%S')
        fixInfos["unit"] = self.hexparser(fixInfo[p:p+4],"schreiben");p+=4
        fixInfos["actualWavelength_nm"] = self.hexparser(fixInfo[p:p+4]) / 10;p+=4
        fixInfos["AO"] = self.hexparser(fixInfo[p:p+8]); p+=8
        fixInfos["AOD"] = self.hexparser(fixInfo[p:p+8]); p+=8
        fixInfos["pulseWidthNo"] = self.hexparser(fixInfo[p:p+4]);p+=4

        fixInfos["pulseWidth_ns"] = []
        for i in range(fixInfos["pulseWidthNo"]):
            fixInfos["pulseWidth_ns"].append(self.hexparser(fixInfo[p:p+4]));p+=4

        resolution_m_p1 = []
        for i in range(fixInfos["pulseWidthNo"]):
            resolution_m_p1.append(self.hexparser(fixInfo[p:p+8]) * (10 ** -8));p+=8

        fixInfos["sampleQty"] = []
        for i in range(fixInfos["pulseWidthNo"]):
            fixInfos["sampleQty"].append(self.hexparser(fixInfo[p:p+8]));p+=8

        fixInfos['ior'] = self.hexparser(fixInfo[p:p+8]); p+=8
        fixInfos["refractionIndex"] = fixInfos['ior']* (10 ** -5)
        fixInfos["fiberLightSpeed_km/ms"] = self.c / fixInfos['refractionIndex']

        fixInfos["resolution_m"] = []
        for i in range(fixInfos["pulseWidthNo"]):
            fixInfos["resolution_m"].append(resolution_m_p1[i] * fixInfos["fiberLightSpeed_km/ms"] )

        fixInfos["backscatteringCo_dB"] = self.hexparser(fixInfo[p:p+4]) * -0.1;p +=4
        fixInfos["averaging"] = self.hexparser(fixInfo[p:p+8]);p+=8
        fixInfos["averagingTime_M"] = round(self.hexparser(fixInfo[p:p+4])/600,3);p+=4


        fixInfos["range_m"] = []
        for i in range(fixInfos["pulseWidthNo"]):
            fixInfos["range_m"].append(round(fixInfos["sampleQty"][i] * fixInfos["resolution_m"][i],3))

        return fixInfos

    def dataPts(self):
        def dB(point):
            return point * -1000 * (10 ** -6)
    
        dtpoints = self.hexdata[self.SecLocs["DataPts"][1]*2:self.SecLocs[self.GetNext("DataPts")][1]*2][40:]
        self.dataset = []
        for s in range(self.jsonoutput["pulseWidthNo"]):
            for length in range(self.jsonoutput['sampleQty'][s]):
                passedlen = round(length * self.jsonoutput['resolution_m'][s],3)
                self.dataset.append((passedlen,dB(self.hexparser(dtpoints[length*4:length*4 + 4]))))
        # self.dataset = sorted(self.dataset, key=lambda x: x[0])

    def mapKeyEvents(self,events):
        m = {}
        start = 4
        evnumbers= self.hexparser(events[:start])
        for i in range(1,evnumbers+1):
            if i == evnumbers:
                m[i]=(start,start+84)
            else:
                end = events.find("0"+str(i+1)+"00",start+84)
                m[i]=(start,end)
                start=end
        return m
    
    def keyEvents(self):
        keyevents = {}
        events = self.hexdata[(self.SecLocs["KeyEvents"][1]+10)*2:self.SecLocs[self.GetNext("KeyEvents")][1]*2]
        p = self.mapKeyEvents(events)
        eventhexlist= [events[v[0]:v[1]] for v in list(p.values())]
        for e in eventhexlist:
            eNum = self.hexparser(e[:4])
            keyevents[eNum] = {}
            keyevents[eNum]["eventPoint_m"] = self.hexparser(e[4:12]) * (10 ** -4) * self.jsonoutput["fiberLightSpeed_km/ms"]
            stValue = keyevents[eNum]["eventPoint_m"] % self.jsonoutput["resolution_m"][0]
            if stValue >= self.jsonoutput["resolution_m"][0] / 2:
                keyevents[eNum]["eventPoint_m"] = round(keyevents[eNum]["eventPoint_m"] +(self.jsonoutput["resolution_m"][0] - stValue),3)
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

def find_scale(c,lenRef):
    for k,v in c.dataset:
        if k > lenRef and k < lenRef + 12:
            return (k,v)
        
def align_scales(sor_objects,ref_object,refLen):
    for s in sor_objects:
        _,vs = find_scale(s,refLen)
        _,vref = find_scale(ref_object,refLen)
        diff = vref - vs
        # s.dataset = {k: v+diff for k, v in s.dataset.items()}
        s.dataset = [(i,j+diff) for i,j in s.dataset]

def merge_scans(sorlist,refsor,reflen):

    align_scales(sorlist,refsor,reflen)
    cx = sorlist[0]
    allEvents = []
    for d in sorlist:
        cx.dataset+=d.dataset
        # cx.dataset = sorted(cx.dataset, key=lambda x: x[0])
        allEvents += [e for _,e in d.jsonoutput["events"].items()]
    
    sorted_events = sorted(allEvents, key=lambda x: x['eventPoint_m'])
    cx.jsonoutput["events"] = {i: v for i, v in enumerate(sorted_events)}
    return cx

if __name__ == "__main__":
    p1 = "/Users/aramneja/Downloads/P1.sor"
    p2 = "/Users/aramneja/Downloads/P2.sor"
    p3 = "/Users/aramneja/Downloads/P3.sor"
    p4 = "/Users/aramneja/Downloads/P4.sor"
    p5 = "/Users/aramneja/Downloads/P5.sor"
    p6 = "/Users/aramneja/Downloads/P6.sor"
    cADV = "/Users/aramneja/TS-A1601-OTDR-1-10-P1-A1601_IROADM-1-3-LINEOUT-ILA_ASWG-1-3-LINEIN-PROFILE2-21-20240603_20-44-20.sor"
    cALL = "/Users/aramneja/Downloads/ALL.sor"
    c1 = sorReader(p1)
    c2 = sorReader(p2)
    c3 = sorReader(p3)
    c4 = sorReader(p4)
    c5 = sorReader(p5)
    c6 = sorReader(p6)
    # CADV = sorReader(cADV)
    # CALL = sorReader(cALL)

    # pp(c1.jsonoutput)
    # pp(c2.jsonoutput)
    # pp(c3.jsonoutput)
    # pp(c4.jsonoutput)
    # pp(c5.jsonoutput)
    # pp(c6.jsonoutput)
    # pp(CADV.jsonoutput)
    # pp(CALL.jsonoutput)
    ref = 500
    # print(find_scale(c1,ref))
    # print(find_scale(c2,ref))
    # print(find_scale(c3,ref))
    # print(find_scale(c4,ref))
    # print(find_scale(c5,ref))
    # print(find_scale(c6,ref))
    cx = merge_scans([c1,c2,c3,c4,c5,c6],c1,ref)

    # print(find_scale(c1,ref))
    # print(find_scale(c2,ref))
    # print(find_scale(c3,ref))
    # print(find_scale(c4,ref))
    # print(find_scale(c5,ref))
    # # print(find_scale(c6,ref))
    # c1.ploter()
    # c2.ploter()
    # c3.ploter()
    # c4.ploter()
    # c5.ploter()
    # c6.ploter()
    # CADV.ploter()
    # CALL.plotly("s")
    # CALL.ploter()
    # pp(cx.jsonoutput)
    # cx.plotly("jj")
    cx.ploter()


"""
P1:
 'pulseWidth_ns': [10000],
 'range_m': [265832.466],
 'refractionIndex': 1.465,
 'resolution_m': [10.231802696587032],
 'sampleQty': [25981],

P2:
'pulseWidth_ns': [3000],
'range_m': [163514.439],
'refractionIndex': 1.465,
'resolution_m': [5.115901348293516],
'sampleQty': [31962],

P3:
 'pulseWidth_ns': [1000],
 'range_m': [81621.648],
 'refractionIndex': 1.465,
 'resolution_m': [2.557950674146758],
 'sampleQty': [31909],

 P4:
 'pulseWidth_ns': [100],
 'range_m': [40728.33],
 'refractionIndex': 1.465,
 'resolution_m': [0.6394876685366895],
 'sampleQty': [63689],

 P5:
 'pulseWidth_ns': [30],
 'range_m': [20230.192],
 'refractionIndex': 1.465,
 'resolution_m': [0.31974383426834474],
 'sampleQty': [63270],

 P6:
 'pulseWidth_ns': [10],
 'range_m': [10003.026],
 'refractionIndex': 1.465,
 'resolution_m': [0.15987191713417237],
 'sampleQty': [62569],
"""