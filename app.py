from flask import Flask

app = Flask(__name__)


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



# TODO: 2. create the function for algorithm sorting (Yash)


@app.route('/')
def home():
    return 'Hello, World!'


if __name__ == '__main__':
    app.run(debug=True)
