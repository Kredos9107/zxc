import os, runpy, sys
from pathlib import Path
def setxattr(path, name, value):
    with open(str(path) + ':' + name, 'wb') as stream:
        stream.write(value)
def getxattr(path, name):
    with open(str(path) + ':' + name, 'rb') as stream:
        return stream.read()
os.setxattr = setxattr
os.getxattr = getxattr
helper = Path(__file__).with_name('library_file_transfer.py')
sys.argv[0] = str(helper)
runpy.run_path(str(helper), run_name='__main__')
