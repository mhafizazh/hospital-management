# TODO: pull all the data down, use the authorize api from google calendar to send to the doctor to authorize, then add or delete task thing with it!
# TODO: OTHER: log in page for admin
from pymongo import MongoClient
from bson import ObjectId
from classes import Patient,Hospital

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

    def update_doctor(self, doctor_id, update_data):
        result = self.db.doctors.update_one({'_id': ObjectId(doctor_id)}, {'$set': update_data})
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
        patients = [Patient(patient_data['first_name'], 
                            patient_data['last_name'], 
                            patient_data['age'], 
                            patient_data['gender'], 
                            patient_data['symptoms'], 
                            patient_data['urgency_rating']) for patient_data in patients_cursor]

        # Sort patients by urgency rating in descending order
        patients.sort(key=lambda x: x.urgency_rating, reverse=True)

        # Fetch all doctors and create Doctor instances
        doctors_cursor = self.db.doctors.find()
        doctors = [Hospital.Doctor(doctor_data['name_doctor'], doctor_data['time_available']) for doctor_data in doctors_cursor]

        # Initialize a schedule dictionary
        schedule = {}

        # Schedule appointments based on doctor and patient availability and urgency
        for patient in patients:
            for doctor in doctors:
                # Find a matching slot where both doctor and patient are available
                for day, hours in doctor.time_available.items():
                    # Assuming patient.availability is a dictionary with days and available hours
                    patient_available_hours = patient.availability.get(day, [])
                    # Find the first common hour that both patient and doctor are available
                    common_hour = next((hour for hour in hours if hour in patient_available_hours), None)
                    if common_hour is not None:
                        # Schedule the appointment
                        appointment = {
                            'patient_id': patient.patient_id,  # Assuming Patient class has patient_id attribute
                            'doctor_id': doctor.doctor_id,  # Assuming Doctor class has doctor_id attribute
                            'day': day,
                            'hour': common_hour,
                            'urgency': patient.urgency_rating
                        }
                        self.db.appointments.insert_one(appointment)  # Assuming there is an appointments collection

                        # Update doctor's availability in the database
                        doctor.remove_time(day, [common_hour])
                        self.update_doctor(doctor.doctor_id, {'time_available': doctor.time_available})

                        # Add appointment to schedule dictionary
                        if doctor.name_doctor not in schedule:
                            schedule[doctor.name_doctor] = []
                        schedule[doctor.name_doctor].append(appointment)

                        # No need to look for other slots for this patient
                        break
         # Print the schedule
        for doctor_name, appointments in schedule.items():
            print(f"Schedule for Dr. {doctor_name}:")
            for appt in appointments:
                patient_info = self.db.patients.find_one({'_id': ObjectId(appt['patient_id'])})
                print(f"  Patient: {patient_info['first_name']} {patient_info['last_name']} - {appt['day']} at {appt['hour']}:00 - Urgency: {appt['urgency']}")
            print("\n")


def main():
    mongo_operations = MongoDBOperations("mongodb://localhost:27017/", "medical_database")
    mongo_operations.schedule_appointments()




if __name__ == '__main__':
    main()
