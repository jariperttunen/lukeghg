import glob
import setuptools
from setuptools import setup
setup(name='lukeghg',
      version='1.0',
      description='LUKE GHG Inventory Support Tools',
      author='Jari Perttunen',
      author_email='jari.perttunen@luke.fi',
      license='LUKE',
      install_requires=['numpy','pandas','xlsxwriter','xlrd','paramiko','openpyxl'],
      packages=setuptools.find_packages(),
      scripts=glob.glob('lukeghg/bin/[A-Za-z]*.py')+glob.glob('lukeghg/bin/[A-Za-z]*.sh')+['lukeghg/check/checkinventoryvalues.py','lukeghg/utility/convertutf8.py']
      )
