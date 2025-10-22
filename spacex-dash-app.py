# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Build dropdown options: 'ALL' + sitios únicos
site_options = (
    [{'label': 'All Sites', 'value': 'ALL'}] +
    [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]
)

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown de selección de sitio
    dcc.Dropdown(
        id='site-dropdown',
        options=site_options,
        value='ALL',  # default: todos los sitios
        placeholder='Select a Launch Site here',
        searchable=True,
        clearable=False
    ),

    html.Br(),

    # TASK 2: Pie chart
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Range slider de payload
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload],
        allowCross=False
    ),

    # TASK 4: Scatter payload vs. éxito
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: callback para actualizar el pie chart según el dropdown
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_success_pie(selected_site):
    if selected_site == 'ALL':
        # Para todos los sitios: contar SOLO los éxitos (class=1) por sitio
        df = (spacex_df[spacex_df['class'] == 1]
              .groupby('Launch Site')
              .size()
              .reset_index(name='count'))
        fig = px.pie(
            df, values='count', names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        # Para un sitio específico: Success vs Failure en ese sitio
        df_site = spacex_df[spacex_df['Launch Site'] == selected_site]
        counts = (df_site['class']
                  .value_counts()
                  .rename_axis('Outcome')
                  .reset_index(name='count'))
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            counts, values='count', names='Outcome',
            title=f'Success vs Failure for site {selected_site}'
        )
    return fig

# TASK 4: callback para el scatter payload vs éxito
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range

    # Filtrar por rango de payload
    df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Filtrar por sitio si no es ALL
    title_site = 'All Sites'
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title_site = selected_site

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        title=f'Correlation between Payload and Success ({title_site})'
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(port=8000)
