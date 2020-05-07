# Python lab 6 workflow for geodatabase creation

# Zack Quarterman, Western Washington university (2020)
# Python 3.4, ArcGIS PRO 2.4.1

try:
    import arcpy
    import os
    import re
## Change workspace file path as required. This is explicitly stated 3 times in this script.
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_6/Data_Lab6/Data_From_Lab5"
    arcpy.env.parallelProcessingFactor = "100%"
    workspaces = arcpy.ListWorkspaces("*", "FileGDB")
    print(workspaces)
    files = arcpy.ListFiles("*.gdb")
    print(files)
    output_gdb_path = "B:/GIS_Projects/421/Lab_6/Data_Lab6/ENVS421_WWU_Survey_Lab6.gdb"
    output_fc_name = "ENVS421_WWU_SurveyPoints"
    target_output = os.path.join(output_gdb_path, output_fc_name)
    name_dict = dict(zip(files, workspaces))
    for key, value in name_dict.items():
        print("Key = %s \nValue = %s"%(key, value))
    for item in workspaces:
        arcpy.env.workspace = item
        for fc in arcpy.ListFeatureClasses("", "POINT"):
            print(fc)
            print("Attempting to append the fc to the target....")
            #arcpy.Append_management(fc, target_output, "NO_TEST")
            print("Added %s to feature class"%(fc))
    print("Attempting new segment.....\n\n\n\n\n")
## Set up empty lists to populate with field names and types for a correct template to use later in QA QC
    corr_field_names = []
    corr_field_types = []
    corr_field_dict = {}
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_6/Data_Lab6/Data_From_Lab5"
    parent_wrk = "B:/GIS_Projects/421/Lab_6/Data_Lab6/Data_From_Lab5"
## Define a function that allows for retrevial of all keys in common with a input test value.    
    def searchKeysByVal(dict, byVal):
        keysList = []
        itemsList = dict.items()
        for item in itemsList:
            if item[1] == byVal:
                keysList.append(item[0])
        return keysList    
## Choose a good working template feature class with correct field names and data types to update a master
## dictionary with. Here I chose Askerooth_ENVS421_Lab5.gdb.   
    for item in arcpy.ListWorkspaces("*", "FileGDB"):
        print("\nChanging workspace..\n")        
        print(item)
        wrkspace = item.replace("\\", "/")
        print(wrkspace)
        arcpy.env.workspace = wrkspace
## Template input feature class with correct field name and field type path        
        if wrkspace == "B:/GIS_Projects/421/Lab_6/Data_Lab6/Data_From_Lab5/Askerooth_ENVS421_Lab5.gdb":
            print("Using %s as the template dataset for correct field names and types."%(wrkspace))
            for fc in arcpy.ListFeatureClasses("*", "Point"):
                print("Target Feature Class:\n%s"%(fc))
## Make a list of the correct fields                
                corr_fields = arcpy.ListFields(fc)
## Use list to build a dictionary as a template to test field names and data types on target fc.                 
                for field in corr_fields:
                    corr_field_dict.update({field.name: field.type})
                    print("added %s : %s as key value pair to corr_field_dict"%(field.name, field.type))
                print(corr_field_dict)
## All further analysis is still inside \\Data_From_Lab5\\        
        else:
            for fc in arcpy.ListFeatureClasses("*", "Point"):
                print("\nTarget feature class:\n%s\n---------------\nField Name : Data Type\n-------------- "%(fc))
## Make lists for the field name and data type. Doing these at the same time should mean they will have the 
## same indexing so you can zip them in a dict.
                list_name = "%s_name"%(fc)
                list_name = []
                list_type = "%s_type"%(fc)
                list_type = []
                test_dict = dict(zip())
                for field in arcpy.ListFields(fc):
                    print("%s : %s"%(field.name, field.type))
## Add field.name and field.type to their respective lists.                    
                    list_name.append(field.name)
                    list_type.append(field.type)
                    #print("This is the test_dict. Did it work?:")
                    test_dict.update({field.name: field.type})
                    #print("Test_dict_testing boiiii")
                    #print(test_dict)
## zip the two lists together in a dictionary
                    if field.name in corr_field_dict.keys():
                        print("-----%s is correct. Checking field type in fields dict..."%(field.name))
                        pass_name = str(field.name)
                        test_type = str(field.type)
                        if field.type == corr_field_dict[pass_name]:
                            print("-----Both %s and %s are correct"%(pass_name, field.type))
## Condition for if input field is correct but incorrect data type.                        
                        else:
                            print("!!!----Incorrect data type.\n-------%s (test) not equal to %s (target).\nREQUIRES ATTENTION."%(field.type, corr_field_dict[pass_name]))
## Condition for if the input field name does not match the template field name. 
## Checking if the data type matches the template dictionary with a similiar name. 
## Regex expressions might take a while to config.-----
## This condition first checks if field name = POINT_X or POINT_Y, if satisfied they will be
## skipped for further error checking because they are non-essential fields.
                    else:
                        point_search = ["POINT_X","POINT_Y"]
                        for item in point_search:
                            xy_template_name = str(item)
                            xy_test_name = str(field.name)
                            xy_match = re.match(xy_template_name, xy_test_name)
                            xy_reverse_match = re.match(xy_test_name, xy_template_name)
                            if xy_match:
                                print("-----Regex matches: ", xy_match.group())
                            elif xy_reverse_match:
                                print("-----Reverse Regex matches: ", xy_reverse_match.group())
                            else:()
    ## POTENTIALLY FLIP ORDER ON THESE
                        if field.name in point_search:
                        #if field.name == "POINT_X" or field.name == "POINT_Y": ##Still need to refine...some "POINT_X-_-_-_" Use in?
                            print("------%s is not required, therefore it will be omitted from the merge on target"%(field.name))                        
                        #elif not field.name == "POINT_X" and not field.name == "POINT_Y":
                        else:
                            print("!!!---%s is INCORRECT.\n------ %s data type unconfirmed"%(field.name, field.type))
                            common_keys = searchKeysByVal(corr_field_dict, field.type)
                            if int(len(common_keys)) == 0:
                                print("------- There are no common keys")
                                for key in corr_field_dict.keys():
                                    template_name = str(key)
                                    test_name = str(field.name)
                                    match = re.match(template_name, test_name)
                                    if match:
                                        print("Regex matches: ", match.group())
                                    else:
                                        reverse_match = re.match(test_name, template_name)
                                        if reverse_match:
                                            print("-------Regex matches: ", reverse_match.group())
                                        else:()
                            # elif int(len(common_keys)) > 0:
                            #     for ele in enumerate(common_keys):
                            #         value = str(ele)
                            #         print("-------These are target keys with the same value. Doe it match the test field name?\n--------%s"%(value))                                    
                            else:
                                for item in corr_field_types:
                                    sub_index = item.find(field.name) 
                                    print("This is the index of the substring found")
                                    if item in field.name:
                                        print("This name contains the exact name required with extra characters")
                                        print(item)
                                    else:
                                        print("%s might still be a POINT_X or POINT_Y like field..."%(field.name))
                                #fail_field_name = field.name.find()
                            #elif "POINT_X" or "POINT_Y" in field.name:
                            #if field.name in "POINT_X" or field.name in "POINT_Y": ##Still need to refine...some "POINT_X-_-_-_" Use in?
                                #print("%s is not required, therefore it will be omitted from the merge on target"%(field.name))
                        # else:
                        #     print("---!-%s is INCORRECT.\n---but %s unconfirmed"%(field.name, field.type))
                        #     common_keys = searchKeysByVal(corr_field_dict, field.type)
                        #     print("These are target keys with the same value. Doe it match the test field name?")
                        #     for ele in enumerate(common_keys):
                        #         value = str(ele)
                        #         print(common_keys, value)
                        #search_string = 
                        #searchObj = re.search( r'')
    # outpath = "F:/GIS_Projects/421/Lab_4/Data" 
    # ## Create geodtaabase for the outputs of this script
    # arcpy.CreateFileGDB_management(outpath, "Still_Outputs.gdb")
    # output_gdb = 'Still_Outputs.gdb'
    # ## Create variable for the gdb path for easy reference
    # out_gdb_path = os.path.join(outpath, output_gdb)
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
