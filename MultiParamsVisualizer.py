import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd
import os
import numpy as np

class MultiParamsVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi Parameters Visualization")
        
        # Data storage
        self.data = {'Date': [], 'Value': [], 'Parameter': []}
        
        # File path for data storage
        self.data_file = 'medical_data.csv'
        
        # Load existing data if available
        self.load_data()
        
        # Available parameters with their units and normal ranges
        self.parameters = {
            'Vitamin D': {'unit': 'ng/mL', 'min': 20, 'max': 50},
            'Blood Pressure (Systolic)': {'unit': 'mmHg', 'min': 90, 'max': 120},
            'Blood Pressure (Diastolic)': {'unit': 'mmHg', 'min': 60, 'max': 80},
            'Blood Sugar': {'unit': 'mg/dL', 'min': 70, 'max': 100},
            'Cholesterol': {'unit': 'mg/dL', 'min': 125, 'max': 200},
            'Hemoglobin': {'unit': 'g/dL', 'min': 13.5, 'max': 17.5},
            'TSH': {'unit': 'µIU/mL', 'min': 0.4, 'max': 4.0},
            'Creatinine': {'unit': 'mg/dL', 'min': 0.6, 'max': 1.2}
        }
        
        # Create input frame
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Parameter selection
        ttk.Label(self.input_frame, text="Select Parameter:").grid(row=0, column=0, padx=5, pady=5)
        self.parameter_var = tk.StringVar()
        self.parameter_combo = ttk.Combobox(self.input_frame, textvariable=self.parameter_var, values=list(self.parameters.keys()))
        self.parameter_combo.grid(row=0, column=1, padx=5, pady=5)
        self.parameter_combo.bind('<<ComboboxSelected>>', self.update_unit_label)
        
        # Date input
        ttk.Label(self.input_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
        self.date_entry = ttk.Entry(self.input_frame)
        self.date_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Value input
        self.value_label = ttk.Label(self.input_frame, text="Value:")
        self.value_label.grid(row=2, column=0, padx=5, pady=5)
        self.value_entry = ttk.Entry(self.input_frame)
        self.value_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Add button
        self.add_button = ttk.Button(self.input_frame, text="Add Data Point", command=self.add_data)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Create figure for plotting
        self.fig = plt.figure(figsize=(15, 10))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().grid(row=1, column=0, padx=10, pady=10)
        
        # Update plot with loaded data
        self.update_plot()
        
        # Bind window close event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
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

    def on_closing(self):
        self.save_data()
        self.root.destroy()

    def update_unit_label(self, event=None):
        selected_param = self.parameter_var.get()
        if selected_param in self.parameters:
            param_info = self.parameters[selected_param]
            self.value_label.config(text=f"Value ({param_info['unit']}):")

    def add_data(self):
        try:
            if not self.parameter_var.get():
                messagebox.showerror("Error", "Please select a parameter")
                return
                
            date = datetime.strptime(self.date_entry.get(), '%Y-%m-%d')
            value = float(self.value_entry.get())
            parameter = self.parameter_var.get()
            
            self.data['Date'].append(date)
            self.data['Value'].append(value)
            self.data['Parameter'].append(parameter)
            
            self.update_plot()
            self.save_data()  # Save after adding new data
            
            # Clear entries
            self.date_entry.delete(0, tk.END)
            self.value_entry.delete(0, tk.END)
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid date (YYYY-MM-DD) and numeric value")

    def update_plot(self):
        # Clear the figure
        self.fig.clear()
        
        # Get unique parameters that have data
        df = pd.DataFrame(self.data)
        unique_params = df['Parameter'].unique()
        
        if len(unique_params) == 0:
            return
            
        # Calculate grid dimensions
        n_params = len(unique_params)
        n_cols = 2  # Number of columns in the grid
        n_rows = (n_params + n_cols - 1) // n_cols  # Calculate number of rows needed
        
        # Create subplots
        for idx, param in enumerate(unique_params):
            ax = self.fig.add_subplot(n_rows, n_cols, idx + 1)
            param_data = df[df['Parameter'] == param].sort_values('Date')
            param_info = self.parameters[param]
            
            # Split data into normal and abnormal ranges
            normal_mask = (param_data['Value'] >= param_info['min']) & (param_data['Value'] <= param_info['max'])
            abnormal_mask = ~normal_mask
            
            # Plot normal range data in green
            if normal_mask.any():
                normal_data = param_data[normal_mask]
                ax.plot(normal_data['Date'], normal_data['Value'], 
                       marker='o', color='green', label='Normal')
            
            # Plot abnormal range data in red
            if abnormal_mask.any():
                abnormal_data = param_data[abnormal_mask]
                ax.plot(abnormal_data['Date'], abnormal_data['Value'], 
                       marker='o', color='red', label='Abnormal')
            
            # Add horizontal lines for normal range
            ax.axhline(y=param_info['min'], color='gray', linestyle='--', alpha=0.3)
            ax.axhline(y=param_info['max'], color='gray', linestyle='--', alpha=0.3)
            
            # Customize subplot
            ax.set_title(f'{param} ({param_info["unit"]})')
            ax.set_xlabel('Date')
            ax.set_ylabel('Value')
            ax.tick_params(axis='x', rotation=45)
            ax.legend()
            
            # Add normal range text
            ax.text(0.02, 0.98, f'Normal Range: {param_info["min"]}-{param_info["max"]} {param_info["unit"]}',
                   transform=ax.transAxes, verticalalignment='top', fontsize=8)
        
        # Adjust layout
        plt.tight_layout()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = MultiParamsVisualizer(root)
    root.mainloop()
