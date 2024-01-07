from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['hospital_db']
class Hospital:
    def __init__(self, name_hospital, postal_code, doctors):
        self.name_hospital = name_hospital
        self.postal_code = postal_code
        self.doctors = {}
class Doctor:
    def __init__(self, name_doctor: str, time_available: dict = None):
        self.name_doctor = name_doctor
        self.time_available = time_available or {
            "Monday": [], "Tuesday": [], "Wednesday": [],
            "Thursday": [], "Friday": [], "Saturday": [], "Sunday": [],
        }

    def add_time(self, day: str, hours: list) -> None:
        if day in self.time_available:
            valid_hours = [hour for hour in hours if 1 <= hour <= 24]
            self.time_available[day].extend(valid_hours)
        else:
            print(f"Invalid day: {day}")

    def remove_time(self, day: str, hours: list) -> None:
        if day in self.time_available:
            self.time_available[day] = [hour for hour in self.time_available[day] if hour not in hours]
        else:
            print(f"Invalid day: {day}")

class Patient:
    def __init__(self, first_name, last_name, age, gender, symptoms, urgency_rating):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.symptoms = symptoms
        self.urgency_rating = urgency_rating

class Task:
    def __init__(self, patient_id, day, hour, is_operation=False):
        self.patient_id = patient_id
        self.day = day
        self.hour = hour
        self.is_operation = is_operation
        self.urgency = None

def get_ml_urgency_rating(symptoms):
    #todo implement the ML algo
    return round(sum(ord(c) for c in symptoms) % 100 / 100, 2)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    urgency_rating = get_ml_urgency_rating(data['symptoms'])
    patient = Patient(data['first_name'], data['last_name'], data['age'], data['gender'], data['symptoms'], urgency_rating)
    patient_id = db.patients.insert_one(patient.__dict__).inserted_id
    return jsonify({'patient_id': str(patient_id)})

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task = Task(data['patient_id'], data['day'], data['hour'], data.get('is_operation', False))
    task.urgency = db.patients.find_one({'_id': ObjectId(data['patient_id'])})['urgency_rating']
    db.tasks.insert_one(task.__dict__)
    return jsonify({'message': 'Task added successfully'})

def schedule_tasks():
    tasks = list(db.tasks.find().sort('urgency', -1))
    
    for task in tasks:
        doctors = list(db.doctors.find())
        for doc in doctors:
            doctor = Doctor(doc['name_doctor'], doc['time_available'])
            if task['hour'] in doctor.time_available.get(task['day'], []):
                doctor.remove_time(task['day'], [task['hour']])
                db.doctors.update_one({'_id': doc['_id']}, {'$set': {'time_available': doctor.time_available}})
                db.tasks.update_one({'_id': ObjectId(task['_id'])}, {'$set': {'scheduled': True, 'doctor_id': doc['_id']}})
                break

@app.route('/schedule')
def show_schedule():
    schedule_tasks()
    scheduled_tasks = db.tasks.find({'scheduled': True})
    return jsonify([{'task_id': str(task['_id']), 'doctor_id': str(task.get('doctor_id', 'N/A'))} for task in scheduled_tasks])

if __name__ == '__main__':
    app.run(debug=True)
