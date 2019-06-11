import pandas as pd
from sklearn.model_selection import train_test_split
import pickle
import datetime

# Convert time of day to numeric representation
def time_to_number(x):
    hour = x
    if ':' in hour:
        hour = int(x.split(':')[0])
        hour = hour +.5

    return float(hour)

# Get the daily customer data and process it to be used for training
def get_data():
    now = datetime.datetime.now()
    month = now.month
    if month < 10:
        month = "0"+str(month)
    else:
        month = str(month)

    date = str(now.year)+"-"+month+"-"+str(now.day)
    x = pd.read_csv("aggregated_data.csv")
    x = x[x['Date'] == date]
    x['Date'] = pd.to_datetime(x['Date'])
    x['Month'] = x['Date'].dt.month.astype(int)
    x['LatLon'] = x["Latitude"].astype(str)+','+x["Longitude"].astype(str)
    x = x[x['LatLon'] == "43.849,-79.339"]
    x = x.drop(['Date',"Unnamed: 0", "Longitude", "Latitude", "LatLon"], axis=1)
    x["Time"] = x["Time"].apply(time_to_number)
    return x

# Load up data and seperate into features and target variables
customers = get_data()

# Check if there is data to train with
X = customers.drop('NumberOfPeople', axis=1)
y = customers['NumberOfPeople']

if len(y.unique()) > 1:
    # Load up the model
    filename = 'model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))

    # Train the model
    loaded_model.fit(X,y)

    # Save the model
    pickle.dump(loaded_model, open(filename, 'wb'))
