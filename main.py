# TODO: pull all the data down, use the authorize api from google calendar to send to the doctor to authorize, then add or delete task thing with it!
# TODO: OTHER: log in page for admin


from pymongo import MongoClient
from bson import ObjectId

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


def main():
    mongo_operations = MongoDBOperations("mongodb://localhost:27017/", "medical_database")

    # Fetch all patients
    all_patients = mongo_operations.fetch_all_patients()
    for patient, data in all_patients.items():
        data["Age"] = "1"

    # mongo_operations.update_entire_collection(all_patients)

    for patient, data in all_patients.items():
        print(patient, data)



if __name__ == '__main__':
    main()
