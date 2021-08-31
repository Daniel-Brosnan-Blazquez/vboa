"""
Setup configuration for the vboa application

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
from setuptools import setup, find_packages

setup(name="vboa",
      version="1.0.0",
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
          "Flask-DebugToolbar",
          "flask-security-too",
          "bcrypt",
          "gunicorn",
          "bleach"
      ],
      extras_require={
          "tests" :[
              "selenium"
          ]
      },
      test_suite='nose.collector')
