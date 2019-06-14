from flask import Flask
from flask_restful import Api, Resource, reqparse
from flask import request
from flask_cors import CORS
from flask_cors import cross_origin
from flask import send_file
import signal
import json
import datetime
import requests
import base64
import os

#Defining The API Application
app = Flask(__name__)
cors = CORS(app, origins="*")
api = Api(app)

#Convert military time to twelve hour clock
def convert_mil_to_twelve(military):
    #Split between hour and minute
    hour = int(military.split(":")[0])
    #Calculate whether it is AM or PM
    twelve = "AM"
    if hour >= 12:
        twelve = "PM"
        if hour != 12:
            hour -= 12
    #Return the twelve hour time
    return str(hour) + ":" + military.split(":")[1] + " " + twelve

#Handle a given signal
def signal_handler(a, b):
    pass
    

#Server information
storage_file = "server_storage.csv"
api_url = "https://p10a156.pbm.ihost.com/powerai-vision/api/dlapis/7342cc0c-85aa-46bb-994f-f438cddb212e"
server_url = "http://127.0.0.1:5000/dent"
#website_server_file = "../../../../var/www/html/TimsLine/"
#website = True
auto_reset = True
save_image = True

#Set up the signal to be handled
signal.signal(signal.SIGHUP, signal_handler)

# Create a URL route in the application for "/"
@app.route('/')

#The class that contains all of the rest api calls
#If a function is missing then it is qualified as not allowed for the url
class User(Resource):
    #Run when recieve a get rest api call
    #Reads off the data from the server file
    def get(self):
        if request.args.get("kill") == "True" and auto_reset:
            os.kill(os.getpid(), signal.SIGINT)
        
        #Find the server data and return it to the client
        server_data = open(storage_file, 'r')  
        data = server_data.read()
        server_data.close()
        
        #Break apart the storage data
        data_list = []
        for line in data.split("\n"):
            data_list.append(line.split(","))
        #Remove header line and reverse list
        data_list = data_list[1:][::-1]
        
        #Iterate through the file checking if the locations match
        for line in data_list:
            if line != ['']:
                return line[3] + "," + convert_mil_to_twelve(line[2])
        return "No Dent,Data"

    #Run when recieve a put rest api call
    #Writes the call arguments to the server file    
    def put(self):
        #Grabs the arguments from the call
        args = request.args
        data = args["data"]
        
        #Writes the data to the server storage file
        server_data = open(storage_file, 'a+')
        server_data.write("\n" + data)
        server_data.close()
        
        print(data)
        return data

    #Run when recieve a post rest api call
    def post(self):
        #Grabs the time when the post call is made
        img_time = datetime.datetime.now()

        #Get the values from the request
        val = list(request.files.values())
        
        #On Android
        if val == []:
            val = list(request.values.values())
        
            if val == []:
                return "No Image Sent"
            
            image = val[0]
            
            #Compensate for any missing padding
            #Should not be required anymore but still good to keep to be safe
            pad = 4 - (len(image) % 4)
            if pad == 4:
                pad = 0
    
            #Decodes the image with base 64	
            image = base64.b64decode(image + "=" * pad)
            files = {"files": ('image.jpg', image)}
        
        #On IOS
        else:
            #Get long and lat of the client
            files = {"files": ('image.jpg', val[0].read())}
            
        #Uncomment below and comment above if doing it from non application
        #files = request.files

        #Sends an api call to AI Vision
        req = requests.post(url = api_url, files=files, verify=False)       
        response = json.loads(req.text)

        #Checks the amount of people in the line
        amount_in_line = len(response['classified'])
        
        #Builds the put call's parameters using the amount of people in line and the time of the original call        
        img_time_str = img_time.strftime("%H:%M")
        img_day_str = img_time.strftime("%Y-%m-%d")        
        week_day = img_time.weekday() + 1
        
        if week_day == 7: 
            weekday -= 7
        
        server_data = img_day_str + ",%d," % week_day + img_time_str + ",%d," % amount_in_line
        
        #Save the photo (comment out normally)
        if save_image:
            f = open("DentImages/" + server_data.replace(",", "_") + ".jpg", "wb")
            f.write(files["files"][1])
            f.close()        
        
        #Sends a put call to itself
        server_req = requests.put(url = server_url, params={"data": server_data})
        return server_data

#Runs the rest api application
api.add_resource(User, "/dent")
app.run(host='0.0.0.0', debug=True)
#app.run(debug=True)
