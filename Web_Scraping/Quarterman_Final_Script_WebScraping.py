#Python 3.6 (default, May 15 2013, 22:43:36) [MSC v.1500 32 bit (Intel)] on win32

#********************************************************************************************************************
# Name:              Quarterman_Final_Script_WebScraping.py
# Created:           6/13/2019 12:00
# Version:           ArcGIS 10.4.1
# Author:            Zack Qarterman
# Description:       This script uses a dataset obtained from the EPA website that contains all the 303d listed
#                    impaired streams and rivers in all 50 states. At over 300,000 features I decided to use the
#                    feature class to feature class conversion arcpy module to create a new feature class inside 
#                    of a new geodatabase with only features where "GEOSTATE" = 'WA'. This new feature class is 
#                    named "WA_303d" and is housed in the created Output.gdb. It has roughly 2,800 features and
#                    thus makes the process of data scraping much more manageable. Recently I have become 
#                    fascinated with the concept of data/web scraping and when searching for datasets to use I 
#                    saw an opportunity to get some practice with the built in urllib module. In WA_303d there 
#                    is a "FEATUREDETAILURL" field containing a unique URL for each record in the features 
#                    attribute table. 
#                    
#                    I have learned that web scraping can have detrimental effects on the hosts
#                    servers due to the quantity and frequency of requests, so having a dataset where each URL
#                    is unique decreased my chances of unintentionally causing a ruckus and having to change my
#                    project. I figured since it was public information in individual locations I would not be
#                    raising any red flags. 
#
#                    Each website is written in the same HTML code and therefore I was able to search for a 
#                    specific pattern in the code where my desired data was. For each row in the attribute table
#                    I used urllib.request.Request(url) and urllib.request.urlopen() to access data on the web page
#                    and then used re.findall(r'<td align="left">(.*?)</td>' to find all occurrences of table cells
#                    on the web page. The water quality parameters and statuses of their TMDL's were listed in HTML
#                    tables so It made targeting the data easier. The order of table from left to right was: 
#                    parameter, parameter category, and TMDL status. Using the indexing positions of the TMDL
#                    status, I was able to subtract 2 from the index value to get the parameter that either had
#                    a TMDL completed or still needed a TMDL. I added two fields (TMDL_Needed and TMDL_Completed)
#                    to  WA_303d to populate based on the web page content. For sites that had multiple parameters 
#                    for either category I used a " | " to separate them when adding to the field. Some of the 
#                    parameters were IUPAC chemical names containing commas and hyphens so my options were limited.
#                    
#                    Now instead of having to open the URl for each record to see what parameters are causing 
#                    impairment there are fields indicating which have been addressed and still require a TMDL.
#                    
#                    Depending on your Internet connection, this script can take quite a while to harvest data from 
#                    nearly 3,000 web pages. However, I encourage  you to run it for a couple minutes and see it 
#                    in action.
#
#                    ******MAY REQUIRE ROTATION OF WEB CREDENTIALS and/or PROXY IPs FOR FULL COMPLETION*********   
#                    
#                    Data Source: https://www.epa.gov/waterdata/waters-geospatial-data-downloads
#                    Under: 303(d) Listed Impaired Waters NHDPlus Indexed Dataset with Program Attributes:
#                     "ESRI 10.x File Geodatabase"

#                      
#                    
#                    
#---------------------------------------------------------------------------
#Import modules into the script
import sys, string, os, arcpy, traceback, datetime, math, urllib, datetime, re, urllib.request
from arcpy import env
from os import path
from urllib.request import urlopen

# Begin deployment of verbose error catcher....

try:
  # Variable for timestamp
  start = datetime.datetime.now()
  print ("Script started : ")
  print (start.strftime("%Y-%m-%d %H:%M:%S"))
# Geodatabase workspace and target feature class
  arcpy.env.workspace = "F:\ENVS423\Final_Project\EPA_303d\rad_303d_20150501.gdb"
  gdb = "F:\ENVS423\Final_Project\EPA_303d\rad_303d_20150501.gdb"
  fc_in = "F:\\ENVS423\\Final_Project\\EPA_303d\\rad_303d_20150501.gdb\\rad_303d_l"
  # Make output folder to house all new created features 
  output_folder = "F:\ENVS423\Final_Project\Final_output"
  os.mkdir(output_folder)
  # Make new geodatabase within the new folder to house the output data for just WA streams 
  out_geo = "Output.gdb"
  arcpy.CreateFileGDB_management(output_folder,out_geo)
  out_geo_path = "F:\ENVS423\Final_Project\Final_output\Output.gdb"
  # Select only WA streams/waterbodies from feature class to export as new feature class
  arcpy.env.workspace = "F:\ENVS423\Final_Project\Final_output\Output.gdb"
  arcpy.FeatureClassToFeatureClass_conversion(fc_in,out_geo_path,"WA_303d","GEOGSTATE = 'WA'")
  # Make variable for output path
  WA_303d_path = os.path.join(out_geo_path,"WA_303d")
  # Add 2 fields to new feature class
  arcpy.AddField_management("WA_303d", "TMDL_NEEDED","TEXT","","","","TMDL_Needed","NULLABLE","")
  print( "TMDL_Needed field added to WA_303d feature class")
  arcpy.AddField_management("WA_303d","TMDL_COMPLETED","TEXT","","","","TMDL_Completed","NULLABLE","")
  print("TMDL_Completed field added to WA_303d feature class")
# ------------------------------------------------------------- WA features prepped for analysis--------------
  WA_303d_row_count = arcpy.GetCount_management("WA_303d") # 2764 records---> Might be faster to just use static number for counter 
  counter = 0
  print("Number of records in WA_303d : %s"%(WA_303d_row_count))
  with arcpy.da.UpdateCursor(WA_303d_path,["SOURCE_ORIGINATOR","SOURCE_FEATUREID","GEOGSTATE","FEATUREDETAILURL","TMDL_NEEDED","TMDL_COMPLETED"]) as cursor:
    for row in cursor:
      counter = counter + 1
      # Printing general information for each row. Including URL so that if web access issues arise the URL that triggered it
      # can be analyzed.
      print("%s of %s completed"%(counter,WA_303d_row_count))
      print("Source_Originator = %s , Source_FeatureID = %s , GeogState = %s ------------"%(row[0],row[1],row[2]))
      url = row[3]
      print("URL : %s\n"%(url))
      print("Accessing server...")
      # Functions for accessing data from URL
      req = urllib.request.Request(url)
      resp = urllib.request.urlopen(req)
      respData = resp.read()
      # Can target different elements on site using different string in re.findall()
      table_rows = re.findall(r'<td align="left">(.*?)</td>',str(respData))
      # table_rows contains values other than water quality parameters and TMDl status, the list is sorted below:
#--------------------------------------------------------------- Data from URL loaded-------------------------
# Analyzing page for "TMDl needed" ---------------------------------------------------------------------------      
      needed_count = table_rows.count('TMDL needed')
      if needed_count > 0:
        needed_indices = [i for i, x in enumerate(table_rows) if x == "TMDL needed"]
        #print("TMDL needed index locations : %s"%(needed_indices))
        need_last = needed_indices[-1]
        need_trim = need_last + 1
        need_param_index = []
        for i in needed_indices:
          parameter = i-2
          need_param_index.append(parameter)
        #print("TMDL needed parameters index values : %s"%(need_param_index))
        need_param = []
        for i in need_param_index:
          value = table_rows[int(i)]
          need_param.append(value)
        #print("TMDL needed parameters : %s"%(need_param))
        need_field_entry = ' | '.join([str(elem) for elem in need_param])
        print("TMDL needed field entry : %s"%(need_field_entry)) 
        row[4] = need_field_entry
      else: 
        needed_count = 0
        print("TMDL needed   NOT FOUND")
        need_field_entry = "<Null>"      
        row[4] = need_field_entry
# Analyzing page for "TMDL completed" -------------------------------------------------------------------------   
      completed_count = table_rows.count('TMDL completed')
      if completed_count > 0:
        completed_indices = [i for i,x in enumerate(table_rows) if x == "TMDL completed"]
        #print("TMDL completed index locations : %s"%(completed_indices))
        comp_last = completed_indices[-1]
        comp_trim = comp_last + 1
        comp_param_index = []
        for i in completed_indices:
          parameter = i-2
          comp_param_index.append(parameter)
        #print("TMDL needed parameters index values : %s"%(comp_param_index))
        comp_param = []
        for i in comp_param_index:
          value = table_rows[int(i)]
          comp_param.append(value)
        #print("TMDL needed parameters : %s"%(comp_param))
        comp_field_entry = ' | '.join([str(elem) for elem in comp_param])
        print("TMDL needed field entry : %s"%(comp_field_entry)) 
        row[5] = comp_field_entry     
      else:
        completed_count = 0
        print("TMDL completed   NOT FOUND")
        comp_field_entry = "<Null>"
        row[5] = comp_field_entry
      cursor.updateRow(row)
      print("Fields updated. -------------------------------------------------------------------------------------------------\n")
# Calculate total processing time
  end = datetime.datetime.now()
  total_time = end - start
  print ("Finished processing.")
  print(end.strftime("%Y-%m-%d %H:%M:%S"))
  print(" Total time elapsed : ")
  print (total_time.strftime("%Y-%m-%d %H:%M:%S")) 
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
