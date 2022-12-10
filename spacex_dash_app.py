# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
options = [{'label': 'All Sites', 'value': 'ALL'}]
for LS in spacex_df['Launch Site'].unique():
    options.append({'label': LS, 'value': LS})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=options,
                                    value='ALL',
                                    placeholder='Select a Launch Site Here',
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    value=[min_payload, max_payload]
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df
    if entered_site == 'ALL':
        df = spacex_df.groupby(['Launch Site']).sum()[['class']]
        df.reset_index(inplace=True)
        fig = px.pie(df,
                     values='class',
                     names='Launch Site',
                     title='Total Successful Launches By Site'
                     )
        return fig
    else:
        df = spacex_df[spacex_df['Launch Site'] == entered_site].groupby(['class'])[['Launch Site']].count()
        df.reset_index(inplace=True)
        fig = px.pie(df,
                     values='Launch Site',
                     names='class',
                     title=f'Total Successful Launches for {entered_site}'
                     )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output

@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
                [Input(component_id='site-dropdown', component_property='value'),
                Input(component_id="payload-slider", component_property="value")]
              )
def get_graph(entered_site, mass_range):
    df = spacex_df[['Launch Site','class',"Booster Version Category","Payload Mass (kg)"]]
    if entered_site != 'ALL':
        df  = df[df['Launch Site'] == entered_site]
    #Range set
    df = df[df["Payload Mass (kg)"] > mass_range[0]]
    df = df[df["Payload Mass (kg)"] < mass_range[1]]

    fig = px.scatter(df,
            x="Payload Mass (kg)",
            y="class",
            color="Booster Version Category",
            size='Payload Mass (kg)',
            hover_data=['Payload Mass (kg)']
            )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
