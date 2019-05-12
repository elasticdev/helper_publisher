from distutils.core import setup
from setuptools import find_packages

pkgdir="ed_helper_publisher"
version = "0.100"

setup(name='ed_helper_publisher',
      version=version,
      description='The helper package for publishing on elasticdev.io',
      long_description='The helper package for publishing on elasticdev.io',
      url='http://github.com/elasticev/helper_publisher',
      author='Gary Leong',
      author_email='gary@elasticdev.io',
      license="Copyright Jiffy, LLC 2019",
      packages=find_packages(),
      include_package_data=True,
      install_requires=[
      ],
      classifiers=[
          "Programming Language :: Python :: 2",
          "Intended Audience :: Developers",
          "Topic :: Software Development",
          "Topic :: Utilities",
          "Environment :: Console",
          "Operating System :: OS Independent",
      ],
      zip_safe=False)
