import os
import random

from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import StringField, RadioField
from wtforms.validators import InputRequired

import data
from model import db, Teacher, Goal, Day, Hour, Request, Booking, Client, Time


app = Flask(__name__)
app.secret_key = 'very_random_string'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB4_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

FIRST_LAUNCH = False
week = {}
goals = {}
goals_choice = [("", "")]
hours = {}
hours_choice = [("", "")]
teachers = []

if not FIRST_LAUNCH:
    with app.app_context():
        for elem in Day.query.all():
            week[elem.code] = elem.name

        for elem in Hour.query.all():
            hours[elem.code] = elem.name
        hours_choice = [(key, value) for key, value in hours.items()]

        for elem in Goal.query.all():
            goals[elem.code] = elem.name
        goals_choice = [(key, value) for key, value in goals.items()]

        for elem in Teacher.query.all():
            new_teacher = {}
            new_teacher['id'] = elem.id
            new_teacher['name'] = elem.name
            new_teacher['rating'] = elem.rating
            new_teacher['price'] = elem.price
            new_teacher['picture'] = elem.picture
            new_teacher['free'] = elem.free
            new_teacher['about'] = elem.about
            teacher_goals = Goal.query.filter(Goal.teachers.any(Teacher.id == elem.id)).all()
            new_teacher['goals'] = [elem.code for elem in teacher_goals]
            teachers.append(new_teacher)


def get_teacher(id):
    for elem in teachers:
        if elem['id'] == id: return elem
    return None


@app.route('/')
def render_index():
    max = 6 if len(teachers) > 6 else len(teachers)
    return render_template('index.html',
                           goals=goals,
                           teachers=random.sample(teachers, max))


@app.route('/all/')
def render_all():
    return render_template('all.html',
                           goals=goals,
                           teachers=teachers)


@app.route('/goals/<goal>/')
def render_goal(goal):
    return render_template('goal.html',
                           goals=goals,
                           goal=goal,
                           teachers=teachers)


@app.route('/profiles/<int:id>/')
def render_profile(id):
    days = {}
    teacher = get_teacher(id)
    for day in week:
        days[day] = 0
        for status in teacher['free'][day].values():
            if status:
                days[day] += 1

    return render_template('profile.html',
                           goals=goals,
                           week=week,
                           id=id,
                           teacher=teacher,
                           days=days)


class RequestForm(FlaskForm):
    name = StringField('Вас зовут', [InputRequired()])
    phone = StringField('Ваш телефон', [InputRequired()])
    goals = RadioField('Какая цель занятий?', choices=goals_choice, default=goals_choice[0][0])
    hours = RadioField('Сколько времени есть?', choices=hours_choice, default=hours_choice[0][0])


@app.route('/request/', methods=["GET", "POST"])
def render_request():
    if request.method == 'POST':
        form = RequestForm()

        goal = form.goals.data
        hour = form.hours.data
        name = form.name.data
        phone = form.phone.data

        with app.app_context():
            new_client = Client(name=name, phone=phone)
            db.session.add(new_client)

            new_request = Request(client=new_client,
                                  hour=Hour.query.filter(Hour.code == hour).first(),
                                  goal=Goal.query.filter(Goal.code == goal).first())
            db.session.add(new_request)

            db.session.commit()

        return render_template('request_done.html',
                               goal=goals[goal],
                               hours=hours[hour],
                               name=name,
                               phone=phone)
    else:
        form = RequestForm()

        return render_template('request.html',
                               form=form)


class BookingForm(FlaskForm):
    name = StringField('Вас зовут', [InputRequired()])
    phone = StringField('Ваш телефон', [InputRequired()])
    id = StringField('id')
    day = StringField('day')
    time = StringField('time')


@app.route('/booking/<int:id>/<day>/<time>/', methods=["GET", "POST"])
def render_booking(id, day, time):
    if request.method == 'POST':
        form = BookingForm()

        id = form.id.data
        name = form.name.data
        phone = form.phone.data
        day = form.day.data
        time = form.time.data

        with app.app_context():
            new_client = Client(name=name, phone=phone)
            db.session.add(new_client)

            new_booking = Booking(client=new_client,
                                  teacher_id=id,
                                  day=Day.query.filter(Day.code == day).first(),
                                  time=Time.query.filter(Time.code == time).first())
            db.session.add(new_booking)

            db.session.commit()

        return render_template('booking_done.html',
                               name=name,
                               phone=phone,
                               day=week[day],
                               time=time)
    else:
        form = BookingForm()

        return render_template('booking.html',
                               week=week,
                               id=id,
                               teacher=get_teacher(id),
                               day=day,
                               time=time,
                               form=form)


if __name__ == '__main__':
    if FIRST_LAUNCH:
        with app.app_context():

            for k, v in data.hours.items():
                hour = Hour(code=k, name=v)
                db.session.add(hour)
            
            for k, v in data.week.items():
                day = Day(code=k, name=v)
                db.session.add(day)
            
            for k, v in data.goals.items():
                goal = Goal(code=k, name=v)
                db.session.add(goal)

            for k, v in data.times.items():
                time = Time(code=k, name=v)
                db.session.add(time)

            for t in data.teachers:
                teacher = Teacher(id=t['id'],
                                  name=t['name'],
                                  about=t['about'],
                                  rating=t['rating'],
                                  picture=t['picture'],
                                  price=t['price'],
                                  free=t['free'])
                db.session.add(teacher)
                for g in t['goals']:
                    new_goal = Goal.query.filter(Goal.code == g).first()
                    teacher.goals.append(new_goal)

            db.session.commit()
    app.run()
