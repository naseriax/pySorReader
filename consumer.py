from pySorReader import sorReader
from pprint import pprint as pp
import os


if __name__ == "__main__":
    # path_2212 = '/Users/aramneja/Library/CloudStorage/OneDrive-Nokia/UDM/MyData/MacData/Projects/Belgium/Elia/OTDR Issue/otdrs/22.12_Files/'
    # path_2312 = '/Users/aramneja/Library/CloudStorage/OneDrive-Nokia/UDM/MyData/MacData/Projects/Belgium/Elia/OTDR Issue/otdrs/23.12_Files/'
    # path_orig = '/Users/aramneja/Library/CloudStorage/OneDrive-Nokia/UDM/MyData/MacData/Projects/Belgium/Elia/OTDR Issue/otdrs/orig/'
    # B2Path = '/Users/aramneja/Library/CloudStorage/OneDrive-Nokia/UDM/MyData/MacData/Projects/Belgium/Elia/OTDR Issue/B2'
    # v = path_orig+u"TS-auvel150d1-OTDR-1-10-P3-OTS_DW067_auvel150d1-achen380d1-PROFILE2-11287-20231204_16-32-02.sor"
    # r = sorReader(u"/Users/aramneja/Downloads/BL-B3201-OTDR-1-17-P1-A1601_IROADM-1-3-LINEOUT-B3201_IROADM-1-2-LINEIN-PROFILE2-881-20240318_09-14-57.sor")
    # r = sorReader(u"/Users/aramneja/Downloads/forj3_01_04_LO_20240321_11-56-49.sor")  #Disconnected Before FORJ
    # r = sorReader(u"/Users/aramneja/Downloads/500m_01_06_LO_20240523_13-43-39.sor")  #Disconnected Before FiberSpool
    # r = sorReader(u"/Users/aramneja/BL-A1601-OTDR-1-10-P1-A1601_IROADM-1-3-LINEOUT-ILA_ASWG-1-3-LINEIN-AllProfiles-66-20240605_07-59-09.sor")
    r = sorReader(u"/Users/aramneja/Desktop/ML_OTDR/orig/TS-auvel150d1-OTDR-1-10-P3-OTS_DW067_auvel150d1-achen380d1-PROFILE2-11289-20231204_17-15-58.sor")  #Connected
    # pp(r.jsonoutput)
    # r.ploter()
    # r.plotly("line")
    pp(r.jsonoutput)
    r.ploter()

    # print("FileName,TotalLength")
    # for i in os.listdir(path_orig):
    #         if ".sor" in i:

    #             v = path_orig + i
    #             r = sorReader(v)
                
    #             print(i,",",r.jsonoutput['fiberLength_m'])
                # pp(r.jsonoutput)
                # r.ploter()


