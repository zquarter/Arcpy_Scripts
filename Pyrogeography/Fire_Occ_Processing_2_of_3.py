## Script 2 of 3
## Developed by Zack Quarterman, Western Washington University (2020)

## This script seperates the ecoregions and states FC into three different parts (AK, HI, and Lower 48) 
## so they can be reprojected to match the projections of the MFRI data (All Albers EA but with different
## prime meridians due to their different geographic location).
##
## The Fire Occurrence feature class created last quarter contained all of the fires within a single feature class
## and therefore all fires shared the same projection and while the MFRI rasters for the lower 48, AK, and HI were 
## in different Albers projections. This workflow insures that the fire occurrence data and MFRI data are in the 
## projection so calculations can be more accurate. 
##
## The second part of this script contains the necessary geoprocessing required to rasterize the fire occurrence 
## polygon for AK, HI and the Lower 48 states in 3 different rasters. This produces the inputs required to directly
## compare the fire occurrence with the MFRI for each 30m pixel in all 50 states.

## This script creates:
## Geodatabase:
## Fire_Occ.gdb
##
## Folders:
## Summary_Tables
##
## Feature classes:
## F_O_AK, F_O_AK_Dissolve, F_O_AK_Prj, F_O_AK_Raster, F_O_AK_Union
## F_O_HI, F_O_HI_Dissolve, F_O_HI_Prj, F_O_HI_Raster, F_O_HI_Union
## F_O_US_Prj, F_O_US_Dissolve, F_O_US_Raster, F_O_US_Union

## Summary Tables:
## FO__AK_By_Eco, FO__AK_By_State, FO__HI_By_Eco, FO__HI_By_State, FO__US_By_Eco, FO__US_By_State
## All of these tables are converted to csv and saved in the Summary_Tables folder

try:
  
    import arcpy
    from arcpy import env
    from arcpy.sa import *
    import os
    import pandas as pd
    import re

    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    arcpy.env.parallelProcessingFactor = "100%"
    outpath = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
## Create new file gdb to house all products created in rasterizing the fire occurrence data
    gdb_name = "Fire_Occ.gdb"
    out_gdb_path = os.path.join(outpath, gdb_name)
    arcpy.CreateFileGDB_management(outpath, gdb_name)
    print("%s created"%(out_gdb_path))
## Set workspace to the new geodatabase "Fire_Occ.gdb"    
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    in_fc = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb/Fire_Occurrence_Albers_EA_1992_2012"
## Seperate the fires into 3 groups, (AK, HI, and Lower 48)    
    ## SQL where statements to filter out where fires are
    ak_where = ''' "STATE" = 'AK' '''
    hi_where = ''' "STATE" = 'HI' '''
    us_where = ''' "STATE" = 'AK' OR "STATE" = 'HI' '''
    ak_out = 'F_O_AK'
    hi_out = 'F_O_HI'
## The native projection of the feature class being selected from is going to be carried through
## for the lower 48 and therefore it will not need to be reprojected. Changing the name at this point
## was done to match the naming conventions of the future F_O_AK_Prj and F_O_HI_Prj feature classes.    
    us_out = 'F_O_US_Prj'
## For each selection, copy features to make new feature class containing the selected area.    
    print("Selecting %s"%(ak_where))
    ak_sel = arcpy.SelectLayerByAttribute_management(in_fc, "NEW_SELECTION", ak_where)
    print("Copying features to %s"%(ak_out))
    arcpy.CopyFeatures_management(ak_sel, ak_out)
    print("Selecting %s"%(hi_where))
    hi_sel = arcpy.SelectLayerByAttribute_management(in_fc, "NEW_SELECTION", hi_where)
    print("Copying features to %s"%(hi_out))
    arcpy.CopyFeatures_management(hi_sel, hi_out)
    print("Selecting %s"%(us_where))
    us_sel = arcpy.SelectLayerByAttribute_management(in_fc, "NEW_SELECTION", us_where)
    print("Inverting selection so areas that are NOT AK and NOT HI are selected, even null values")
    us_sel_out = arcpy.SelectLayerByAttribute_management(us_sel, "SWITCH_SELECTION", "")
    print("Copying features to %s"%(us_out))
    arcpy.CopyFeatures_management(us_sel_out, us_out)
    fc_list = arcpy.ListFeatureClasses()
    for fc in fc_list:
        print("%s now in Fire_Occ.gdb"%(fc))
##------------------Project each area into correct projection---------------
    ## The F_O_US is already in the correct projection "USA Contiguious Albers Equal Area Conic"
    ak_prj_out = 'F_O_AK_Prj'
    hi_prj_out = 'F_O_HI_Prj'
    ak_prj = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Projections/AK_Albers_EA.prj"
    hi_prj = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Projections/HI_Albers_EA.prj"
    us_prj = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Projections/USA_Albers_EA.prj"
    for fc in fc_list:
        if fc == ak_out:
            print("Projecting %s into AK_Albers_EA.prj"%(fc))
            arcpy.Project_management(fc, ak_prj_out, ak_prj, "", "", "PRESERVE_SHAPE")
            print("%s created"%(ak_prj_out))
        elif fc == hi_out:
            print("Projecting %s into HI_Albers_EA.prj"%(fc))
            arcpy.Project_management(fc, hi_prj_out, hi_prj, "", "", "PRESERVE_SHAPE")
            print("%s created"%(hi_prj_out))
        else:
            print("%s already in correct projection"%(fc))
##---------Use the 3 seperate feature classes to tabulate intersect for ecoregions and states---------
## This is a quicker way of calculating the area burned by ecoregion/state compared to the fire occurrence by
## ecoregion results previously produced. Thgis will only produce a table summarizing the total area of fire 
## polygons by ecoregion/state. These will be used later to calculate fire defecit/surplus for each area.
    ## Variables for ecoregion and state feature classes
    USA = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb/USA_Generalized_Albers_EA_US"
    eco = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb/TNC_US_Ecoregions_Albers_EA_US"
    ## List of ecoregions that are outside of 50 states (Guam, Virgin Islands, Samoa etc..)
    exclude_list = ["NT1402", "OC0112", "OC0203", "OC0703", "NT0226", "NT0155", "NT0134", "NT1305", "OC0117"]
    exclude_list.sort()
    ## List of ecoregions in AK (to use different projection)
    ak_list = ["NA1106", "NA1105", "NA1104", "NA1102", "NA0612", "NA0611", "NA0610", "NA0607", "NA0602", "NA0601", "NA0518", "NA0509"]
    ak_list.sort()
    ## List of ecoregions in HI (to use different projection)
    hi_list = ["OC0106", "OC0202", "OC0701", "OC0702"]
    hi_list.sort()
    ## Switching workspace to 
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    ## Load as many fields as necessary into the search cursor, if 2 are loaded a dictionary can be created to link link field values to desired names. 
    ## In this case the names were simply too long to use.
    code_field = ["ECO_CODE", "ECO_NAME"]
    ## This list will include the ecoregions inside of all 50 states.
    eco_code_list = []
    with arcpy.da.SearchCursor(eco, code_field) as cursor:
        for row in cursor:
            if not row[0] in exclude_list:
                na = row[0]
                yo = row[1]
                eco_code_list.append(na)
                #print("%s added to eco_code_list as %s\n"%(yo, na))
            else:
                da = row[0]
                #print("%s is a not inside of the studied area"%(da))
    eco_code_list.sort()
    print("This is the full list of eco codes that will be used to tabulate intersect with fire occurrence data: \n %s"%(eco_code_list))
    lower_48_list_HI = [x for x in eco_code_list if not x in ak_list]# or ak_list.remove(x)]
    print("This is the list of ecoregions     without ecoregions in Alaska")
    print(lower_48_list_HI)
    print("Double check with the AK list")
    print(ak_list)
    for item in lower_48_list_HI:
        if item in ak_list:
            print("%s in AK_List....Filtering failed"%(item))
        else:
            print("%s is in the us but not in AK"%(item))
    lower_48_list = [x for x in lower_48_list_HI if not x in hi_list]# or hi_list.remove(x)]
    print("This is the list of ecoregions to be processed in the lower 48:")
    print(lower_48_list)
    print("Double check with the HI list")
    print(hi_list)
    for item in lower_48_list:
        if item in hi_list:
            print("%s in HI_List......Filtering failed"%(item))
        else:
            print("%s is in the US but not in AK or HI"%(item))
    ## Lists to select ecoregions in AK, HI and the lower 48 are:
    ## ----------> ak_list
    ## ----------> hi_list
    ## ----------> lower_48_list
    ## These will be used to select each ecoregion one by one and add it to a collective selection comprised of all items
    ## from each list for each of the 3 lists. This will be used to create new feature classes for the sub-regions so they 
    ## will have matching projections with the Ecoregion_MFRI rasters (different Albers EA for AK, HI, and lower 48).
    ##
    ## Use "CLEAR_SELECTION" before each run to clear previously selected areas from the ecoregion feature class.
    process_out = 'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb'
    selection_lists = ["ak_list", "hi_list", "lower_48_list"]
    AK_ECO = 'AK_Ecoregions'
    HI_ECO = 'HI_Ecoregions'
    US_ECO = 'US_Ecoregions'
    AK_ECO_path = os.path.join(process_out, AK_ECO)
    HI_ECO_path = os.path.join(process_out, HI_ECO)
    US_ECO_path = os.path.join(process_out, US_ECO) 
    arcpy.SelectLayerByAttribute_management(eco, "CLEAR_SELECTION")
    print("Clearing selection...")
## Producing fc with all ecoregions in AK    
    for item in ak_list:
        print("This Ecoregion is in AK")
        print("%s selected successfully from %s"%(item, eco))
        length = str(len(ak_list))
        position = str(ak_list.index(item) + 1)        
        if ak_list.index(item) < len(ak_list) - 1:
            print("%s of %s selected\n"%(position, length))
        else:
            print("%s of %s selected\n--\n--\n--\n-- Reached end of selection\n"%(position, length))
            print("Copying selected features to %s"%(AK_ECO_path))            
            AK_where = "ECO_CODE in ('" + '\',\''.join(ak_list) + "')"  
            arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(ak_prj)
            arcpy.env.parallelProcessingFactor = "100%"            
            sel_eco = arcpy.SelectLayerByAttribute_management(eco, "NEW_SELECTION", AK_where)
            arcpy.CopyFeatures_management(sel_eco, AK_ECO_path)
            print("%s created\n"%(AK_ECO))
    arcpy.SelectLayerByAttribute_management(eco, "CLEAR_SELECTION")
    print("\nClearing selection...")
## Producing fc with all ecoregions in HI 
    for item in hi_list:
        print("This Ecoregion is in HI")
        print("%s selected successfully from %s"%(item, eco))
        length = str(len(hi_list))
        position = str(hi_list.index(item) + 1)
        if hi_list.index(item) < len(hi_list) - 1:
            print("%s of %s selected\n"%(position, length))
        else:
            print("%s of %s selected\n--\n--\n--\n-- Reached end of selection\n"%(position, length))
            print("Copying selected features to %s"%(HI_ECO_path))
            HI_where = "ECO_CODE in ('" + '\',\''.join(hi_list) + "')"             
            arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(hi_prj)            
            arcpy.env.parallelProcessingFactor = "100%"            
            sel_eco = arcpy.SelectLayerByAttribute_management(eco, "NEW_SELECTION", HI_where)
            arcpy.CopyFeatures_management(sel_eco, HI_ECO_path)                       
            print("%s created\n"%(HI_ECO))
    arcpy.SelectLayerByAttribute_management(eco, "CLEAR_SELECTION")
    print("\nClearing selection...")
## Producing fc with all ecoregions in lower 48
    for item in lower_48_list:  
        print("This Ecoregion is in the US, but AK or HI")
        print("%s selected successfully from %s"%(item, eco))
        length = str(len(lower_48_list))
        position = str(lower_48_list.index(item) + 1)        
        if lower_48_list.index(item) < len(lower_48_list) - 1:
            print("%s of %s selected\n"%(position, length))
        else:
            print("%s of %s selected\n--\n--\n--\n-- Reached end of selection\n"%(position, length))
            print("Copying selected features to %s"%(US_ECO_path))            
            US_where = "ECO_CODE in ('" + '\',\''.join(lower_48_list) + "')"            
            arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(us_prj)
            arcpy.env.parallelProcessingFactor = "100%"             
            sel_eco = arcpy.SelectLayerByAttribute_management(eco, "NEW_SELECTION", US_where)            
            arcpy.CopyFeatures_management(sel_eco, US_ECO_path)
            print("%s created\n"%(US_ECO))
    print("%s, %s, and %s now located in Outputs.gdb"%(AK_ECO, HI_ECO, US_ECO))
## From here all ecoregions in AK, HI, or the Lower 40 (US) are projected in different versions of the Albers
## EA Coordinate system. Now the the selecting features are in the same projection as the wildfires so a 
## tabulate intersect can be preformed to determine the amount of fire by ecoregion. This is a replication of the 
## Ecoregion Fire Occurrence analysis completed in Fall 2019, but this method is faster.
##    
    ## Ecoregoins inputs = AK_Ecoregions, HI_Ecoregions, US_Ecoregions <----Can use AK/HI/US_ECO_path variables
    ## for pathname
    ## Fire Occurrence inputs = F_O_AK_Prj, F_O_HI_Prj, F_O_US_Prj <----All in Fire_Occ.gdb
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb"
    arcpy.env.parallelProcessingFactor = "100%"   
    zone_field = "ECO_CODE"
    sum_field = "FIRE_SIZE"
    F_O_output_eco = ["FO__AK_By_Eco", "FO__HI_By_Eco", "FO__US_By_Eco"]
    for fc in arcpy.ListFeatureClasses():
        if fc == "F_O_AK_Prj":
            print("Tabulating intersect with %s and %s with HECTARES as output units"%(fc, AK_ECO_path))
            arcpy.TabulateIntersection_analysis(AK_ECO_path, zone_field, fc, F_O_output_eco[0], "", sum_field, "", "HECTARES")
            print("Tabulate intersect completed.\n%s created"%(F_O_output_eco[0]))
        elif fc == "F_O_HI_Prj":
            print("Tabulating intersect with %s and %s with HECTARES as output units"%(fc, HI_ECO_path))
            arcpy.TabulateIntersection_analysis(HI_ECO_path, zone_field, fc, F_O_output_eco[1], "", sum_field, "", "HECTARES")
            print("Tabulate intersect completed.\n%s created"%(F_O_output_eco[1]))            
        elif fc == "F_O_US_Prj":
            print("Tabulating intersect with %s and %s with HECTARES as output units"%(fc, US_ECO_path))
            arcpy.TabulateIntersection_analysis(US_ECO_path, zone_field, fc, F_O_output_eco[2], "", sum_field, "", "HECTARES")
            print("Tabulate intersect completed.\n%s created"%(F_O_output_eco[2]))            
        else:
            print("%s is not a target"%(fc))
##
##-----------------Repeat the same geoprocessing workflow but for the 50 states-------------------
## USA has already been assigned to the feature class as a variable containing all of the 50 states and territories.
## Use a list to filter out the areas that are territories and not states.
    terr_list = ["United States Virgin Islands", "Puerto Rico", "Guam", "District of Columbia", "Commonwealth of the Northern Mariana Islands", "American Samoa"] 
    USA_Fields = ["STUSPS", "NAME"]
    AK_state_list = ['AK']
    HI_state_list = ['HI']
    USA_dict = {}
    USA_abb_list = []
## Add items for each row to USA_abb_list and to USA_dict.    
    with arcpy.da.SearchCursor(USA, USA_Fields) as cursor:
        for row in cursor:
            if not row[1] in terr_list:
                abb = str(row[0])
                name = str(row[1])
                USA_abb_list.append(row[0])
                USA_dict.update({abb: name})
                print("%s : %s added to USA_dict as Key : Value pair"%(abb, name))
            else:
                print("%s is in the territory list, item not selected."%(row[1]))
    print("This is the full dictionary of items that will be selected from the USA feature class for analysis:")
    print(USA_dict)
    sorted_USA_abb = sorted(USA_abb_list)
## Use sorted_USA_abb as the list of 48 states to select the Lower 48 and copy features    
    sorted_USA_abb.remove('AK')
    sorted_USA_abb.remove('HI')
    print("Removed AK and HI from the sorted USA_abb list to create a list of 48 states:")
    print(sorted_USA_abb)
    sorted_USA = sorted(USA_dict)
    print(sorted_USA)
## Create file path variables to use later.    
    AK_State_out = 'AK_State'
    HI_State_out = 'HI_State'
    US_48_out = 'Lower_48_States'
    AK_State_path = os.path.join(process_out, AK_State_out)
    HI_State_path = os.path.join(process_out, HI_State_out)
    US_48_states_path = os.path.join(process_out, US_48_out) 
## Clear any previous selection for the USA feature class to eliminate errors
    arcpy.SelectLayerByAttribute_management(USA, "CLEAR_SELECTION")
    print("Clearing any previous selection...")
##
## Producing fc for the state of Alaska -------------------
    print("Producing FC for the state of Alaska")
    print("Copying selected features to %s"%(AK_State_path))            
    AK_where = "STUSPS in ('" + '\',\''.join(AK_state_list) + "')" 
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(ak_prj)
    arcpy.env.parallelProcessingFactor = "100%"            
    sel_state = arcpy.SelectLayerByAttribute_management(USA, "NEW_SELECTION", AK_where)
    arcpy.CopyFeatures_management(sel_state, AK_State_path)
    print("%s created\n"%(AK_State_out))
    arcpy.SelectLayerByAttribute_management(USA, "CLEAR_SELECTION")
    print("\nClearing selection...")
##
## Producing fc with all ecoregions in HI ------------------
    print("Producing FC for the state of Hawaii")
    print("Copying selected features to %s"%(HI_State_path))
    HI_where = "STUSPS in ('" + '\',\''.join(HI_state_list) + "')"          
    arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(hi_prj)            
    arcpy.env.parallelProcessingFactor = "100%"            
    sel_state = arcpy.SelectLayerByAttribute_management(USA, "NEW_SELECTION", HI_where)
    arcpy.CopyFeatures_management(sel_state, HI_State_path)                       
    print("%s created\n"%(HI_State_out))
    arcpy.SelectLayerByAttribute_management(USA, "CLEAR_SELECTION")
    print("\nClearing selection...")
##
## Producing fc with all ecoregions in lower 48 --------------
    for item in sorted_USA_abb:  
        print("This state is in the US, but AK or HI")
        print("%s selected successfully from %s"%(item, USA))
        length = str(len(sorted_USA_abb))
        position = str(sorted_USA_abb.index(item) + 1)        
        if sorted_USA_abb.index(item) < len(sorted_USA_abb) - 1:
            print("%s of %s selected\n"%(position, length))
        else:
            print("%s of %s selected\n--\n--\n--\n-- Reached end of selection\n"%(position, length))
            print("Copying selected features to %s"%(US_48_states_path))            
            US_where = "STUSPS in ('" + '\',\''.join(sorted_USA_abb) + "')"            
            arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(us_prj)
            arcpy.env.parallelProcessingFactor = "100%"             
            sel_state = arcpy.SelectLayerByAttribute_management(USA, "NEW_SELECTION", US_where)            
            arcpy.CopyFeatures_management(sel_state, US_48_states_path)
            print("%s created\n"%(US_48_out))
    print("%s, %s, and %s now located in Outputs.gdb"%(AK_State_out, HI_State_out, US_48_out))
##
##---------------------------------------------------------------------------------------------------------------
## Now there are three feature classes created for AK, HI, and the Lower 48 states.
## They are going to now be used as input boundary features for tabulate intersect with the 3 fire occurrence
## feature classes to generate the area burned by state in 3 summary tables that will eventuallly be joined to 
## create a summary of 50 state fire occurrence.
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb"
    arcpy.env.parallelProcessingFactor = "100%"   
    zone_field = "NAME"
    sum_field = "FIRE_SIZE"
    F_O_output_state = ["FO__AK_By_State", "FO__HI_By_State", "FO__US_By_State"] ## NOTE: FO__ uses 2 underscores. 
    ## When I tried to delete old outputs which used a single underscore (ex: FO_AK_By_State) pro would not lift the
    ## schema lock on the tables for some reason. Even after restarting. Probably a bug. Hence the double underscore after FO. 
    for fc in arcpy.ListFeatureClasses():
        if fc == "F_O_AK_Prj":
            print("Tabulating intersect with %s and %s with HECTARES as output units"%(fc, AK_State_path))
            arcpy.TabulateIntersection_analysis(AK_State_path, zone_field, fc, F_O_output_state[0], "", sum_field, "", "HECTARES")
            print("Tabulate intersect completed.\n%s created"%(F_O_output_state[0]))
        elif fc == "F_O_HI_Prj":
            print("Tabulating intersect with %s and %s with HECTARES as output units"%(fc, HI_State_path))
            arcpy.TabulateIntersection_analysis(HI_State_path, zone_field, fc, F_O_output_state[1], "", sum_field, "", "HECTARES")
            print("Tabulate intersect completed.\n%s created"%(F_O_output_state[1]))            
        elif fc == "F_O_US_Prj":
            print("Tabulating intersect with %s and %s with HECTARES as output units"%(fc, US_48_states_path))
            arcpy.TabulateIntersection_analysis(US_48_states_path, zone_field, fc, F_O_output_state[2], "", sum_field, "", "HECTARES")
            print("Tabulate intersect completed.\n%s created"%(F_O_output_state[2]))            
        else:
            print("%s is not a target"%(fc))
##--------------------------------------------------------------
## So far this script has produced Fire occurrence tabulate intersect summary tables for ecoregions in AK, HI and the Lower 48
## and fire occurrence tabulate intersect summary tables for AK, HI and the Lower 48 states. 6 Tables in total.
## THe next sequence of this script will load those tables into multiple pandas data frames and combine them as one dataframe and 
## write the frame to a .csv. 
##
## After .csv's are created for the states and ecoregions, the MFRI estimates for each corresponding row will be joined to the .csv.
## From that point the table will include the estimated area burned for each ecoregion/state (low and high estimates) and the actual area 
## burned. This will allow for the identification of areas wehre there are fire defecits and surpluses. 
##
##Eventually the .csv will be joined to the original feature class that the bounding feature originated from.
## Meaning the summary table for states will be joined back with the 50 states feature class and the summary table for the ecoregions
## will be joined back with the ecoregions feature class. 

## Looks like the tables need to be saved as csv so they can be loaded into a dataframe without the use of external python packages.
    print("Making output directory for summary tables")
    os.mkdir('B:\\GIS_Projects\\SP_Wildfire\\Reprocessing\\Workspace\\Summary_Tables')
    print("Summary_Tables Created in Workspace folder.\nThis file will house all of the csv summary table outputs for both ecoregoin and state F_O analysis")
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb"
    out_dir = 'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables'
    os.chdir(r'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables')
    s_tbl_list = arcpy.ListTables()
    for table in s_tbl_list:
        print(table)
        tbl_nm = str(table)
        out_csv = "".join((table, ".csv"))
        full_out_path = os.path.join(out_dir, out_csv)
        arcpy.TableToTable_conversion(table, out_dir, out_csv)
        print("%s created in %s"%(out_csv, out_dir))
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Summary_Tables"
    state_suff = "State"
    state_table = []
    eco_suff = "Eco"
    eco_table = []
    for table in arcpy.ListTables():
        print(table)
        str_table = str(table)
        if "State" in table:
            print("%s is a state table, added to state table list"%(table))
            st_table = str(table)
            state_table.append(str_table)
        elif "Eco" in table:
            print("%s is an ecoregion table, added to ecoregoin table list"%(table))
            st_table = str(table)
            eco_table.append(str_table)
    print("These are the states summary tables:\n%s\n"%(state_table))
    print("These are the ecoregion summary tables:\n%s\n"%(eco_table))
## Load all of the summary tables into pandas dataframes for easy handling. The goal is to append the tables to create
## one summary table for states and one for ecoregions. The reason they are all split up is because they used appropriate 
## projections. It seems like a hassle but it is worth it!    
    for table in state_table:
        if "AK" in table:
            df_AK_state = pd.read_csv(table)
            print("This is the AK state data frame:")
            print(df_AK_state)
        elif "HI" in table:
            df_HI_state = pd.read_csv(table)
            print("This is the HI state data frame:")
            print(df_HI_state)
        elif "US" in table:
            df_US_states = pd.read_csv(table)
            print("This is the lower 48 states data frame:")
            print(df_US_states)
        else:
            print("%s rejected for some reason..."%(table))
    state_frames = [df_AK_state, df_HI_state, df_US_states]
    df_master_state = pd.concat(state_frames)
    del df_master_state['OBJECTID']
    print(df_master_state)
    print("This is the master summary table for fire occurrence by state:\n")
    print(df_master_state)
    for table in eco_table:
        if "AK" in table:
            df_AK_eco = pd.read_csv(table)
            print("This is the AK Ecoregion data frame:")
            print(df_AK_eco)
        elif "HI" in table:
            df_HI_eco = pd.read_csv(table)
            print("This is the HI Ecoregoin data frame:")
            print(df_HI_eco)
        elif "US" in table:
            df_US_eco = pd.read_csv(table)
            print("This is the Lower 48 Ecoregions data frame:")
            print(df_US_eco)
        else:
            print("%s was rejected for some reason..."%(table))
    eco_frames = [df_AK_eco, df_HI_eco, df_US_eco]
    df_master_eco = pd.concat(eco_frames)
    print("This is the master summary table for fire occurrence by ecoregion:\n")
    print(df_master_eco)
    del df_master_eco['OBJECTID']
    print(df_master_eco)
    eco_col_list = ["ECO_CODE", "FIRE_SIZE", "AREA", "PERCENTAGE"]
    state_col_list = ["NAME", "FIRE_SIZE", "AREA", "PERCENTAGE"]
    df_master_eco.to_csv('Ecoregion_F_O.csv', columns = eco_col_list)
    df_master_state.to_csv('States_F_O.csv', columns = state_col_list)
## Now there are two csv files that summarize the fire occurrence for Ecoregions and States in 
## the Summary_tables folder inside the workspace directory. These files will be used to join to 
## the MFRI summary tables previously created. Go to Summary_Statistics.py to continue analysis.

# #####-----Continue processing to eventually be able to produce rasters with fire quantity as cell value---------
# ## Perform a union to make areas of overlap while transfering ONLY_FID to output.
    ak_union_out = 'F_O_AK_Union'
    hi_union_out = 'F_O_HI_Union'
    us_union_out = 'F_O_US_Union'
    union_list = []
    union_list.append(ak_union_out)
    union_list.append(hi_union_out)
    union_list.append(us_union_out)
    print("List of union feature classes:\n%s"%(union_list))
    print("Conducting Union Analysis on %s"%(ak_prj_out))
    arcpy.Union_analysis(ak_prj_out, ak_union_out, "ONLY_FID", "", "GAPS")
    print("%s created"%(ak_union_out))
    print("Conducting Union Analysis on %s"%(hi_prj_out))
    arcpy.Union_analysis(hi_prj_out, hi_union_out, "ONLY_FID", "", "GAPS")
    print("%s created"%(hi_union_out))
    print("Conducting Union Analysis on %s"%(us_out))
    arcpy.Union_analysis(us_out, us_union_out, "ONLY_FID", "", "GAPS")
    print("%s created"%(us_union_out))
##-----------------Add geometry attributes to identify common areas--------
    updated_fc_list = arcpy.ListFeatureClasses()
    centroid_list = [["Centroid_X", "CENTROID_X"], ["Centroid_Y", "CENTROID_Y"]]
    alt_centroid_list = []
    for fc in updated_fc_list:
        if fc in union_list:
            print("Calculating Centroid X and Centroid Y for %s"%(fc))
            arcpy.AddGeometryAttributes_management(fc, "CENTROID")
            arcpy.AddGeometryAttributes_management(fc, "CENTROID")
            arcpy.CalculateGeometryAttributes_management(fc, centroid_list)
            print("Centroid X and Centroid Y Fields added and calculated for %s"%(fc))
        else:
            print("%s not in %s"%(fc, updated_fc_list))
# ##----------------------Pairwise dissolve--------------------------
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    dissolve_output = ['F_O_AK_Dissolve', 'F_O_HI_Dissolve', 'F_O_US_Dissolve']
    dissolve_fields = ["CENTROID_X", "CENTROID_Y"]
    for fc in arcpy.ListFeatureClasses():
        print(fc)
        if fc == union_list[0]: ## Alaska
            print("Starting pairwise dissolve on %s using CENTROID_X and CENTROID_Y as dissolve fields"%(fc))
            arcpy.PairwiseDissolve_analysis(fc, dissolve_output[0], dissolve_fields, [["FID_F_O_AK_Prj", "COUNT"]], "MULTI_PART")
            print("Pairwise dissolve completed for %s"%(fc))
        elif fc == union_list[1]: ## Hawaii
            print("Starting pairwise dissolve on %s using CENTROID_X and CENTROID_Y as dissolve fields"%(fc))
            arcpy.PairwiseDissolve_analysis(fc, dissolve_output[1], dissolve_fields, [["FID_F_O_HI_Prj", "COUNT"]], "MULTI_PART")
            print("Pairwise dissolve completed for %s"%(fc))
        elif fc == union_list[2]: ## Lower 48
            print("Starting pairwise dissolve on %s using CENTROID_X and CENTROID_Y as dissolve fields"%(fc))
            arcpy.PairwiseDissolve_analysis(fc, dissolve_output[2], dissolve_fields, [["FID_F_O_US_Prj", "COUNT"]], "MULTI_PART")
            print("Pairwise dissolve completed for %s"%(fc))
        else:
            print("%s is not in union_list"%(fc))
    print("All Pairwise dissolve operations completed.")
##---------------------------Rasterize the dissolve outputs----------------------------------
    ## Start with Alaska. Set snap raster to alaska MFRI
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb"
    fire_quantity_field = ["COUNT_FID_F_O_AK_Prj", "COUNT_FID_F_O_HI_Prj", "COUNT_FID_F_O_US_Prj"]
    output_raster = ["F_O_AK_Raster", "F_O_HI_Raster", "F_O_US_Raster"]    
    snap_raster = ["B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/ak_mfri_masked", 
                   "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/hi_mfri_masked",
                   "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/us_mfri_masked"]
    #cell_size = ["E:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Inputs.gdb/ak_120mfri",
                 #"E:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Inputs.gdb/hi_120mfri",
                 #"E:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Inputs.gdb/us_120mfri"]
    for fc in arcpy.ListFeatureClasses():
        print(fc)
    ## AK Dissolve    
        if fc == dissolve_output[0]:
            print("Converting %s to raster"%(fc))
            arcpy.env.snapRaster = snap_raster[0]
            arcpy.PolygonToRaster_conversion(fc, fire_quantity_field[0], output_raster[0], "", "", snap_raster[0])
            print("%s converted to raster: %s\n"%(fc, output_raster[0]))
    ## HI Dissolve    
        elif fc == dissolve_output[1]:
            print("Converting %s to raster"%(fc))
            arcpy.env.snapRaster = snap_raster[1]
            arcpy.PolygonToRaster_conversion(fc, fire_quantity_field[1], output_raster[1], "", "", snap_raster[1])
            print("%s converted to raster: %s\n"%(fc, output_raster[1]))
    ## US Dissolve    
        elif fc == dissolve_output[2]:
            print("Converting %s to raster"%(fc))
            arcpy.env.snapRaster = snap_raster[2]
            arcpy.PolygonToRaster_conversion(fc, fire_quantity_field[2], output_raster[2], "", "", snap_raster[2])
            print("%s converted to raster: %s\n"%(fc, output_raster[2]))
        else:
            print("%s not of concern...\n"%(fc))
    F_O_raster_list = arcpy.ListRasters("*", "ALL")
    for raster in F_O_raster_list:
        print("%s is now in Fire_occ.gdb"%(raster))
##
##--------------------Use ecoregions and states fc to extract the F_O_AK/HI/US_Rasters by mask-----------------
## Outpath is already defined as being the workspace directory which houses all of the other geodatabases
##
## Create 2 .gdbs. They will house the fire occurrence rasters broken up by ecoregion or state
    States_FO_gdb_name = "States_FO.gdb"
    Ecoregions_FO_gdb_name = "Ecoregions_FO.gdb"
## These will be used to join to the output extracted rasters for file paths    
    states_fo_gdb_path = os.path.join(outpath, States_FO_gdb_name)
    eco_fo_gdb_path = os.path.join(outpath, Ecoregions_FO_gdb_name)
    arcpy.CreateFileGDB_management(outpath, States_FO_gdb_name)
    print("%s created"%(States_FO_gdb_name))
    arcpy.CreateFileGDB_management(outpath, Ecoregions_FO_gdb_name)
    print("%s created"%(Ecoregions_FO_gdb_name))
## Create lists of the ecoregions and states bounding fcs to use in extract by mask analysis
    FO_raster = ["B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb/F_O_AK_Raster",
                 "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb/F_O_HI_Raster",
                 "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Fire_Occ.gdb/F_O_US_Raster"]
## Create lists for snap rasters to use so the pixels line up. These features will be the MFRI rasters
## that already exist.    
## State snap rasters    
    state_snap = []
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb"
    s_mfri_gdb = 'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb'
    for raster in arcpy.ListRasters("*", "All"):
        print("Adding %s to state_snap list"%(raster))
        item = os.path.join(s_mfri_gdb, raster)
        state_snap.append(item)
    print("Here is the list of state mfri snap rasters:\n")
    for item in state_snap:
        print(item)
## List for ecoregion snap rasters    
    eco_snap = []
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb"
    e_mfri_gdb = 'B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb'
    for raster in arcpy.ListRasters("*", "All"):
        print("Adding %s to eco_snap list"%(raster))
        item = os.path.join(e_mfri_gdb, raster)
        eco_snap.append(item)
    print("Here is the list of ecoregion mfri snap rasters:\n")
    for item in eco_snap:
        print(item)
## Switch workspace    
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
## Lists of bounding feature classes to use to select areas to extract by mask    
    state_ext_list = [] ## items: AK_State, HI_State, Lower_48_States
    eco_ext_list = []  ## items: AK_Ecoregions, HI_Ecoregions, US_Ecoregions
    for fc in arcpy.ListFeatureClasses():
        fc_name = str(fc)
        eco_match = re.search("Ecoregions", fc_name)
        state_match = re.search("State", fc_name)
        if eco_match:
            eco_ext_list.append(fc)
            print("%s added to eco_ext_list"%(fc))
        elif state_match:
            state_ext_list.append(fc)
            print("%s added to state_ext_list"%(fc))
        else:
            print("%s not a target"%(fc))
## Go through the contents of state_ext_list and extract each state from the fire occurrence raster to produce 
## fire occurrence rasters for each individual state.   
    for item in state_ext_list:
        if item == "AK_State":
            print("Processing state: %s"%(item))
            outname = "USA_AK_F_O"
            outpath = os.path.join(states_fo_gdb_path, outname)
            arcpy.env.snapRaster = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb/USA_AK_MFRI"
            print("Extracting by mask...")
            outExtractByMask = ExtractByMask(FO_raster[0], item)
            outExtractByMask.save(outpath)
            print("%s created.\n"%(outname))
        elif item == "HI_State":
            print("Processing state: %s"%(item))
            outname = "USA_HI_F_O"
            outpath = os.path.join(states_fo_gdb_path, outname)
            arcpy.env.snapRaster = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb/USA_HI_MFRI"
            print("Extracting by mask...")
            outExtractByMask = ExtractByMask(FO_raster[1], item)
            outExtractByMask.save(outpath)
            print("%s created.\n"%(outname))
        elif item == "Lower_48_States":
            print("%s requires the use of a search cursor to individually select areas and extract..."%(item))
            state_abb_list = []
            cur_fields = ["STUSPS"]
            with arcpy.da.SearchCursor(item, cur_fields) as cursor:
                for row in cursor:
                    abb = str(row[0])
                    state_abb_list.append(abb)
                    print("%s added to abb list"%(abb))
            for state in state_abb_list:
                arcpy.SelectLayerByAttribute_management(item, "CLEAR_SELECTION")
                name_where = ''' "STUSPS" = '{0}' '''.format(state)
                outname = "USA_%s_F_O"%(state)
                outpath = os.path.join(states_fo_gdb_path, outname)
                snap_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_MFRI.gdb/USA_%s_MFRI"%(state)
                sel_state = arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", name_where)
                print("%s selected from %s"%(state, item))
                arcpy.env.snapRaster = snap_ras
                print("Extracting %s from %s"%(state, item))
                outExtractByMask = ExtractByMask(FO_raster[2], sel_state)
                outExtractByMask.save(outpath)
                print("%s created.\n"%(outname))
        else:
            print("%s did not meet requirements.."%(item))

     print("Finished processing the state boundaries.\nMoving on to Ecoregions...\n")
## Do the same extraction for the ecoregions.    
    for item in eco_ext_list:
        if item == "AK_Ecoregions":
            print("Processing ecoregions in AK:\n")
            ak_eco_list = []
            cur_fields = ["ECO_CODE"]
            with arcpy.da.SearchCursor(item, cur_fields) as cursor:
                for row in cursor:
                    code = str(row[0])
                    ak_eco_list.append(code)
                    print("%s added to AK ecoregion list"%(code))
            for eco_code in ak_eco_list:
                arcpy.SelectLayerByAttribute_management(item, "CLEAR_SELECTION")
                name_where = ''' "ECO_CODE" = '{0}' '''.format(eco_code)
                outname = "%s_F_O_AK"%(eco_code)
                outpath = os.path.join(eco_fo_gdb_path, outname)
                snap_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb/%s_MFRI_AK"%(eco_code)
                sel_eco = arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", name_where)
                print("%s selected from %s"%(eco_code, item))
                arcpy.env.snapRaster = snap_ras
                print("Extracting %s from %s"%(eco_code, item))
                outExtractByMask = ExtractByMask(FO_raster[0], sel_eco)
                outExtractByMask.save(outpath)
                print("%s created.\n"%(outname))
        elif item == "HI_Ecoregions":
            print("Processing ecoregions in HI:\n")
            hi_eco_list = []
            cur_fields = ["ECO_CODE"]
            with arcpy.da.SearchCursor(item, cur_fields) as cursor:
                for row in cursor:
                    code = str(row[0])
                    hi_eco_list.append(code)
                    print("%s added to HI ecoregion list"%(code))
            for eco_code in hi_eco_list:
                arcpy.SelectLayerByAttribute_management(item, "CLEAR_SELECTION")
                name_where = ''' "ECO_CODE" = '{0}' '''.format(eco_code)
                outname = "%s_F_O_HI"%(eco_code)
                outpath = os.path.join(eco_fo_gdb_path, outname)
                snap_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb/%s_MFRI_HI"%(eco_code)
                sel_eco = arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", name_where)
                print("%s selected from %s"%(eco_code, item))
                arcpy.env.snapRaster = snap_ras
                print("Extracting %s from %s"%(eco_code, item))
                outExtractByMask = ExtractByMask(FO_raster[1], sel_eco)
                outExtractByMask.save(outpath)
                print("%s created.\n"%(outname))
        elif item == "US_Ecoregions":
            print("Processing ecoregions in the lower 48:\n")
            us_eco_list = []
            cur_fields = ["ECO_CODE"]
            with arcpy.da.SearchCursor(item, cur_fields) as cursor:
                for row in cursor:
                    code = str(row[0])
                    us_eco_list.append(code)
                    print("%s added to US ecoregion list"%(code))
            for eco_code in us_eco_list:
                arcpy.SelectLayerByAttribute_management(item, "CLEAR_SELECTION")
                name_where = ''' "ECO_CODE" = '{0}' '''.format(eco_code)
                outname = "%s_F_O_US"%(eco_code)
                outpath = os.path.join(eco_fo_gdb_path, outname)
                snap_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_MFRI.gdb/%s_MFRI_US"%(eco_code)
                sel_eco = arcpy.SelectLayerByAttribute_management(item, "NEW_SELECTION", name_where)
                print("%s selected from %s"%(eco_code, item))
                arcpy.env.snapRaster = snap_ras
                print("Extracting %s from %s"%(eco_code, item))
                outExtractByMask = ExtractByMask(FO_raster[2], sel_eco)
                outExtractByMask.save(outpath)
                print("%s created.\n"%(outname))
        else:
            print("%s did not meet requirements"%(item))
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/States_FO.gdb"
    print("\nThese rasters are now in States_FO.gdb:")
    USA_fo_ras_list = arcpy.ListRasters("*", "All")
    for item in USA_fo_ras_list:
        print(item)
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Ecoregions_FO.gdb"
    print("\nThese rasters are now in Ecoregions_FO.gdb:")
    ECO_fo_ras_list = arcpy.ListRasters("*", "All")
    for item in ECO_fo_ras_list:
        print(item)

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
    print(pymsg + "\n")
    print(msgs)
# End deployment of verbose error catcher......
print("\n\n--> Finished Script... ")
#end_time = datetime.now()
#print("Duration: {}".format(end_time - start_time))
