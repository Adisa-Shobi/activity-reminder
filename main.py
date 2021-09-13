from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.exc import IntegrityError
from flask_bootstrap import Bootstrap
from datetime import datetime, time
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, NumberRange, InputRequired
from wtforms import StringField, SelectMultipleField, SubmitField, IntegerField, TextAreaField, FieldList

from notification_manager import NotificationManager

from time import sleep

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///activities.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
Bootstrap(app)

PHONE_NO = os.environ.get('PHONE_NO')


class ActivityForm(FlaskForm):
    activity = StringField(label='Activity Name e.g Go to work', validators=[DataRequired()])
    hour = IntegerField(label='Hour(24hr format)', validators=[DataRequired(), NumberRange(min=0, max=24)])
    minute = IntegerField(label='Minute', validators=[InputRequired(), NumberRange(min=0, max=59)])
    days = SelectMultipleField(label='On which days do you want to be notified(Hold Ctrl to multiple select)',
                               choices=[('Mon', 'Mon'),
                                        ('Teu', 'Teu'),
                                        ('Wed', 'Wed'),
                                        ('Thu', 'Thu'),
                                        ('Fri', 'Fri'),
                                        ('Sat', 'Sat'),
                                        ('Sun', 'Sun'),
                                        ],
                               validators=[DataRequired()]
                               )
    reminders = TextAreaField(label="Enter reminders e.g Close windows before leaving(Each Reminder goes on a new line)",
                              validators=[DataRequired()]
                              )
    submit = SubmitField(label='submit')


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    time = db.Column(db.String(100), nullable=False)
    days = db.Column(db.String(400), nullable=False)
    reminders = db.Column(db.String(300), nullable=False)


class Manager:
    def __init__(self):
        self.model = Activity

    def add_new_entry(self, activity_name: str, activity_time: str, activity_days: str, activity_reminders: str):
        new_entry = self.model(
            name=activity_name,
            time=activity_time,
            days=activity_days,
            reminders=activity_reminders,
        )
        db.session.add(new_entry)
        db.session.commit()

    def get_all_entries(self):
        return db.session.query(self.model).all()

    def search_by_name(self, entry_name):
        return self.model.query.filter_by(name=entry_name).first()

    def search_by_id(self, entry_id):
        return self.model.query.filter_by(id=entry_id).first()

    def search_by_time(self, entry_time):
        return self.model.query.filter_by(time=entry_time).first()


manager = Manager()
notification_manager = NotificationManager()
# Initial database creation
db.create_all()

# first entry
# new_activity = Activity(
#     name='Rest up',
#     time=time(hour=6, minute=0, second=0),
#     days="('Mon', 'Teu', 'Wed', 'Thu', 'Fri')",
#     reminders="('Don\'t forget to clean up: Brush your teeth and take a shower',"
#               " 'Make sure to take a nutritious breakfast before heading out',"
#               " 'Wait, did you make your bed?')"
# )
# db.session.add(new_activity)
# print("tried to create")
# db.session.commit()


@app.route('/')
def home():
    activities = manager.get_all_entries()
    alert_times = [activity.time for activity in activities]
    while True:
        sleep(60)
        time_now = datetime.now()
        day = time_now.strftime('%a')
        formatted_time = time_now.strftime("%H:%M")
        if formatted_time in alert_times:
            entry = manager.search_by_time(formatted_time)
            # check if today is included in the reminder entry
            days = entry.days.split(',')
            if day in days:
                activity_name = entry.name
                reminders = entry.reminders
                message = f"Hey there!!\nIt's '{activity_name}' time\nDon't forget to:\n{reminders}"
                notification_manager.send_message(message=message, phone_no=PHONE_NO)
        # return render_template('index.html', time=formatted_time)


@app.route('/add', methods=["GET", "POST"])
def add_activity():
    form = ActivityForm()
    if form.validate_on_submit():
        # Transforming the days the user selected into suitable format
        activity_days = ""
        for day in form.days.data:
            activity_days += f"{day}, "
        activity_days.replace("'", "")
        # Adding the user submission into the database via database manager
        try:
            manager.add_new_entry(
                activity_name=form.activity.data,
                activity_time=time(hour=form.hour.data, minute=form.minute.data).strftime("%H:%M"),
                activity_days=activity_days,
                activity_reminders=form.reminders.data,
            )
        except IntegrityError:
            return "Sorry, the activity you entered already exists"
        else:
            return "Successfully added activity 👍"
    return render_template('add.html', form=form)


if __name__ == "__main__":
    app.run(debug=True)
