import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from datetime import date, timedelta

sns.set(palette='pastel')

# Data input. Can we automatically pull from some website????
daily_infections = np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1,
                             1, 0, 2, 1, 6, 4, 3, 3, 3, 4, 12, 5, 10, 13, 17, 15, 33, 37, 68, 94, 81, 176, 129, 146,
                             204, 251, 142])

sdate = date(2020, 1, 26)   # start date
edate = date.today() + timedelta(days=4)  # end date

delta = edate - sdate       # as timedelta

day_list = []
for i in range(delta.days + 1):
    day_list.append(sdate + timedelta(days=i))

daily_total_infections = []
for i in range(0, len(daily_infections)):
    daily_total_infections.append(np.sum(daily_infections[0:i+1]))

plt.plot(day_list[0:-5], daily_total_infections, label='Actual', color='red')
plt.gcf().autofmt_xdate()


def projected_value(daily_total_infections, day):
    three_day_rate_of_growth = (daily_total_infections[day-1]/daily_total_infections[day-2] +
                                daily_total_infections[day-2]/daily_total_infections[day-3] +
                                daily_total_infections[day-3]/daily_total_infections[day-4])/3
    projected_daily_total_infections = three_day_rate_of_growth * daily_total_infections[day-1]
    return projected_daily_total_infections, three_day_rate_of_growth



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

plt.plot(day_list[4::], projected_daily_total_infections, linestyle='--', label='Projected', color='black')
plt.gcf().autofmt_xdate()
plt.title('Total Infections - Canada')
plt.legend()


plt.figure()
plt.plot(day_list[4:-5], three_day_rate_of_growth)
plt.gcf().autofmt_xdate()
plt.title('Rate of growth')

# plot daily infections and projected
plt.figure()
plt.plot(day_list[0:-5], daily_infections, label='Actual', color='red')
plt.gcf().autofmt_xdate()
plt.title('Daily Infections - Canada')


projected_daily_infections = projected_daily_total_infections[0:-4] - np.array(daily_total_infections[3::])
for i in range(len(projected_daily_total_infections) - 4, len(projected_daily_total_infections)):
    projected_daily_infections = np.hstack([projected_daily_infections,
                                            projected_daily_total_infections[i] -
                                            projected_daily_total_infections[i-1]])
    # projected_daily_infections.append(projected_daily_total_infections[i] - projected_daily_total_infections[i-1])

plt.plot(day_list[4::], projected_daily_infections, linestyle='--', label='Projected', color='black')
plt.gcf().autofmt_xdate()
plt.title('Daily Infections - Canada')
plt.legend()