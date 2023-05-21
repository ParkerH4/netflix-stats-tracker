import dash
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


# Define constants
CSV_FILE_PATH = 'NetflixViewingHistory.csv'

# Read file
df = pd.read_csv(CSV_FILE_PATH)

# ------------------------ Loading Data --------------------

# Dropping unused columns
df = df.drop(['Profile Name', 'Attributes', 'Supplemental Video Type', 'Bookmark', 'Latest Bookmark',
              'Country'], axis=1)

# Split the 'Start Time' column into separate day, month, year, and time columns
df[['Day', 'Month', 'Year', 'Time']] = df['Start Time'].apply(lambda x: pd.Series([x.split(' ')[0].split('-')[2], x.split(' ')[0].split('-')[1], x.split(' ')[0].split('-')[0], x.split(' ')[1]]))

# Extract the actual weekday name from the 'Start Time' column
df['Weekday'] = pd.to_datetime(df['Start Time']).dt.day_name()

# Split up title to not include episode names
df['Title'] = df['Title'].str.split(':').str[0].str.strip()

# Convert the 'Duration' column to timedelta format
df['Duration'] = pd.to_timedelta(df['Duration'])

# Make the duration filter out anything below 1 min because Netflix data counts autoplays and ads
df = df[df['Duration']> '00:1:00']

# ------------------------ Analyzing Data --------------------


# Calculate total hours watched
hours_watched = df['Duration'].sum().total_seconds() / 3600

# Calculate the number of unique content watched
unique_content = df['Title'].nunique()

# Calculate the total number of content
total_content = df.shape[0]




# Calculate watch time per show and then sort
watch_time_per_show = df.groupby('Title')['Duration'].sum().reset_index()
watch_time_per_show = watch_time_per_show.sort_values('Duration', ascending=False)

# Select the top 10 shows based on watch time
top_10_shows = watch_time_per_show.head(10)

# Calculate the top 10 hours watched and put into variable
top_10_shows['Hours Watched'] = top_10_shows['Duration'].dt.total_seconds() / 3600





# Calculate the shows with the most episodes watched 
most_episodes_watched = df.groupby('Title')['Day'].count().reset_index()
most_episodes_watched = most_episodes_watched.rename(columns={'Day': 'Episodes Watched'})

# Calculate average hours spent watching the show
avg_hours_watched = df.groupby('Title').apply(lambda x: x['Duration'].sum() / pd.to_timedelta(x['Day'].nunique(), unit='D')).reset_index()
avg_hours_watched = avg_hours_watched.rename(columns={0: 'Avg Hrs Watched'})

# Combine the top 10 fastest binge watches by most episodes in one day, and average hours per day and sort accordingly
top_10_fastest_binges = pd.merge(top_10_shows, most_episodes_watched, on='Title')
top_10_fastest_binges = pd.merge(top_10_fastest_binges, avg_hours_watched, on='Title')





# Calculate the number of views per device
device_views = df['Device Type'].apply(lambda x: ' '.join(x.split()[:2])).value_counts().head(5)

# Calculate watch time by specific weekday
watch_time_by_weekday = df.groupby('Weekday')['Duration'].sum().reset_index()

# Calculate the percentage of watch time for each weekday
watch_time_by_weekday['Percentage'] = (watch_time_by_weekday['Duration'].dt.total_seconds() / df['Duration'].sum().total_seconds()) * 100



# ------------------------ Building Data Visualization with Dash --------------------

# Create a pie chart to display the percentage of watch time on each weekday
weekday_pie_chart = go.Figure(data=go.Pie(
    labels=watch_time_by_weekday['Weekday'],
    values=watch_time_by_weekday['Percentage'],
    textinfo='label+percent',
    marker=dict(colors=px.colors.qualitative.Pastel)
))

# Create an HTML table to display the top 10 shows based on watch time
top_10_shows_table = html.Table(
    className='table',
    style={ 'text-align': 'center', 'margin': '0', 'border-collapse': 'collapse'},
    children=[
        html.Thead(
            html.Tr([
                html.Th('Title', style={ 'border': '1px solid white', 'padding': '5px'}),
                html.Th('Hours Watched', style={ 'border': '1px solid white', 'padding': '5px'})
            ], style={'background-color': 'red'})
        ),
        html.Tbody([
            html.Tr([
                html.Td(title, style={'background-color': '#D8D8D8', 'color': 'black','border': '1px solid white', 'padding': '5px'}),
                html.Td(f'{hours:.2f}', style={'background-color': '#D8D8D8', 'color': 'black', 'border': '1px solid white', 'padding': '5px'})
            ])
            for title, hours in zip(top_10_shows['Title'], top_10_shows['Hours Watched'])
        ])
    ]
)

# Create an HTML table to display the top 10 binged shows
top_10_fastest_binges_table = html.Table(
    className='table',
    style={'background-color': '#333', 'text-align': 'center', 'margin': '0', 'border-collapse': 'collapse'},
    children=[
        html.Thead(
            html.Tr([
                html.Th('Title', style={'border': '1px solid white', 'padding': '5px'}),
                html.Th('Episodes Watched', style={'border': '1px solid white', 'padding': '5px'}),
                html.Th('Avg Hrs Watched', style={'border': '1px solid white', 'padding': '5px'})
            ], style={'background-color': 'red'})
        ),
        html.Tbody([
            html.Tr([
                html.Td(title, style={'background-color': '#D8D8D8', 'color': 'black', 'border': '1px solid white', 'padding': '5px'}),
                html.Td(episodes_in_one_day, style={'background-color': '#D8D8D8', 'color': 'black', 'border': '1px solid white', 'padding': '5px'}),
                html.Td(f'{episodes_in_one_day / hours:.2f}', style={'background-color': '#D8D8D8', 'color': 'black', 'border': '1px solid white', 'padding': '5px'})
            ])
            for title, episodes_in_one_day, hours in zip(
                top_10_fastest_binges['Title'],
                top_10_fastest_binges['Episodes Watched'],
                top_10_shows['Hours Watched']
            )
        ])
    ]
)


# Create a pie chart to display the number of views per device
device_views_pie_chart = go.Figure(data=go.Pie(
    labels=device_views.index,
    values=device_views.values,
    textinfo='label+percent',
    marker=dict(colors=px.colors.qualitative.Pastel)
))

# Remove the background colors of the pie chart
device_views_pie_chart.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
      title_font_color='white'
)


# Update the layout of the weekday pie chart
weekday_pie_chart.update_layout(
    title={
        'text': 'Which day is watched the most?',
        'font': {
            'color': 'white'
        },
        'x': 0.5,  # Set the x position to center align the title
        'y': 0.9   # Set the y position to center align the title
    },
     legend={
        'font': {
            'color': 'white'
        }
    },
    paper_bgcolor='rgba(0, 0, 0, 0)',  # Set the background color of the plot area
    plot_bgcolor='rgba(0, 0, 0, 0)'   # Set the background color of the chart
)

# Update the layout of the device pie chart
device_views_pie_chart.update_layout(
    title={
        'text': 'Most used Netflix devices?',
         'font': {
            'color': 'white'
        },
        'x': 0.5,  # Set the x position to center align the title
        'y': 0.9   # Set the y position to center align the title
    },
     legend={
        'font': {
            'color': 'white'
        }
    },
    paper_bgcolor='rgba(0, 0, 0, 0)',  # Set the background color of the plot area
    plot_bgcolor='rgba(0, 0, 0, 0)'   # Set the background color of the chart
)


#-------------Create the Dash application------------------------
app = dash.Dash(__name__)

# Setting up the layout of the dashboard
app.layout = html.Div(
    style={'height': '100vh', 'width': '100%',  'display': 'flex', 'justify-content': 'center', 'align-items': 'center', },
    children=[
        html.Div(
            style={'background-color': '#969493', 'padding': '10px', 'width': '900px', 'text-align': 'center', 'color': 'white', },
            children=[
                # Title
                html.H1('Netflix Viewing Statistics', style={'background-color': 'red', 'display': 'inline-block', 'margin-bottom': '20px', 'width': '60%', 'border': '1px solid white'}),
                html.Div(
                    className='row',
                    children=[
                        html.Div(
                            # 3 stats cards section
                            className='card',
                            style={'background-color': 'red', 'display': 'inline-block', 'margin-right': '5px', 'width': '30%', 'border': '3px solid white'},
                            children=[
                                html.H3('Hours Watched', style={'color': 'white'}),
                                html.H2(f'{hours_watched:.2f}', style={'color': 'white'})
                            ]
                        ),
                        html.Div(
                            className='card',
                            style={'background-color': 'red', 'display': 'inline-block', 'margin-right': '5px', 'width': '30%', 'border': '3px solid white'},
                            children=[
                                html.H3('Total Content Watched', style={'color': 'white'}),
                                html.H2(total_content, style={'color': 'white'})
                            ]
                        ),
                        html.Div(
                            className='card',
                            style={'background-color': 'red', 'display': 'inline-block', 'margin-right': '5px', 'width': '30%', 'border': '3px solid white'},
                            children=[
                                html.H3('Unique Content', style={'color': 'white'}),
                                html.H2(unique_content, style={'color': 'white'})
                            ]
                        )
                    ]
                ),

               
                html.Div(
                # top 10 shows based on watch time
                    className='row',
                    children=[
                        html.Div(
                            className='card',
                            style={'width': '50%', 'display': 'inline-block'},
                            children=[
                                html.H3('Top 10 Shows Based on Watch Time'),
                                html.Div(
                                    id='top-10-shows-table',
                                    children=top_10_shows_table,
                                    style={'padding-left': '50px'}  
                                )
                            ]
                        ),
                        html.Div(
                             # top 10 binged shows
                            className='card',
                            style={'width': '50%', 'display': 'inline-block', },
                            children=[
                                html.H3('Top 10 Binged Shows'),
                                html.Div(
                                    id='top-10-fastest-binges-table',
                                    children=top_10_fastest_binges_table,
                                    style={'padding-left': '20px'}  
                                )
                            ]
                        )
                    ]
                ),

                html.Div(
                    # weekday pie chart
                    className='row',
                    children=[
                        html.Div(
                            className='card',
                            children=[
                                dcc.Graph(
                                    id='weekday-pie-chart',
                                    figure=weekday_pie_chart
                                )
                            ],
                            style={'width': '50%',  'margin-bottom': '0', 'display': 'inline-block'}
                        ),
                        html.Div(
                            # device pie chart
                            className='card',
                            children=[
                                dcc.Graph(
                                    id='device-views-pie-chart',
                                    figure=device_views_pie_chart
                                )
                            ],
                            style={'width': '50%',  'margin-bottom': '0',  'display': 'inline-block'}
                        )
                    ]
                )
            ]
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)