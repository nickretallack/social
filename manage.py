from flaskext.script import Manager
from main import app, User, hashed

manager = Manager(app)

@manager.command
def create_user(name, password):
    if User.find_one(name=name):
        print "The user \"%s\" already exists" % name
    else:
        user = User(name=name, hashed_password=hashed(password))
        user.save()


if __name__ == "__main__":
    manager.run()
