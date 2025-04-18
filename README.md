# Multi Parameters Visualizer

A Python-based desktop application for tracking and visualizing various parameters over time. This tool helps you monitor multiple parameters with visual indicators for normal and abnormal ranges. Developed using cursor AI.

## Features

- Track multiple parameters simultaneously
- Visual representation of data with separate graphs for each parameter
- Color-coded data points (green for normal range, red for abnormal)
- Automatic data persistence using CSV storage
- Pre-defined normal ranges for common parameters
- Parameters controlled by a JSON file
- Easy-to-use interface with dropdown selection
- **Web-based Graph Rendering**: Uses Plotly to render interactive graphs in the web browser
- **QR Code Display**: Generates a QR code for easy sharing or accessing the application
- **Data Extraction Logic**: Converts XML data to JSON and extracts relevant data into CSV format for further processing

## Requirements

- Python 3.x
- Required Python packages:
  - pandas
  - numpy
  - plotly
  - dash
  - dash-bootstrap-components
  - xmltodict

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-params-visualizer.git
cd multi-params-visualizer
```

2. Install the required packages:
```bash
pip install pandas numpy plotly dash dash-bootstrap-components xmltodict
```

## Usage

1. Run the application (assuming data already exists in files pointed in config.py, if not, go to Step-2)
```bash
python3 App.py
```

2. To process XML data, Use the `extractData.py` script to convert XML data into JSON and CSV formats:
```bash
python3 extractData.py <path_to_input_xml>
```

3. Open the application in your browser:
   - The application will generate interactive graphs for each parameter using Plotly.
   - A QR code will be displayed for easy access to the application, on other devices on same network.

## Data Extraction Logic

The application includes a robust data extraction pipeline:
1. **XML to JSON Conversion**: The `extractData.py` script uses `xmltodict` to parse XML files into JSON format.
2. **JSON to CSV Conversion**: Extracts relevant data (e.g., headers and rows) from the JSON and saves it as a CSV file.
3. **Parameter Normalization**: Processes the extracted data to compute normal ranges and stores them in a JSON file (`parameters.json`).
4. **Data Storage**: Combines historical data with new data and saves it in `stored_data.csv`.

## Data Storage

All data is stored in a CSV file (`stored_data.csv`) with the following columns:
- Date: The date of the measurement
- Value: The measured value
- Parameter: The type of measurement

## Contributing

Feel free to submit issues and enhancement requests!