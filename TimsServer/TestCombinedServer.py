import json
import requests
import datetime

api_url = "http://drv-ctp6.canlab.ibm.com:5000/data"
image_param = "?image=True"
get = False
image = False

if (get):
    req = requests.get(url = api_url + (image_param * int(image)))
else:    
    img = "test.jpg"
    file = open(img, "rb")
    img_time = datetime.datetime.now()
    req = requests.post(url = api_url, files={"files": (img, file)}, verify=False)
    
print(req)
if image:
    response = req.content
    f = open("Stuff and Things.png", "wb")
    f.write(response)
    f.close()
else:
    response = json.loads(req.text)
    print(response)
