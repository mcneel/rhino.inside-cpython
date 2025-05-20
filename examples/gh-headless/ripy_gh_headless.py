import sys
sys.path.append(r"C:\Users\ein\gits\rhino.inside-cpython")

# requirements: rhinoinside
import os
import rhinoinside
rhinoinside.load()


def gh_headless():
    """Loads a grasshopper file in headleass mode"""
    import Rhino # type: ignore

    #Start grasshopper in "headless" mode
    plugin = Rhino.RhinoApp.GetPlugInObject("Grasshopper")
    if not plugin:
        raise Exception("Failed to load Grasshopper")

    plugin.RunHeadless()
    import Grasshopper # type: ignore

    #f ile path to .gh file to evaluate
    this_dir = os.path.dirname(__file__)
    gh_def_path = os.path.join(this_dir,"simple_def.gh")

    if not os.path.isfile(gh_def_path):
        raise Exception("Failed to find {gh_def_path}")

    io = Grasshopper.Kernel.GH_DocumentIO()

    if not io.Open(gh_def_path):
        raise Exception("Failed to load Grasshopper file from {gh_def_path}")

    doc = io.Document
    doc.Enabled = True

    for obj in doc.Objects:
        try:
            param = Grasshopper.Kernel.IGH_Param(obj)
            if param.NickName == "CollectMe":
                param.CollectData()
                param.ComputeData()

                for item in param.VolatileData.AllData(True):
                    try:
                        success, line = item.CastTo(Rhino.Geometry.Line())
                        if success:
                            return line
                    except:
                        pass
        except:
            continue


if __name__ == "__main__":
    line = gh_headless()
    print("Got a Line: {}".format(line))
