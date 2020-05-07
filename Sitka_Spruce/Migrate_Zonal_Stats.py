#____For processing on school computers change path to : C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 from C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 
# make sure all paths are changed before processing
# C:/GIS_Projects/420/Quarterman_ENVS420_Lab4
try:
  
  import arcpy
  from arcpy import env
  from arcpy.sa import *
  import os
  import sys

  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  input_gdb = "Final_Variables.gdb"
# Copy each file with a .csv extension to a dBASE file
  print("Creating GDB for the outputs to be stored in")
  out_folder = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  gdb_name = "Output_Zonal_Stats.gdb"
  gdb_path_full = os.path.join(out_folder, gdb_name)
  arcpy.CreateFileGDB_management(out_folder, gdb_name)
  print("Climate_Variables.gdb created!")
  #ras_list = arcpy.ListRasters("*", "GRID")
  arcpy.env.workspace = 'C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Final_Variables.gdb'
  for raster in arcpy.ListDatasets("*", "Raster"):
  #rasters = arcpy.ListRasters()
  #for raster in rasters:
    #if raster == 'NORM_6190_MAT_BL' or raster == 'NORM_6190_MCMT_BL' or raster == 'NORM_6190_MWMT_BL'
    if not raster == 'NORM_6190_AHM_BL' or raster == 'NORM_6190_MAP_BL':
      print("Adding field TEMP to %s in geodatabase"%(raster))
      field_name = "TEMP"
      arcpy.AddField_management(raster, field_name, "FLOAT", "", "", "", field_name, "NULLABLE", "NON_REQUIRED")
      print("Added TEMP field to %s"%(raster))
      print("Calculating TEMP field value to correct for deg C*10")
      arcpy.CalculateField_management(raster, "TEMP", "!Value! / 10", "PYTHON3","")
      print("TEMP field calculated for %s"%(raster))
    else:()
  print("Field corrections all finished, moving on to calculating zonal statistics")
  upd_ras_list = arcpy.ListRasters("*", "GRID")
  for raster in upd_ras_list:
    sit_spruce = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Sitka_Spruce_Correct_Projection/Sitka_Spruce_Range.shp"
    outZonalStats = ZonalStatistics(sit_spruce, "Sitka_Pres", raster, "MEAN", "DATA")
    rasname = "%s"%(raster)
    short_name = rasname.replace("NORM_6190_", "")
    shorter_name = short_name.replace("_BL", "")
    out_ras_mean = "%s_MEAN"%(shorter_name)
    name_mean = os.path.join(gdb_path_full, out_ras_mean)
    outZonalStats.save(name_mean)
    print("Out Zonal Stats Raster created: %s"%(out_ras_mean))
    print("Now calculating zonal stats for the standard deviation of %s"%(raster))
    outZonalStats = ZonalStatistics(sit_spruce, "Sitka_Pres", raster, "STD", "DATA")
    out_ras_sd = "%s_SD"%(shorter_name)
    name_sd = os.path.join(gdb_path_full, out_ras_sd)
    outZonalStats.save(name_sd)
    print("Out Zonal Stats Raster created: %s"%(out_ras_sd))






  # coor_sys = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Sitka_Spruce_Correct_Projection/Lambert_Conformal_Conic_VARIABLES.prj"
  # arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Climate_Variables.gdb"
  # dir_name = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Lab5_Data"
  # for filename in os.listdir(dir_name):
  #   if not filename.endswith(".asc"): continue
  #   print(filename)
  #   full_path = os.path.join(dir_name, filename)
  #   print(full_path)
  #   # outASCII = '%s.asc' % (full_path,)
  #   out_int = filename.rstrip(".asc")
  #   print(out_int)
  #   out_ras = out_int.replace(".", "_")
  #   print(out_ras)
  #   print("Starting ASCII to Raster conversion for %s"%(out_ras))
  #   arcpy.ASCIIToRaster_conversion(full_path, out_ras)
  #   print("%s raster created in Climate_Variables.gdb"%(out_ras))
  #   print("Defining the projection for %s as:\n %s"%(out_ras, coor_sys))
  #   arcpy.DefineProjection_management(out_ras, coor_sys)
  #   print("Projection successfully defined! \n")

  #       #NAD_1983_HARN_StatePlane_ Washington_South_FIPS_4602
  #   outworkspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Climate_Variables_projected_BL.gdb" 
  #   from_sr = arcpy.Describe(out_ras).spatialReference
  #   outfc = os.path.join(outworkspace, out_ras) 
  #   outCS = arcpy.SpatialReference("C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Sitka_Spruce_Correct_Projection/Sitka_Spruce_Range.prj")
  #   print("Input spatial reference for %s is:\n %s"%(out_ras, from_sr))
  #   exte = arcpy.Describe(out_ras).extent
  #   print("Spatial extent of impot:")
  #   print(exte)
  #   trans_list = arcpy.ListTransformations(from_sr, outCS, exte)
  #   print("List of transformations here:")
  #   print(trans_list)
  #   trans = trans_list[0]
  #   print("Projecting: %s  to match the defined projection of Sitka_Spruce_Range" %(out_ras))
  #   arcpy.ProjectRaster_management(out_ras, outfc, outCS, "BILINEAR", "1000", trans, "#", "#")
  #   print(out_ras + '   Projected!')        	








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
