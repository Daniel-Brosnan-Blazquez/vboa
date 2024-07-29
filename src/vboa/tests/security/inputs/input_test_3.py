from flask import Blueprint, render_template_string

bp = Blueprint("view", __name__)

@app.before_first_request
def view():
    return render_template_string("INDEX")