import numpy as np
from datetime import date, timedelta
import requests
from scipy.optimize import curve_fit
from scipy.special import expit

class Playground:

    def __init__(self):
        return

    def projected_value(self,daily_total_infections, day):
        three_day_rate_of_growth = (daily_total_infections[day - 1] / daily_total_infections[day - 2] +
                                    daily_total_infections[day - 2] / daily_total_infections[day - 3] +
                                    daily_total_infections[day - 3] / daily_total_infections[day - 4]) / 3
        projected_daily_total_infections = three_day_rate_of_growth * daily_total_infections[day - 1]
        return projected_daily_total_infections, three_day_rate_of_growth


    def sigmoid_projection(self,daily_total_infections):
        def f_sigmoid(x, a, b, c):
            # a = sigmoid midpoint
            # b = curve steepness (logistic growth)
            # c = max value
            return c * expit(b * (x - a))

        ydata = daily_total_infections
        xdata = np.arange(0, len(ydata))

        popt, pcov = curve_fit(f_sigmoid, xdata, ydata, [np.median(xdata)+20, 1, max(ydata)], method='lm')

        one_stdev = np.sqrt(np.diag(pcov))
        a_ymin = popt[0] + 3 * one_stdev[0]
        b_ymin = popt[1] - 3 * one_stdev[1]
        c_ymin = popt[2] - 3 * one_stdev[2]
        a_ymax = popt[0] - 3 * one_stdev[0]
        b_ymax = popt[1] + 3 * one_stdev[1]
        c_ymax = popt[2] + 3 * one_stdev[2]

        x_pred = np.arange(0, len(ydata) + 20)
        y_pred = f_sigmoid(x_pred, popt[0], popt[1], popt[2])
        y_pred_min = f_sigmoid(x_pred, a_ymin, b_ymin, c_ymin)
        y_pred_max = f_sigmoid(x_pred, a_ymax, b_ymax, c_ymax)

        sdate = date(2020, 1, 22)  # start date
        day_list = []

        for i in range(len(y_pred)):
            day_list.append(sdate + timedelta(days=i))

        return day_list, y_pred, y_pred_min, y_pred_max


    def plot_provincial_data(self,province_id):
        url = 'https://coronavirus-tracker-api.herokuapp.com/v2/locations/' + str(province_id)

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

        sdate = date(2020, 1, 22)  # start date
        edate = date.today() + timedelta(days=5)  # end date

        delta = edate - sdate  # as timedelta

        day_list = []
        for i in range(delta.days + 1):
            day_list.append(sdate + timedelta(days=i))

        daily_total_infections = []
        for i in range(0, len(daily_infections)):
            daily_total_infections.append(np.sum(daily_infections[0:i + 1]))

        day_list, y_pred, y_pred_min, y_pred_max = self.sigmoid_projection(daily_total_infections)

        return daily_total_infections, day_list, y_pred, y_pred_min, y_pred_max