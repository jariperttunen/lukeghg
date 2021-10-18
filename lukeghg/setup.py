import glob
import setuptools
from setuptools import setup
#It seems pandas  1.2.0 and later cannot create  excel files correctly
#with openpyxl. pandas 1.1.5+openpyxl seems  to be the latest that can
#generate files excel  can open without warning.  openpyxl version can
#be the latest.
setup(name='lukeghg',
      version='1.0',
      description='LUKE GHG Inventory Support Tools',
      author='Jari Perttunen',
      author_email='jari.perttunen@luke.fi',
      license='LUKE',
      install_requires=['numpy','pandas==1.1.5','xlsxwriter','xlrd','paramiko','openpyxl'],
      packages=setuptools.find_packages(),
      scripts=glob.glob('lukeghg/bin/[A-Za-z]*.py')+glob.glob('lukeghg/bin/[A-Za-z]*.sh')+['lukeghg/utility/convertutf8.py']
      )
