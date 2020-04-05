import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import date, timedelta
from bs4 import BeautifulSoup   
import requests
from operator import add
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input,Output
import dash_bootstrap_components as dbc

sns.set(palette='pastel')

app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server
app.config.suppress_callback_exceptions = True

#set the app.layout
app.layout = html.Div([
    dcc.Tabs(id="tabs", value='ontario', children=[
        dcc.Tab(label='Alberta', value='35'),
        dcc.Tab(label='British Columbia', value='36'),
        dcc.Tab(label='Manitoba', value='38'),
        dcc.Tab(label='New Brunswick', value='39'),
        dcc.Tab(label='Newfoundland & Labrador', value='40'),
        dcc.Tab(label='Nova Scotia', value='41'),
        dcc.Tab(label='Ontario', value='42'),
        dcc.Tab(label='Prince Edward Island', value='43'),
        dcc.Tab(label='Quebec', value='44'),
        dcc.Tab(label='Saskatchewan', value='45'),
        dcc.Tab(label='Canada', value='all'),
    ]),
    html.Div(id='tabs-content')
])

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
    #plt.figure()
    if len(one_day_rate_of_growth[25::]) < len(day_list[26:-5]):
        plt.plot(day_list[26:-6], one_day_rate_of_growth[25::])
    else:
        plt.plot(day_list[26:-5], one_day_rate_of_growth[25::])
    plt.gcf().autofmt_xdate()
    plt.title('Rate of growth')

    # plot daily infections and projected
    #plt.figure()
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

all_province_case_data = {}
all_province_projection_data = {}

cumulative_total, cumulative_projected_total = plot_provincial_data(35)
all_province_case_data['35'] = cumulative_total
all_province_projection_data['35'] = cumulative_projected_total

# Set the URL of the REST api we are getting data from (i.e. location 42 is for the province of Ontario)
for province_id in range(36,46):  
    if (province_id == 37):
        continue  
    all_province_case_data[str(province_id)], all_province_projection_data[str(province_id)] = plot_provincial_data(province_id)  
    cumulative_total = list( map(add, cumulative_total,all_province_case_data[str(province_id)]))
    cumulative_projected_total = list(map(add, cumulative_projected_total,all_province_projection_data[str(province_id)]))

# plot daily infections and projected
#plt.figure()
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

def figure_creator(id):
    return {
        'data': [
            dict(
                y = all_province_case_data[id],
                x = day_list[0:-5],
                mode ='lines+markers',
                opacity = 1,
                marker = {
                    'size': 8,
                    'line': {'width': 0.5, 'color': 'blue'}
                },
                name = 'Confirmed Cases'
            ),
            dict(
                y = all_province_projection_data[id],
                x = day_list[4::],
                mode ='lines+markers',
                opacity = 0.4,
                marker = {
                    'size': 8,
                    'line': {'width': 0.5, 'color': 'black'},   
                    'color':'black'       
                }, 
                name = 'Projected Cases') 
        ],
        'layout': dict(
            xaxis = {'type': 'date', 'title': 'Day'},
            yaxis = {'title': 'DAVID-19 Cases'},
            margin = {'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend = {'x': 0, 'y': 1},
            hovermode = 'closest'
        )
    }
        

# callback to control content
@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'all':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure={
                    'data': [
                        dict(
                            y = cumulative_total,
                            x = day_list[0:-5],
                            mode ='lines+markers',
                            opacity = 1,
                            marker = {
                                'size': 8,
                                'line': {'width': 0.5, 'color': 'blue'}
                            },
                            name = 'Days v Confirmed Cases'
                        ),
                        dict(
                            y = cumulative_projected_total,
                            x = day_list[4::],
                            mode ='lines+markers',
                            opacity = 0.4,
                            marker = {
                                'size': 8,
                                'line': {'width': 0.5, 'color': 'black'},   
                                'color':'black'       
                            }, 
                            name = 'Projected Cases')                         
                    ],
                    'layout': dict(
                        xaxis = {'type': 'date', 'title': 'Day'},
                        yaxis = {'title': 'Confirmed Cases'},
                        margin = {'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend = {'x': 0, 'y': 1},
                        hovermode = 'closest'
                    )
                }
            )
        ])
    elif tab == '35':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('35')
            )
        ])
    elif tab == '36':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('36')
            )
        ])
    elif tab == '38':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('38')
            )
        ])
    elif tab == '39':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('39')
            )
        ])
    elif tab == '40':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('40')
            )
        ])
    elif tab == '41':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('41')
            )
        ])
    elif tab == '42':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('42')
            )
        ])
    elif tab == '43':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('43')
            )
        ])
    elif tab == '44':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('44')
            )
        ])
    elif tab == '45':
        return html.Div([
            dcc.Graph(
                id='covid',
                figure=figure_creator('45')
            )
        ])
    


app.run_server()