
#____For processing on school computers change path to : C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 from C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 
# make sure all paths are changed before processing
# C:/GIS_Projects/420/Quarterman_ENVS420_Lab4
try:
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
  print("-------------------------PART C--------------------------------------------------------------------------\n\n")
  
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb" 
  arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/NAD_1983_HARN_StatePlane_Washington_South_FIPS_4602_Meters.prj")

# Adding  and calculating field for area square kilometers
  print("initializing add and calculate field batch sequence...")
#----Create new field and multiply corresponding field name by WEIGHT--------------------------
  #multiply the Total Population (for Ethnicity), ---> "total_pop" --->"W_ETH_totalPOP"
  #Total Population (for Poverty), ---> "total_pop1" ---> "W_POV_totalPOP"
  #Non-Hispanic White Population, ---> "NHWA" ---> "W_NHWA"
  #Minority Population (total minus non-Hispanic whites), ---> "Minority" ---> "W_Minority"
  #Poverty ---> "Poverty" ---> "W_Poverty"
  #by the WEIGHT field ---> "WEIGHT"
  # Make a dictionary of field names to create and values to multiply by WEIGHT to fill them
  targ = "Pop_Tracts_Hazardous_Buffer_Union"
  cendict = {
    "W_ETH_totalPOP": "!total_pop!",
    "W_POV_totalPOP": "!total_pop_1!",
    "W_NHWA": "!NHWA!",
    "W_Minority": "!Minority!",
    "W_Poverty": "!Poverty!"
    }
  print(cendict)
  field_names = list(cendict.keys())
  print("\nThese are the field names:\n %s"%(field_names))
  coef_weight = list(cendict.values())
  print("\n\nThese are the items to multiply by WEIGHT:\n %s"%(coef_weight))
  arcpy.AddField_management(targ, "WEIGHT", "FLOAT")
  for key, item in cendict.items():
    #arcpy.AddField_management(targ,
    print("Key: %s \nItem: %s"%(key, item))
    express = "%s * !WEIGHT!"%(item)
    print("Expression:\n %s"%(express))
    print("Adding %s field to %s"%(key, targ))
    arcpy.AddField_management(targ, key, "FLOAT")
    print("Calculating value of %s using expression: %s"%(key, express))
    arcpy.CalculateField_management(targ, key, express, "PYTHON_9.3")
    print("%s field calculated successfully!"%(key))
#----------------Adding 2 fields to calculate percent poverty and percent minority-----
  m_per = "Percent_Minority"
  m_exp = "(!Minority! / !total_pop!) * 100 "
  p_per = "Percent_Poverty"
  p_exp = "(!Poverty! / !total_pop_1!) * 100"
  print("Creating fields: %s and %s"%(m_per, p_per))
  arcpy.AddField_management(targ, m_per, "FLOAT")
  arcpy.AddField_management(targ, p_per, "FLOAT")
  arcpy.CalculateField_management(targ, m_per, m_exp, "PYTHON_9.3")
  arcpy.CalculateField_management(targ, p_per, p_exp, "PYTHON_9.3")

  #Adding field for if polygon is inside hazardous buffer
  arcpy.AddField_management(targ, "Inside_Haz_Buff", "TEXT")
  fds = ["FID_Populated_Hazardous_Buffers", "Inside_Haz_Buff"]
  with arcpy.da.UpdateCursor(targ, fds) as cursor:
    for row in cursor:
      #val = row[0]
      if row[0] == -1:
        row[1] = "OUT"
        print("Area not inside hazardous buffer, Inside_Haz_Buff = OUT")
        cursor.updateRow(row)
      else:
        row[1] = "IN"
        print("Area inside hazardous buffer, Inside_Haz_Buff = IN")
        cursor.updateRow(row)
  print("Percent_Minority and Percent_Poverty fields calculated successfully!")

  #----Summary statistics for both percent fields and all weighted fields (5 of them)
  stat_fields = [["W_ETH_totalPOP", "SUM"],["W_POV_totalPOP", "SUM"],["W_NHWA", "SUM"],["W_Minority", "SUM"],["W_Poverty", "SUM"],["Percent_Poverty", "MEAN"],["Percent_Minority", "MEAN"]]
  summary_table = "King_County_2016_Census_Statistics"
  arcpy.Statistics_analysis(targ, summary_table, stat_fields, "Inside_Haz_Buff")










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
