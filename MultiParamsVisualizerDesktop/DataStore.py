import pandas as pd
import os
from tkinter import messagebox

class DataStore:
    def __init__(self):
          # Data storage
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
            