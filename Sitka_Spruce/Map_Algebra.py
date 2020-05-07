#____For processing on school computers change path to : F:/GIS_Projects/420/Quarterman_ENVS420_Lab4 from F:/GIS_Projects/420/Quarterman_ENVS420_Lab4 
# make sure all paths are changed before processing
# F:/GIS_Projects/420/Quarterman_ENVS420_Lab4
try:
  
  import arcpy
  from arcpy import env
  from arcpy.sa import *
  import os
  import sys
  arcpy.env.overwriteOutput = True
  arcpy.env.workspace = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  input_gdb = "Final_Variables_2080.gdb"
# Copy each file with a .csv extension to a dBASE file

  print("Creating GDB for the outputs to be stored in")
  out_folder = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  gdb_name = "Output_Zonal_Stats_2080.gdb"
  inputgdb_name_full = os.path.join(out_folder, input_gdb)
  gdb_path_full = os.path.join(out_folder, gdb_name)
  arcpy.CreateFileGDB_management(out_folder, gdb_name)
  print("Output_Zonal_Stats_2080.gdb created!")
  #ras_list = arcpy.ListRasters("*", "GRID")
  arcpy.env.workspace = 'F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Final_Variables_2080.gdb'
  for raster in arcpy.ListRasters():
  #rasters = arcpy.ListRasters()
  #for raster in rasters:
    #if raster == 'NORM_6190_MAT_BL' or raster == 'NORM_6190_MCMT_BL' or raster == 'NORM_6190_MWMT_BL'
    if not raster == 'ENSEMBLE_A1B_2080s_AHM' and not raster == 'ENSEMBLE_A1B_2080s_MAP':
      print("Using map algebra to calculate rasters that use temeprature")
      outRas = Raster(raster) // 10
      rasname = "%s_corr"%(raster)
      og_name = os.path.join(inputgdb_name_full, rasname)
      outRas.save(og_name)
      print("%s raster saved with updated values"%(raster))
      arcpy.Delete_management(raster)
      print("old raster deleted")
    else:
      print("%s skipped for whatever reason..."%(raster))
  print("Field corrections all finished, moving on to calculating zonal statistics")
  for raster in arcpy.ListRasters():
    sit_spruce = "F:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Sitka_Spruce_Correct_Projection/Sitka_Spruce_Range.shp"
    outZonalStats = ZonalStatistics(sit_spruce, "Sitka_Pres", raster, "MEAN", "DATA")
    rasname = "%s"%(raster)
    short_name = rasname.replace("ENSEMBLE_A1B_2080s_", "A1B_2080_")
    shorter_name = short_name.replace("_BL", "")
    shortest_name = shorter_name.replace("_corr", "")
    out_ras_mean = "%s_MEAN"%(shortest_name)
    name_mean = os.path.join(gdb_path_full, out_ras_mean)
    outZonalStats.save(name_mean)
    print("Out Zonal Stats Raster created: %s"%(out_ras_mean))
    print("Now calculating zonal stats for the standard deviation of %s"%(raster))
    outZonalStats = ZonalStatistics(sit_spruce, "Sitka_Pres", raster, "STD", "DATA")
    out_ras_sd = "%s_SD"%(shortest_name)
    name_sd = os.path.join(gdb_path_full, out_ras_sd)
    outZonalStats.save(name_sd)
    print("Out Zonal Stats Raster created: %s"%(out_ras_sd))


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


