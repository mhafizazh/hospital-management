from flask import Flask, request, jsonify, render_template, redirect
from flask_pymongo import PyMongo
from bson import ObjectId


app = Flask(__name__, template_folder= "./templates", static_folder = './templates/static')
app.config["MONGO_URI"] = "mongodb://localhost:27017/medical_database"
mongo = PyMongo(app)

# TODO: 1. create class object that can create the hospital and it's doctors (Hafiz)
class Hospital:
    def __init__(self, name_hospital, postal_code, doctors):
        self.name_hospital = name_hospital
        self.postal_code = postal_code
        self.doctors = {}

    class Doctor:
        def __init__(self, name_doctor: str, time_available: dict):
            self.name_doctor = name_doctor
            self.time_available = {
                "Monday": [],
                "Tuesday": [],
                "Wednesday": [],
                "Thursday": [],
                "Friday": [],
                "Saturday": [],
                "Sunday": [],
            }

        def add_time(self, day: str, hours:list) -> None:
            # Ensure the day is a valid key in the dictionary
            if day in self.time_available:
                # Filter out any hours not in the range 1-24
                valid_hours = [hour for hour in hours if 1 <= hour <= 24]
                # Add these hours to the time available for the specified day
                self.time_available[day].extend(valid_hours)
            else:
                print(f"Invalid day: {day}")

        def remove_time(self, day: str, hours: list) -> None:
            if day in self.time_available:
                self.time_available[day] = [hour for hour in self.time_available[day] if hour not in hours]
            else:
                print(f"Invalid day: {day}")



# TODO: 2. create the function for algorithm sorting (Yash)

#TODO: For Hafiz to implement
def format_availability(available_days):
    return {"Monday": [1, 2, 3], "Wednesday": [12, 13, 14, 15]}

@app.route('/')
def home():
    return render_template('homepage.html')

@app.route("/patient_form")
def patient_form():
    return render_template('patientForm.html')  # Replace with your actual patient form template

@app.route("/patients", methods=['POST'])
def add_patient():
    data = request.json  # Get the JSON data sent from the form
    print(data)  # For debugging, print the data to the console
    
    # return a dict like this {"Monday": [1, 2, 3], "Wednesday": [12, 13, 14, 15]}
    formatted_data = format_availability(data['availability'])

    #TODO: availability
    if request.method == 'POST':
            # Prepare the document to insert
        patient_document = {
            "First_name": data['first_name'],
            "Last_name": data['last_name'],
            "Phone_number": data['phone_number'],
            "Gender": data['gender'],
            "Age": data['age'],          
            "Availability": formatted_data,
            "Symptoms": data['symptoms']
        }

        # Insert into the MongoDB collection
        mongo.db.patients.insert_one(patient_document)

    # Here, you would normally process the data and insert it into the database
    print(list(mongo.db.patients.find()))
    return jsonify({'msg': 'Patient added successfully'}) 

@app.route("/admin_form")
def login():
    return render_template('adminForm.html')  # Replace with your actual login page template

@app.route('/doctors', methods=['POST'])
def add_doctor():
    if request.method == 'POST':
        data = request.json
        formatted_data = format_availability(data)
        # Example doctor document
        doctor_document = {
            "First_name": data['first_name'],
            "Last_name": data['last_name'],
            "Email": data['email'],
            "Availability": formatted_data,
            "Operations": data['operations']
        }

    # Insert into the MongoDB collection
    mongo.db.doctors.insert_one(doctor_document)
    return jsonify({'msg': 'Doctor added successfully'}) 


if __name__ == '__main__':
    app.run(debug=True)
