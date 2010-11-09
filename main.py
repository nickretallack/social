from flask import Flask, g, request, session, redirect, abort, url_for, render_template, flash
from pymongo import Connection
import mongorm
app = Flask(__name__)
app.config.from_object(__name__)
connection = Connection()
db = mongorm.db = connection.social

# Models
class User(Record):
    _collection = 'user'

# Views
@app.route('/')
def front():
    return render_template('front.html')

@app.route('/login', methods=['POST'])
def login():
    user = User
    
# Run
if __name__ == "__main__":
    app.run(debug=True)
