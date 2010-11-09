from flask import Flask, g, request, session, redirect, abort, url_for, render_template, flash
from pymongo import Connection
import mongorm
app = Flask(__name__)
app.config.from_object(__name__)
connection = Connection()
db = mongorm.db = connection.social

PASSWORD_SALT = 'insecure'
app.secret_key = 'insecure'


from hashlib import sha1 as hasher
def hashed(password):
    return hasher.new(password, PASSWORD_SALT).hexdigest()

# Models
class User(mongorm.Record):
    _collection = 'user'

from flaskext.wtf import Form, TextField, PasswordField, Required
from wtforms.validators import ValidationError

class AuthenticatesUser(object):
    def __init__(self, name_field, message=None):
        self.name_field = name_field
        self.message = message

    def __call__(self, form, field):
        name = form[self.name_field].data
        password = field.data

        user = User.find_one(name=name)
        if user is None:
            raise ValidationError("No such user: %s" % name)
        if user.hashed_password != hashed(password):
            raise ValidationError("Incorrect password for user: %s" % name)

        session['user'] = user._id
        g.user = user

class LoginForm(Form):
    name = TextField('Name', validators=[Required()])
    password = PasswordField('Password', validators=[Required(), AuthenticatesUser('name')])

anonymous_user = User(name='anonymous')

# Views
@app.before_request
def set_user():
    if 'user' in session:
        g.user = User.find(_id=session['user'])
        g.logged_in = True
    else:
        g.user = anonymous_user
        g.logged_in = False

@app.route('/')
def front():
    return render_template('front.html')

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Logged in as " % g.user['name'])
        return redirect(url_for('front'))
    return render_template('login.html', form=form)

# Run
if __name__ == "__main__":
    app.run(debug=True)
