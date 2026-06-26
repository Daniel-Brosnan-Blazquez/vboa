"""
Setup configuration for the vboa application

Written by Daniel Brosnan Blázquez

module vboa
"""
from setuptools import setup, find_packages

setup(name="vboa",
      version="1.0.10",
      description="Visualization tool for Business Operation Analysis",
      url="https://bitbucket.org/dbrosnan/vboa/",
      author="Daniel Brosnan",
      author_email="d.brosnan.b@gmail.com",
      packages=find_packages(),
      include_package_data=True,
      python_requires='>=3',
      install_requires=[
          "eboa",
          "Werkzeug==3.0.6",
          "Flask==2.2.5",
          "Flask-DebugToolbar==0.15.1",
          "flask-security-too==4.1.6",
          "bcrypt==4.3.0",
          "gunicorn==23.0.0",
          "bleach==6.2.0",
          "geopy==2.4.1",
          "pytz==2026.1.post1",
          "argon2-cffi==25.1.0"
      ],
      extras_require={
          "tests" :[
              "selenium==3.14.0"
          ]
      },
      test_suite='nose.collector')
