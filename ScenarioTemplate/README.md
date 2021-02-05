This directory two tempalate excel files for 
GHG scenarios. The python program is ghgscenario.py.

Example command line for ghgscenario.py is as follows:
python ghgscenario.py --files 'malusepo-jatkuvakasvu/crf/*.csv' --uid UIDMatrix.xlsx --scen ScenarioTemplate.xlsx  -m ../GHG2018/lukeghg/300_500_mappings_1.1.csv -o TestFile.xlsx

+ UIDMatrix.xlsx: UID for each time series
+ ScenarioTemplate.xlsx: Defines the excel sheet for output
   Additional sheets will be created for each land use class.

The idea is to use UIDMatrix.xlsx to identify time series
from the scenario files (format as in GHG Inventory) and
insert them to their proper places in ScenarioTemplate.xlsx. 
