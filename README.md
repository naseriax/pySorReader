# pySorReader
An OTDR Sor file reader app to export the OTDR information to JSON format and draw the OTDR Reflection/Loss graph

# Usage:
## Install the requirements
```
pip install -r /path/to/requirements.txt
```
## Create consumer.py to parse the sor file:
```
from pySorReader import sorReader
from pprint import pprint as pp

c = sorReader("otdr_p2.sor")          # Reads/Parses the sor file.
pp(c.jsonoutput)                      # Prints the extracted data.
c.jsondump()                          # Dumps the extracted data as filename.json .
c.plotter()                           # Plots the OTDR graph using matplotlib.    

```
