import greedyAI
class Hospital:
    def __init__(self, name_hospital, postal_code):
        self.name_hospital = name_hospital
        self.postal_code = postal_code
        self.doctors = {}

    class Doctor:
        def __init__(self, first_name: str, last_name: str, availability: dict, operation):
 
            self.last_name = last_name

            self.time_available = availability

            self.schedule = []



        def add_time(self, day: str, hours: list) -> None:
            if day in self.time_available:
                valid_hours = [hour for hour in hours if 1 <= hour <= 24]
                self.time_available[day].extend(valid_hours)

        def remove_time(self, day: str, hours: list) -> None:
            if day in self.time_available:
                self.time_available[day] = [hour for hour in self.time_available[day] if hour not in hours]

        def add_to_schedule(self, task):
            self.schedule.append(task)

        # def add_operation(self, operation):
        #     self.operations.append(operation)
        #     self.urgency = max(self.urgency, operation.urgency)

class Patient:
    def __init__(self, first_name, last_name, phone_number, gender, age, availability, symptoms, urgency_rating):
        self.first_name = first_name
        self.last_name = last_name
        self.phone_number = phone_number
        self.age = age
        self.gender = gender
        self.availability = availability
        self.symptoms = symptoms
        self.urgency_rating = urgency_rating 

    def function_greed(self) -> None:
        self.urgency_rating = greedyAI.machineLearning(text=self.symptoms)[0]

class Task:
    def __init__(self, patient, day, hour):
        self.patient = patient
        self.urgency = patient.urgency_rating
        self.day = day
        self.hour = hour
