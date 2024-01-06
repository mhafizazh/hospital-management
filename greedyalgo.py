from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['hospital_db']  # Replace with your database name

# Collections
doctors_col = db['doctors']
patients_col = db['patients']
tasks_col = db['tasks']

# Simulate ML AI for urgency ratings
def get_ml_urgency_rating(symptoms):
    # Placeholder for ML AI logic
    # In real-world, replace with actual ML model predictions
    return round(sum(ord(c) for c in symptoms) % 100 / 100, 2)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    data = request.json
    data['urgency_rating'] = get_ml_urgency_rating(data.get('symptoms', ''))
    patients_col.insert_one(data)
    return jsonify({'message': 'Patient added successfully'})

@app.route('/add_task', methods=['POST'])
def add_task():
    data = request.json
    task = {
        'patient_id': ObjectId(data['patient_id']),
        'day': data['day'],
        'hour': data['hour'],
        'is_operation': data.get('is_operation', False),
        'urgency': patients_col.find_one({'_id': ObjectId(data['patient_id'])})['urgency_rating']
    }
    tasks_col.insert_one(task)
    return jsonify({'message': 'Task added successfully'})

def schedule_tasks():
    tasks = list(tasks_col.find().sort('urgency', -1))
    
    for task in tasks:
        doctor = doctors_col.find_one({'available_hours.{}'.format(task['day']): {'$in': [task['hour']]}})
        if doctor:
            doctors_col.update_one({'_id': doctor['_id']}, {'$pull': {'available_hours.{}'.format(task['day']): task['hour']}})
            tasks_col.update_one({'_id': task['_id']}, {'$set': {'scheduled': True, 'doctor_id': doctor['_id']}})

@app.route('/schedule')
def show_schedule():
    schedule_tasks()
    scheduled_tasks = tasks_col.find({'scheduled': True})
    return jsonify([{'task_id': str(task['_id']), 'doctor_id': str(task['doctor_id'])} for task in scheduled_tasks])

if __name__ == '__main__':
    app.run(debug=True)
