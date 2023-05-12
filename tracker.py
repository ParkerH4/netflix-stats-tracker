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

# Calculate total hours watched
hours_watched = df['Duration'].sum().total_seconds() / 3600

# Calculate the number of unique content watched
unique_content = df['Title'].nunique()

# Calculate the total number of content
total_content = df.shape[0]

# Calculate watch time per show
watch_time_per_show = df.groupby('Title')['Duration'].sum().reset_index()

# Sort the Data by watch time in descending order
watch_time_per_show = watch_time_per_show.sort_values('Duration', ascending=False)

# Select the top 10 shows 
top_10_shows = watch_time_per_show.head(10)

# top 10 hours watched
top_10_shows['Hours Watched'] = top_10_shows['Duration'].dt.total_seconds() / 3600

# Calculate the shows with the most episodes watched in a single day
most_episodes_in_one_day = df.groupby('Title')['Day'].count().reset_index()
most_episodes_in_one_day = most_episodes_in_one_day.rename(columns={'Day': 'Record episodes in a day'})

# Calculate average hours per day spent on the show
avg_hours_per_day = df.groupby('Title').apply(lambda x: x['Duration'].sum() / x['Day'].nunique()).reset_index()
avg_hours_per_day = avg_hours_per_day.rename(columns={0: 'Average Hours per Day'})

# Combine the top 10 fastest binge watches by : most episodes in one day, and average hours per day and sort accordingly
top_10_fastest_binges = pd.merge(top_10_shows, most_episodes_in_one_day, on='Title')
top_10_fastest_binges = pd.merge(top_10_fastest_binges, avg_hours_per_day, on='Title')
top_10_fastest_binges = top_10_fastest_binges.sort_values('Record episodes in a day', ascending=False) # sort table

# Calculate the number of views per device
device_views = df['Device Type'].value_counts().head(5)

# Calculate watch time by weekday
watch_time_by_weekday = df.groupby('Weekday')['Duration'].sum().reset_index()

# Calculate the percentage of watch time on weekdays
watch_time_by_weekday['Percentage'] = (watch_time_by_weekday['Duration'].dt.total_seconds() / df['Duration'].sum().total_seconds()) * 100



# ------------------------ Building Data Visualization with Dash --------------------


#------------------------- Create the Dash application ------------------------


if __name__ == '__main__':
    app.run_server(debug=True)