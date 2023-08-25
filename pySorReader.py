###################################################################
###    Category                : Automation                     ###
###    Created by              : Naseredin aramnejad            ###
###    Tested Environment      : Python 3.9.4                   ###
###    Last Modification Date  : 25/08/2023                     ###
###    Contact Information     : naseredin.aramnejad@gmail.com  ###
###    Requirements            : "pip3 install matplotlib"      ###
###################################################################
_
_author__ = "Naseredin Aramnejad"

class sorReader:
    def __init__(self,filename):
        self.filename = filename
        self.jsonoutput = {}
        self.c = 299.79181901
        with open(filename,"rb") as rawdata:
            self.rawdecodedfile = rawdata.read()
        self.hexdata = self.rawdecodedfile.hex()
        self.decodedfile = "".join(list(map(chr,self.rawdecodedfile)))
        self.SecLocs = self.GetOrder()
        self.jsonoutput["bellcoreVersion"] = self.bellcore_version()
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
                if k == key:
                    continue
                if v[0] > index and v[0] < next:
                    next = v[0]
            for k,v in self.SecLocs.items():
                if v[0] == next:
                    return k
        return None

    def GetOrder(self):
        sections = [
                        "SupParams",
                        "Map",
                        "FxdParams",
                        "DataPts",
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

        c = plt.subplots(figsize=(13,8))[1]
        c.plot(self.dataset.keys(),self.dataset.values(),color='tab:green',lw=0.6)
        for ev in self.jsonoutput["events"]:
            refQ = ""
            lossQ = ""
            tmp1 = self.jsonoutput["events"][ev]['eventPoint_m']
            tmp2 = self.jsonoutput['events'][ev]
            
            if float(tmp2['reflectionLoss_dB']) == 0:
                eventType = "Splice"
                refQ = " - OK"
            else:
                eventType = "Connector"
                if float(tmp2['reflectionLoss_dB']) <= -40:
                    refQ = " - OK"
                else:
                    refQ = " - !!!"
            
            if float(tmp2['spliceLoss_dB']) == 0:
                lossQ = " - Ghost!"
            elif float(tmp2['spliceLoss_dB']) <= 1:
                lossQ = " - OK"
            else:
                lossQ = " - !" 
                
            c.annotate("",xy=(tmp1,self.dataset[tmp1] + 1),
                       xytext=(tmp1,self.dataset[tmp1] - 1),
                        arrowprops=dict(arrowstyle="<->",color="red",connectionstyle= "bar,fraction=0"))

            c.annotate(f"  Event:{ev}\n  Type:  {eventType}\n  Len:   {round(tmp1,1)}m\n  Ref:   {tmp2['reflectionLoss_dB']}dB{refQ}\n  Loss:  {tmp2['spliceLoss_dB']}dB{lossQ}",
                      xy=(tmp1,self.dataset[tmp1]),
                          xytext=(tmp1,self.dataset[tmp1]-1))

        c.set(xlabel='Fiber Length (m)', ylabel='Optical Power(dB)',title='OTDR Graph')
        plt.grid()
        plt.show()

    def hexparser(self,cleanhex,mode="sauber"):
        if mode == "schmutzig":
            return int("0x" + "".join(list(map(hex,list(map(ord,cleanhex))))[::-1]).replace("0x",""),0)
        elif mode == "schreiben":
            return bytes.fromhex("".join([cleanhex[i:i+2] for i in range(0,len(cleanhex),2)])).decode("ASCII")
        else:
            return int("0x"+"".join([cleanhex[i:i+2] for i in range(0,len(cleanhex),2)][::-1]),0)   

    def jsondump(self):
        with open(self.filename.replace("sor","json"),"w") as output:
            json.dump(self.jsonoutput,output)
        print("json file generated!")

    def bellcore_version(self):
        return self.hexparser((self.hexdata[(self.SecLocs["Map"][0]+4)*2:(self.SecLocs["Map"][0]+5)*2]))/ 100

    def totalloss(self):
        totallossinfo = self.hexdata[(self.SecLocs["WaveMTSParams"][1]-22)*2:(self.SecLocs["WaveMTSParams"][1]-18)*2]
        return str(round(self.hexparser(totallossinfo)*0.001,3))

    def fiberlength(self):
        length = self.hexparser(self.hexdata[(self.SecLocs["WaveMTSParams"][1]-14)*2:(self.SecLocs["WaveMTSParams"][1]-10)*2])
        return round(length * 10 ** -4 * self.c / self.jsonoutput['refractionIndex'],3)

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
        fixInfos["refractionIndex"] = fixInfos['ior']* 10 ** -5
        fixInfos["fiberLightSpeed_km/ms"] = self.c / fixInfos['refractionIndex']
        fixInfos["resolution_m"] = self.hexparser(fixInfo[40:48]) * 10 ** -8 * fixInfos["fiberLightSpeed_km/ms"]
        fixInfos["backscatteringCo_dB"] = self.hexparser(fixInfo[64:68]) * -0.1
        fixInfos["averaging"] = self.hexparser(fixInfo[68:76])
        fixInfos["averagingTime_M"] = round(self.hexparser(fixInfo[76:80])/600,3)
        fixInfos["range_m"] = round(fixInfos["sampleQty"] * fixInfos["resolution_m"],3)
        return fixInfos

    def dataPts(self):
        def dB(point):
            return point * -1000 * 10 ** -6
    
        dtpoints = self.hexdata[self.SecLocs["DataPts"][1]*2:self.SecLocs[self.GetNext("DataPts")][1]*2][40:]
        self.dataset = {}
        for length in range(self.jsonoutput['sampleQty']):
            passedlen = round(length * self.jsonoutput['resolution_m'],3)
            self.dataset[passedlen]=dB(self.hexparser(dtpoints[length*4:length*4 + 4]))

    def keyEvents(self):
        keyevents = {}
        events = self.hexdata[self.SecLocs["KeyEvents"][1]*2:self.SecLocs[self.GetNext("KeyEvents")][1]*2]
        evnumbers= self.hexparser(events[20:24])
        pure_events = events[24:-44]
        eventhex = wrap(pure_events, width=int(len(pure_events)/evnumbers))
        for e in eventhex:
            eNum = self.hexparser(e[:4])
            keyevents[eNum] = {}
            keyevents[eNum]["eventPoint_m"] = self.hexparser(e[4:12]) * 10 ** -4 * self.jsonoutput["fiberLightSpeed_km/ms"]
            stValue = keyevents[eNum]["eventPoint_m"] % self.jsonoutput["resolution_m"]
            if stValue >= self.jsonoutput["resolution_m"] / 2:
                keyevents[eNum]["eventPoint_m"] = round(keyevents[eNum]["eventPoint_m"] + \
                                            (self.jsonoutput["resolution_m"] - stValue),3)
            else:
                keyevents[eNum]["eventPoint_m"] = round(keyevents[eNum]["eventPoint_m"] - stValue , 3)
            keyevents[eNum]["slope"] = round(self.hexparser(e[14:16]) * 0.001,3)
            keyevents[eNum]["spliceLoss_dB"] = round(self.hexparser(e[16:20]) * 0.001,3)
            keyevents[eNum]["reflectionLoss_dB"] = round((self.hexparser(e[20:28]) - 2**32) * \
                0.001 if self.hexparser(e[20:28]) > 0 else self.hexparser(e[20:28]),3)
            keyevents[eNum]["eventType"] = self.hexparser(e[28:44],"schreiben")
            keyevents[eNum]["endOfPreviousEvent"] = self.hexparser(e[44:52])
            keyevents[eNum]["beginningOfCurrentEvent"] = self.hexparser(e[52:60])
            keyevents[eNum]["endOfCurrentEvent"] = self.hexparser(e[60:68])
            keyevents[eNum]["beginningOfNextEvent"] = self.hexparser(e[68:76])
            keyevents[eNum]["peakpointInCurrentEvent"] = self.hexparser(e[76:84])

        return keyevents
