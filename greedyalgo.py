from flask import Flask

app = Flask(__name__)

class Hospital:
    def __init__(self, name_hospital, postal_code):
        self.name_hospital = name_hospital
        self.postal_code = postal_code
        self.doctors = {}

    class Doctor:
        def __init__(self, name_doctor: str):
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
            self.schedule = []
            self.operations = []
            self.urgency = 0

        def add_time(self, day: str, hours: list) -> None:
            if day in self.time_available:
                valid_hours = [hour for hour in hours if 1 <= hour <= 24]
                self.time_available[day].extend(valid_hours)

        def remove_time(self, day: str, hours: list) -> None:
            if day in self.time_available:
                self.time_available[day] = [hour for hour in self.time_available[day] if hour not in hours]

        def add_to_schedule(self, task):
            self.schedule.append(task)

        def add_operation(self, operation):
            self.operations.append(operation)
            self.urgency = max(self.urgency, operation.urgency)

class Patient:
    def __init__(self, first_name, last_name, age, gender, symptoms, urgency_rating):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.gender = gender
        self.symptoms = symptoms
        self.urgency_rating = urgency_rating

    def greedyAI(self):

class Task:
    def __init__(self, patient, day, hour):
        self.patient = patient
        self.urgency = patient.urgency_rating
        self.day = day
        self.hour = hour

def schedule_tasks(hospital, tasks):
    tasks.sort(key=lambda x: x.urgency, reverse=True)

    for task in tasks:
        for doctor in hospital.doctors.values():
            if task.hour in doctor.time_available[task.day]:
                doctor.add_to_schedule(task)
                doctor.add_operation(task.patient)
                doctor.remove_time(task.day, [task.hour])
                break

@app.route('/schedule')
def show_schedule():
    hospital = Hospital("City Hospital", "12345")
    # Example doctor and times
    dr_smith = hospital.Doctor("Smith")
    dr_smith.add_time("Monday", [9, 10, 11])
    hospital.doctors["Smith"] = dr_smith

    # Example patients and tasks
    patients = [
        Patient("John", "Doe", 30, "Male", "Flu symptoms", 2),
        Patient("Jane", "Smith", 25, "Female", "Severe abdominal pain", 4),
        Patient("Alice", "Johnson", 40, "Female", "Sprained ankle", 1),
        Patient("Bob", "Williams", 55, "Male", "Chest pain", 4)
    ]
    tasks = [Task(patient, "Monday", 9 + i) for i, patient in enumerate(patients)]

    schedule_tasks(hospital, tasks)

    schedules = {}
    for doctor in hospital.doctors.values():
        schedules[doctor.name_doctor] = [(task.patient.first_name + " " + task.patient.last_name, task.day, task.hour) for task in doctor.schedule]

    return schedules

if __name__ == '__main__':
    app.run(debug=True)
