
#____For processing on school computers chande path to : C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 from C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 
# make sure all paths are changed before processing
# C:/GIS_Projects/420/Quarterman_ENVS420_Lab4
try:
  # Variable for timestamp
  print ("start")
  
  import arcpy
  import os
  import sys
  import pandas as pd
  from pandas import ExcelWriter
  from pandas import ExcelFile
  import string
  import re

  #----------------------------------------------PART B--------------
  # Creating datasets that only reside within king county (TRI, Superfund sites, and census block groups)
  print("-------------------------PART B--------------------------------------------------------------------------\n\n")
  print("Selecting areas of TRI, Superfund sites, and Census block groups that are inside of King County")
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb" 
  arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/NAD_1983_HARN_StatePlane_Washington_South_FIPS_4602_Meters.prj")
  # Select features, then copy features managment to export to new feature class only containing King County Data
  tracts_where = """ "COUNTYFP" = '033'"""
  super_where = """ "COUNTY" = 'KING'"""
  tri_where = """ "County" = 'KING'"""
  release_where = """ "Total_rele" > '0'"""
  print("Selecting tracts in tl_2016_53_bg where: %s"%(tracts_where))
  king_tracts = arcpy.SelectLayerByAttribute_management("tl_2016_53_bg", "NEW_SELECTION", tracts_where)
  arcpy.CopyFeatures_management(king_tracts, 'King_County_2016_Census_Tracts')
  print("King_County_2016_Census_Tracts created in Vector_Inputs_NAD83.gdb\n")
  print("Selecting points in superfund_npl where: %s"%(super_where))
  king_super = arcpy.SelectLayerByAttribute_management("superfund_npl", "NEW_SELECTION", super_where)
  arcpy.CopyFeatures_management(king_super, 'King_County_Superfund_Sites')
  print("King_County_Superfund_Sites created in Vector_Inputs_NAD83.gdb\n")
  print("Selecting points in Toxic_Release_Inventory_2016 where: %s"%(tri_where))
  king_tri = arcpy.SelectLayerByAttribute_management("Toxic_Release_Inventory_2016", "NEW_SELECTION", tri_where)
  king_refined_tri = arcpy.SelectLayerByAttribute_management(king_tri, 'SUBSET_SELECTION', '"Total_rele" > 0')
  arcpy.CopyFeatures_management(king_refined_tri, 'King_County_Toxic_Release_Inventory')
  print("King_County_Toxic_Release_Inventory created in Vector_Inputs_NAD83.gdb\n")
  newfcs = arcpy.ListFeatureClasses()
  print("Feature classes contained in Vector_Inputs_NAD83.gdb:\n %s"%(newfcs))

  # Merge TRI and Superfund feature classes and then buffer
  print("Merging Superfund sites and toxic release sites into Hazardous_Sites")
  sfundking = "King_County_Superfund_Sites"
  toxking = "King_County_Toxic_Release_Inventory"
  outsites = "Hazardous_Sites"
  arcpy.Merge_management([sfundking, toxking], outsites, "", "ADD_SOURCE_INFO")
  print("Merge complete")
  # Create multiring buffer from Hazardous_Sites feature class
  arcpy.MultipleRingBuffer_analysis(outsites, "Hazardous_Buffers", [1,2,3,4], "kilometers", "", "ALL")

  # Adding field to calculate minority in census feature class
  #-----------------------HERE----------------------------------
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb"
  census = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb/King_County_2016_Census_Tracts"
  print("Adding and calculating field for minority population")
  arcpy.AddField_management('King_County_2016_Census_Tracts',"Minority", "LONG", "", "", "", "", "", "")
  arcpy.CalculateField_management(census, "Minority", "!total_pop! - !NHWA!", "PYTHON3","")
  # Add and calculate poverty field
  print("Adding and calculating field for total population with income less than twice the poverty line")
  arcpy.AddField_management('King_County_2016_Census_Tracts',"Poverty", "LONG", "", "", "", "", "", "")
  arcpy.CalculateField_management(census, "Poverty", "!sub_0_50! + !f0_50to0_9! + !f1_00to1_2! + !f1_50to1_8! + !f1_85to1_9!", "PYTHON3","")



  # Land use areas to include in merge with buffers:
  # general commercial, office/business park, industrial/manufacturing, aviation and transportation, park/golf course, mineral resources, and forest) 
  # Waterbodies
  print("Selecting areas from the land use layer that will be subtracted from census tracts")
  landuse_where = """ "CONSOL20" = 'General Commercial' OR  "CONSOL20" = 'Office/Business Park' OR "CONSOL20" = 'Industrial/Manufacturing' OR "CONSOL20" = 'Aviation and Transportation-Related' OR "CONSOL20" = 'Park/Golf Course/Trail/Open Space' OR "CONSOL20" = 'Mineral Resource-Related' OR "CONSOL20" = 'Forest'"""
  water = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb/Waterbodies"
  nonpop = "Non_Populated_Areas"
  #selected_landuse = arcpy.SelectLayerByAttribute_management("landuse_zoning", "NEW_SELECTION", landuse_where)
  print("Merging selected areas within land use areas with the waterbodies layer")
  arcpy.Merge_management([selected_landuse, water], nonpop, "", "ADD_SOURCE_INFO")
  print("Non_Populated_Areas created inside Vector_Inputs_NAD83.gdb")
  
  # ------------Erasing areas from census blocks from unpopulated areas------------
  erase_output = "Tracts_Populated"
  erase_buffer_input = "Hazardous_Buffers"
  erase_input = "King_County_2016_Census_Tracts"
  erase_buffer_output = "Populated_Hazardous_Buffers"
  print("Erasing non pop areas from census tracts")
  arcpy.Erase_analysis(erase_input, nonpop, erase_output)
  print("Erase analysis successfull: Tracts_Populated created!")

  print("Erasing non pop areas from hazardous buffers")
  arcpy.Erase_analysis(erase_buffer_input, nonpop, erase_buffer_output)
  print("Erase analysis successfull: buffers_Populated created!")
#-------------------------------------------------------------------------------------------
# Adding  and calculating field for area square kilometers
  print("Calculating the geometry of the area field added to the populated census blocks")
  tempPgs = "Tracts_Populated"
  arcpy.AddField_management(tempPgs, "area_SqKm", "FLOAT")
  exp = "!SHAPE.AREA@SQUAREKILOMETERS!"
  arcpy.CalculateField_management(tempPgs, "area_SqKm", exp, "PYTHON_9.3")
  print("Area (square kilometers) successfully calculated")

  print("Merging Tracts_Populated with Populated_Hazardous_Buffers via UNION tool")
  infeatures = [["Tracts_Populated", 1], ["Populated_Hazardous_Buffers", 2]]
  outfeatures = "Pop_Tracts_Hazardous_Buffer_Union"
  arcpy.Union_analysis(infeatures, outfeatures)
  print("Union analysis completed!")
  #------------Adding fields for subarea and weight in the merged Pop_Tracts_Hazardous_Buffer_Union fc-----
  targ = "Pop_Tracts_Hazardous_Buffer_Union"
  # Field for SUBAREA
  print("Adding field: SUBAREA")
  arcpy.AddField_management(targ, "SUBAREA", "FLOAT")
  # Field for WEIGHT
  print("Adding field: WEIGHT")
  arcpy.AddField_management(targ, "WEIGHT", "FLOAT")
  # Expression for area in square kilometers
  exp = "!SHAPE.AREA@SQUAREKILOMETERS!"
  # Calculating SUBAREA value
  print("Calculating SUBAREA value")
  arcpy.CalculateField_management(targ, "SUBAREA", exp, "PYTHON_9.3")
  print("Field: SUBAREA calculated!")
  # Calculating WEIGHT value
  print("Calculating WEIGHT value")
  exp_w = "!SUBAREA! / !area_SqKm!"
  arcpy.CalculateField_management(targ, "WEIGHT", exp_w, "PYTHON_9.3")
  print("Field: WEIGHT calculated!")
  







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

print  ('\n\n--> Finished Script... ')
