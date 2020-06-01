import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()


teachers_goals = db.Table('teachers_goals',
                          db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id')),
                          db.Column('goal_id', db.Integer, db.ForeignKey('goals.id'))
                          )


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    picture = db.Column(db.String)
    free = db.Column(JSON)
    about = db.Column(db.String)

    goals = db.relationship('Goal', secondary=teachers_goals, back_populates='teachers')
    bookings = db.relationship("Booking", back_populates="teacher")


class Goal(db.Model):
    __tablename__ = 'goals'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

    teachers = db.relationship('Teacher', secondary=teachers_goals, back_populates='goals')
    requests = db.relationship("Request", back_populates="goal")


class Day(db.Model):
    __tablename__ = 'days'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

    bookings = db.relationship("Booking", back_populates="day")


class Hour(db.Model):
    __tablename__ = 'hours'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

    requests = db.relationship("Request", back_populates="hour")


class Time(db.Model):
    __tablename__ = 'times'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)

    bookings = db.relationship("Booking", back_populates="time")


class Client(db.Model):
    __tablename__ = 'clients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)

    request = db.relationship("Request", back_populates="client")
    booking = db.relationship("Booking", back_populates="client")


class Request(db.Model):
    __tablename__ = 'requests'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    goal_id = db.Column(db.Integer, db.ForeignKey('goals.id'))
    hour_id = db.Column(db.Integer, db.ForeignKey('hours.id'))

    client = db.relationship("Client", back_populates="request")
    goal = db.relationship("Goal", back_populates="requests")
    hour = db.relationship("Hour", back_populates="requests")


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    day_id =  db.Column(db.Integer, db.ForeignKey('days.id'))
    time_id = db.Column(db.Integer, db.ForeignKey('times.id'))

    client = db.relationship("Client", back_populates="booking")
    teacher = db.relationship("Teacher", back_populates="bookings")
    day = db.relationship("Day", back_populates="bookings")
    time = db.relationship("Time", back_populates="bookings")