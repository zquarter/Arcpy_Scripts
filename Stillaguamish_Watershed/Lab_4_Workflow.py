# Zack Quarterman, Western Washington university (2020)
# Python 3.6, ArcGIS PRO 2.5.0

# Stillaguamish Watershed geoprocessing for forest roads and fish bearing streams.
# This script relies heavily upon the use of lists and for/if/elif statements.
# Most parameters in the arcpy functions are calling on intems from a list so changing
# the items should be done within the list that is being called instead of directly in the tools parameters.


## This script is formatted to run through the three items in the hydro_bounds list.
## Which consists of the Stillaguamish_Watershed, Stillaguamish_Subwatershed, and
## Stillaguamish_Catchments feature classes.
## Therefore it can be divided into 3 parts, one part for Watershed, one for Sub-watershed, and
## one part for Catchments. For each feature class in hydro_list, the length of streams in miles, 
## road length in miles, road density, stream density, number of road and strem intersections, and density of
## intersections by number of intersections per stream mile will be appended to the feature class attribute table
## and calculated for each row in the attribute table. 

try:
  
    import arcpy
    from arcpy import env
    import os
## Change workspace file path as required. Lines 23, 29, 51, and 84 have explicit flie paths. Edit as needed.
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_4/Data/SourceData_Lab4.gdb"
    ## Parallel processing is an optional parameter and not all tools support it. But if 
    ## your machine does not utilize 100% of the available processor cores when using a tool
    ## that supports parallel processing this environment setting will decrease analysis time.
    arcpy.env.parallelProcessingFactor = "100%"
    ## Change according to your workspace needs.
    outpath = "B:/GIS_Projects/421/Lab_4/Data" 
    ## Create geodtaabase in the workspace for the outputs of this script.
    arcpy.CreateFileGDB_management(outpath, "Still_Outputs.gdb")
    output_gdb = 'Still_Outputs.gdb'
    ## Create variable for the gdb path for easy reference
    out_gdb_path = os.path.join(outpath, output_gdb)
    ## Clip the Stillaguamish_Watershed to the extent of the Stillaguamish_Subwatershed due to the 
    ## overlap along the coastline.
    clip_watershed_fc = 'Stillaguamish_Watershed'
    ## Output file path for the file geodatabase to be used in the clip analysis.
    clip_output_path = os.path.join(out_gdb_path, clip_watershed_fc)
    print("Clipping Stillaguamish_Watershed to Stillaguamish_Subwatershed extent due to waterfront overlap")
    arcpy.Clip_analysis('Stillaguamish_Watershed', 'Stillaguamish_Subwatershed', clip_output_path)
    print("Clip_analysis completed")
    ## Move the 3 input Watershed, Sub-watershed, and Catchment polygon feature classes to the output geodatabase so
    ## that all analysis is contained within one workspace. This is not required but it makes for a cleaner geoprocessing
    ## environment. 
    print("Moving:\n Stillaguamish_Subwatershed, Stillaguamish_Catchment, FishStream, and ForestRoad\n to %s"%(out_gdb_path))
    arcpy.FeatureClassToGeodatabase_conversion(['Stillaguamish_Subwatershed' , 'Stillaguamish_Catchment', 'FishStream', 'ForestRoad'], out_gdb_path)
    print("FC to geodatabase conversion completed")
##----------------Alter miles field name for ForestRoad and FishStream------------------------------
## Change workspace file path as required.  
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_4/Data/Still_Outputs.gdb"
    arcpy.env.parallelProcessingFactor = "100%"    
    ## These are the target feature classes. Change them as necessary to suit your analysis.
    stream_road = ['FishStream', 'ForestRoad']
    fclist = arcpy.ListFeatureClasses()
    print(fclist)
    for fc in fclist:
        if fc == stream_road[0]:
            fieldlist = arcpy.ListFields(fc)
            print("%s fields:\n"%(fc))
            for field in fieldlist:
                print(field.name)
                ## Change "Miles" field to "Stream_Miles" to be more descriptive.
                if field.name == 'Miles':
                    print("Changing %s to Stream_Miles"%(field))
                    arcpy.AlterField_management(fc, field.name, 'Stream_Miles', 'Fish Stream Miles')
                    print("%s now contains Stream_Miles"%(fc))
                else:()
        elif fc == stream_road[1]:
            fieldlist = arcpy.ListFields(fc)
            print("%s fields:\n"%(fc))            
            for field in fieldlist:
                print(field.name)
                ## Change "Miles" to "Road_Miles" to be more descriptive.
                if field.name == 'Miles':
                    print("Changing %s to Road_Miles"%(field))
                    arcpy.AlterField_management(fc, field.name, 'Road_Miles', 'Road Miles')
                    print("%s now contains Road_Miles"%(fc))
                else:()
        else:
            print("%s is not FishStream or ForestRoad"%(fc))
##----------------Intersect ForestRoad and FishStream-----------------------------------------------
    ## Change workspace file path as required.      
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_4/Data/Still_Outputs.gdb"
    arcpy.env.parallelProcessingFactor = "100%"
    ## The inputs for the intersect analysis.
    inter_inputs = ['ForestRoad', 'FishStream']
    ## Output point feature class for the road and stream intersections
    inter_out_name = 'Stream_Road_Xings'
    print("Intersecting FishStream and ForestRoad feature classes to produce Stream_Road_Xings point feature class.")
    arcpy.Intersect_analysis(inter_inputs, inter_out_name, "", "", "point")
    print("%s created in Still_Outputs.gdb"%(inter_out_name))
  ##---------------Process watershed, subwatershed, and catchment using tabulate intersection for stream xings-------------
    ## List of input watershed boundary feature classes. For the following lists, the order of the list items will
    ## follow the same indexing as the hydro_bounds lists.
    hydro_bounds = ['Stillaguamish_Watershed' ,'Stillaguamish_Subwatershed', 'Stillaguamish_Catchment']
    ## List of inputs for tabulate intersection analysis
    class_feat = ['Stream_Road_Xings', 'ForestRoad', 'FishStream']  
    ## List of fields for each item in hydro_bounds to use for joining
    bound_field = ['WRIA_NM', 'WAU_NM', 'AU_ID']  
    ## List of output tables for each item in hydro_bounds produced containing the number of intersections for
    ## each row in the attribute table of each feature class.
    xing_table_out = ['Wshed_Xings', 'SubWshed_Xings', 'Catch_Xings']
    ## List of output tables for each item in hydro_bounds produced containing the road length in miles for
    ## each row in the attribute table of each feature class.
    road_table_out = ['Wshed_Roads', 'SubWshed_Roads', 'Catch_Roads']
    ## List of output tables for each item in hydro_bounds produced containing the stream length in miles for
    ## each row in the attribute table of each feature class.    
    stream_table_out = ['Wshed_Streams', 'SubWshed_Streams', 'Catch_Streams']
    ## List containing fields in the output tables for number of intersections, road length, and stream length
    ## in miles for each row in the attribute table of each fc in hydro_bounds.
    miles_table = ['PNT_COUNT', 'Road_Miles', 'Stream_Miles']
    ## A list containing the field name and alias to be used for changing the "PNT_COUNT" to stream_road_field[0]
    stream_road_field = ['Stream_Road_Xings', 'Stream Road Crossings']
    ## List of fields to add to the attribute tables of each fc in hydro_bounds for density calculations.
    add_field = ['Xing_Density', 'Road_Density', 'Stream_Density']
    ## List of field aliases for each of the density calculation fields.
    alias = ['Crossings Per Mile of Streams', 'Road Density', 'Stream Density']
    ## Expressions for calculating density field values 
    xing_dens_exp = "!Stream_Road_Xings! / !Stream_Miles!"
    road_dens_exp = "!Road_Miles! / !SquareMiles!"
    stream_dens_exp = "!Stream_Miles! / !SquareMiles!"
    ## Working through the areas of study: Watershed, Subwatershed, and Catchment.
    ## For hydro_bounds[0], most parameters will call on items from lists with index [0]
    for item in hydro_bounds:
        if item == hydro_bounds[0]:  ## Stillaguamish_Watershed
            for entry in add_field:
                if entry == add_field[0]: ## Add fields for density calculations 
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[0], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
                elif entry == add_field[1]:
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[1], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
                else:
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[2], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
            for feature in class_feat:
                if feature == class_feat[0]:  ## Stream_Road_Xings
                    print("Tabulating road and stream intersections for %s \nresults in %s"%(item, xing_table_out[0]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[0], feature, xing_table_out[0])
                    print("%s created in %s\n\n"%(xing_table_out[0], out_gdb_path))
                    ## Change tabulate intersection output field name from PNT_COUNT to 'Stream_Road_Xings'
                    fieldlist = arcpy.ListFields(xing_table_out[0])
                    for field in fieldlist:
                        if field.name == miles_table[0]:
                            print("Changing %s to %s"%(field.name, stream_road_field[0]))
                            arcpy.AlterField_management(xing_table_out[0], field.name, stream_road_field[0], stream_road_field[1])
                            print("%s changed to %s in %s"%(miles_table[0], stream_road_field[0], xing_table_out[0]))
                        else:()
                    print("Joining the results from %s to %s"%(xing_table_out[0], item))
                    arcpy.JoinField_management(item, bound_field[0], xing_table_out[0], bound_field[0], stream_road_field[0])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(stream_road_field[0], item))
                elif feature == class_feat[1]:  ## ForestRoad
                    print("Tabulating road miles for %s \nresults in %s"%(item, road_table_out[0]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[0], feature, road_table_out[0], "", miles_table[1], "", "MILES")
                    print("%s created in %s\n\n"%(road_table_out[0], out_gdb_path))
                    print("Joining the results from %s to %s"%(road_table_out[0], item))
                    arcpy.JoinField_management(item, bound_field[0], road_table_out[0], bound_field[0], miles_table[1])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(miles_table[1], item))                    
                elif feature == class_feat[2]:  ## FishStream
                    print("Tabulating stream miles for %s \nresults in %s"%(item, stream_table_out[0]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[0], feature, stream_table_out[0], "", miles_table[2], "", "MILES")
                    print("%s created in %s\n\n"%(stream_table_out[0], out_gdb_path))
                    print("Joining the results from %s to %s"%(stream_table_out[0], item))
                    arcpy.JoinField_management(item, bound_field[0], stream_table_out[0], bound_field[0], miles_table[2])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(miles_table[2], item))
                else:()
            ## Using the created fields in the script above, calculate density fields within add_field list.
            print("Calculating %s value"%(add_field[0]))
            arcpy.CalculateField_management(item, add_field[0], xing_dens_exp, "PYTHON3", "")
            print("Calculating %s value"%(add_field[1]))
            arcpy.CalculateField_management(item, add_field[1], road_dens_exp, "PYTHON3", "")
            print("Calculating %s value"%(add_field[2]))
            arcpy.CalculateField_management(item, add_field[2], stream_dens_exp, "PYTHON3", "")
        ## For hydro_bounds[1], most parameters will call on items from lists with index [1]        
        elif item == hydro_bounds[1]:  ## Stillaguamish_Subwatershed
            for entry in add_field:
                if entry == add_field[0]: ## Add fields for density calculations 
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[0], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
                elif entry == add_field[1]:
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[1], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
                else:
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[2], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))            
            for feature in class_feat:
                if feature == class_feat[0]:  ##Stream_Road_Xings
                    print("Tabulating road and stream intersections for %s \nresults in %s"%(item, xing_table_out[1]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[1], feature, xing_table_out[1])
                    print("%s created in %s\n\n"%(xing_table_out[1], out_gdb_path))
                    ## Change tabulate intersection output field name from PNT_COUNT to 'Stream_Road_Xings'
                    fieldlist = arcpy.ListFields(xing_table_out[1])
                    for field in fieldlist:
                        if field.name == miles_table[0]:
                            print("Changing %s to %s"%(field.name, stream_road_field[0]))
                            arcpy.AlterField_management(xing_table_out[1], field.name, stream_road_field[0], stream_road_field[1])
                            print("%s changed to %s in %s"%(miles_table[0], stream_road_field[0], xing_table_out[1]))
                        else:()                    
                    print("Joining the results from %s to %s"%(xing_table_out[1], item))
                    arcpy.JoinField_management(item, bound_field[1], xing_table_out[1], bound_field[1], stream_road_field[0])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(stream_road_field[0], item))                    
                elif feature == class_feat[1]:  ## ForestRoad
                    print("Tabulating road miles for %s \nresults in %s"%(item, road_table_out[1]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[1], feature, road_table_out[1], "", miles_table[1], "", "MILES")
                    print("%s created in %s\n\n"%(road_table_out[1], out_gdb_path))
                    print("Joining the results from %s to %s"%(road_table_out[1], item))
                    arcpy.JoinField_management(item, bound_field[1], road_table_out[1], bound_field[1], miles_table[1])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(miles_table[1], item))  
                elif feature == class_feat[2]:  ## FishStream
                    print("Tabulating stream miles for %s \nresults in %s"%(item, stream_table_out[1]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[1], feature, stream_table_out[1], "", miles_table[2], "", "MILES")
                    print("%s created in %s\n\n"%(stream_table_out[1], out_gdb_path))
                    print("Joining the results from %s to %s"%(stream_table_out[1], item))
                    arcpy.JoinField_management(item, bound_field[1], stream_table_out[1], bound_field[1], miles_table[2])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(miles_table[2], item))  
                else:()
            ## Using the created fields in the script above, calculate density fields within add_field list.            
            print("Calculating %s value"%(add_field[0]))
            arcpy.CalculateField_management(item, add_field[0], xing_dens_exp, "PYTHON3", "")
            print("Calculating %s value"%(add_field[1]))
            arcpy.CalculateField_management(item, add_field[1], road_dens_exp, "PYTHON3", "")
            print("Calculating %s value"%(add_field[2]))
            arcpy.CalculateField_management(item, add_field[2], stream_dens_exp, "PYTHON3", "")               
        ## For hydro_bounds[2], most parameters will call on items from lists with index [2]        
        elif item == hydro_bounds[2]:  ##Stillaguamish_Catchment
            for entry in add_field:
                if entry == add_field[0]: ## Add fields for density calculations 
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[0], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
                elif entry == add_field[1]:
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[1], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))
                else:
                    print("Adding field: %s to %s attribute table"%(entry, item))
                    arcpy.AddField_management(item, entry, "DOUBLE", "", "", "", alias[2], "", "", "")
                    print("%s added to attribute table of %s"%(entry, item))            
            for feature in class_feat:
                if feature == class_feat[0]:  ## Stream_Road_Xings
                    print("Tabulating road and stream intersections for %s \nresults in %s"%(item, xing_table_out[2]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[2], feature, xing_table_out[2])
                    print("%s created in %s\n\n"%(xing_table_out[2], out_gdb_path))
                    ## Change tabulate intersection output field name from PNT_COUNT to 'Stream_Road_Xings'
                    fieldlist = arcpy.ListFields(xing_table_out[2])
                    for field in fieldlist:
                        if field.name == miles_table[0]:
                            print("Changing %s to %s"%(field.name, stream_road_field[0]))
                            arcpy.AlterField_management(xing_table_out[2], field.name, stream_road_field[0], stream_road_field[1])
                            print("%s changed to %s in %s"%(miles_table[0], stream_road_field[0], xing_table_out[2]))
                        else:()                      
                    print("Joining the results from %s to %s"%(xing_table_out[2], item))
                    arcpy.JoinField_management(item, bound_field[2], xing_table_out[2], bound_field[2], stream_road_field[0])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(stream_road_field[0], item))                    
                elif feature == class_feat[1]:  ## ForestRoad
                    print("Tabulating road miles for %s \nresults in %s"%(item, road_table_out[2]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[2], feature, road_table_out[2], "", miles_table[1], "", "MILES")
                    print("%s created in %s\n\n"%(road_table_out[2], out_gdb_path))
                    print("Joining the results from %s to %s"%(road_table_out[2], item))
                    arcpy.JoinField_management(item, bound_field[2], road_table_out[2], bound_field[2], miles_table[1])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(miles_table[1], item))
                elif feature == class_feat[2]:  ## FishStream
                    print("Tabulating stream miles for %s \nresults in %s"%(item, stream_table_out[2]))
                    arcpy.TabulateIntersection_analysis(item, bound_field[2], feature, stream_table_out[2], "", miles_table[2], "", "MILES")
                    print("%s created in %s\n\n"%(stream_table_out[2], out_gdb_path))
                    print("Joining the results from %s to %s"%(stream_table_out[2], item))
                    arcpy.JoinField_management(item, bound_field[2], stream_table_out[2], bound_field[2], miles_table[2])
                    print("%s field joined to %s\n- - - - - - - - - - - - - - -"%(miles_table[2], item))
                else:()
            ## Using the created fields in the script above, calculate density fields within add_field list.            
            print("Calculating %s value"%(add_field[0]))
            arcpy.CalculateField_management(item, add_field[0], xing_dens_exp, "PYTHON3", "")
            print("Calculating %s value"%(add_field[1]))
            arcpy.CalculateField_management(item, add_field[1], road_dens_exp, "PYTHON3", "")
            print("Calculating %s value"%(add_field[2]))
            arcpy.CalculateField_management(item, add_field[2], stream_dens_exp, "PYTHON3", "")
        else:()
    tables = arcpy.ListTables()
    for table in tables:
        print("%s now present in %s"%(table, out_gdb_path))
    print("Each of these tables has been joined to their corresponding study area (Watersheds, Subwatersheds, and Catchments) for the Stillaguamish watershed.")
    print("Analysis completed for all items %s"%(hydro_bounds))

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
