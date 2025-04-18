import pandas as pd
import json
import plotly.graph_objs as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc
import config
import webbrowser
import ipqr
import threading
import time
import argparse
import extractdata
# === Load Data ===
df = pd.read_csv(config.data_file)
with open(config.param_file, 'r') as f:
    param_info = json.load(f)['parameters']

# Convert date to datetime
df['Date'] = pd.to_datetime(df['Date'])

# === Initialize Dash App ===
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# === Generate Graphs ===
graphs = []

for param in df['Parameter'].unique():
    param_df = df[df['Parameter'] == param].sort_values('Date')

    if param not in param_info:
        continue

    meta = param_info[param]
    min_val = meta.get('min', float('-inf'))
    max_val = meta.get('max', float('inf'))
    unit = meta.get('unit', '')
    description = meta.get('description', '')

    # Determine colors for lines
    param_df['Color'] = param_df['Value'].apply(
        lambda x: 'green' if min_val <= x <= max_val else 'red'
    )

    trace = go.Scatter(
        x=param_df['Date'],
        y=param_df['Value'],
        mode='lines+markers',
        line=dict(color='green'),  # default
        marker=dict(color=param_df['Color']),
        name=param
    )

    # Add normal range as horizontal band
    shapes = [
        dict(
            type="rect",
            xref="paper", yref="y",
            x0=0, x1=1,
            y0=min_val, y1=max_val,
            fillcolor="rgba(0,255,0,0.1)",
            line=dict(width=0)
        )
    ]

    layout = go.Layout(
        title=f"{param} ({unit})",
        height=300,
        margin=dict(l=40, r=40, t=40, b=40),
        shapes=shapes,
        legend=dict(orientation="h"),
        xaxis=dict(title="Date"),
        yaxis=dict(title=f"{param} ({unit})"),
        hovermode='closest'
    )

    fig = go.Figure(data=[trace], layout=layout)

    # Create card for each parameter graph
    graphs.append(
        dbc.Card([
            dbc.CardHeader(html.H5(param)),
            dbc.CardBody([
                html.P(description, style={"fontSize": "0.9rem", "color": "#555"}),
                dcc.Graph(figure=fig)
            ])
        ], className="mb-4")
    )

# === App Layout ===
app.layout = dbc.Container([
    html.H2("Tracker | Vaaheguru", className="my-4"),
    html.Div(graphs, style={"maxHeight": "90vh", "overflowY": "scroll"})
], fluid=True)

def run_server():
    app.run(host='0.0.0.0',port=8050, debug=False, use_reloader=False)
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Convert XML to JSON and extract data to CSV.")
    parser.add_argument("input_xml", type=str, nargs="?", help="Path to the input XML file")  # Use nargs="?" to make it optional
    args = parser.parse_args()

    if args.input_xml:
        # Process the input XML file
        input_xml = args.input_xml
        extractdata.process(input_xml)
      # Start server in a background thread
    threading.Thread(target=run_server, daemon=False).start()

    # Small delay to ensure server has started
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8050", new=1)
    time.sleep(3)
    ipqr.showqr()
