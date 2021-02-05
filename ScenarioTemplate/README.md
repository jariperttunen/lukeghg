This directory contains two tempalate excel files for 
GHG scenarios. The python program is ghgscenario.py.
For instructions see InstallAndUpdateLukeGHG.

+ UIDMatrix.xlsx: UID or other identification tag for each time series
+ ScenarioTemplate.xlsx: Defines the template Excel sheet for output.
   One sheet will be created for each land use and land use change class.

The idea is to use UIDMatrix.xlsx and ScenarioTemplate.xlsx to identify time series
from the scenario files (format as in GHG Inventory) and
insert them to their proper places in their respective sheets
in the resulting scenarion Excel file. 
