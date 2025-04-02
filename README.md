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

## Requirements

- Python 3.x
- Required Python packages:
  - tkinter (usually comes with Python)
  - matplotlib
  - pandas
  - numpy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/multi-params-visualizer.git
cd multi-params-visualizer
```

2. Install the required packages:
```bash
pip install matplotlib pandas numpy
```

## Usage

1. Run the application:
```bash
python MultiParamsVisualizer.py
```

2. To add a new data point:
   - Select the parameter from the dropdown menu
   - Enter the date in YYYY-MM-DD format
   - Enter the value
   - Click "Add Data Point"

3. The data will be automatically saved to `stored_data.csv` in the same directory.

## Data Storage

All data is stored in a CSV file (`stored_data.csv`) with the following columns:
- Date: The date of the measurement
- Value: The measured value
- Parameter: The type of measurement

## Contributing

Feel free to submit issues and enhancement requests! 