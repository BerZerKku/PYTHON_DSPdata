from distutils.core import setup
from glob import glob
import py2exe
import sys

from distutils.filelist import findall
import matplotlib

sys.path.append("C:\\Python27\\Microsoft.VC90.CRT")

data_files = [("Microsoft.VC90.CRT", glob(r'C:\Python27\Microsoft.VC90.CRT\*.*'))]
data_files.extend(matplotlib.get_py2exe_datafiles())

setup(
    console=['DSPdata.py'],
    options={
        'py2exe':{
			"compressed": 2, 
			#"bundle_files": 3,
			"includes":["sip"],
            'packages' : ['matplotlib'],
            'dll_excludes': ['libgdk-win32-2.0-0.dll',
                            'libgobject-2.0-0.dll',
                            'libgdk_pixbuf-2.0-0.dll']
		}
    },
	zipfile = "shared.lib",
    data_files = data_files
)
