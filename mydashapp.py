import pandas as pd
import numpy as np
import bs4
import requests
import sqlite3
from time import time
from unicodedata import name
from dash import Dash, dcc, html, Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

app = Dash(__name__)
server = app.server
con = sqlite3.connect("hr.db")
df = pd.read_sql_query('select * from jobs;', con)
employees = pd.read_sql_query("select * from employees;", con)
jobs = pd.read_sql_query("select * from jobs;", con)


job_titles = jobs['job_title'].values[1:]
job_counts = [len(employees[employees['job_id'] == i]) for i in jobs['job_id']][1:]
mins = jobs['min_salary'].values[1:]
maxs = jobs['max_salary'].values[1:]

df_jobs = pd.DataFrame(list(zip(job_titles, job_counts, mins, maxs)), columns=['title', 'count', 'min', 'max'])
year = [2020, 2021, 2022] 

def getPercentiles():
    """Return a dictionary with percentiles from website"""

    result = {10:[],
              25:[],
              75:[],
              90:[]}
    
    url = 'https://www.itjobswatch.co.uk/jobs/uk/sqlite.do'
    html = requests.get(url).content
    soup = bs4.BeautifulSoup(html, 'html.parser')

    table  = soup.find('table', class_='summary')
    rows = table.find_all('tr')
    for i in rows:
        if "<td>10<sup>th</sup> Percentile</td>" in str(i):
            for b in i.find_all('td', class_='fig'):
                if str(b.text[1:])!= "":
                    result[10].append(int(b.text[1:].replace(",", "")))
                else:
                    result[10].append(None)
        if "<td>25<sup>th</sup> Percentile</td>" in str(i):
            for b in i.find_all('td', class_='fig'):
                if str(b.text[1:])!= "":
                    result[25].append(int(b.text[1:].replace(",", "")))
                else:
                    result[25].append(None)
        if "<td>75<sup>th</sup> Percentile</td>" in str(i):
            for b in i.find_all('td', class_='fig'):
                if str(b.text[1:])!= "":
                    result[75].append(int(b.text[1:].replace(",", "")))
                else:
                    result[75].append(None)
        if "<td>90<sup>th</sup> Percentile</td>" in str(i):
            for b in i.find_all('td', class_='fig'):
                if str(b.text[1:]) != "":
                    result[90].append(int(b.text[1:].replace(",", "")))
                else:
                    result[90].append(None)

    return result

def part_a(df):
    fig = px.bar(x=df['title'], y=df['count'])
    fig.update_layout(
        title="Count of Jobs",
        xaxis_title="Names",
        yaxis_title="Counts",
        legend_title="Job Title",
        xaxis = dict(
        tickmode = 'array',
        tickvals = [i for i in range(len(job_titles))],
        ticktext = job_titles,
        tickangle = 90
        )
    )

    return fig


def part_b(df):
    fig = go.Figure()

    fig.add_trace(go.Bar(x=df['max'] - df['min'], y=df["title"], orientation='h'))

    fig.update_layout(
        title="Salaries of different Jobs",
        xaxis_title="Salary",
        yaxis_title="Job Title",
    )



    return fig

def part_c(y):
    percentiles = getPercentiles()
    avg_salary = employees['salary'].mean()
    ind = [year.index(i) for i in sorted(y)]
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=year, y=[avg_salary for i in sorted(y)], name='Average Salary', line=dict(color="#000000")))

    for i in percentiles:
        yi = [percentiles[i][b] for b in ind]
        fig.add_trace(go.Scatter(x=year, y=yi, name=f'{i}th Percentile', line=dict(color="#30f216")))
    
    return fig






app.layout = html.Div([
    html.Div("Final exam", className='neon-text'),

    html.Div([

        html.P("Task 2", style={'text-align': 'center', "padding": "5px", "font-size": "30px"}),
        
        dcc.Dropdown(
                options=job_titles,
                multi=True,
                value='all',
                id="input1"),

        dcc.Graph(id="fig1", figure=part_a(df_jobs)),

        html.P("Task 3", style={'text-align': 'center', "padding": "5px", "font-size": "30px"}),
        dcc.Graph(id="fig2", figure=part_b(df_jobs)),
        dcc.RangeSlider(1000, 20000, 1000, value=[1000, 15000], id='range-slider'),

        html.P("Task 4", style={'text-align': 'center', "padding": "5px", "font-size": "30px"}),
        dcc.Dropdown(
                options=year,
                multi=True,
                value='all',
                id="input2"),
        dcc.Graph(id="fig3", figure=part_c(year)),

    ], className="mainDiv")
])

@app.callback(
    Output('fig2', 'figure'),
    [Input('range-slider', 'value')])
def update_output(value):
    return part_b(df_jobs[df_jobs['min']>value[0]][df_jobs['max']<value[1]])

@app.callback(
    Output('fig1', 'figure'),
    [Input('input1', 'value')])
def update_output(value):
    if len(value) == 0:
        return part_a(df_jobs)
    else:
        return part_a(df_jobs[df_jobs['title'].isin(value)])

@app.callback(
    Output('fig3', 'figure'),
    [Input('input2', 'value')])
def update_output(value):
    if len(value) == 0:
        return part_c(year)
    else:
        return part_c(value)
if __name__ == '__main__':
    app.run_server(debug=True)