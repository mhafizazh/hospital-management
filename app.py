from flask import Flask

app = Flask(__name__)



# TODO: 1. create class object that can create the hospital and it's doctors (Hafiz)


# TODO: 2. create the function for algorithm sorting (Yash)


@app.route('/')
def home():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
