import rhinoinside
rhinoinside.load()
import os

# bring Rhino library from rhinoinside module
# in order to have RhinoCore loaded in the same context.
Rhino = rhinoinside.Rhino

def gh_headless():
    """ Loads a grasshopper file in headleass mode"""

    #Start grasshopper in "headless" mode
    pluginObject = Rhino.RhinoApp.GetPlugInObject("Grasshopper")
    if pluginObject:
        pluginObject.RunHeadless()
    else: return

    import Grasshopper

    #file path to .gh file to evaluate
    filePath =(os.path.join(os.getcwd(),"simple_def.gh"))

    if not os.path.isfile(filePath):
        print ("incorrect file path")
        return

    io = Grasshopper.Kernel.GH_DocumentIO()

    if not io.Open(filePath):
        print("File loading failed.")
    else:
        doc = io.Document
        doc.Enabled = True

        for obj in doc.Objects:
            try:
                param = Grasshopper.Kernel.IGH_Param(obj)
            except:
                continue

            #look for param with nickname "CollectMe"
            if param.NickName == "CollectMe":
                param.CollectData()
                param.ComputeData()

                for item in param.VolatileData.AllData(True):
                    try:
                        success, line = item.CastTo(Rhino.Geometry.Line())
                        if success: print("Got a Line: {}".format(line))
                    except:
                        pass

if __name__ == "__main__":
    gh_headless()
