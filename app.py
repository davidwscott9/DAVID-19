import seaborn as sns
from datetime import date, timedelta
from operator import add
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
from scipy.optimize import curve_fit
from scipy.special import expit
import playground as pg

sns.set(palette='pastel')

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>DAVID-19</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# set the app.layout
app.layout = html.Div([    
    html.H1('DAVID-19'),
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

# Start script
playground = pg.Playground()

sdate = date(2020, 1, 22)  # start date
edate = date.today() + timedelta(days=5)  # end date
delta = edate - sdate  # as timedelta

day_list = []
for i in range(delta.days + 1):
    day_list.append(sdate + timedelta(days=i))

all_province_case_data = {}
all_province_projection_data = {}
all_province_projection_data_min = {}
all_province_projection_data_max = {}

cumulative_total, day_list_pred, cumulative_projected_total, \
cumulative_projected_total_min, \
cumulative_projected_total_max = playground.plot_provincial_data(35)

all_province_case_data['35'] = cumulative_total
all_province_projection_data['35'] = cumulative_projected_total
all_province_projection_data_min['35'] = cumulative_projected_total_min
all_province_projection_data_max['35'] = cumulative_projected_total_max

# Set the URL of the REST api we are getting data from (i.e. location 42 is for the province of Ontario)
for province_id in range(36, 46):
    if (province_id == 37):
        continue
    all_province_case_data[str(province_id)], day_list_pred, all_province_projection_data[str(province_id)], \
    all_province_projection_data_min[str(province_id)], \
    all_province_projection_data_max[str(province_id)] = playground.plot_provincial_data(province_id)
    cumulative_total = list(map(add, cumulative_total, all_province_case_data[str(province_id)]))
    cumulative_projected_total = list(
        map(add, cumulative_projected_total, all_province_projection_data[str(province_id)]))
    cumulative_projected_total_min = list(
        map(add, cumulative_projected_total_min, all_province_projection_data_min[str(province_id)]))
    cumulative_projected_total_max = list(
        map(add, cumulative_projected_total_max, all_province_projection_data_max[str(province_id)]))


def figure_creator(id):
    return {
        'data': [
            dict(
                y=all_province_projection_data[id],
                x=day_list_pred,
                mode='lines+markers',
                opacity=0.4,
                marker={
                    'size': 8,
                    'line': {'width': 0.5, 'color': 'gray'},
                    'color': 'gray'
                },
                name='Projected Cases,'
            ),
            dict(
                y=all_province_projection_data_max[id],
                x=day_list_pred,
                mode='none',
                opacity=0.4,
                marker={
                    'size': 8,
                    'line': {'width': 0.5, 'color': 'black'},
                    'color': 'black'
                },
                showlegend=False,
                name='Projected Error',
                fill='tonexty',
                fillcolor='rgba(0, 0, 0, 0)'
            ),
            dict(
                y=all_province_projection_data_min[id],
                x=day_list_pred,
                mode='none',
                opacity=0.4,
                marker={
                    'size': 8,
                    'line': {'width': 0.5, 'color': 'black'},
                    'color': 'black'
                },
                name='Projected Error',
                fill='tonexty',
                fillcolor='rgba(0, 0, 0, 0.1)'
            ),
            dict(
                y=all_province_case_data[id],
                x=day_list[0:-5],
                mode='lines+markers',
                opacity=1,
                marker={
                    'size': 8,
                    'line': {'width': 0.5, 'color': 'red'},
                    'color': 'red'
                },
                name='Confirmed Cases'
            )
        ],
        'layout': dict(
            xaxis={'type': 'date', 'title': 'Day'},
            yaxis={'title': 'DAVID-19 Cases'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
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
                            y=cumulative_projected_total,
                            x=day_list_pred,
                            mode='lines+markers',
                            opacity=0.4,
                            marker={
                                'size': 8,
                                'line': {'width': 0.5, 'color': 'gray'},
                                'color': 'gray'
                            },
                            name='Projected Cases'
                        ),
                        dict(
                            y=cumulative_projected_total_max,
                            x=day_list_pred,
                            mode='none',
                            opacity=0.4,
                            marker={
                                'size': 8,
                                'line': {'width': 0.5, 'color': 'black'},
                                'color': 'black'
                            },
                            showlegend=False,
                            name='Projected Error',
                            fill='tonexty',
                            fillcolor='rgba(0, 0, 0, 0)'
                        ),
                        dict(
                            y=cumulative_projected_total_min,
                            x=day_list_pred,
                            mode='none',
                            opacity=0.4,
                            marker={
                                'size': 8,
                                'line': {'width': 0.5, 'color': 'black'},
                                'color': 'black'
                            },
                            name='Projected Error',
                            fill='tonexty',
                            fillcolor='rgba(0, 0, 0, 0.1)'
                        ),
                        dict(
                            y=cumulative_total,
                            x=day_list[0:-5],
                            mode='lines+markers',
                            opacity=1,
                            marker={
                                'size': 8,
                                'line': {'width': 0.5, 'color': 'red'},
                                'color': 'red'
                            },
                            name='Confirmed Cases'

                        )
                    ],
                    'layout': dict(
                        xaxis={'type': 'date', 'title': 'Day'},
                        yaxis={'title': 'Confirmed Cases'},
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
                        legend={'x': 0, 'y': 1},
                        hovermode='closest'
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

if __name__ == '__main__':
    app.run_server()
