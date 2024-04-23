import dash
from dash import dcc, html
import webbrowser
import os

# Create a Dash application
app = dash.Dash(__name__)

image_dir = os.path.join(os.getcwd(),"Images/")
logo = os.path.join(image_dir,"LOGO.png")

# Define the CSS styles for the dark YouTube theme
app.layout = html.Div(style={'backgroundColor': '#181818', 'color': 'white', 'margin': '-8px', 'height': '100vh'}, children=[
    # Header with YouTube logo and title
    html.Header(style={'display': 'flex', 'alignItems': 'center', 'padding': '10px 20px', 'backgroundColor': '#FF0000'}, children=[
        html.Img(src=logo, style={'height': '40px'}),  # Ensure the image path is correct
        html.H1('Dashboard', style={'marginLeft': '20px', 'color': 'white'})
    ]),
    
    # Container for the graphs
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around', 'padding': '20px'}, children=[
        # Each graph in a floating box with a header and settings icon
        html.Div(style={'width': '45%', 'backgroundColor': '#202020', 'margin': '10px', 'padding': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'overflow': 'hidden'}, children=[
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                html.H2('Shorts Performance', style={'color': 'white'}),
                html.Img(src='Images/settings_icon.png', style={'width': '24px', 'cursor': 'pointer'})  # Ensure the image path is correct
            ]),
            html.Iframe(srcDoc=open('Images/shorts.html', 'r').read(), style={'width': '100%', 'height': '400px', 'border': 'none', 'overflow': 'hidden'})
        ]),

        html.Div(style={'width': '45%', 'backgroundColor': '#202020', 'margin': '10px', 'padding': '20px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)', 'overflow': 'hidden'}, children=[
            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                html.H2('Weekend Activity', style={'color': 'white'}),
                html.Img(src='Images/settings_icon.png', style={'width': '24px', 'cursor': 'pointer'})  # Ensure the image path is correct
            ]),
            html.Iframe(srcDoc=open('Images/week_heatmap.html', 'r').read(), style={'width': '100%', 'height': '400px', 'border': 'none', 'overflow': 'hidden'})
        ]),
        # Repeat for other graphs
        # Add more graphs as needed
    ])

])

# Open the web browser
if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/')
    app.run_server(debug=True)
