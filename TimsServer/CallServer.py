from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask import request

#Defining The API Application
app = Flask(__name__)
api = Api(app)

server_file = "server_data.dat"

# Create a URL route in the application for "/"
@app.route('/')

#The class that contains all of the rest api calls
#If a function is missing then it is qualified as not allowed for the url
class User(Resource):
    #Run when recieve a get rest api call
    #Reads off the data from the server file
    def get(self):
        server_data = open(server_file, 'r')  
        data = server_data.read()
        server_data.close()
        return data
    
    #Run when recieve a put rest api call
    #Writes the call arguments to the server file
    def put(self):
        #Grabs the arguments from the call
        args = request.args
        data = args["data"]
        #Writes the arguments to the server file
        server_data = open(server_file, 'w')  
        server_data.write(data)
        server_data.close()
        return data

#Runs the rest api application
api.add_resource(User, "/data")
app.run(debug=True)