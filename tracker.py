import dash
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Define constants and file paths
CSV_FILE_PATH = 'NetflixViewingHistory.csv'

# Load the CSV file into a Pandas DataFrame
df = pd.read_csv(CSV_FILE_PATH)

# ------------------------ Loading Data --------------------


# ------------------------ Analyzing Data --------------------


# ------------------------ Building Data Visualization with Dash --------------------


#------------------------- Create the Dash application ------------------------


if __name__ == '__main__':
    app.run_server(debug=True)