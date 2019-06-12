#https://p10a156.pbm.ihost.com/powerai-vision/api/dlapis/7342cc0c-85aa-46bb-994f-f438cddb212e
import json
import requests
import datetime

#Server values
#Api url for the AI Vision
api_url = "https://p10a156.pbm.ihost.com/powerai-vision/api/dlapis/7342cc0c-85aa-46bb-994f-f438cddb212e"
#Image being sent to AI Vision
img = "test.jpg"
file = open(img, "rb")
#The time the server originally sends the api call
img_time = datetime.datetime.now()

#Completes the AI Vision api call
req = requests.post(url = api_url, files={"files": (img, file)}, verify=False)

print("Power AI Call")
print(req)
response = json.loads(req.text)
#print(response)

#Checks the amount of people in the line
amount_in_line = len(response['classified'])
#Builds the put call's parameters using the amount of people in line and the time of the original call
img_time = "Date: " + img_time.strftime("%a, %b %d, %Y") + " & Time: " + img_time.strftime("%I:%M:%S %p")
server_data = "Number Of People: %d & " % amount_in_line + img_time

#Sends a put call to the call server to be saved as a file on the server
server_url = "http://127.0.0.1:5000/data"
server_req = requests.put(url = server_url, params={"data": server_data})
print("Call Server Call")
print(server_req)
#print(json.loads(server_req.text))
#print(server_url)



