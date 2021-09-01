from flask import Blueprint, render_template_string

bp = Blueprint("view", __name__)

@app.route("/test/<string:text>")
@roles_accepted("admin", "operator")
def view():
    return render_template_string("INDEX")