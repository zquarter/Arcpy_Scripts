try:
  
    import arcpy
    import os

    arcpy.env.workspace = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    workspace_path = "B:/GIS_Projects/SP_Wildfire/Reprocessing/Workspace"
    arcpy.env.parallelProcessingFactor = "100%"
    geodatabases = arcpy.ListWorkspaces("*", "FileGDB")
    for gdb in geodatabases:
        arcpy.env.workspace = workspace_path
        print("\n\n-------------%s-------------"%(gdb))
        gdb_path = os.path.join(workspace_path, gdb)
        arcpy.env.workspace = gdb_path
        contents = arcpy.ListDatasets("*", "All")
        feature_classes = arcpy.ListFeatureClasses()
        print("%s contains feature classes: %s"%(gdb, feature_classes))
        print("%s contains datasets: %s"%(gdb, contents))
        for item in feature_classes:
            print("%s ---------------------"%(item))
            spatial_ref = arcpy.Describe(item).spatialReference
            name = spatial_ref.name
            proj_name = spatial_ref.projectionName
            proj_code = spatial_ref.projectionCode
            fac_code = spatial_ref.factoryCode
            linear_unit = spatial_ref.linearUnitName
            central_meridian = spatial_ref.centralMeridian
            print("Name: %s"%(name))
            print("Projection Name: %s"%(proj_name))
            print("Projection Code: %s"%(proj_code))
            print("Factory code: %s"%(fac_code))
            print("Linear unit name: %s"%(linear_unit))
            print("Central Meridian: %s"%(central_meridian))
        for item in contents:
            print("%s ---------------------"%(item))
            spatial_ref = arcpy.Describe(item).spatialReference
            name = spatial_ref.name
            proj_name = spatial_ref.projectionName
            proj_code = spatial_ref.projectionCode
            fac_code = spatial_ref.factoryCode
            linear_unit = spatial_ref.linearUnitName
            central_meridian = spatial_ref.centralMeridian
            print("Name: %s"%(name))
            print("Projection Name: %s"%(proj_name))
            print("Projection Code: %s"%(proj_code))
            print("Factory code: %s"%(fac_code))
            print("Linear unit name: %s"%(linear_unit))
            print("Central Meridian: %s"%(central_meridian))
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
    print(pymsg + "\n")
    print(msgs)
# End deployment of verbose error catcher......
print("\n\n--> Finished Script... ")
#end_time = datetime.now()
#print("Duration: {}".format(end_time - start_time))
