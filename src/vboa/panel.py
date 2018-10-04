"""
VBOA inital panel section definition

Written by DEIMOS Space S.L. (dibb)

module vboa
"""
# Import flask utilities
from flask import Blueprint, flash, g, redirect, render_template, request, url_for

bp = Blueprint('panel', __name__)

@bp.route('/')
def index():
    """
    Show initial panel.
    """

    return render_template('panel/index.html')


