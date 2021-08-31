from flask import Blueprint, render_template_string

bp = Blueprint("view", __name__)

@auth_required()
def view():
    return render_template_string("INDEX")