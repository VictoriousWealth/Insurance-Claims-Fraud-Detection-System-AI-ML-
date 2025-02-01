from fastapi import FastAPI
import pandas
import numpy as np
import random
import kagglehub
from dash import Dash, dcc, html, dash_table, Output, Input
import dash 
from starlette.middleware.wsgi import WSGIMiddleware
import uvicorn
import requests
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import urllib.parse

# Load datasets
employee_dataset = pandas.read_csv("./resources/employee_data.csv")
insurance_dataset = pandas.read_csv("./resources/insurance_data.csv")
vendor_dataset = pandas.read_csv("./resources/vendor_data.csv")

# Print dataset information
print("Employee dataset shape: ", employee_dataset.shape)
print("Employee dataset first 10 values: \n", employee_dataset.head(10))
print("Columns: ", employee_dataset.columns)

# Connecting to postgres
username = "postgres"
password = "Oldham18@"
host = "localhost"
port = "5432"
database = "Insurance-Claims-Fraud-Detection-System-Database"
encoded_password = urllib.parse.quote_plus(password)
connection_string = f"postgresql://{username}:{encoded_password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# creating tables
employee_dataset.to_sql('Employee', engine, if_exists='replace', index=False)
insurance_dataset.to_sql('Insurance', engine, if_exists='replace', index=False)
vendor_dataset.to_sql('Vendor', engine, if_exists='replace', index=False)

# Initialize FastAPI
fastapi_app = FastAPI()

# Enable CORS (needed when integrating with React.js later)
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
    query = 'SELECT * FROM "Employee";'
    df = pandas.read_sql_query(query, engine)
    return df.to_dict(orient='records')

# API Route to return sample data
@fastapi_app.get("/api/insurance")
def get_employees():
    query = 'SELECT * FROM "Insurance";'
    df = pandas.read_sql_query(query, engine)
    return df.to_dict(orient='records')

# API Route to return sample data
@fastapi_app.get("/api/vendors")
def get_employees():
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
        style_table={"overflowX": "auto"}
    ),
    html.H1("Displaying the data for claims"),
    dash_table.DataTable(
        id="insurance_table",
        page_size=20,
        style_table={"overflowX": "auto"}
    ),
    html.H1("Displaying the data for investigators"),
    dash_table.DataTable(
        id="vendor_table",
        page_size=20,
        style_table={"overflowX": "auto"}
    ),
    html.Button("Load Data", id="btn", n_clicks=0, hidden=True),
    dcc.Store(id="data-store")
])

# Employee table display processes
@dash_app.callback(
    Output("employee_table", "columns"),
    Output("employee_table", "data"),
    Input("btn", "n_clicks")
)
def update_employee_table(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/employees") 
    if response.status_code == 200:
        data = response.json()
        columns = [{"name": col, "id": col} for col in list(data[0].keys())]
        return columns, data
    else:
        return None, None

# Insurance table display processes
@dash_app.callback(
    Output("insurance_table", "columns"),
    Output("insurance_table", "data"),
    Input("btn", "n_clicks")
)
def update_insurance_table(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/insurance") 
    if response.status_code == 200:
        data = response.json()
        columns = [{"name": col, "id": col} for col in list(data[0].keys())]
        return columns, data
    else:
        return None, None

# Vendor table display processes
@dash_app.callback(
    Output("vendor_table", "columns"),
    Output("vendor_table", "data"),
    Input("btn", "n_clicks")
)
def update_vendor_table(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/vendors") 
    if response.status_code == 200:
        data = response.json()
        columns = [{"name": col, "id": col} for col in list(data[0].keys())]
        return columns, data
    else:
        return None, None



# Mount Dash inside FastAPI
fastapi_app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
