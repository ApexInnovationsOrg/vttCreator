import os

from flask import Flask
from flask import request
from FileValidator import FileValidator

app = Flask(__name__)

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    #set application/json
    response.headers['Content-Type'] = 'application/json'
    return response

@app.route("/", methods = ['GET', 'POST'] )
def hello_world():
    if request.method == 'GET':
        return {
            'message': 'Oops, please send a POST request.',
            'error': 'Something went wrong.',
             'code': 500
        }
    Validator = FileValidator(request.form)
    try:
     Validator.has_valid_params()
     Validator.download_file()
     Validator.create_closed_caption()
     data = Validator.format()
    except Exception as error:
        return 'Caught this error: ' + repr(error)
    return data

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))