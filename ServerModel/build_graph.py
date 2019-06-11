import matplotlib
matplotlib.use("agg")
import matplotlib.pyplot as plt
import random
import seaborn as sns
import pandas as pd
import datetime

# Round all times to a half hour increment: Takes string x and returns modified string
def half_hour(x):
    s = x.split(':')
    if int(s[1]) > 30:
        return str(int(s[0]))+":30"
    else:
        return str(int(s[0]))

# Validate wether time is in the appropriate hour of operation of Tim Horton's at 8200 Warden Ave
# Takes a string and returns modified string
def validate_time(x):
    s = x.split(':')
    if int(s[0]) >= 7 and int(s[0]) < 19:
        return half_hour(x)
    else:
        return None

# Creates numeric versions of times (ie: 7:30 -> 7.5), used to sort the data frame by time
# Takes string returns float
def create_sort_keys(x):
    s = x.split(':')
    hour = int(s[0])
    if ":" in x:
        hour = hour +.5
    return hour

def not_military(x):
    s = x.split(':')
    if int(s[0]) > 12:
        if len(s) > 1:
            return str(int(s[0])-12)+':'+s[1]
        else:
            return str(int(s[0])-12)
    else:
        return x

def process_dataframe(user_data):
    user_data = user_data[['Time', 'NumberOfPeople']]
    user_data['Time'] = user_data['Time'].apply(validate_time)
    user_data = user_data.dropna()
    user_data = user_data.groupby('Time').mean().round()
    user_data['NumberOfPeople'] = user_data['NumberOfPeople'].astype(int)
    user_data = user_data.reset_index(level=0)

    # Fills in missing times in the data frame with zero values
    for x in time:
        if not x in user_data['Time'].unique():
            user_data.loc[user_data['Time'].shape[0]] = [x,0]
    # Create sort keys to organize dataframe chronologically
    user_data['SortKey'] = user_data['Time'].apply(create_sort_keys)
    user_data = user_data.sort_values(by=['SortKey'])
    user_data['NotMilitary'] = user_data['Time'].apply(not_military)
    return user_data

# Set up a half hour incremented list of times from 7 - 5
time = []

for x in range(12):
    t = x+7

    time.append(str(t))
    time.append(str(t)+":30")

# Take the server stored data from user image uploads and aggregate it by time averaging customer
# counts per half half hour
user_data = pd.read_csv("../TimsServer/server_storage.csv")
user_data['LatLon'] = user_data['Latitude'].astype(str)+","+user_data['Longitude'].astype(str)
lines = user_data['LatLon'].unique()

now = datetime.datetime.now()
DATE = "{}-{}-{}".format(now.year, now.month, now.day)

weekday = now.weekday()
if weekday == 6:
    weekday = 0
else:
    weekday = weekday +1

DAY = weekday

data = []
if not lines == []:
    for x in lines:
        d = user_data[user_data['LatLon'] == x]
        d = process_dataframe(d)
        data.append(d)

# Bring in the predictions file
predictions = pd.read_csv("predictions.csv")

for l,d in enumerate(data):
    ## Create plot that will be used in the app to show the actual and predicted number of people
    plt.figure(figsize = (17,13))
    plt.rcParams.update({'font.size': 45})
    plt.margins(x=0)
    plt.tick_params(top=False, bottom=True, left=True, right=False, labelleft=True, labelbottom=True)
    sns.despine(left=True, bottom=True, right=True)
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(13))

    yticks = plt.gca().yaxis.get_major_ticks()
    yticks[0].label1.set_visible(False)

    bars = plt.bar(d['NotMilitary'], d['NumberOfPeople'],color = ("#cfebdf", "#c7f2a7"), width=1.0, label = 'Actual')

    if lines[l] == "43.849,-79.339":
        line = plt.plot(predictions['Time'], predictions['NumberOfPeople'], "r-", alpha = .4, label='Predicted')

    plt.ylabel("People")
    plt.xlabel("Time of Day")
    plt.title("Average Number of People at Location")
    plt.legend()


    for i,item in enumerate(bars[::1]):

        height = item.get_height()
        plt.text(item.get_x() + item.get_width()/2, item.get_height()+(d['NumberOfPeople'].max()/100), str(int(height)),
                     ha='center', color='black', fontsize=30)

    plt.savefig("../TimsServer/Graphs/{}graph.png".format(lines[l]))
    if lines == "43.849,-79.339":
        plt.savefig("../../../../var/www/html/TimsLine/server_graph.png")
    
    ##

    # Check if it is 5 P.M or later and save the days aggregated data
    if lines[l] == "43.849,-79.339": #datetime.datetime.now().time().hour >= 17 and
        d = d.drop('SortKey', axis = 1)
        agg = pd.read_csv("aggregated_data.csv")
        agg = agg.drop('Unnamed: 0', axis=1)
        d['Date'],d['DayOfTheWeek']= DATE, DAY
        d['Latitude'], d['Longitude'] = 43.849,-79.339
        d = d[['Date','DayOfTheWeek','Time','Latitude','Longitude','NumberOfPeople']]
        agg = agg.append(d)
        agg.to_csv("aggregated_data.csv")
