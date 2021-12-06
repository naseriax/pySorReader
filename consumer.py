from pySorReader import sorReader
from pprint import pprint as pp


if __name__ == "__main__":
    r = sorReader(r"1 (8).sor")
    pp(r.jsonoutput)
    r.ploter()
    
