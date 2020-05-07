## Script 1 of 3 for Ecoregion and State fire deficit calculations
## Developed by Zack Quarterman, Western Washington University (2020)

## This script masks the input MFRI rasters using the EVT rasters to set null areas that are agricultural,
## developed, or water. The masked MFRI rasters are used as rolled dough for individual ecoregions and states to be cut from (really extracted)
## Individual rasters are created for each state and each ecoregion within the study area.


## This script will create:
##  Geodatabases:
##      Outputs.gdb
##          us_mfri_masked
##          hi_mfri_masked
##          ak_mfri_masked     
##
##      Ecoregions_MFRI.gdb
##          "NA0403_MFRI_US" Individual rasters for each ecoregion. Prefix is the "ECO_CODE" and the suffix US, AK, or HI indicate what projection
##
##      States_MFRI.gdb
##          "USA_CO_MFRI" Individual rasters for all 50 states. This example is Colorado. AK and HI will use different projections.
##

try:
  
    import arcpy
    from arcpy import env
    from arcpy.sa import *
    import os
    import sys
    # Change workspace and folder paths accordingly to run this script. 

    ## -----------Masking MFRI rasters with existing vegetation cover----------------------------
    ## Call on rasters inside of a geodatabase populated with the MFRI and EVT Landfire datasets for AK, HI, & Lower 48 states.
    ## So inside of the existing "Inputs.gdb":
    ## ak_120mfri, ak_140evt, hi_120mfri, hi_140evt, us_120mfri, us_120evt

    print("Creating file gdb for the outputs created by this script")
    gdbpath = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    gdbname = "Outputs.gdb"
    arcpy.CreateFileGDB_management(gdbpath, gdbname)
    print("%s created in %s"%(gdbname, gdbpath))
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Inputs.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    ## Processing lower 48
    print("Processing the lower 48...hang tight...")
    MFRI = "us_120mfri"
    EVC = "us_140evt"
    us_out_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/us_mfri_masked"
    us_where = """"EVT_LF" = 'Agriculture' OR "EVT_LF" = 'Developed'"""
    us_set_null = SetNull(EVC, MFRI, us_where)
    us_set_null.save(us_out_ras)
    print("us_mfri_masked created, located: %s"%(us_out_ras))
    print("Processing Hawaii...hang tight...")
    ## Processing Hawaii
    hiMFRI = "hi_120mfri"
    hiEVC = "hi_140evt"
    hi_out_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/hi_mfri_masked"
    hi_set_null = SetNull(hiEVC, hiMFRI, us_where)
    hi_set_null.save(hi_out_ras)
    print("hi_mfri_masked created, located: %s"%(hi_out_ras))
    print("Processing Alaska...hang tight...")
    ## Processing Alaska
    akMFRI = "ak_120mfri"
    akEVC = "ak_140evt"
    ak_out_ras = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb/ak_mfri_masked"
    ak_set_null = SetNull(akEVC, akMFRI, us_where)
    ak_set_null.save(ak_out_ras)
    print("ak_mfri_masked created, located: %s"%(ak_out_ras))
    print("Masked MFRI rasters created")

    ##------------------------------------------------------------------------------------------------

    ## Using search cursor for each of the orignial mfri datasets to generate a dictionary of values and corrosponding timeframes
    ## Still working out of the Inputs.gdb...
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Inputs.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    us_dict = {f[0]:f[1] for f in arcpy.da.SearchCursor(MFRI,["VALUE","LABEL"])}
    print(us_dict)
    us_dict[1] = "1-5 Years"
    print(us_dict)
    hi_dict = {f[0]:f[1] for f in arcpy.da.SearchCursor(hiMFRI,["VALUE","LABEL"])}
    print(hi_dict) 
    ak_dict = {f[0]:f[1] for f in arcpy.da.SearchCursor(akMFRI,["VALUE","LABEL"])}
    print(ak_dict)
    #-------------------------------------------------------------------------------------------------
    # Adding field to populate with MFRI range to each raster
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Outputs.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    for ras in arcpy.ListRasters():
    arcpy.AddField_management(ras, "MFRI", "TEXT")
    print("MFRI field added to %s"%(ras))
    fields = ["Value","MFRI"]
    if ras == 'us_mfri_masked':
        with arcpy.da.UpdateCursor(ras, fields) as I:
            for row in I:
                val = row[0]
                if val in us_dict:
                    row[1] = us_dict[val]
                    I.updateRow(row)
                    print("Updated row")
                else:()
    elif ras =='hi_mfri_masked':
        with arcpy.da.UpdateCursor(ras, fields) as d:
            for row in d:
                val = row[0]
                if val in hi_dict:
                    row[1] = hi_dict[val]
                    d.updateRow(row)
                    print("Updated row")
                else:()
    elif ras =='ak_mfri_masked':
        with arcpy.da.UpdateCursor(ras, fields) as e:
            for row in e:
                val = row[0]
                if val in ak_dict:
                    row[1] = ak_dict[val]
                    e.updateRow(row)
                    print("Updated row")
                else:()
    else:
        print("This input is apparently not AK, HI or Lower48...")
    ##-------------------------------------------------------------------------------------------------
    ## Clip ak_mfri_masked, hi_mfri_masked, and us_mfri_masked to extent of USA_Generalized_Albers_EA_US
    ## for political state boundaries. Also clip to extent of each ecoregion in TNC_US_Ecoregions_Albers_EA_US

    ###-------------------------------------------------------------------------------------------------
    ## Alternate route for clipping the rasters.....
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    arcpy.env.parallelProcessingFactor = "100%"
    outpath = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace" 
    USA = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb/USA_Generalized_Albers_EA_US"
    eco = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb/TNC_US_Ecoregions_Albers_EA_US"
    eco_gdb_name = "Ecoregions_MFRI.gdb"
    usa_gdb_name = "States_MFRI.gdb"
    eco_path = os.path.join(outpath, eco_gdb_name)
    usa_path = os.path.join(outpath, usa_gdb_name)

    ## Creating gdb for eco outputs
    print("Creating geodatabase: %s"%(eco_gdb_name))
    arcpy.CreateFileGDB_management(outpath, eco_gdb_name)
    print("%s created \n"%(eco_gdb_name))
    ## Creating gdb for usa outputs
    print("Creating geodatabase: %s"%(usa_gdb_name))
    arcpy.CreateFileGDB_management(outpath, usa_gdb_name)
    print("%s created \n"%(usa_gdb_name))
    ## use ak_out_ras hi_out_ras us_out_ras as the raster inputs
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    ####--------------------------------------------------50 States MFRI Processing--------------------------------------------------------

    state_field = "NAME"
    state_list = []
## The terr_list contains all of the ares to exclude from the analysis (outside of the 50 states)
    terr_list = ["United States Virgin Islands", "Puerto Rico", "Guam", "District of Columbia", "Commonwealth of the Northern Mariana Islands", "American Samoa"]
    with arcpy.da.SearchCursor(USA, state_field) as cursor:
        for row in cursor:
            if not row[0] in terr_list:
                na = row[0]
                state_list.append(na)
                print("%s added to state_list"%(na))
            else:
                da = row[0]
                print("%s is a not a state"%(da))
    ## Alphabetize the list...
    state_list.sort()
    ## Create list of abbreviations to zip into dict
    abb = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
    print(state_list)
    print(abb)
    st_abb_dict = dict(zip(state_list, abb))
    print(st_abb_dict)
    ## Test the dictionary to get the state abbreviation to be used in naming the output mfri rasters
    for item in state_list:
        yas = st_abb_dict.get(item)
        print(yas)
    ## Now state_list is populated with all 50 states to use for extracting the mfri rasters by the state mask
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    for item in state_list:
        if not item == "Hawaii" and not item == "Alaska":  
            state = "'%s'"%(item)
            #name_where = ''' "[NAME] = '{0}'" '''.format(item)
            name_where = ''' "NAME" = '{0}' '''.format(item)            
            sel_state = arcpy.SelectLayerByAttribute_management(USA, "NEW_SELECTION", name_where)
            print("%s selected successfully from USA"%(item))
            abb_name = st_abb_dict.get(item)
            clp_nm = "USA_%s_MFRI"%(abb_name)
            usoutname = os.path.join(usa_path, clp_nm) 
            print("Clipping %s by selected state"%(us_out_ras))
            outExtractByMask = ExtractByMask(us_out_ras, sel_state)
            outExtractByMask.save(usoutname)      
            print("%s created in %s \n"%(clp_nm, usa_path))
        elif item == "Hawaii":
            state = "'%s'"%(item)
            #name_where = ''' "[NAME] = '{0}'" '''.format(item)            
            name_where = ''' "NAME" = '{0}' '''.format(item)
            sel_state = arcpy.SelectLayerByAttribute_management(USA, "NEW_SELECTION", name_where)
            print("%s selected successfully from USA"%(item))
            abb_name = st_abb_dict.get(item)
            clp_nm = "USA_%s_MFRI"%(abb_name)
            usoutname = os.path.join(usa_path, clp_nm) 
            print("Clipping %s by selected state"%(hi_out_ras))
            outExtractByMask = ExtractByMask(hi_out_ras, sel_state)
            outExtractByMask.save(usoutname)      
            print("%s created in %s \n"%(clp_nm, usa_path))
        elif item == "Alaska":
            state = "'%s'"%(item) 
            #name_where = ''' "[NAME] = '{0}'" '''.format(item)            
            name_where = ''' "NAME" = '{0}' '''.format(item)
            sel_state = arcpy.SelectLayerByAttribute_management(USA, "NEW_SELECTION", name_where)
            print("%s selected successfully from USA"%(item))
            abb_name = st_abb_dict.get(item)
            clp_nm = "USA_%s_MFRI"%(abb_name)
            usoutname = os.path.join(usa_path, clp_nm) 
            print("Clipping %s by selected state"%(ak_out_ras))
            outExtractByMask = ExtractByMask(ak_out_ras, sel_state)
            outExtractByMask.save(usoutname) 
            print("%s created in %s \n"%(clp_nm, usa_path))
        else:
            print("!!!!\n!\n!\n!\n! %s REJECTED....\n\n\n\n"%(item))
    ##-------------------------ECOREGION Processing-------------------------------------------------------------------------------------------------------------
    ## Now to incorporate the ecoregions. First create a list of codes to use as identifiers. Use a search cursor to populate the list to call on for output names
    ## Remember to create ecoregion list of areas that are only in Ak and HI to use for clipping their respective rasters
    exclude_list = ["NT1402", "OC0112", "OC0203", "OC0703", "NT0226", "NT0155", "NT0134", "NT1305", "OC0117"]
    exclude_list.sort()
    ak_list = ["NA1106", "NA1105", "NA1104", "NA1102", "NA0612", "NA0611", "NA0610", "NA0607", "NA0602", "NA0601", "NA0518", "NA0509"]
    ak_list.sort()
    hi_list = ["OC0106", "OC0202", "OC0701", "OC0702"]
    hi_list.sort()
    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace/Shared_Data.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    ## Load as many fields as necessary into the search cursor, if 2 are loaded a dictionary can be created to link link field values to desired names. 
    ## In this case the names were simply too long to use.
    code_field = ["ECO_CODE", "ECO_NAME"]
    eco_code_list = []
    with arcpy.da.SearchCursor(eco, code_field) as cursor:
        for row in cursor:
            if not row[0] in exclude_list:
                na = row[0]
                yo = row[1]
                eco_code_list.append(na)
                print("%s added to eco_code_list as %s\n"%(yo, na))
            else:
                da = row[0]
                print("%s is a not inside of the studied area"%(da))
    eco_code_list.sort()
    print("This is the full list of eco codes that the MFRI rasters will be extracted with: \n %s"%(eco_code_list))
    #skipped_list = ["OC0202", "OC0701", "OC0702"] # Use this list to troubleshoot if any codes generate an error with the tool.
    ## IF an error is thrown, then the ecoregion is outside the extent of the raster to be extracted. 
    ## Use the skipped_list to finish the processing
    #for item in skipped_list:
    for item in eco_code_list:
        if item in hi_list:
            print("This Ecoregion is in HI\n")
            name_where = ''' "ECO_CODE" = '{0}' '''.format(item)
            arcpy.env.parallelProcessingFactor = "100%"
            sel_eco = arcpy.SelectLayerByAttribute_management(eco, "NEW_SELECTION", name_where)
            print("%s selected successfully from %s"%(item, eco))
            clp_nm = "%s_MFRI_HI"%(item)
            usoutname = os.path.join(eco_path, clp_nm) 
            print("Clipping %s by selected %s ecoregion"%(hi_out_ras, item))
            arcpy.env.parallelProcessingFactor = "100%"
            outExtractByMask = ExtractByMask(hi_out_ras, sel_eco)
            arcpy.env.parallelProcessingFactor = "100%"
            outExtractByMask.save(usoutname)      
            print("%s created in %s \n\n"%(clp_nm, eco_path))      
        elif item in ak_list:
            print("This Ecoregion is in AK\n")
            name_where = ''' "ECO_CODE" = '{0}' '''.format(item)
            arcpy.env.parallelProcessingFactor = "100%"
            sel_eco = arcpy.SelectLayerByAttribute_management(eco, "NEW_SELECTION", name_where)
            print("%s selected successfully from %s"%(item, eco))
            clp_nm = "%s_MFRI_AK"%(item)
            usoutname = os.path.join(eco_path, clp_nm) 
            print("Clipping %s by selected %s ecoregion"%(ak_out_ras, item))
            arcpy.env.parallelProcessingFactor = "100%"
            outExtractByMask = ExtractByMask(ak_out_ras, sel_eco)
            arcpy.env.parallelProcessingFactor = "100%"
            outExtractByMask.save(usoutname)      
            print("%s created in %s \n\n"%(clp_nm, eco_path))     
        elif not item in hi_list and not item in ak_list:  
            print("This Ecoregion is in the US, but AK or HI\n")
            name_where = ''' "ECO_CODE" = '{0}' '''.format(item)
            arcpy.env.parallelProcessingFactor = "100%"
            sel_eco = arcpy.SelectLayerByAttribute_management(eco, "NEW_SELECTION", name_where)
            print("%s selected successfully from %s"%(item, eco))
            clp_nm = "%s_MFRI_US"%(item)
            usoutname = os.path.join(eco_path, clp_nm) 
            print("Clipping %s by selected %s ecoregion"%(us_out_ras, item))
            arcpy.env.parallelProcessingFactor = "100%"
            outExtractByMask = ExtractByMask(us_out_ras, sel_eco)
            arcpy.env.parallelProcessingFactor = "100%"
            outExtractByMask.save(usoutname)      
            print("%s created in %s \n\n"%(clp_nm, eco_path))
        else:
            print("\n\n\n\n\n\n\n %s NOT PROCESSED! \n\n\n\n\n\n\n\n\n"%(item))
    print("Clipping of AK, HI, and USA MFRI Rasters by Ecoregions completed!\n Double check:\n Ecoregions_MFRI.gdb for any processing errors.\n")
    print("There should be:\n 4 ecoregions in HI\n12 ecoregions in AK\n 71 in the lower 48.")

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
