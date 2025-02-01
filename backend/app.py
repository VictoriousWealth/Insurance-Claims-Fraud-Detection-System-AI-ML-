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

# Load datasets
employee_dataset = pandas.read_csv("./resources/employee_data.csv")
insurance_dataset = pandas.read_csv("./resources/insurance_data.csv")
vendor_dataset = pandas.read_csv("./resources/vendor_data.csv")

# Print dataset information
print("Employee dataset shape: ", employee_dataset.shape)
print("Employee dataset first 10 values: \n", employee_dataset.head(10))
print("Columns: ", employee_dataset.columns)

# Initialize FastAPI
fastapi_app = FastAPI()

# Enable CORS (needed when integrating with React.js later)
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow all origins (for testing, restrict in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Route to return sample data
@fastapi_app.get("/api/data")
def get_data():
    return {"x": [1, 2, 3], "y": [5, 3, 7]}

# Initialize Dash App
dash_app = Dash(
    __name__,
    requests_pathname_prefix="/dash/"  # Ensure Dash assets are served correctly
)

# Dash Layout
dash_app.layout = html.Div([
    html.H1("Dynamic Graph from FastAPI"),
    dcc.Graph(id="graph"),
    html.Button("Load Data", id="btn", n_clicks=0),
    dcc.Store(id="data-store")
])

# Dash Callback
@dash_app.callback(
    Output("graph", "figure"),
    Input("btn", "n_clicks")
)
def update_graph(n_clicks):
    response = requests.get("http://127.0.0.1:8000/api/data")  # Fetch data from FastAPI
    data = response.json()
    return {"data": [{"x": data["x"], "y": data["y"], "type": "line"}]}

# Mount Dash inside FastAPI
fastapi_app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)
