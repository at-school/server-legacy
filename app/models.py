from hashlib import md5

from werkzeug.security import check_password_hash, generate_password_hash


class User():

    def __init__(self, username, firstname, lastname, email, accessLevel, **kwargs):
        self.username = username
        self.firstname = firstname
        self.lastname = lastname
        self.email = email
        self.accessLevel = accessLevel
        self.avatar = 'https://www.gravatar.com/avatar/{}?d=identicon&s=256'.format(
            md5(self.username.lower().encode('utf-8')).hexdigest())

    def get_default_avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    @classmethod
    def findUsers(self, id=None, username=None, firstname=None):
        if (id):
            # search user by id here
            pass
        elif (username):
            # search user by name here
            return Database.db.users.find({"username": username})
        elif (firstname):
            pass

        return None

    @classmethod
    def checkPassword(self, password, password1):
        """Checks a password against the hash."""
        return check_password_hash(password, password1)

class Falcuty(db.Model):
    __tablename__ = "falcuty"

    id = db.Column(db.Integer, primary_key=True)
    falcuty_name = db.Column(db.String(200))
    class_id = db.relationship("Class", backref="classes", lazy="dynamic")

class Line(db.Model):
    __tablename__ = "line"

    id = db.Column(db.Integer, primary_key=True)
    schedule = db.relationship("Day", secondary="line_schedule", lazy="dynamic")
    class_id = db.relationship("Class", backref="class_schedule", lazy="dynamic")

class Day(db.Model):
    __tablename__ = "day"

    id = db.Column(db.String(10), primary_key=True)
    line = db.relationship("Line", secondary="line_schedule", lazy="dynamic")

class Line_Schedule(db.Model):
    __tablename__ = "line_schedule"

    line_id = db.Column(db.Integer, db.ForeignKey("line.id"), primary_key=True)
    day_id = db.Column(db.Integer, db.ForeignKey("day.id"), primary_key=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    description = db.Column(db.String(255))

    def __repr__(self):
        return "<Post {}>".format(self.title)
        
class Roll(db.Model):
    __tablename__ = "roll"

    user_id = db.Column(db.Integer)
    class_id = db.Column(db.Integer)

    def __repr__(self):
        return "<Roll {} contains user {}>".format(
            self.class_id, self.user_id
        )

class Grades(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    task_id = db.Column(db.Integer)
    score = db.Column(db.Integer)

    def __repr__(self):
        return "<Grade {}>".format(self.id)


class Task(db.Model):
    __tablename__ = "task"

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('class.id'))
    title = db.Column(db.String(100))
    users = db.Column(db.String(1000))
    desc = db.Column(db.String(300))
    file_loc = db.Column(db.String(300))
    due_date = db.Column(db.String(100))
    active = db.Column(db.Boolean())

    def __repr__(self):
        return "<Task {} Due: {}>".format(self.id, self.due_date)

    def notify(self):
        for student in self.users:
            try:
                User.query.filter_by(id=student)
            # user.notify()

    def __str__(self):
        return "User" + self.firstname + self.lastname

    def __repr__(self):
        return "<User {}>".format(self.username)


    def __repr__(self):
        return '<State {}>'.format(self.name)
