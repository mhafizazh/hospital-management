from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__, template_folder= "./template", static_folder = './template/static')
app.config["MONGO_URI"] = "mongodb://localhost:27017/medical_database"
mongo = PyMongo(app)

def format_availability(available_days):
    return {"Monday": [1, 2, 3], "Wednesday": [12, 13, 14, 15]}

@app.route('/patients', methods=['POST'])
def add_patient():
    data = request.json  # Get the JSON data sent from the form
    print(data)  # For debugging, print the data to the console
    
    # return a dict like this {"Monday": [1, 2, 3], "Wednesday": [12, 13, 14, 15]}
    formatted_data = format_availability(data["Availability"])

    #TODO: availability
    if request.method == 'POST':
            # Prepare the document to insert
        patient_document = {
            "First_name": data['first_name'],
            "Last_name": data['last_name'],
            "Gender": data['gender'],
            "Availability": formatted_data
        }

        # Insert into the MongoDB collection
        mongo.db.patients.insert_one(patient_document)

    # Here, you would normally process the data and insert it into the database
    print(list(mongo.db.patients.find()))
    return render_template('index.html') # Send a response back
    

@app.route('/doctors', methods=['POST'])
def add_doctor():
    if request.method == 'POST':
        data = request.json

        formatted_data = format_availability(data)
        # Example doctor document
        doctor_document = {
            "First_name": data['first_name'],
            "Last_name": data['last_name'],
            "Availability": formatted_data,
            "Operations": data.get('operations', [])
        }

        # Insert into the MongoDB collection
        mongo.db.doctors.insert_one(doctor_document)

        # Print all doctors for debugging
        # doctors = mongo.db.doctors.find()
        # for doctor in doctors:
        #     doctor_str = {k: str(v) if isinstance(v, ObjectId) else v for k, v in doctor.items()}
        #     print(doctor_str)

    return render_template('index.html')



@app.route("/", methods = ['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form
        print(data)
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)