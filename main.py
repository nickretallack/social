from flask import Flask, g, request, session, redirect, abort, url_for, render_template, flash
from pymongo import Connection
import mongorm
from base64 import b64decode

CSRF_ENABLED = False
app = Flask(__name__)
app.config.from_object(__name__)
connection = Connection()
db = mongorm.db = connection.social

PASSWORD_SALT = 'insecure'
app.secret_key = 'insecure'


from hashlib import sha1 as hasher
def hashed(password):
    return hasher(password + PASSWORD_SALT).hexdigest()

# Models
class User(mongorm.Record):
    _collection = 'user'

class Thing(mongorm.Record):
    _collection = 'thing'


from flaskext.wtf import Form, TextField, PasswordField, Required
from wtforms.validators import ValidationError

class AuthenticatesUser(object):
    def __init__(self, name_field):
        self.name_field = name_field

    def __call__(self, form, field):
        name = form[self.name_field].data
        password = field.data

        user = User.find_one(name=name)
        if user is None:
            raise ValidationError("No such user: %s" % name)
        if user.hashed_password != hashed(password):
            raise ValidationError("Incorrect password for user: %s" % name)

        g.user = user

class LoginForm(Form):
    name = TextField('Name', validators=[Required()])
    password = PasswordField('Password', validators=[Required(), AuthenticatesUser('name')])

anonymous_user = User(name='anonymous')

# Views
@app.before_request
def set_user():
    if 'user' in session:
        g.user = User.find_one(_id=session['user'])
        g.logged_in = True
    else:
        g.user = anonymous_user
        g.logged_in = False

@app.route('/')
def front():
    return render_template('front.html')

# TODO: https
@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session['user'] = g.user._id
        return redirect(url_for('front'))
    else:
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    del session['user']
    return redirect(url_for('front'))


@app.route('/invite', methods=['GET','POST'])
def invite():
    form = InviteForm()
    if form.validate_on_submit():
        return redirect(url_for('invite'))
    return render_template('invite.html', form=form)

from random import randint
@app.route('/upload', methods=['POST'])
def upload():
    filename = request.headers['UP-FILENAME']
    data = b64decode(request.data)
    with open(filename, 'wb') as file:
        file.write(data)
    return "uploaded"


# Run
if __name__ == "__main__":
    app.run(debug=True)
