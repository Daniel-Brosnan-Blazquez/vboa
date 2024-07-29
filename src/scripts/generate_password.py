#!/usr/bin/env python3
"""
Script for generating a hashed password to access vboa

Written by DEIMOS Space S.L.

module vboa
"""
# Import python utilities
import argparse

# Import flask security utils
from flask_security import hash_password

# Create an app context to hash passwords (this is because the hash_password depends on configurations related to the app)
import vboa

if __name__ == "__main__":

    args_parser = argparse.ArgumentParser(description="Generate a hashed password.")
    args_parser.add_argument("-p", "--password", type=str, nargs=1,
                             help="Password to hash", required=True)

    args = args_parser.parse_args()

    password = None
    app = vboa.create_app()
    with app.app_context():
        password = hash_password(args.password[0])
    # end with

    print("Received password '{}' has been hashed to the following value:".format(args.password[0]))
    print(password)

    exit(0)
