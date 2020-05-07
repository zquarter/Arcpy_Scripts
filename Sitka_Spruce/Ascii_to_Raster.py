
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
  import glob
  arcpy.env.workspace = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Lab5_Data"
  
# Copy each file with a .csv extension to a dBASE file
  print("Creating GDB for the climate variables to be stored in")
  out_folder = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  gdb_name = "Climate_Variables_2080.gdb"
  prj_gdb = "Climate_Variables_2080_projected_BL.gdb"
  #arcpy.CreateFileGDB_management(out_folder, gdb_name)
  print("Climate_Variables_2080.gdb created!")
  #arcpy.CreateFileGDB_management(out_folder, prj_gdb)
  print("Climate_Variables_projected_NN.gdb created!")

  coor_sys = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Sitka_Spruce_Correct_Projection/Lambert_Conformal_Conic_VARIABLES.prj"
  arcpy.env.workspace = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Climate_Variables_2080.gdb"
  dir_name = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Climate_Variables_2080"
  for filename in os.listdir(dir_name):
    if not filename.endswith(".asc"): continue
    print(filename)
    full_path = os.path.join(dir_name, filename)
    print(full_path)
    # outASCII = '%s.asc' % (full_path,)
    out_int = filename.rstrip(".asc")
    print(out_int)
    out_ras = out_int.replace(".", "_")
    print(out_ras)
    print("Starting ASCII to Raster conversion for %s"%(out_ras))
    arcpy.ASCIIToRaster_conversion(full_path, out_ras)
    print("%s raster created in Climate_Variables.gdb"%(out_ras))
    print("Defining the projection for %s as:\n %s"%(out_ras, coor_sys))
    arcpy.DefineProjection_management(out_ras, coor_sys)
    print("Projection successfully defined! \n")

        #NAD_1983_HARN_StatePlane_ Washington_South_FIPS_4602
    outworkspace = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Climate_Variables_2080_projected_BL.gdb" 
    from_sr = arcpy.Describe(out_ras).spatialReference
    outfc = os.path.join(outworkspace, out_ras) 
    outCS = arcpy.SpatialReference("F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Sitka_Spruce_Correct_Projection/Sitka_Spruce_Range.prj")
    print("Input spatial reference for %s is:\n %s"%(out_ras, from_sr))
    exte = arcpy.Describe(out_ras).extent
    print("Spatial extent of impot:")
    print(exte)
    trans_list = arcpy.ListTransformations(from_sr, outCS, exte)
    print("List of transformations here:")
    print(trans_list)
    trans = trans_list[0]
    print("Projecting: %s  to match the defined projection of Sitka_Spruce_Range" %(out_ras))
    arcpy.ProjectRaster_management(out_ras, outfc, outCS, "BILINEAR", "1000", trans, "#", "#")
    print(out_ras + '   Projected!')        	








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
