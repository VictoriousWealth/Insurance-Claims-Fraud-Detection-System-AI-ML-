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
        id="losses_plot_tabs",
        value="line",  # default selected tab
        children=[
            dcc.Tab(label="Line Plot", value="line"),
            dcc.Tab(label="Scatter Plot", value="scatter"),
            dcc.Tab(label="Histogram", value="histogram")
        ]
    ),
    dcc.Graph(
        id="losses_graph",
        figure={"data": [], "layout": {"title": "Loading..."}}  
    ),
    
    html.H2("Claims against premium amount"),
    dcc.Tabs(
        id="claim_vs_premium_tabs",
        value="scatter",  
        children=[
            dcc.Tab(label="Scatter Plot", value="scatter"),
        ]
    ),
    dcc.Graph(
        id="claim_vs_premium_graph",
        figure={"data": [], "layout": {"title": "Loading..."}}  
    ),
    
    html.H2("Polocy date against Loss date"),
    dcc.Tabs(
        id="policy_vs_loss_tabs",
        value="scatter",  
        children=[
            dcc.Tab(label="Scatter Plot", value="scatter"),
        ]
    ),
    dcc.Graph(
        id="policy_vs_loss_graph",
        figure={"data": [], "layout": {"title": "Loading..."}} 
    ),

    html.H2("Claim Amount Against Days of Grace"),
    dcc.Tabs(
        id="days_of_grace_vs_claim_tabs",
        value="scatter",  
        children=[
            dcc.Tab(label="Scatter Plot", value="scatter"),
            dcc.Tab(label="Line Plot", value="line"),
            dcc.Tab(label="Histogram Plot", value="histogram"),
        ]
    ),
    dcc.Graph(
        id="days_of_grace_vs_claim_graph",
        figure={"data": [], "layout": {"title": "Loading..."}} 
    ),
    
    
    html.H1("Displaying the data for investigators"),
    dash_table.DataTable(
        id="vendor_table",
        page_size=20,
        filter_action="native", 
        sort_action="native",
        style_table={"overflowX": "auto"}
    ),
    
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

# graph no of claims against time
@dash_app.callback(
    Output("losses_graph", "figure"),
    Input("losses_plot_tabs", "value")
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

# graph claim amount vs premium amount
@dash_app.callback(
    Output("claim_vs_premium_graph", "figure"),
    Input("claim_vs_premium_tabs", "value")
)
def update_plot(selected_plot):
    response = requests.get("http://127.0.0.1:8000/api/insurance")
    if response.status_code == 200:
        data = response.json()
        claimsVsPremiums = [[record.get("CLAIM_AMOUNT"), record.get("PREMIUM_AMOUNT")] for record in data if "CLAIM_AMOUNT" and "PREMIUM_AMOUNT" in record]
        df = pandas.DataFrame(claimsVsPremiums, columns=["CLAIM_AMOUNT", "PREMIUM_AMOUNT"])
        if not df.empty:
            return px.scatter(
                df,
                x="PREMIUM_AMOUNT",
                y="CLAIM_AMOUNT",
                title="Scatter Plot: Premium Against Claims"
            )
    return {"data": [], "layout": {"title": "No data available"}}

# graph report date vs policy effectual date
@dash_app.callback(
    Output("policy_vs_loss_graph", "figure"),
    Input("policy_vs_loss_tabs", "value")
)
def update_plot(selected_plot):
    response = requests.get("http://127.0.0.1:8000/api/insurance")
    if response.status_code == 200:
        data = response.json()
        policyVsLoss = [[record.get("POLICY_EFF_DT"), record.get("LOSS_DT")] for record in data if "POLICY_EFF_DT" and "LOSS_DT" in record]
        df = pandas.DataFrame(policyVsLoss, columns=["POLICY_EFF_DT", "LOSS_DT"])
        
        # converting into datetime objects
        df["LOSS_DT"] = pandas.to_datetime(df["LOSS_DT"], errors='coerce')
        df = df.dropna(subset=["LOSS_DT"])
        df["POLICY_EFF_DT"] = pandas.to_datetime(df["POLICY_EFF_DT"], errors='coerce')
        df = df.dropna(subset=["POLICY_EFF_DT"])

        if not df.empty:
            return px.scatter(
                df,
                x="POLICY_EFF_DT",
                y="LOSS_DT",
                title="Scatter Plot: Policy date Against Loss date"
            )
    return {"data": [], "layout": {"title": "No data available"}}

@dash_app.callback(
    Output("days_of_grace_vs_claim_graph", "figure"),
    Input("days_of_grace_vs_claim_tabs", "value")
)
def update_plot(selected_plot):
    # Fetch insurance data from the API
    response = requests.get("http://127.0.0.1:8000/api/insurance")
    if response.status_code == 200:
        data = response.json()
        # Build a list of tuples only if all required keys exist
        records = [
            (
                record.get("POLICY_EFF_DT"),
                record.get("LOSS_DT"),
                record.get("CLAIM_AMOUNT")
            )
            for record in data
            if "POLICY_EFF_DT" in record and "LOSS_DT" in record and "CLAIM_AMOUNT" in record
        ]
        
        # If there are no valid records, return an empty figure.
        if not records:
            return {"data": [], "layout": {"title": "No data available"}}
        
        # Create a DataFrame with proper column names.
        df = pandas.DataFrame(records, columns=["POLICY_EFF_DT", "LOSS_DT", "CLAIM_AMOUNT"])
        
        # Convert date columns to datetime objects.
        df["POLICY_EFF_DT"] = pandas.to_datetime(df["POLICY_EFF_DT"], errors='coerce')
        df["LOSS_DT"] = pandas.to_datetime(df["LOSS_DT"], errors='coerce')
        # Drop rows with invalid dates or missing claim amounts.
        df = df.dropna(subset=["POLICY_EFF_DT", "LOSS_DT", "CLAIM_AMOUNT"])
        
        # Compute the difference between LOSS_DT and POLICY_EFF_DT in days.
        df["DAYS_OF_GRACE"] = (df["LOSS_DT"] - df["POLICY_EFF_DT"]).dt.days
        
        # Create the figure based on the selected tab.
        if selected_plot == "line":
            # For a line plot, sort by DAYS_OF_GRACE.
            fig = px.line(
                df.sort_values("DAYS_OF_GRACE"),
                x="DAYS_OF_GRACE",
                y="CLAIM_AMOUNT",
                title="Line Plot: Claim Amount vs. Days of Grace"
            )
        elif selected_plot == "scatter":
            fig = px.scatter(
                df,
                x="DAYS_OF_GRACE",
                y="CLAIM_AMOUNT",
                title="Scatter Plot: Claim Amount vs. Days of Grace"
            )
        elif selected_plot == "histogram":
            # Histogram showing the distribution of claim amounts over different grace periods.
            fig = px.histogram(
                df,
                x="DAYS_OF_GRACE",
                y="CLAIM_AMOUNT",
                title="Histogram: Claim Amount vs. Days of Grace",
                nbins=50
            )
        else:
            # In case of an unrecognized tab value, return an empty figure.
            fig = {"data": []}
        
        return fig
    # If the API call fails, return an empty figure with a message.
    return {"data": [], "layout": {"title": "No data available"}}

# Mount Dash inside FastAPI
fastapi_app.mount("/dash", WSGIMiddleware(dash_app.server))

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="127.0.0.1", port=8000)

# check the date difference between report date and policy effective date
# check the date difference between incident date and policy effective date
# check where incident date is before policy effective date
# check where report date is before policy effective date