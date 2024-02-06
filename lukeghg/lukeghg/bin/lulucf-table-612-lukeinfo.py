#!python
import argparse
import pandas as pd
import xlsxwriter


excel_sheet="Table-6.1-2"
category_id = [13,1,2,3,4,5,6,7,8,14,9,49,3,4,7,15,19,49,3,48,7,6,16,9,10,11,12,17,9,10,47,7,18,18,19,19,""]
s_category_id=pd.Series(category_id)
report_id =[8,1,1,1,1,1,1,1,1,8,2,2,2,2,2,8,3,3,3,3,3,3,8,4,4,4,4,8,5,5,5,5,6,17,7,17,""]
s_report_id=pd.Series(report_id)

report_data_belongs=["","4A Metsämaa","4A Metsämaa","4A Metsämaa","4A Metsämaa","4A Metsämaa","4A Metsämaa","4A Metsämaa","4A Metsämaa",
                     "Yhteensä","4B Viljelysmaa","4B Viljelysmaa","4B Viljelysmaa","4B Viljelysmaa","4B Viljelysmaa","Yhteensä",
                     "4C Ruohikkoalueet","4C Ruohikkoalueet","4C Ruohikkoalueet","4C Ruohikkoalueet","4C Ruohikkoalueet",
                     "4C Ruohikkoalueet","Yhteensä","4D Kosteikot","4D Kosteikot","4D Kosteikot","4D Kosteikot","Yhteensä",
                     "4E Rakennetut alueet","4E Rakennetut alueet","4E Rakennetut alueet","4E Rakennetut alueet",
                     "4.G Puutuotteet","Yhteensä","4(IV) Epäsuorat N2O-päästöt","Yhteensä",""]
s_report_data_belongs=pd.Series(report_data_belongs)
#Insert double rows

def lulu622tolukeinfo(file_name:str,start:int,end:int):
    """
    Read LULUTable-6.1-2 excel file and the first excel sheet
    @par file_name LULUTable-6.1-2 excel file name
    @return Data frame with GHG inventory values rows transposed
    """
    year_id_ls = list(range(1,(end+2)-start))
    year_ls = list(range(start,end+1))
    xlsx = pd.ExcelFile(file_name)
    df1 = pd.read_excel(xlsx,excel_sheet)
    #In the model excel some rows were duplicated
    df_tmp=df1[df1['Mt CO2eq']== '4.G Harvested wood products']
    df2= pd.concat([df1.iloc[:df_tmp.index[0]], df_tmp, df1.iloc[df_tmp.index[0]:]]).reset_index(drop=True)
    df_tmp=df2[df2['Mt CO2eq']=='4(IV) Indirect N2O emissions']
    df3= pd.concat([df2.iloc[:df_tmp.index[0]], df_tmp, df2.iloc[df_tmp.index[0]:]]).reset_index(drop=True)
    df3.insert(0,'category_id',s_category_id)           
    df3.insert(2,'report_id',s_report_id)
    df3.insert(3,'report_data_belongs',s_report_data_belongs)
    #Double rows are inserted, slice the first block that includes names for
    #GHG inventory categories
    df_box = df3.iloc[:37,0:4]
    #Remeber the original block 
    df_box_orig = df_box.copy()

    #Fill the first block with first year year_id, year_ls and GHG inventory values
    year_id_ls_0 = [year_id_ls[0]]*len(df_box.index)
    year_ls_0 = [year_ls[0]]*len(df_box.index)
    df_value = df3.loc[:36,year_ls[0]]
    df_box.insert(len(df_box.columns),"year_id",year_id_ls_0)
    df_box.insert(len(df_box.columns),"year",year_ls_0)
    df_box.insert(len(df_box.columns),"value",df_value)

    #Repeat the excercise for the rest of the years
    for (year_id,year) in zip(year_id_ls[1:],year_ls[1:]):
        #Fresh block
        df_box_temp = df_box_orig.copy()
        year_id_ls = [year_id]*len(df_box_temp.index)
        year_ls = [year]*len(df_box_temp.index)
        #Slice the n'th  year data
        df_value = df3.loc[:36,year]
        df_box_temp.insert(len(df_box_temp.columns),"year_id",year_id_ls)
        df_box_temp.insert(len(df_box_temp.columns),"year",year_ls)
        df_box_temp.insert(len(df_box_temp.columns),"value",df_value)
        df_box=pd.concat([df_box,df_box_temp]).reset_index(drop=True)
        
    return df_box

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--excel_input",dest="f1",type=str,required=True,help="LULUTable6.1-2 excel file")
    parser.add_argument("-o","--excel_output",dest="f2", type=str,required=True,help="Excel output file for Luke info")
    parser.add_argument("-s","--start",dest="f3", type=int,required=True,help="GHG inventory start year")
    parser.add_argument("-e","--end",dest="f4", type=int,required=True,help="GHG inventory end year")
    args = parser.parse_args()
    print("Reading file", args.f1)
    df = lulu622tolukeinfo(args.f1,args.f3,args.f4)
    print("Writing file",args.f2)
    writer = pd.ExcelWriter(args.f2,engine='xlsxwriter')
    df.to_excel(writer,sheet_name="Table6-1.2",index=False,na_rep='NA')
    writer.close()
