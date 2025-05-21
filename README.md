# rhinoinside python package
Embed Rhino in CPython

```sh
pip install --user rhinoinside
```

## Requirements:
- Rhino 7, 8, 9 (WIP)
- Windows
- 64 bit version of CPython (>= 3.7)

## Join the discussion

https://discourse.mcneel.com/t/rhino-inside-python/78987

## How to use

```python
import rhinoinside
rhinoinside.load()    # this will load rhino 7 on dotnet framework (net48)
import System
import Rhino

# for now, you need to explicitly use floating point
# numbers in Point3d constructor
pts = System.Collections.Generic.List[Rhino.Geometry.Point3d]()
pts.Add(Rhino.Geometry.Point3d(0.0,0.0,0.0))
pts.Add(Rhino.Geometry.Point3d(1.0,0.0,0.0))
pts.Add(Rhino.Geometry.Point3d(1.5,2.0,0.0))

crv = Rhino.Geometry.Curve.CreateInterpolatedCurve(pts,3)
print (crv.GetLength())
```

You can pass arguments to the `.load()` function to start a different version of rhino on a specific dotnet framework

```python
# Loading Rhino 7
rhinoinside.load(7) # defaults to net48
rhinoinside.load(7, 'net48')
rhinoinside.load(r"C:\Program Files\Rhino 7\System") # defaults to net48
rhinoinside.load(r"C:\Program Files\Rhino 7\System", 'net48')

# Loading Rhino 8
rhinoinside.load(8) # defaults to net48
rhinoinside.load(8, 'net48')
rhinoinside.load(8, 'net7.0')
rhinoinside.load(8, 'net8.0')
rhinoinside.load(r"C:\Program Files\Rhino 8\System") # defaults to net48
rhinoinside.load(r"C:\Program Files\Rhino 8\System", 'net48')
rhinoinside.load(r"C:\Program Files\Rhino 8\System", 'net7.0')
rhinoinside.load(r"C:\Program Files\Rhino 8\System", 'net8.0')

# Loading Rhino 9
rhinoinside.load(9) # defaults to net48
rhinoinside.load(9, 'net48')
rhinoinside.load(9, 'net9.0')
rhinoinside.load(r"C:\Program Files\Rhino 9 WIP\System") # defaults to net48
rhinoinside.load(r"C:\Program Files\Rhino 9 WIP\System", 'net48')
rhinoinside.load(r"C:\Program Files\Rhino 9 WIP\System", 'net9.0')
```