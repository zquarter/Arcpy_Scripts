
## Python lab 6 workflow 
##
## Zack Quarterman, Western Washington university (2020)
## Python 3.6.9, ArcGIS PRO 2.5.0
##
## This tool is designed to check the name and data type of fields from attribute tables before merging multiple
## feature classes together. Its set up to look in a directory containing multiple geodatabases. In this application
## all geodatabases contain a single point feature class that will be examined.
##
## This can be run multiple times to determine if the edits were successful. It will not return errors if the data
## is in the desired format.
## 
## The last ~10 lines are for appending the feature classes to the target feature class. So if you are wanting to just
## edit the fields, comment out the last section under the -_-_-_-_-_ line.
## 
## Change workspace file path as needed. Works on the contents inside uncompressed .zip for lab 6.
## Explicit workspace/file path on lines: 24, 30, 48, 298, 301, 302 
try:
    import arcpy
    import os
    import re
## Change workspace file path as required. This is explicitly stated 3 times in this script.
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_6/Data_Lab6/Data_From_Lab5"
    arcpy.env.parallelProcessingFactor = "100%"
## Set up empty lists to populate with field names and types for a correct template to use later in QA QC
    corr_field_names = []
    corr_field_types = []
    corr_field_dict = {}
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
                    test_dict.update({field.name: field.type})
## zip the two lists together in a dictionary
                    if field.name in corr_field_dict.keys():
                        print("-----%s is correct. Checking field type in fields dict..."%(field.name))
                        pass_name = str(field.name)
                        test_type = str(field.type)
                        if field.type == corr_field_dict[pass_name]:
                            print("-----%s is correct"%(field.type))
## Condition for if input field is correct but incorrect data type.                        
                        else:
                            field_values_transfer = []
                            print("!!!----Incorrect data type.\n-------%s (test) not equal to %s (target).\n------- REQUIRES ATTENTION."%(field.type, corr_field_dict[pass_name]))
                            print("This is the scenario where the name is correct but the data type is not...\n Using a search cursor to populate a list of values for this field")
                            with arcpy.da.SearchCursor(fc, pass_name) as cursor:
                                for row in cursor:
                                    field_values_transfer.append(row[0])
                            print("This is a list of values with incorrect data type but correct values to transfer:\n%s"%(field_values_transfer))
                            new_field_type = str(corr_field_dict[pass_name])
                            print(new_field_type)
                            print("Adding field with temp name to transfer values to correct data type")
                            temp_name = "TEMP_%s"%(pass_name)
                            arcpy.AddField_management(fc, temp_name, new_field_type, "", "", "", "", "", "", "")
                            print("%s field added to attribute table."%(temp_name))
                            field_list = [pass_name, temp_name]
                            ## row[0], row[1]
                            print(field_list)
                            with arcpy.da.UpdateCursor(fc, field_list) as cursor:
                                for row in cursor:
                                    print("Transfering %s to value of %s"%(row[0], row[1]))
                                    transfer_value = int(row[0])
                                    row[1] = transfer_value
                                    cursor.updateRow(row)
                            print("Values transfered:\nDeleting field containing incorrect data type.\nChanging name of %s to %s"%(temp_name, pass_name))
                            arcpy.DeleteField_management(fc, pass_name)
                            print("The original %s field has been deleted from the attribute table"%(pass_name))
                            arcpy.AlterField_management(fc, temp_name, pass_name, pass_name, "", "", "", "")
                            print("Field name %s has been changed to %s and contains the correct data type"%(temp_name, pass_name))
                            arcpy.DeleteField_management(fc, temp_name)
## Condition for if the input field name does not match the template field name. 
## Checking if the data type matches the template dictionary with a similiar name. 
## Regex expressions might take a while to config.-----
## This condition first checks if field name = POINT_X or POINT_Y, if satisfied they will be
## skipped for further error checking because they are non-essential fields.
##                  
## This condition is if the field name is incorrect...
                    else:
                        point_search = ["POINT_X","POINT_Y"]
                        if field.name in point_search:
                            print("------%s is not required, therefore it will be omitted from the merge on target"%(field.name))                                           
                        else:
                            print("!!!---%s is INCORRECT.\n------ %s data type unconfirmed"%(field.name, field.type))
                            common_keys = searchKeysByVal(corr_field_dict, field.type)
                            ## Common keys is an artifact of a failed script structure but in this case its serving as a check 
                            ## like "if something or nothing exists": continue...
                            if int(len(common_keys)) >= 0:
                                print("------- There are no common keys, looking deeper...")
                                A_match_list = []
                                B_match_list = []
                                snip_match_list = []
                                for key in corr_field_dict.keys():
                                    ## Good field name
                                    template_name = key #str(key)
                                    ## Field name being tested
                                    test_name = field.name #str(field.name)
                                    ## End index of test name
                                    ending = int(len(test_name) + 1)
                                    ## [-8:-1] of test name
                                    middle = int(ending - 8)
                                    ## Didn't want to do this, but this takes the last 8 characters of the test name
                                    snip_test_name = test_name[middle:ending]
                    ## Regex expressions comparing the test field name and the template field name                
                                    bingo = re.search(template_name, test_name)
                                    reverse_bingo = re.search(test_name, template_name)
                                    snip_bingo = re.search(snip_test_name, template_name)
                    ## Bingo represents if the template name is found INDISE the test name
                                    if bingo:
                                        print("----A--------Regex matches: ", bingo.group())
                                        m_g_str = str(bingo.group())
                                        print("%s should be renamed to: %s"%(test_name, template_name))
                                        A_match_list.append(template_name)
                                        print("Match: %s added to A_match_list"%(template_name))
                    ## reverse_bingo represents if the test name is found INSIDE the template name
                                    elif reverse_bingo:
                                        print("---B----Regex matches: ", reverse_bingo.group())
                                        rm_g_str = str(reverse_bingo.group())
                                        print("%s should be renamed to: %s"%(test_name, template_name))
                                        B_match_list.append(template_name)
                                        print("Match: %s added to B_match_list"%(template_name))
                    ## snip_bingo represents if the last 10 characters in the test name are found INSIDE the template name                
                                    elif snip_bingo:
                                        print("-_-_-_-_-_-_-_-Regex matches: ", snip_bingo.group())
                                        rm_8_str = str(snip_bingo.group())
                                        print("%s should be renamed to : %s"%(test_name, template_name))
                                        snip_match_list.append(template_name)
                                        print("Match: %s added to snip_match_list"%(template_name))
                                    else:()
                    ## If there are multiple matches in the bingo regex. This was caused by the "Noise", "NoiseComment", "Safety", and "SafetyComment"
                    ## fields. the A_match_list would only contain multiple values when checking if the template fields were in "NoiseComment" or "SafetyComment".
                    ## The template fields that matched these were Noise, Noisecomment, Safety, and Safetycomment.            
                                if len(A_match_list) > 1:
                                    field_values_transfer = []
                                    replacement_name = str(A_match_list[1])
                                    print("The correct replacement name is %s"%(replacement_name))
                                    incorr_name = str(field.name)
                                    with arcpy.da.SearchCursor(fc, incorr_name) as cursor:
                                        for row in cursor:
                                            field_values_transfer.append(row[0])
                                    print("This is a list of values with incorrect data type but correct values to transfer:\n%s"%(field_values_transfer))
                                    new_field_type = str(corr_field_dict[replacement_name])
                                    print(new_field_type)
                                    print("Adding field with temp name to transfer values to correct data type")
                                    arcpy.AddField_management(fc, replacement_name, new_field_type, "", "", "", "", "", "", "")
                                    print("%s field added to attribute table."%(replacement_name))
                                    field_list = [incorr_name, replacement_name]
                                    ## row[0], row[1]
                                    print(field_list)
                                    with arcpy.da.UpdateCursor(fc, field_list) as cursor:
                                        for row in cursor:
                                            print("Transfering %s to value of %s"%(row[0], row[1]))
                                            transfer_value = row[0]
                                            row[1] = transfer_value
                                            cursor.updateRow(row)
                                    arcpy.DeleteField_management(fc, incorr_name)
                                    print("The original %s field has been deleted from the attribute table"%(incorr_name))
                    ## The list only had one value for the shorter fields that would show up in other checks. This worked for Noise and Safety.            
                                elif len(A_match_list) == 1:
                                    field_values_transfer = []
                                    replacement_name = str(A_match_list[0])
                                    print("The correct replacement name is %s"%(replacement_name))
                                    incorr_name = str(field.name)
                                    with arcpy.da.SearchCursor(fc, incorr_name) as cursor:
                                        for row in cursor:
                                            field_values_transfer.append(row[0])
                                    print("This is a list of values with incorrect data type but correct values to transfer:\n%s"%(field_values_transfer))
                                    new_field_type = str(corr_field_dict[replacement_name])
                                    print(new_field_type)
                                    print("Adding field with temp name to transfer values to correct data type")
                                    arcpy.AddField_management(fc, replacement_name, new_field_type, "", "", "", "", "", "", "")
                                    print("%s field added to attribute table."%(replacement_name))
                                    field_list = [incorr_name, replacement_name]
                                    ## row[0], row[1]
                                    print(field_list)
                                    with arcpy.da.UpdateCursor(fc, field_list) as cursor:
                                        for row in cursor:
                                            print("Transfering %s to value of %s"%(row[0], row[1]))
                                            transfer_value = row[0]
                                            row[1] = transfer_value
                                            cursor.updateRow(row)
                                    arcpy.DeleteField_management(fc, incorr_name)
                                    print("The original %s field has been deleted from the attribute table"%(incorr_name))
                    ## If the test name was found INSIDE the template name (fields missing "_ID" or other small snippets)            
                                elif len(B_match_list) == 1:    
                                    field_values_transfer = []
                                    replacement_name = str(B_match_list[0])
                                    print("The correct replacement name is %s"%(replacement_name))
                                    incorr_name = str(field.name)
                                    with arcpy.da.SearchCursor(fc, incorr_name) as cursor:
                                        for row in cursor:
                                            field_values_transfer.append(row[0])
                                    print("This is a list of values with incorrect data type but correct values to transfer:\n%s"%(field_values_transfer))
                                    new_field_type = str(corr_field_dict[replacement_name])
                                    print(new_field_type)
                                    print("Adding field with temp name to transfer values to correct data type")
                                    arcpy.AddField_management(fc, replacement_name, new_field_type, "", "", "", "", "", "", "")
                                    print("%s field added to attribute table."%(replacement_name))
                                    field_list = [incorr_name, replacement_name]
                                    ## row[0], row[1]
                                    print(field_list)
                                    with arcpy.da.UpdateCursor(fc, field_list) as cursor:
                                        for row in cursor:
                                            print("Transfering %s to value of %s"%(row[0], row[1]))
                                            transfer_value = row[0]
                                            row[1] = transfer_value
                                            cursor.updateRow(row)
                                    arcpy.DeleteField_management(fc, incorr_name)
                                    print("The original %s field has been deleted from the attribute table"%(incorr_name))
                    ## By this point I was targeting the fields with misspellings ex: "SurvreyDateTime"            
                                elif len(snip_match_list) == 1:    
                                    field_values_transfer = []
                                    replacement_name = str(snip_match_list[0])
                                    print("The correct replacement name is %s"%(replacement_name))
                                    incorr_name = str(field.name)
                                    with arcpy.da.SearchCursor(fc, incorr_name) as cursor:
                                        for row in cursor:
                                            field_values_transfer.append(row[0])
                                    print("This is a list of values with incorrect data type but correct values to transfer:\n%s"%(field_values_transfer))
                                    new_field_type = str(corr_field_dict[replacement_name])
                                    print(new_field_type)
                                    print("Adding field with temp name to transfer values to correct data type")
                                    arcpy.AddField_management(fc, replacement_name, new_field_type, "", "", "", "", "", "", "")
                                    print("%s field added to attribute table."%(replacement_name))
                                    field_list = [incorr_name, replacement_name]
                                    ## row[0], row[1]
                                    print(field_list)
                                    with arcpy.da.UpdateCursor(fc, field_list) as cursor:
                                        for row in cursor:
                                            print("Transfering %s to value of %s"%(row[0], row[1]))
                                            transfer_value = row[0]
                                            row[1] = transfer_value
                                            cursor.updateRow(row)
                                    arcpy.DeleteField_management(fc, incorr_name)
                                    print("The original %s field has been deleted from the attribute table"%(incorr_name))                       
                                else:()
                    ## This is for catching the nonconforming field names that contain the POINT_x and POINT_y names.
                    ## No further action is requried because they will not be used in the output.
                                for item in point_search:
                                    xy_template_name = str(item)
                                    xy_test_name = str(field.name)
                                    xy_match = re.search(xy_template_name, xy_test_name)
                                    xy_reverse_match = re.search(xy_test_name, xy_template_name)
                                    if xy_match:
                                        print("--C----- Regex matches: ", xy_match.group())
                                        print("--------- %s is not required, therefore it will be omitted from the merge on target"%(field.name))  
                                    elif xy_reverse_match:
                                        print("--D----- Reverse Regex matches: ", xy_reverse_match.group())
                                        print("--------- %s is not required, therefore it will be omitted from the merge on target"%(field.name))  
                                    else:()
                                                #print("CHECK HERE \n\n\n")
                                print("\nMoving on...\n")
                            else:()
    print("\n\nQA / QC Complete!\n\n")
##-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_
##                              Section of script where the edited feature classes are appended to the master fc
    arcpy.env.workspace = "B:/GIS_Projects/421/Lab_6/Data_Lab6/Data_From_Lab5"
    arcpy.env.parallelProcessingFactor = "100%"
    workspaces = arcpy.ListWorkspaces("*", "FileGDB")
    output_gdb_path = "B:/GIS_Projects/421/Lab_6/Data_Lab6/ENVS421_WWU_Survey_Lab6.gdb"
    output_fc_name = "ENVS421_WWU_SurveyPoints"
    target_output = os.path.join(output_gdb_path, output_fc_name)
    print("Appending items from workspaces to %s\n\n"%(output_fc_name))
    for item in workspaces:
        arcpy.env.workspace = item
        arcpy.env.parallelProcessingFactor = "100%"
        for fc in arcpy.ListFeatureClasses("", "POINT"):
            print(fc)
            print("Attempting to append the fc to the target....")
            arcpy.Append_management(fc, target_output, "NO_TEST")
            print("Added %s to feature class\n"%(fc))
    print("\n\nAll items added to %s."%(output_fc_name))

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
