## Script 3 of 3
## Developed by Zack Quarterman, Western Washington University (2020)

## This script is for calcluating the total area for each MFRI interval inside each ecoregion and
## summarizing the results in a table for each ecoregion with a LOW_ACRES field representing the
## lower number of the MFRI range (1-5 year range would use 1 year as the LOW_Acres input) and a 
## HIGH_ACRES field representing the higher number in the MFRI range (5 from the example above). 
## These fields yield a counterintuitive result in which the LOW_ACRES has the higher quantity 
## because the fires are happening more frequently (lower number for time interval).

try:
  
    import arcpy
    import pandas as pd
    from arcpy import env
    from arcpy.sa import *
    import os
    import sys

    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    outpath = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace" 
    #USA = "B:/GIS_Projects/ENVS428/Shared_Data.gdb/USA_Generalized_Albers_EA_US"
    #eco = "B:/GIS_Projects/ENVS428/Shared_Data.gdb/TNC_US_Ecoregions_Albers_EA_US"
    eco_gdb_name = 'Ecoregions_MFRI.gdb'
    usa_gdb_name = 'States_MFRI.gdb'
## Create callable path variables for states and ecoregion .gsb    
    eco_path = os.path.join(outpath, eco_gdb_name)
    usa_path = os.path.join(outpath, usa_gdb_name)
    arcpy.env.parallelProcessingFactor = "100%"
    workspaces = arcpy.ListWorkspaces("*", "FileGDB")
    ## These dictionaries will be used to calculate the low end and high end (of MFRI range) area estimates in the processing below.
## Shorter expected MFRI    
    low_dict = { 
    '1-5 Years': 1,
    '6-10 Years' : 6,
    '11-15 Years' : 11,
    '16-20 Years' : 16,
    '21-25 Years' : 21,
    '26-30 Years' : 26,
    '31-35 Years' : 31,
    '36-40 Years' : 36,
    '41-45 Years' : 41,
    '46-50 Years' : 46,
    '51-60 Years' : 51,
    '61-70 Years' : 61,
    '71-80 Years' : 71,
    '81-90 Years' : 81,
    '91-100 Years' : 91,
    '101-125 Years' : 101,
    '126-150 Years' : 126,
    '151-200 Years' : 151,
    '201-300 Years' : 201,
    '301-500 Years' : 301,
    '501-1000 Years' : 501,
    '>1000 Years' : 1000
    }
## Longer expected MFRI    
    high_dict = { 
    '1-5 Years': 5,
    '6-10 Years' : 10,
    '11-15 Years' : 15,
    '16-20 Years' : 20,
    '21-25 Years' : 25,
    '26-30 Years' : 30,
    '31-35 Years' : 35,
    '36-40 Years' : 40,
    '41-45 Years' : 45,
    '46-50 Years' : 50,
    '51-60 Years' : 60,
    '61-70 Years' : 70,
    '71-80 Years' : 80,
    '81-90 Years' : 90,
    '91-100 Years' : 100,
    '101-125 Years' : 125,
    '126-150 Years' : 150,
    '151-200 Years' : 200,
    '201-300 Years' : 300,
    '301-500 Years' : 500,
    '501-1000 Years' : 1000,
    '>1000 Years' : 1000
    }
## Convert the values in both dicitonaries to integer values so they can be multiplied later on  
    for key in low_dict:
        low_dict[key] = int(low_dict[key])
    for key in high_dict:
        high_dict[key] = int(high_dict[key])
    field = "AREA_ha"
    low_field = "LOW_AREA_ha"
    high_field = "HIGH_AREA_ha"
    ha_exp = """!Count! * 0.09"""    
    cursor_fields = ["MFRI", "AREA_ha", "LOW_AREA_ha", "HIGH_AREA_ha"]    
    for wrk in workspaces:
        print(wrk)
## Ecoregions MFRI Processing
## Add 3 fields, calculate the AREA_ha using field calculator. Then fill the values of LOW_AREA_ha and HIGH_AREA_ha
## using an update cursor and a calculation.
        if wrk == "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace\Ecoregions_MFRI.gdb":
            arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb"
            arcpy.env.parallelProcessingFactor = "100%"
            ds = arcpy.ListDatasets()
            for dataset in ds:
                print("-\n--\n---\n----\nProcessing Ecoregions_MFRI dataset: %s\n"%(dataset))
                #print("Adding field: %s to %s\n"%(field, dataset))
                #arcpy.AddField_management(dataset, field, "FLOAT", "", "", "", field, "NULLABLE", "NON_REQUIRED", "")
                #arcpy.AddField_management(dataset, low_field, "FLOAT", "", "", "", low_field, "NULLABLE", "NON_REQUIRED", "")
                #arcpy.AddField_management(dataset, high_field, "FLOAT", "", "", "", high_field, "NULLABLE", "NON_REQUIRED", "")
                #print("%s field added to %s\n"%(field, dataset))
                #print("%s field added to %s\n"%(low_field, dataset))
                #print("%s field added to %s\n"%(high_field, dataset))
                #arcpy.CalculateField_management(dataset, field, ha_exp, "PYTHON3", "")
                #print("%s calculated in %s"%(field, dataset)) 
                arr = arcpy.da.TableToNumPyArray(dataset, ('Value', 'Count', 'MFRI', 'AREA_ha'))
                #print("These are the results:\n %s\n"%(arr))
                ## Now opening an update cursor to calculate LOW_AREA_ha and HIGH_AREA_ha:
                with arcpy.da.UpdateCursor(dataset, cursor_fields) as cursor:
                    for row in cursor:
                        if row[0] in low_dict:
                            key = row[0]
                            coeff = int(low_dict.get(key))
                            updated_value = row[1] / coeff
                            #row[2] = updated_value
                            #print("%s in %s updated with value %s"%(key, dataset, updated_value))
                            #print("Calculating the value of HIGH_AREA_ha using %s"%(high_dict))
                            coeff_high = int(high_dict.get(key))
                            updated_value_high = row[1] / coeff_high
                            #row[3] = updated_value_high
                            #cursor.updateRow(row)
                        else:
                            key = row[0]
                            print("%s is not in low dict"%(key))
                            #print("%s is not in %s for some reason"%(key, low_dict))
                #print(ds)
## 50 States MFRI Processing
## Add 3 fields, calculate the AREA_ha using field calculator. Then fill the values of LOW_AREA_ha and HIGH_AREA_ha
## using an update cursor and a calculation.
        elif wrk == "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace\States_MFRI.gdb":
            arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb"
            arcpy.env.parallelProcessingFactor = "100%"
            ds = arcpy.ListDatasets()
            for dataset in ds:
                print("-\n--\n---\n----\nProcessing States_MFRI dataset: %s\n"%(dataset))
                print("Adding field: %s to %s\n"%(field, dataset))
                arcpy.AddField_management(dataset, field, "FLOAT", "", "", "", field, "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(dataset, low_field, "FLOAT", "", "", "", low_field, "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(dataset, high_field, "FLOAT", "", "", "", high_field, "NULLABLE", "NON_REQUIRED", "")
                print("%s field added to %s\n"%(field, dataset))
                print("%s field added to %s\n"%(low_field, dataset))
                print("%s field added to %s\n"%(high_field, dataset))
                arcpy.CalculateField_management(dataset, field, ha_exp, "PYTHON3", "")
                print("%s calculated in %s"%(field, dataset)) 
                ## The array is for display purposes only. No calculations are associated with this feature.
                arr = arcpy.da.TableToNumPyArray(dataset, ('Value', 'Count', 'MFRI', 'AREA_ha'))
                #print("These are the results:\n %s\n"%(arr))
            ## Now opening an update cursor to calculate LOW_AREA_ha and HIGH_AREA_ha:
                with arcpy.da.UpdateCursor(dataset, cursor_fields) as cursor:
                    for row in cursor:
                        if row[0] in low_dict:
                            key = row[0]
                            coeff = int(low_dict.get(key))
                            updated_value = row[1] / coeff
                            row[2] = updated_value
                            print("%s in %s updated with value %s"%(key, dataset, updated_value))
                            print("Calculating the value of HIGH_AREA_ha using %s"%(high_dict))
                            coeff_high = int(high_dict.get(key))
                            updated_value_high = row[1] / coeff_high
                            row[3] = updated_value_high
                            cursor.updateRow(row)
                        else:
                            key = row[0]
                            print("%s is not in the dictionary of inputs"%(key))
                            print("%s is not in %s"%(key, low_dict))
                print(ds)
        else:
            print("%s is not what wer are looking for!\n"%(wrk))
    print("Finished adding and calculating fields for all State and Ecoregion MFRI rasters\n")
##
## -----Summarize the MFRI rasters using the new fields, produce summary tables for each raster with the total area in each
##      MFRI range.
    os.chdir("B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace")
    print("Making directory ECO_MFRI_Tables to house the output summary statistics tables for proceeding raster analysis.")
    os.mkdir("ECO_MFRI_Tables")
    print("ECO_MFRI_Tables created")
    ## Creating gdb for eco outputs
    arcpy.CreateFileGDB_management("B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace", "ECO_TABLES.gdb")
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb"
    summary_fields = [["LOW_AREA_ha", "Sum"], ["HIGH_AREA_ha", "Sum"]]
    for dataset in arcpy.ListDatasets():
        print(dataset)
        field_list = arcpy.ListFields(dataset)
        print(field_list)
        ## Making output path for summary stats:
        output_parent = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/ECO_TABLES.gdb"
        ## This is to take the first values of the dataset name and use them to join to the excel table later on. 
        ## The first 6 letters contain the ECO_CODE pulled from the ecoregion attribute table
        outstr = dataset[0:6]
        print(outstr)
        outname = "%s"%(outstr)
        ## Redundant making a string a string...
        str_outname = str(outname)
        tbl_folder_path = os.path.join(output_parent, str_outname)
        print("Processing summary table for %s"%(str_outname))
        arcpy.Statistics_analysis(dataset, tbl_folder_path, summary_fields)
        print("%s created in %s"%(str_outname, tbl_folder_path))
        ## Generate a dictionary of naming conventions to map table names to fields in the excel doc.
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    name_dict = {}
    dict_field_list = ["ECO_CODE", "ECO_NAME"]
    eco_layer = 'TNC_US_Ecoregions_Albers_EA_US'
    with arcpy.da.SearchCursor(eco_layer, dict_field_list) as cursor:
        for row in cursor:
            key = str(row[0])
            #key = row[0]
            value = str(row[1])
            #value = row[1]
            name_dict.update({ key : value })
            print("\n%s and %s added to name_dict as key : value pair\n"%(key, value))
    print(name_dict)
    ## Now that we have a dictionary of names and codes to map to the excel table, we can load the excel file into a data frame and go from there.
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/ECO_TABLES.gdb"
    tbl_fields = ["SUM_LOW_AREA_ha", "SUM_HIGH_AREA_ha"]
    sum_list = []
    for table in arcpy.ListTables():
        with arcpy.da.SearchCursor(table, tbl_fields) as cursor:
            for row in cursor:
                if table in name_dict:
                    long_name = name_dict.get(table)
                    print("%s is %s"%(table,long_name))
                    side = [long_name, table, row[0], row[1]]
                    print(side)
                    sum_list.append(side)
                else:
                    print("%s skipped..."%(table))
    # Define function to sort list of lists based on the first item in thhe list which is the long name.  
    def getKey(item):
        return item[0]
    print(sum_list)
    ordered_sum_list = sorted(sum_list, key=getKey)
    print("\n\n\n\nThis is the sorted list of items:\n%s"%(ordered_sum_list))
    ## Previously anemd "dfa"
    df_eco_mfri = pd.DataFrame(ordered_sum_list, columns = ["ECO_NAME", "ECO_CODE", "SUM_LOW_AREA_ha", "SUM_HIGH_AREA_ha"])
    print("\n\n\n")
    print(df_eco_mfri)
    print("Saving this data frame as a csv for keeping...")
    eco_mfri_field_list = ["ECO_NAME", "ECO_CODE", "SUM_LOW_AREA_ha", "SUM_HIGH_AREA_ha"]
    df_eco_mfri.to_csv('B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/Ecoregions_MFRI.csv')
    print("Ecoregions_MFRI.csv saved to Summary_Table directory")
##################################################################################################
## This snippet was for joining to the summary table that Kaylene produced during fall quarter.
## The analysis as is continues using newly generated inputs that utilize the tabulate intersect tool. 
## This means the summary tables that were produced by the Pre_Processing_FO.py script will be read
## into a data frame and joined with the MFRI results for the Ecoregions and States.
    
## Snippet start:
    ## Open the csv file into another pandas dataframe so a join can take place.  
    #os.chdir("B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace")
    #df = pd.read_csv('Fire_Occurrence_By_EcoRegion.csv')
    #print(df)
    #boss_table = df.merge(dfa, how='left', left_on='ECO_NAME', right_on='ECO_NAME')
    #print("\n\n\n\n")
    #print(boss_table)
    #boss_table.to_csv(r"B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Merged_FO_BY_ECO_code.csv")
## Snippet end.
#####################################################################################################
    os.chdir('B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables')
    df_eco_fo = pd.read_csv('Ecoregion_F_O.csv')
    print("This is the ecoregion fire occurrence summary data frame:\n")
    print(df_eco_fo)
    df_merged_eco = pd.merge(df_eco_mfri, df_eco_fo, on="ECO_CODE")
    print("Merged data frames:")
    print(df_merged_eco)
    df_merged_eco.to_csv('B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/Merged_Ecoregion.csv')
    df_merged_eco.to_excel(r'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/Merged_Ecoregion_Excel.xls', index=None, header=True)

    print("The fire occurence data has been added to Merged_FO_BY_ECO_code.csv\n Processing complete!")
    print("Now converting the excel file to a geodatabase table...")
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables"
    output_table = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/Master_Ecoregion_Summary.dbf"
    arcpy.ExcelToTable_conversion("Merged_Ecoregion_Excel.xls", output_table)
    print("%s created\n\n\n"%(output_table))
## Add 2 fields, one for the high deficit calculation and one for the low deficit calculation
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb"
    low_exp = '''!SUM_LOW_AREA_ha! - (!AREA! / 20)''' ## NORMALIZE FOR 20 YEARS!!!!
    high_exp = '''!SUM_HIGH_AREA_ha! - (!AREA! / 20)''' ## NORMALIZE FOR 20 YEARS!!!
    arcpy.CalculateField_management("Master_Ecoregion_Summary.dbf", "LOW_DEFICIT", low_exp, "PYTHON3", "", "FLOAT")
    print("\nLOW_DEFICIT field calculated for %s"%(output_table))
    arcpy.CalculateField_management("Master_Ecoregion_Summary.dbf", "HIGH_DEFICIT", high_exp, "PYTHON3", "", "FLOAT")
    print("\nHIGH_DEFICIT field calculated for %s"%(output_table))
## Add join and copy features to produce new feature class with fire deficit rich attribute table for visualization
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    arcpy.env.qualifiedFieldNames = False
    Eco_join = arcpy.AddJoin_management("TNC_US_Ecoregions_Albers_EA_US", "ECO_CODE", output_table, "ECO_CODE")
    arcpy.CopyFeatures_management(Eco_join, "Ecoregion_Fire_Deficit_1992_2012")
    print("Ecoregion_Fire_Deficit_1992_2012 created in Shared_Data")

    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    ##-------------------------------------Summary statistics for the USA States ----------------------------------------
    os.chdir("B:/GIS_Projects/ENVS428/Prelim_Research_Project/Real_Data")
    print("Making STATES_TABLES.gdb to house the output summary statistics tables for proceeding raster summary statistics.")
    arcpy.CreateFileGDB_management("B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace", "STATES_TABLES.gdb")
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb"
    summary_fields = [["LOW_AREA_ha", "Sum"], ["HIGH_AREA_ha", "Sum"]]
## List all datasets inside of the States_MFRI.gdb    
    for dataset in arcpy.ListDatasets():
        print(dataset)
        ## Make a list of the fields contained in the dataset
        field_list = arcpy.ListFields(dataset)
        print(field_list)
        ## Making output path variable for summary stats:
        output_parent = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/STATES_TABLES.gdb"
        ## Indexing "USA_WA_MFRI" using [4:] returns "WA_MFRI", this naming convention will be used for all states.
        ## The "USA_" component of each name will be dropped from here forward.
        outstr = dataset[4:]
        print(outstr)
        outname = "%s"%(outstr)
        ## Explicitly convert the indexed string to a string, seems redundant but it works.
        str_outname = str(outname)
        ## Join the name to the STATES_TABLES.gdb path to make an output path for the summary statistics table.        
        tbl_folder_path = os.path.join(output_parent, str_outname)
        print("Processing summary table for %s"%(str_outname))
        arcpy.Statistics_analysis(dataset, tbl_folder_path, summary_fields)
        print("%s created in %s"%(str_outname, tbl_folder_path))
## Generate a dictionary of naming conventions to map table names to fields in the excel doc.
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    name_dict = {}
    dict_field_list = ["STUSPS", "NAME"]
    state_layer = 'USA_Generalized_Albers_EA_US'
    with arcpy.da.SearchCursor(state_layer, dict_field_list) as cursor:
        for row in cursor:
            short_key = row[0]
            key = short_key + "_MFRI" 
            value = row[1]
            name_dict.update({ key : value })
            print("\n%s and %s added to name_dict as key : value pair\n"%(key, value))
    print(name_dict)
    # ## Now that we have a dictionary of names and codes to map to the excel table, we can load the excel file into a data frame and go from there.
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/STATES_TABLES.gdb"
    tbl_fields = ["SUM_LOW_AREA_ha", "SUM_HIGH_AREA_ha"]
    sum_list = []
    for table in arcpy.ListTables():
        with arcpy.da.SearchCursor(table, tbl_fields) as cursor:
            for row in cursor:
                if table in name_dict:
                    long_name = name_dict.get(table)
                    print("%s is %s"%(table,long_name))
                    ## Make a list of the cell values to populate an excel row for the state
                    side = [long_name, table, row[0], row[1]]
                    print(side)
                    ## Make a list of lists
                    sum_list.append(side)
                else:
                    print("%s skipped..."%(table))
## Define function to sort list of lists based on the first item in the list which is the long name.  
## Function already defined during the ecoregions processing. Its used in the ordered_sum_list
   print(sum_list)
    ordered_sum_list = sorted(sum_list, key=getKey)
    print("\n\n\n\nThis is the sorted list of items:\n%s"%(ordered_sum_list))
    df_state_mfri = pd.DataFrame(ordered_sum_list, columns = ["NAME", "STUSPS", "SUM_LOW_AREA_ha", "SUM_HIGH_AREA_ha"])
    print("\n\n\n")
    print(df_state_mfri)
    df_state_mfri.to_csv(r"B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/States_MFRI.csv")
    print("Data frame saved to 'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/States_MFRI.csv'")
#    
    os.chdir('B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables')
    df_state_fo = pd.read_csv('States_F_O.csv')
    print("This is the state fire occurrence summary data frame:\n")
    print(df_state_fo)
    df_merged_state = pd.merge(df_state_mfri, df_state_fo, on="NAME")
    print("Merged data frames:")
    print(df_merged_state)
    df_merged_state.to_csv('B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/Merged_State.csv')
    df_merged_state.to_excel(r'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables/Merged_State_Excel.xls', index=None, header=True)
#
    print("Now converting the excel file to a geodatabase table...")
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables"
    output_table = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/Master_State_Summary.dbf"
    arcpy.ExcelToTable_conversion("Merged_State_Excel.xls", output_table)
    print("%s created\n\n\n"%(output_table))
## Add 2 fields, one for the high deficit calculation and one for the low deficit calculation
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb"
    low_exp = '''!SUM_LOW_AREA_ha! - (!AREA! / 20)''' ## NORMALIZE FOR 20 YEARS!!!
    high_exp = '''!SUM_HIGH_AREA_ha! - (!AREA! / 20)''' ## NORMALIZE FOR 20 YEARS!!!
    arcpy.CalculateField_management("Master_State_Summary.dbf", "LOW_DEFICIT", low_exp, "PYTHON3", "", "FLOAT")
    print("\nLOW_DEFICIT field calculated for %s"%(output_table))
    arcpy.CalculateField_management("Master_State_Summary.dbf", "HIGH_DEFICIT", high_exp, "PYTHON3", "", "FLOAT")
    print("\nHIGH_DEFICIT field calculated for %s"%(output_table))

    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    arcpy.env.qualifiedFieldNames = False
    State_join = arcpy.AddJoin_management("USA_Generalized_Albers_EA_US", "NAME", output_table, "NAME")
    arcpy.CopyFeatures_management(State_join, "USA_Fire_Deficit_1992_2012")
    print("USA_Fire_Deficit_1992_2012 created in Shared_Data")

except:
  import sys, traceback #if needed
  # Get the traceback object
  tb = sys.exc_info()[2]
  tbinfo = traceback.format_tb(tb)[0]
  # Concatenate information together concerning the error into a message string
  pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
  msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"
  # Return python error messages for use in script tool or Python Window
  arcpy.AddError(pymsg)
  arcpy.AddError(msgs)
  # Print Python error messages for use in Python / Python Window
  print (pymsg + "\n")
  print (msgs)

# End deployment of verbose error catcher......

print  ("\n\n--> Finished Script... ")
