"""
Setup configuration for the vboa application

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
from setuptools import setup, find_packages

setup(name="vboa",
      version="0.1.1",
      description="Visualization tool for Business Operation Analysis",
      url="https://bitbucket.org/dbrosnan/vboa/",
      author="Daniel Brosnan",
      author_email="daniel.brosnan@deimos-space.com",
      packages=find_packages(),
      include_package_data=True,
      python_requires='>=3',
      install_requires=[
          "eboa",
          "Flask",
          "Flask-DebugToolbar"
      ],
      extras_require={
          "tests" :[
              "nose",
              "before_after",
              "coverage",
              "termcolor",
              "selenium"
          ]
      },
      test_suite='nose.collector')
