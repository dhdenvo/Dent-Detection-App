import datetime
import pandas as pd
import pickle

# Give numeric labels to weekdays: Takes string Returns int
def categorize(x):
    return {
        "Sunday": 0,
        "Monday": 1,
        "Tuesday": 2,
        "Wednesday": 3,
        "Thursday": 4,
        "Friday": 5,
        "Saturday": 6,
    }[x]

# Convert float number to time: Takes float Returns string
def to_time(x):
    if x > 12.5:
        x = x - 12
    time = str(x)
    arr = time.split(".")
    if arr[1] == "5":
        arr[1] = "3"
        return arr[0]+":"+arr[1]+"0"
    else:
        return arr[0]

# Get the current month and date
now = datetime.datetime.now()
Month = now.month
Date = str(now.year)+"-"+str(now.month)+"-"+str(now.day)

# Set up list of times every half hour from 7 -5
times = []
for x in range(7,17):
    times.append(x)
    times.append(x+.5)

# Create feature dataframe to build the run predictions off of
d = {'Time': times}
features = pd.DataFrame(d)
features['Month'] = Month
features['Date'] = Date
features['Date'] = pd.to_datetime(features['Date'])
features['DayOfTheWeek'] = features['Date'].dt.day_name()
features['DayOfTheWeek'] = features['DayOfTheWeek'].apply(categorize)
features = features[["DayOfTheWeek", "Time", "Month"]]

# Load up the predictive model
filename = 'model.sav'
loaded_model = pickle.load(open(filename, 'rb'))

# Predict
predictions = loaded_model.predict(features)

# Set up predictions output file
features['NumberOfPeople'] = predictions
out = features[['Time','NumberOfPeople']]
out['Time'] = out['Time'].apply(to_time)

# Save the predictions for the day to a file
out.to_csv("predictions.csv")
