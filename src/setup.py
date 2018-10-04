"""
Setup configuration for the vboa application

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
from setuptools import setup, find_packages

setup(name="vboa",
      version="0.1.0",
      description="Visualization tool for Business Operation Analysis",
      url="https://bitbucket.org/dbrosnan/vboa/",
      author="Daniel Brosnan",
      author_email="daniel.brosnan@deimos-space.com",
      packages=["vboa"],
      python_requires='>=3',
      install_requires=[
          "Flask",
          "WTForms"
      ],
      tests_require=[
          "nose",
          "before_after",
          "coverage",
          "termcolor"
      ],
      test_suite='nose.collector')
