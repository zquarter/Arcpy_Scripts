
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

  arcpy.env.workspace = "F:/ENVS420/Quarterman_ENVS420_Lab5/Lab5_Data"

  for item in folder:
    if item 

#----------------------Identify working directory---------

  print ("Original workspace:")
  print (os.getcwd())  # Prints the current working directory
  # Changing working directory from //Tables to //Tables/Plain
  os.chdir('C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain')
  print ("\nNew working directory:")
  print (os.getcwd())  # Prints new working directory
#-----------------------------Preprocessing the census data-------------------------
  # Opening raw census demographic csv
  df = pd.read_csv('ACS_16_5YR_B03002_with_ann.csv', header = 1)
  print (df)
  # Renaming relevant columns
  df.rename(
  	columns={
  	  "Estimate; Total:": "total_pop",
  	  "Estimate; Not Hispanic or Latino: - White alone": "NHWA",
  	  "Estimate; Hispanic or Latino: - White alone": "HWA"
  	},
  	inplace=True
  )
  print(df.dtypes)
  # Changing data type of Id2 from object to string
  df['Id2'] = df['Id2'].astype('str')
  print("Changed data type for Id2 below:")
  print(df.dtypes)
  os.chdir('C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain/Outputs')
  # Save pandas data frame to new csv with relevant columns and proper headers
  df.to_csv('dfa.csv', columns=['Id', 'Id2', 'Geography', 'total_pop', 'NHWA', 'HWA'],index=False)
  # Opening newly formatted demographic csv
  dfa = pd.read_csv('dfa.csv')
  # Writing the clean demographic csv data to xlsx file
  dfa.to_excel('Demographics_2016_KingCounty.xlsx', sheet_name='Ethnicity', index=False)  # index=True to write row index
  #
  # Repeating the same process for the poverty data
  os.chdir('C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain')
  # Opening raw census poverty csv
  pov = pd.read_csv('ACS_16_5YR_C17002_with_ann.csv', header = 1)
  print (pov)
  # Renaming relevant columns
  pov.rename(
  	columns={
  	  "Estimate; Total:": "total_pop",
  	  "Estimate; Total: - Under .50": "sub_0_50",
  	  "Estimate; Total: - .50 to .99":"f0_50to0_99",
  	  "Estimate; Total: - 1.00 to 1.24": "f1_00to1_24",
  	  "Estimate; Total: - 1.25 to 1.49": "f1_25to1_49",
  	  "Estimate; Total: - 1.50 to 1.84": "f1_50to1_84",
  	  "Estimate; Total: - 1.85 to 1.99": "f1_85to1_99",
  	  "Estimate; Total: - 2.00 and over": "eq_or_gtr_thn_2_00"
  	},
  	inplace=True
  )
  print(pov.dtypes)
  # Changing data type of Id2 from object to string
  pov['Id2'] = pov['Id2'].astype('str')
  print("Changed data type for Id2 below:")
  print(pov.dtypes)
  os.chdir('C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain/Outputs')
  # Save pandas data frame to new csv with relevant columns and proper headers
  pov.to_csv('pov.csv', 
  	columns=['Id', 'Id2', 'Geography', 'total_pop', 'sub_0_50', 'f0_50to0_99', 'f1_00to1_24', 'f1_25to1_49','f1_50to1_84','f1_85to1_99','eq_or_gtr_thn_2_00'],index=False)
  # Opening newly formatted poverty csv
  pova = pd.read_csv('pov.csv')
  # Writing the clean poverty csv data to xlsx flie
  pova.to_excel('Poverty_2016_KingCounty.xlsx', sheet_name='Rates', index=False)  # index=True to write row index
 #-----------------------------------------
  #Changing header names to comply with ArcPRO rules for tri_facilities_2016.xlsx
  os.chdir('C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain')
  tri = pd.read_excel('tri_facilities_2016.xlsx', sheet_name='tri_facilities_2016')
  print("Column headings:")
  print(tri.columns)
  cl = list(tri.columns)
  print("\n\n\n\n\n Column list of headings:")
  # Reformat column names using regex
  ncl = [re.sub("[:\-() ]","_",x) for x in cl]
  print(ncl)
  # Create dictionary with old names as keys and new names as values
  headerdict = dict(zip(cl, ncl))
  tri = tri.rename(columns = headerdict)
  print("New Column headings")
  hl = list(tri.columns)
  print(hl)
  os.chdir('C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain/Outputs')
  # Save pandas data frame to excel with edited header names
  tri.to_excel('ToxRelease_2016.xlsx', sheet_name='tri_facilities_2016', index=False)


#------------------------------------------- Importing census shapefile from vector inputs file to Vector_Inputs.gdb-------
   #arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain"
  print("Creating Vector_Inputs.gdb")
  vectorgdb_path = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs"
  gdb_name = "Vector_Inputs.gdb"
  arcpy.CreateFileGDB_management(vectorgdb_path, gdb_name)
  print("Vector_Inputs.gdb created")
  # Creating Vector_Inputs_NAD83.gdb for later projection
  projgdb = "Vector_Inputs_NAD83.gdb"
  arcpy.CreateFileGDB_management(vectorgdb_path, projgdb)
  print("Vector_Inputs_NAD83.gdb created")

  print("Importing Census shapefile from vector inputs folder to Vector_inputs.gdb...")
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs"
  in_features = ['tl_2016_53_bg.shp']
  out_location = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs.gdb"
  arcpy.FeatureClassToGeodatabase_conversion(in_features, out_location)
  print("Census shapefile successfully copied to Vector_Inputs.gdb")
  #
  # Joining 
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Tables/Plain/Outputs"
  # Defining input xlsx files to convert
  demographic_xlsx = 'Demographics_2016_KingCounty.xlsx'
  poverty_xlsx = 'Poverty_2016_KingCounty.xlsx'
  tox_xlsx = 'ToxRelease_2016.xlsx'
  # Defining output table locations
  demouttable = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Demographics_2016_KingCounty.gdb"
  povouttable = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Poverty_2016_KingCounty.gdb"
  toxouttable = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/ToxRelease_2016.gdb" 
  # Converting excel files to table (dbf format)
  print("Converting demographic xlsx to table")
  arcpy.ExcelToTable_conversion(demographic_xlsx, demouttable)
  print("Converting poverty xlsx to table")
  arcpy.ExcelToTable_conversion(poverty_xlsx, povouttable)
  print("Converting tox xlsx to table")
  arcpy.ExcelToTable_conversion(tox_xlsx, toxouttable)

  print("Demographic, Poverty, and Toxic xlsx files converted to tables dbf successfully")
  #
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs"
  demtable = "Demographics_2016_KingCounty.dbf"
  povtable = "Poverty_2016_KingCounty.dbf"
  toxtable = "ToxRelease_2016.dbf"
  # Field variables for demographic and poverty tables to edit
  fieldname = "Id22"
  expression = "!Id2!"
  dropfield = "Id2"
  # Field variables for toxic table to exit
  toxfieldname = "FRS_ID2"
  toxexpression = "!FRS_ID!"
  toxdropfield = "FRS_ID"
  print("Adding field with string data format and duplicating 'Id2', then removing the original for demographic table")
  arcpy.AddField_management(demtable, fieldname, "TEXT")
  arcpy.CalculateField_management(demtable, fieldname, expression, "PYTHON3")
  arcpy.DeleteField_management(demtable, dropfield)
  print("Adding field with string data format and duplicating 'Id2', then removing the original for poverty table")
  arcpy.AddField_management(povtable, fieldname, "TEXT")
  arcpy.CalculateField_management(povtable, fieldname, expression, "PYTHON3")
  arcpy.DeleteField_management(povtable, dropfield)
  print("Adding field with string data format and duplicating 'FRS_ID', then removing the original for toxic table")
  arcpy.AddField_management(toxtable, toxfieldname, "TEXT")
  arcpy.CalculateField_management(toxtable, toxfieldname, toxexpression, "PYTHON3")
  arcpy.DeleteField_management(toxtable, toxdropfield)
  print("Changing id data type to text in Demographic, Poverty, and Toxic release tables was successful")

 #-------------Joining newly formatted tables to the census shapefile--------------------
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs.gdb"
  censhp = 'tl_2016_53_bg.shp'
  demdbf = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Demographics_2016_KingCounty.dbf"
  povdbf = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Poverty_2016_KingCounty.dbf"
  infield = "GEOID"
  join_field = "Id22"
  print("Joining demographic table with census shapefile based on GEOID and Id22")
  arcpy.JoinField_management(censhp, infield, demdbf, join_field)
  print("Joining poverty table with census shapefile based on GEOID and Id22")
  arcpy.JoinField_management(censhp, infield, povdbf, join_field)
  print("Joins complete!")

# ------------------Creating new point feature class from toxic release table ----------------
  print("Creating new point feature class from toxic release inventory table")
  arcpy.env.workspace = r"C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs.gdb"
  toxdbf = r"C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/ToxRelease_2016.dbf"
  toxoutput = "Toxic_Release_Inventory_2016"
  x_coords = "Longitude"
  y_coords = "Latitude"
  # Create Feature class 
  #arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("WGS84")
  # GCS_WGS_1984 factory code = 4326
  # GCS_WGS_1984 vertical coordinate system factory code = 115700
  arcpy.management.XYTableToPoint(toxdbf, toxoutput, x_coords, y_coords, "", arcpy.SpatialReference(4326, 115700))
  print("Successfully created Toxic_Release_Inventory_2016 in Vector_Inputs.gdb")

#---------Importing landuse, waterbodies, and superfund shp's into Vector_Inputs.gdb----------
  print("Exporting landuse, waterbodies, and superfund shapefiles to Vector_Inputs.gdb to set up batch project")
  arcpy.env.workspace = r"C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs"
  in_shp = ['superfund_npl.shp', 'Waterbodies.shp', 'landuse_zoning.shp']
  arcpy.FeatureClassToGeodatabase_conversion(in_shp, out_location)
  print("Successfully exported landuse, waterbodies, and superfund shapefiles to Vector_Inputs.gdb")

#----------------Batch project contents of Vector_Inputs.gdb----------------
  outworkspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb" 
  arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs.gdb"
  for infc in arcpy.ListFeatureClasses():
	# Determine if the input has a defined coordinate system, can't project it if it does not
    dsc = arcpy.Describe(infc)
    if dsc.spatialReference.Name == "Unknown":
        print('skipped this fc due to undefined coordinate system: ' + infc)
    else:
        #NAD_1983_HARN_StatePlane_ Washington_South_FIPS_4602
        from_sr = arcpy.Describe(infc).spatialReference
        outfc = os.path.join(outworkspace, infc) 
        outCS = arcpy.SpatialReference("C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/NAD_1983_HARN_StatePlane_Washington_South_FIPS_4602_Meters.prj")
        print("Input spatial reference for %s is:\n %s"%(infc, from_sr))
        exte = arcpy.Describe(infc).extent
        print("Spatial extent of impot:")
        print(exte)
        trans_list = arcpy.ListTransformations(from_sr, outCS, exte)
        print("List of transformations here:")
        print(trans_list)
        print("Projecting: %s  into NAD_1983_HARN_StatePlane_ Washington_South_FIPS_4602_Meters" %(infc))
        if not trans_list:
        	arcpy.Project_management(infc, outfc, outCS)
        	print("No transformation necessary, %s projected"%(infc))
        	
        else:
        	trans = trans_list[0]
        	arcpy.Project_management(infc, outfc, outCS, trans)
        	print(infc + '   Projected!')
#----------------------------------------------PART B--------------
  # Creating datasets that only reside within king county (TRI, Superfund sites, and census block groups)
  # print("-------------------------PART B--------------------------------------------------------------------------\n\n")
  # print("Selecting areas of TRI, Superfund sites, and Census block groups that are inside of King County")
  # arcpy.env.workspace = "C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/Vector_Inputs_NAD83.gdb" 
  # arcpy.env.outputCoordinateSystem = arcpy.SpatialReference("C:/GIS_Projects/420/Quarterman_ENVS420_Lab4/Vector_Inputs/NAD_1983_HARN_StatePlane_Washington_South_FIPS_4602_Meters.prj")
  # # Select features, then copy features managment to export to new feature class only containing King County Data
  # tracts_where = """ "COUNTYFP" = '033'"""
  # super_where = """ "COUNTY" = 'KING'"""
  # tri_where = """ "County" = 'KING'"""
  # release_where = """ "Total_rele" <> '0'"""
  # print("Selecting tracts in tl_2016_53_bg where: %s"%(tracts_where))
  # king_tracts = arcpy.SelectLayerByAttribute_management("tl_2016_53_bg", "NEW_SELECTION", tracts_where)
  # arcpy.CopyFeatures_management(king_tracts, 'King_County_2016_Census_Tracts')
  # print("King_County_2016_Census_Tracts created in Vector_Inputs_NAD83.gdb\n")
  # print("Selecting points in superfund_npl where: %s"%(super_where))
  # king_super = arcpy.SelectLayerByAttribute_management("superfund_npl", "NEW_SELECTION", super_where)
  # arcpy.CopyFeatures_management(king_super, 'King_County_Superfund_Sites')
  # print("King_County_Superfund_Sites created in Vector_Inputs_NAD83.gdb\n")
  # print("Selecting points in Toxic_Release_Inventory_2016 where: %s"%(tri_where))
  # king_tri = arcpy.SelectLayerByAttribute_management("Toxic_Release_Inventory_2016", "NEW_SELECTION", tri_where)
  # arcpy.SelectLayerByAttribute_management(king_tri, "SUBSET_SELECTION", release_where)
  # arcpy.CopyFeatures_management(king_tri, 'King_County_Toxic_Release_Inventory')
  # print("King_County_Toxic_Release_Inventory created in Vector_Inputs_NAD83.gdb\n")
  # newfcs = arcpy.ListFeatureClasses()
  # print("Feature classes contained in Vector_Inputs_NAD83.gdb:\n %s"%(newfcs))



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
