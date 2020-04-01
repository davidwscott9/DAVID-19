import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date, timedelta
from bs4 import BeautifulSoup   
import requests
from operator import add

sns.set(palette='pastel')

def projected_value(daily_total_infections, day):
    three_day_rate_of_growth = (daily_total_infections[day-1]/daily_total_infections[day-2] +
                                daily_total_infections[day-2]/daily_total_infections[day-3] +
                                daily_total_infections[day-3]/daily_total_infections[day-4])/3
    projected_daily_total_infections = three_day_rate_of_growth * daily_total_infections[day-1]
    return projected_daily_total_infections, three_day_rate_of_growth

def plot_provincial_data(province_id):
    url = 'https://coronavirus-tracker-api.herokuapp.com/v2/locations/'+str(province_id)

    # Connect to the URL
    response = requests.get(url)

    json = response.json()

    timeline_array = json['location']['timelines']['confirmed']['timeline']
    name = json['location']['province']

    base_daily_infections = []
    prev_day = 0

    for key in sorted(timeline_array.keys()):
        base_daily_infections.append(timeline_array[key] - prev_day)
        prev_day = timeline_array[key]

    daily_infections = np.array(base_daily_infections)

    sdate = date(2020, 1, 22)   # start date
    edate = date.today() + timedelta(days=5)  # end date

    delta = edate - sdate       # as timedelta

    day_list = []
    for i in range(delta.days + 1):
        day_list.append(sdate + timedelta(days=i))

    daily_total_infections = []
    for i in range(0, len(daily_infections)):
        daily_total_infections.append(np.sum(daily_infections[0:i+1]))

    if len(daily_total_infections) < len(day_list[0:-5]):
        plt.plot(day_list[0:-6], daily_total_infections, label='Actual', color='red', marker='o')
        plt.gcf().autofmt_xdate()
    else:
        plt.plot(day_list[0:-5], daily_total_infections, label='Actual', color='red', marker='o')
        plt.gcf().autofmt_xdate()

    projected_daily_total_infections = []
    three_day_rate_of_growth = []
    for day in range(4, len(daily_infections)):
        projected, growth = projected_value(daily_total_infections, day)
        projected_daily_total_infections.append(projected)
        three_day_rate_of_growth.append(growth)

    for i in range(0, 5):
        if i == 0:
            projected_daily_total_infections.append(daily_total_infections[-1] * three_day_rate_of_growth[-1])
        else:
            projected_daily_total_infections.append(projected_daily_total_infections[-1] * three_day_rate_of_growth[-1])

    if len(projected_daily_total_infections) < len(day_list[4::]):
        plt.plot(day_list[4:-1], projected_daily_total_infections, linestyle='--', label='Projected', color='black')
    else:
        plt.plot(day_list[4::], projected_daily_total_infections, linestyle='--', label='Projected', color='black')
    plt.gcf().autofmt_xdate()
    plt.title('Total Infections - '+name+', Canada')
    plt.legend()

    one_day_rate_of_growth = np.array(daily_total_infections[1::]) / np.array(daily_total_infections[0:-1])
    plt.figure()
    if len(one_day_rate_of_growth[25::]) < len(day_list[26:-5]):
        plt.plot(day_list[26:-6], one_day_rate_of_growth[25::])
    else:
        plt.plot(day_list[26:-5], one_day_rate_of_growth[25::])
    plt.gcf().autofmt_xdate()
    plt.title('Rate of growth')

    # plot daily infections and projected
    plt.figure()
    if len(daily_infections) < len(day_list[0:-5]):
        plt.plot(day_list[0:-6], daily_infections, label='Actual', color='red', marker='o')
    else:
        plt.plot(day_list[0:-5], daily_infections, label='Actual', color='red', marker='o')
    plt.gcf().autofmt_xdate()
    plt.title('Daily Infections - '+name+', Canada')

    projected_daily_infections = projected_daily_total_infections[0:-4] - np.array(daily_total_infections[3::])
    for i in range(len(projected_daily_total_infections) - 4, len(projected_daily_total_infections)):
        projected_daily_infections = np.hstack([projected_daily_infections,
                                                projected_daily_total_infections[i] -
                                                projected_daily_total_infections[i-1]])
        # projected_daily_infections.append(projected_daily_total_infections[i] - projected_daily_total_infections[i-1])

    if len(projected_daily_infections) < len(day_list[4::]):
        plt.plot(day_list[4:-1], projected_daily_infections, linestyle='--', label='Projected', color='black')
    else:
        plt.plot(day_list[4::], projected_daily_infections, linestyle='--', label='Projected', color='black')
    plt.gcf().autofmt_xdate()
    plt.title('Daily Infections - '+name+', Canada')
    plt.legend()

    return daily_total_infections, projected_daily_total_infections

# Start script
print("Attempting to get data from coronavirus tracker api")

sdate = date(2020, 1, 22)   # start date
edate = date.today() + timedelta(days=5)  # end date
delta = edate - sdate       # as timedelta

day_list = []
for i in range(delta.days + 1):
    day_list.append(sdate + timedelta(days=i))

cumulative_total = []
cumulative_projected_total = []

# Set the URL of the REST api we are getting data from (i.e. location 42 is for the province of Ontario)
for province_id in range(35,46):  
    if (province_id == 37):
        continue  
    provincial_total_infections, provincial_projected_total_infections = plot_provincial_data(province_id)  
    if (province_id == 35):
        cumulative_total = provincial_total_infections
        cumulative_projected_total = provincial_projected_total_infections  
    cumulative_total = list( map(add, cumulative_total,provincial_total_infections))
    cumulative_projected_total = list( map(add, cumulative_projected_total,provincial_projected_total_infections))

# plot daily infections and projected
plt.figure()
if len(cumulative_total) < len(day_list[0:-5]):
    plt.plot(day_list[0:-6], cumulative_total, label='Actual', color='red', marker='o')
else:
    plt.plot(day_list[0:-5], cumulative_total, label='Actual', color='red', marker='o')
plt.gcf().autofmt_xdate()
plt.title('Daily Infections - Canadian Provinces')

if len(cumulative_projected_total) < len(day_list[4::]):
    plt.plot(day_list[4:-1], cumulative_projected_total, linestyle='--', label='Projected', color='black')
else:
    plt.plot(day_list[4::], cumulative_projected_total, linestyle='--', label='Projected', color='black')
plt.gcf().autofmt_xdate()
plt.title('Daily Infections - Canadian Provinces')
plt.legend()

print("Finished.")