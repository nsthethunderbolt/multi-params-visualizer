import pandas as pd
import os
from tkinter import messagebox

# DataStore class to manage data loading and saving
# This class handles the loading and saving of data to a CSV file.
class DataStore:
    def __init__(self):
          # Data storage json
        self.data = {'Date': [], 'Value': [], 'Parameter': []}
    def load_data(self,data_file):
        self.data_file = data_file
        try:
            if os.path.exists(data_file):
                df = pd.read_csv(data_file)
                df['Date'] = pd.to_datetime(df['Date'])
                self.data = df.to_dict('list')
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
    def save_data(self):
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(self.data_file, index=False)
        except Exception as e:
            messagebox.showerror("Error", f"Error saving data: {str(e)}")
            