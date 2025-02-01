from fastapi import FastAPI
import pandas
import numpy as np
from dash import Dash, dcc, html, dash_table, Output, Input
import dash 
from starlette.middleware.wsgi import WSGIMiddleware
import uvicorn
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import urllib.parse
import plotly.express as px

# Connecting to postgres
username = "postgres"
password = "Oldham18@"
host = "localhost"
port = "5432"
database = "Insurance-Claims-Fraud-Detection-System-Database"
encoded_password = urllib.parse.quote_plus(password)
connection_string = f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# Initialize FastAPI
fastapi_app = FastAPI()

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Route to return sample data
@fastapi_app.get("/api/employees")
def get_employees():
    query = """
        SELECT "AGENT_ID",
            "AGENT_NAME",
            "DATE_OF_JOINING",
            CONCAT("ADDRESS_LINE1", ' ', "ADDRESS_LINE2", ', ', "CITY", ', ', "STATE", ' ', "POSTAL_CODE") AS "LOCATION",
            "EMP_ROUTING_NUMBER",
            "EMP_ACCT_NUMBER"
        FROM "Employee";
    """
    df = pandas.read_sql_query(query, engine)
    return df.to_dict(orient='records')

@fastapi_app.get("/api/insurance")
def get_insurance():
    query = 'SELECT * FROM "Insurance";'
    df = pandas.read_sql_query(query, engine)
    return df.to_dict(orient='records')

@fastapi_app.get("/api/vendors")
def get_vendors():
    query = 'SELECT * FROM "Vendor";'
    df = pandas.read_sql_query(query, engine)
    return df.to_dict(orient='records')

# Initialize Dash App
dash_app = Dash(
    __name__,
    requests_pathname_prefix="/dash/"  # Ensure Dash assets are served correctly
)

# Dash Layout
dash_app.layout = html.Div([
    html.H1("Displaying the data for employees"),
    dash_table.DataTable(
        id="employee_table",
        page_size=20,
        filter_action="native", 
        sort_action="native",
        style_table={"overflowX": "auto"}
    ),
    html.H1("Displaying the data for claims"),
    dash_table.DataTable(
        id="insurance_table",
        page_size=20,
        filter_action="native", 
        sort_action="native",
        style_table={"overflowX": "auto"}
    ),
    html.H2("Numbers of losses per date"),
    dcc.Tabs(
        id="plot_tabs",
        value="line",  # default selected tab
        children=[
            dcc.Tab(label="Line Plot", value="line"),
            dcc.Tab(label="Scatter Plot", value="scatter"),
            dcc.Tab(label="Histogram", value="histogram")
        ]
    ),
    dcc.Graph(
        id="losses_graph",
        figure={"data": [], "layout": {"title": "Loading..."}}  # default valid figure
    ),
    html.H1("Displaying the data for investigators"),
    dash_table.DataTable(
        id="vendor_table",
        page_size=20,
        filter_action="native", 
        sort_action="native",
        style_table={"overflowX": "auto"}
    ),
    # For testing, consider making the button visible initially
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # 60 seconds in milliseconds
        n_intervals=0
    ),
    dcc.Store(id="data-store")
])

# Employee table display processes
@dash_app.callback(
    Output("employee_table", "columns"),
    Output("employee_table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_employee_table(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/employees") 
    if response.status_code == 200:
        data = response.json()
        if data:
            columns = [{"name": col, "id": col} for col in list(data[0].keys())]
            return columns, data
    return [], []

# Insurance table display processes
@dash_app.callback(
    Output("insurance_table", "columns"),
    Output("insurance_table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_insurance_table(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/insurance") 
    if response.status_code == 200:
        data = response.json()
        if data:
            columns = [{"name": col, "id": col} for col in list(data[0].keys())]
            return columns, data
    return [], []

# Vendor table display processes
@dash_app.callback(
    Output("vendor_table", "columns"),
    Output("vendor_table", "data"),
    Input("interval-component", "n_intervals"),
)
def update_vendor_table(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/vendors") 
    if response.status_code == 200:
        data = response.json()
        if data:
            columns = [{"name": col, "id": col} for col in list(data[0].keys())]
            return columns, data
    return [], []

@dash_app.callback(
    Output("losses_graph", "figure"),
    Input("plot_tabs", "value")
)
def update_plot(selected_plot):
    response = requests.get("http://127.0.0.1:8000/api/insurance")
    if response.status_code == 200:
        data = response.json()
        # Extract LOSS_DT values if they exist
        loss_dates = [record.get("LOSS_DT") for record in data if "LOSS_DT" in record]
        df = pandas.DataFrame({'LOSS_DT': loss_dates})
        if not df.empty:
            # Convert LOSS_DT to datetime
            df["LOSS_DT"] = pandas.to_datetime(df["LOSS_DT"], errors='coerce')
            df = df.dropna(subset=["LOSS_DT"])
            # For line and scatter plots, group by date to count occurrences
            df_grouped = df.groupby("LOSS_DT").size().reset_index(name="Count")
            df_grouped = df_grouped.sort_values("LOSS_DT")
            
            if selected_plot == "line":
                fig = px.line(
                    df_grouped,
                    x="LOSS_DT",
                    y="Count",
                    title="Line Plot: Losses Over Time"
                )
            elif selected_plot == "scatter":
                fig = px.scatter(
                    df_grouped,
                    x="LOSS_DT",
                    y="Count",
                    title="Scatter Plot: Losses Over Time"
                )
            elif selected_plot == "histogram":
                # Here we can plot a histogram directly on the raw date data
                fig = px.histogram(
                    df,
                    x="LOSS_DT",
                    title="Histogram: Losses Over Time",
                    nbins=50
                )
            else:
                fig = {"data": []}
            return fig
    return {"data": [], "layout": {"title": "No data available"}}

# Mount Dash inside FastAPI
fastapi_app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
