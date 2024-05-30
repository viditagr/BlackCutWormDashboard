import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import folium
from folium.plugins import HeatMap

# Load data
data = pd.read_csv('/Users/vidit/Documents/Entom/Website Scraping/black_cutworm_with_latlongv2.csv')

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Create dropdown options
dropdown_options = [{'label': loc, 'value': loc} for loc in data['Location'].unique()]

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Black Cutworm Dashboard"), width=12, className="mb-2")
    ]),
    dbc.Row([
        # Left half: slider and map
        dbc.Col([
            dcc.Slider(
                id='week-slider',
                min=1,
                max=9,
                marks={
                    1: 'April 4',
                    2: 'April 11',
                    3: 'April 18',
                    4: 'April 25',
                    5: 'May 2',
                    6: 'May 9',
                    7: 'May 16',
                    8: 'May 23',
                    9: 'May 30'
                },
                value=1,
                step=1,
                included=False
            ),
            html.Iframe(id='map', srcDoc='', width='100%', height='600')
        ], width=6, className="mb-2"),
        # Right half: dropdown and graph
        dbc.Col([
            dcc.Dropdown(id='location-dropdown', options=dropdown_options, placeholder="Select a location"),
            dcc.Graph(id='line-chart')
        ], width=6, className="mb-2")
    ])
])

@app.callback(
    Output('line-chart', 'figure'),
    [Input('location-dropdown', 'value')]
)
def update_chart(location):
    if location:
        df = data[data['Location'] == location]
        weeks = [f'Week {i}' for i in range(1, 10)]
        df = df.melt(id_vars=['Location'], value_vars=weeks, var_name='Week', value_name='Count')
        fig = px.line(df, x='Week', y='Count', title=f'Counts for {location}')
        return fig
    return px.line(title='Select a location to see counts')

@app.callback(
    Output('map', 'srcDoc'),
    [Input('week-slider', 'value')]
)
def update_map(selected_week):
    week_column = f'Week {selected_week}'
    heat_data = data[['Latitude', 'Longitude', week_column]].dropna()
    heat_data_list = heat_data[['Latitude', 'Longitude', week_column]].values.tolist()

    map_center = [heat_data['Latitude'].mean(), heat_data['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=6, control_scale=True, zoom_control=False, scrollWheelZoom=False)
    HeatMap(
        heat_data_list,
        radius=21,  # Adjust radius for sensitivity
        blur=10,    # Adjust blur for sensitivity
        min_opacity=0.5  # Set minimum opacity to keep the heatmap consistent
    ).add_to(m)

    # Add JavaScript to control the heatmap behavior
    folium.Element("""
    <script>
    function fixHeatmapZoom(map) {
        map.on('zoomend', function() {
            var currentZoom = map.getZoom();
            var heatmapLayer = map._layers[Object.keys(map._layers).find(key => map._layers[key] instanceof L.HeatLayer)];
            heatmapLayer._maxZoom = currentZoom;
            heatmapLayer._update();
        });
    }
    var map = maps[Object.keys(maps)[0]];
    fixHeatmapZoom(map);
    </script>
    """).add_to(m.get_root())

    map_file_path = '/Users/vidit/Documents/Entom/Website Scraping/black_cutworm_heatmap_temp.html'
    m.save(map_file_path)
    return open(map_file_path, 'r').read()

if __name__ == '__main__':
    app.run_server(debug=True)
