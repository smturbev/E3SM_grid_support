#!/ascldap/users/smturbe/.conda/envs/e3sm-unified_1.11/bin/python
import sys, importlib.util


print("sys.executable:", sys.executable)
print("sys.version:", sys.version.splitlines()[0])
print("first sys.path entries:", sys.path[:6])
print("CONDA_PREFIX env:", repr(__import__('os').environ.get('CONDA_PREFIX')))
print("netCDF4 spec:", importlib.util.find_spec('netCDF4'))
