#UPDATE
from pymongo import MongoClient
from bson import ObjectId
from classes import Patient,Hospital

import random

class MongoDBOperations:
    def __init__(self, uri, db_name):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def fetch_all_patients(self):
        patients_cursor = self.db.patients.find()
        patients_dict = {}
        
        for patient in patients_cursor:
            # Convert the patient's ObjectId to a string and use it as the key
            patient_id_str = str(patient['_id'])
            patients_dict[patient_id_str] = patient

        return patients_dict
    
    def fetch_all_doctors(self):
        doctors_cursor = self.db.doctors.find()
        doctors_dict = {}
        
        for doctor in doctors_cursor:
            # Convert the patient's ObjectId to a string and use it as the key
            doctor_id_str = str(doctor['_id'])
            doctors_dict[doctor_id_str] = doctor

        return doctors_dict

    def update_patient(self, patient_id, update_data):
        result = self.db.patients.update_one({'_id': ObjectId(patient_id)}, {'$set': update_data})
        return result.matched_count, result.modified_count
    
    def update_patient_collection(self, updated_data):
        for patient_id, data in updated_data.items():
            # Convert string patient_id back to ObjectId
            oid = ObjectId(patient_id)

            # Fetch the current data for comparison
            current_data = self.db.patients.find_one({'_id': oid})

            # Determine changes
            changes = {k: v for k, v in data.items() if current_data.get(k) != v}

            # Update document if there are changes
            if changes:
                self.db.patients.update_one({'_id': oid}, {'$set': changes})

    def update_doctor(self, doctor_name, update_data):
        # doctor_name is expected to be a dictionary with 'First_name' and 'Last_name'
        result = self.db.doctors.update_one(
            {'Last_name': doctor_name['Last_name']},
            {'$set': update_data}
        )
        return result.matched_count, result.modified_count

    def update_doctor_collection(self, updated_data):
        for doctor_id, data in updated_data.items():
            # Convert string doctor_id back to ObjectId
            oid = ObjectId(doctor_id)

            # Fetch the current data for comparison
            current_data = self.db.doctors.find_one({'_id': oid})

            # Determine changes
            changes = {k: v for k, v in data.items() if current_data.get(k) != v}

            # Update document if there are changes
            if changes:
                self.db.doctors.update_one({'_id': oid}, {'$set': changes})
    
    def schedule_appointments(self):
        # Fetch all patients and create Patient instances
        patients_cursor = self.db.patients.find()
        patients = [Patient(patient_data['First_name'], 
                            patient_data['Last_name'],
                            patient_data['Phone_number'],
                            patient_data['Gender'], 
                            patient_data['Age'], 
                            patient_data['Availability'],
                            patient_data['Symptoms'], 
                            urgency_rating=0) for patient_data in patients_cursor]

        # Set urgency ratings for each patient
        for patient in patients:
            # patient.function_greed()
            patient.urgency_rating = random.randint(0, 1)


        # Sort patients by urgency rating in descending order
        patients.sort(key=lambda x: x.urgency_rating, reverse=True)

        # Fetch all doctors and create Doctor instances
        doctors_cursor = self.db.doctors.find()
        doctors = [Hospital.Doctor(doctor_data['First_name'], doctor_data['Last_name'], doctor_data['Availability'], doctor_data['Operations']) for doctor_data in doctors_cursor]

        # Initialize a schedule dictionary
        schedule = {}

        # Schedule appointments based on doctor and patient availability and urgency
        for patient in patients:
            for doctor in doctors:
                # Find a matching slot where both doctor and patient are available
                for day, hours in doctor.time_available.items():
                    patient_available_hours = int(list(patient.availability.values())[0][0].split(":")[0])

                    # common_hour = next((hour for hour in hours if hour in patient_available_hours), None)
                    if patient_available_hours is not None:
                        # Schedule the appointment
                        appointment = {
                            'patient_name': f"{patient.first_name} {patient.last_name}",
                            'doctor_name': f"{doctor.last_name}",  
                            'day': day,
                            'hour': patient_available_hours,
                            'urgency': patient.urgency_rating
                        }
                        self.db.appointments.insert_one(appointment)

                        # Update doctor's availability in the database
                        doctor.remove_time(day, [patient_available_hours])
                        self.update_doctor({'Last_name': doctor.last_name}, {'time_available': doctor.time_available})

                        # Add appointment to schedule dictionary
                        doctor_full_name = f"{doctor.last_name}"
                        if doctor_full_name not in schedule:
                            schedule[doctor_full_name] = []
                        schedule[doctor_full_name].append(appointment)

                        # No need to look for other slots for this patient
                        break

        # Print the schedule
        for doctor_full_name, appointments in schedule.items():
            print(f"Schedule for Dr. {doctor_full_name}:")
            for appt in appointments:
                print(f"  Patient: {appt['patient_name']} - {appt['day']} at {appt['hour']}:00 - Urgency: {appt['urgency']}")
            print("\n")



def main():
    mongo_operations = MongoDBOperations("mongodb://localhost:27017/", "medical_database")
    mongo_operations.schedule_appointments()





if __name__ == '__main__':
    main()
