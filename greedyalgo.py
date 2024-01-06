from flask import Flask
from flask_mongoengine import MongoEngine

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'your_database_name',
    'host': 'mongodb://localhost/your_database_name'
}

db = MongoEngine()
db.init_app(app)

class Hospital(db.Document):
    name_hospital = db.StringField(required=True)
    postal_code = db.StringField(required=True)
    # Add other relevant fields and relationships

class Doctor(db.Document):
    name_doctor = db.StringField(required=True)
    time_available = db.DictField()
    operations = db.ListField(db.ReferenceField('Task'))
    urgency = db.FloatField(default=0.0)

    def add_time(self, day: str, hours: list) -> None:
        if day in self.time_available:
            valid_hours = [hour for hour in hours if 1 <= hour <= 24]
            self.time_available[day].extend(valid_hours)

    def remove_time(self, day: str, hours: list) -> None:
        if day in self.time_available:
            self.time_available[day] = [hour for hour in self.time_available[day] if hour not in hours]

    def add_operation(self, operation, urgency):
        self.operations.append(operation)
        self.urgency = max(self.urgency, urgency)

class Patient(db.Document):
    first_name = db
    last_name = db.StringField(required=True)
    age = db.IntField()
    gender = db.StringField()
    symptoms = db.StringField()
    ml_urgency_rating = db.FloatField(default=0.0)  # Rating from ML model

    def set_ml_urgency(self, rating):
        self.ml_urgency_rating = rating

class Task(db.Document):
    patient = db.ReferenceField(Patient)
    day = db.StringField(required=True)
    hour = db.IntField(required=True)
    is_operation = db.BooleanField(default=False)
    urgency = db.FloatField()

    def __init__(self, patient, day, hour, is_operation=False, *args, **values):
        super().__init__(*args, **values)
        self.patient = patient
        self.day = day
        self.hour = hour
        self.is_operation = is_operation
        self.urgency = patient.ml_urgency_rating if not is_operation else None

def schedule_tasks(hospital, tasks):
    for task in tasks:
        if task.is_operation:
            for doctor in Doctor.objects:
                if task.hour in doctor.time_available.get(task.day, []):
                    operation_urgency = determine_operation_urgency(task)  # Define this function based on your logic
                    doctor.add_operation(task, operation_urgency)
                    doctor.remove_time(task.day, [task.hour])
                    break
        else:
            for doctor in Doctor.objects:
                if task.hour in doctor.time_available.get(task.day, []):
                    doctor.operations.append(task)
                    doctor.remove_time(task.day, [task.hour])
                    break

@app.route('/schedule')
def show_schedule():
    # This is where you would initialize your Hospital, Doctors, and Patients
    # For now, this is just a placeholder
    hospital = Hospital.objects.first()  # Assuming you have a hospital in your database
    tasks = Task.objects.all()

    schedule_tasks(hospital, tasks)

    # Format the schedule in a desired way for response
    schedules = {doctor.name_doctor: doctor.operations for doctor in Doctor.objects}
    return str(schedules)

if __name__ == '__main__':
    app.run(debug=True)
