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

# Dropping unused columns
df = df.drop(['Profile Name', 'Attributes', 'Supplemental Video Type', 'Bookmark', 'Latest Bookmark',
              'Country'], axis=1)

# Convert the 'Start Time' column to datetime data type
df['Start Time'] = pd.to_datetime(df['Start Time'])

# Split the 'Start Time' column into separate day, month, year, and time columns
df[['Day', 'Month', 'Year', 'Time']] = df['Start Time'].apply(lambda x: pd.Series([x.day, x.month, x.year, x.time()]))

# Extract the weekday name from the 'Start Time' column
df['Weekday'] = df['Start Time'].dt.day_name()

# Convert the 'Duration' column to timedelta format
df['Duration'] = pd.to_timedelta(df['Duration'], unit='m')


# ------------------------ Analyzing Data --------------------


# ------------------------ Building Data Visualization with Dash --------------------


#------------------------- Create the Dash application ------------------------


if __name__ == '__main__':
    app.run_server(debug=True)