#____For processing on school computers change path to : C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 from C:/GIS_Projects/420/Quarterman_ENVS420_Lab4 
# make sure all paths are changed before processing
# C:/GIS_Projects/420/Quarterman_ENVS420_Lab4

# V3:
# AHM     10 - 300
# CMI     60 - 470
# MAP   1300 - 5400
# MCMT    -3 - 8
# MWMT    11 - 16.8
# TAVESUM 10 - 16




try:
  
  import arcpy
  from arcpy import env
  from arcpy.sa import *
  import os
  import sys
  arcpy.env.overwriteOutput = True
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  input_gdb = "Final_Variables_2080.gdb"
# Copy each file with a .csv extension to a dBASE file

  print("Creating GDB for the outputs to be stored in")
  out_folder = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables"
  gdb_name = "Best_Output_2080_V3.gdb"
  inputgdb_name_full = os.path.join(out_folder, input_gdb)
  gdb_path_full = os.path.join(out_folder, gdb_name)
  arcpy.CreateFileGDB_management(out_folder, gdb_name)
  print("Best_Output_2080_V3.gdb created!")
  #ras_list = arcpy.ListRasters("*", "GRID")
  arcpy.env.workspace = 'C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Final_Variables_2080.gdb'
  #for raster in arcpy.ListRasters():
  #rasters = arcpy.ListRasters()
  outgdbpath = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Best_Output_2080_V3.gdb"
  layer_dict ={"ENSEMBLE_A1B_2080s_AHM" : "AHM","ENSEMBLE_A1B_2080s_MAP" : "MAP","ENSEMBLE_A1B_2080s_MCMT_corr" : "MCMT","ENSEMBLE_A1B_2080s_MWMT_corr" : "MWMT","ENSEMBLE_A1B_2080s_Tave_sm_corr" : "TASM","ENSEMBLE_A1B_2080s_CMI" : "CMI"}
  for ras in arcpy.ListRasters():
    if ras == "ENSEMBLE_A1B_2080s_AHM":
#AHM = "ENSEMBLE_A1B_2080s_AHM" ---->( "%NORM_6190_AHM_BL%" >=8.9636) & ( "%NORM_6190_AHM_BL%" <=163.5038)
      print("Processing: %s \n"%(ras))      
      outcon = Raster(ras)
      output = Con((outcon >= 10) & (outcon <=300), 1, 0)
      short_name = layer_dict.get(ras)
      print(short_name)
      name_output = "%s_2080_out"%(short_name)
      print(name_output)
      outlocation = os.path.join(outgdbpath, name_output)
      output.save(outlocation)
      print("%s saved! \n"%(name_output))
# MAP = "ENSEMBLE_A1B_2080s_MAP" --->( "%NORM_6190_MAP_BL (3)%" >=1595.67) & ("%NORM_6190_MAP_BL (3)%" <=3882.91)    
    elif ras == "ENSEMBLE_A1B_2080s_MAP":
      print("Processing: %s \n"%(ras))      
      outcon = Raster(ras)
      output = Con((outcon >= 1300) & (outcon <=5400), 1, 0)  ##### CHANGED FROM 4000 to 5300 for BEST OUTPUT V2
      short_name = layer_dict.get(ras)
      name_output = "%s_2080_out"%(short_name)
      outlocation = os.path.join(outgdbpath, name_output)
      output.save(outlocation)
      print("%s saved! \n"%(name_output))
# MCMT = "ENSEMBLE_A1B_2080s_MCMT_corr" --->( "NORM_6190_MCMT_BL_corr">=-2.8) & ( "NORM_6190_MCMT_BL_corr"<=4.02)
    elif ras =="ENSEMBLE_A1B_2080s_MCMT_corr":
      print("Processing: %s \n"%(ras))      
      outcon = Raster(ras)
      output = Con((outcon >= -3) & (outcon <= 8), 1, 0)
      short_name = layer_dict.get(ras)
      name_output = "%s_2080_out"%(short_name)
      outlocation = os.path.join(outgdbpath, name_output)
      output.save(outlocation)
      print("%s saved! \n"%(name_output))
# MWMT = "ENSEMBLE_A1B_2080s_MWMT_corr" ---->( "NORM_6190_MWMT_BL_corr">=12.58) & ( "NORM_6190_MWMT_BL_corr"<=16.68)
    elif ras =="ENSEMBLE_A1B_2080s_MWMT_corr":
      print("Processing: %s \n"%(ras))      
      outcon = Raster(ras)
      output = Con((outcon >= 11) & (outcon <= 16.8), 1, 0)
      short_name = layer_dict.get(ras)
      name_output = "%s_2080_out"%(short_name)
      outlocation = os.path.join(outgdbpath, name_output)
      output.save(outlocation)
      print("%s saved! \n"%(name_output))    
# TAVESM = "ENSEMBLE_A1B_2080s_Tave_sm_corr" ---->( "NORM_6190_Tave_sm_BL_corr">=11.57) & ( "NORM_6190_Tave_sm_BL_corr"<=15.59)
    elif ras =="ENSEMBLE_A1B_2080s_Tave_sm_corr":
      print("Processing: %s \n"%(ras))
      outcon = Raster(ras)
      output = Con((outcon >= 10) & (outcon <= 16), 1, 0)
      short_name = layer_dict.get(ras)
      name_output = "%s_2080_out"%(short_name)
      outlocation = os.path.join(outgdbpath, name_output)
      output.save(outlocation)
      print("%s saved! \n"%(name_output))  
    elif ras == "ENSEMBLE_A1B_2080s_CMI":
      print("Processing: %s \n"%(ras))
      outcon = Raster(ras)
      output = Con((outcon >= 60) & (outcon <= 470), 1, 0)
      short_name = layer_dict.get(ras)
      name_output = "%s_2080_out"%(short_name)
      outlocation = os.path.join(outgdbpath, name_output)
      output.save(outlocation)
      print("%s saved! \n"%(name_output))  

    else:
      print("%s not processed for some reason...."%(ras))

## Now calculate the output raster using all 5 of the input rasters created above.
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab5/Climate_Variables/Best_Output_2080_V3.gdb"
  print("Creating a raster summing all outputs")
  print("Creating a new raster multiplying all outputs")
  raster_calc_out = Raster("AHM_2080_out") + Raster("MAP_2080_out") + Raster("MCMT_2080_out") + Raster("MWMT_2080_out") + Raster("TASM_2080_out") + Raster("CMI_2080_out")
  mult_out = Raster("AHM_2080_out") * Raster("MAP_2080_out") * Raster("MCMT_2080_out") * Raster("MWMT_2080_out") * Raster("TASM_2080_out") * Raster("CMI_2080_out")
  outname = "SS_2080_Add"
  out_x_name = "SS_2080_Mult"
  loc = os.path.join(outgdbpath, outname)
  xname = os.path.join(outgdbpath, out_x_name)
  raster_calc_out.save(loc)
  mult_out.save(xname)
  print("%s saved as the sum of all input rasters"%(outname))
  print("%s saved as the product of all input rasters"%(out_x_name))  


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
