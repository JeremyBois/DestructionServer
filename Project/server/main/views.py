# Project/server/main/views.py


from flask import render_template, Blueprint


main_blueprint = Blueprint('main', __name__,)


@main_blueprint.route('/')
def home():
    return render_template('home.html')
