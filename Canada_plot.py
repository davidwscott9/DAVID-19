import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from datetime import date, timedelta

sns.set(palette='pastel')

sdate = date(2020, 1, 26)   # start date
edate = date.today() - timedelta(days=1) # end date

delta = edate - sdate       # as timedelta

day_list = []
for i in range(delta.days + 1):
    day_list.append(sdate + timedelta(days=i))

daily_infections = np.array([1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1,
                             1, 0, 2, 1, 6, 4, 3, 3, 3, 4, 12, 5, 10, 13, 17, 15, 33, 37, 68, 94, 81, 176, 129, 146,
                             204, 251, 142])
start_date = 'Jan 26, 2020'

daily_total_infections = []
for i in range(0, len(daily_infections)):
    daily_total_infections.append(np.sum(daily_infections[0:i+1]))

plt.plot(day_list, daily_total_infections, label='Actual')
plt.gcf().autofmt_xdate()


def projected_value(daily_total_infections, day):
    three_day_rate_of_growth = (daily_total_infections[day-1]/daily_total_infections[day-2] +
                                daily_total_infections[day-2]/daily_total_infections[day-3] +
                                daily_total_infections[day-3]/daily_total_infections[day-4])/3
    projected_daily_total_infections = three_day_rate_of_growth * daily_total_infections[day-1]
    return projected_daily_total_infections, three_day_rate_of_growth


projected_daily_total_infections = []
three_day_rate_of_growth = []
for day in range(4, len(daily_infections)+1):
    projected, growth = projected_value(daily_total_infections, day)
    projected_daily_total_infections.append(projected)
    three_day_rate_of_growth.append(growth)

plt.plot(day_list[3::], projected_daily_total_infections, label='Projected')
plt.gcf().autofmt_xdate()
plt.title('Daily Total Infections - Canada')
plt.legend()


plt.figure()
plt.plot(day_list[3::], three_day_rate_of_growth)
plt.gcf().autofmt_xdate()
