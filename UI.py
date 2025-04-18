import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import pandas as pd

class UI:
    def __init__(self, root, title, ds, ps):
        self.root = root
        self.ds = ds
        self.ps = ps
        self.root.title(title)

        # Set the initial size of the window
        self.root.geometry("1600x1000") 

        # Configure the root grid to allow resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Create input frame
        self.input_frame = ttk.Frame(root, padding="10")
        self.input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Parameter selection
        ttk.Label(self.input_frame, text="Select Parameter:").grid(row=0, column=0, padx=5, pady=5)
        self.parameter_var = tk.StringVar()
        self.parameter_combo = ttk.Combobox(self.input_frame, textvariable=self.parameter_var, values=list(self.ps.parameters.keys()))
        self.parameter_combo.grid(row=0, column=1, padx=5, pady=5)


        # Create a frame for the canvas and scrollbar
        self.plot_frame = ttk.Frame(root)
        self.plot_frame.grid(row=1, column=0, padx=10, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure the plot_frame to expand
        self.plot_frame.columnconfigure(0, weight=1)
        self.plot_frame.rowconfigure(0, weight=1)

        # Add a canvas for the plot
        self.canvas_widget = tk.Canvas(self.plot_frame)
        self.canvas_widget.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add a vertical scrollbar
        self.scrollbar = ttk.Scrollbar(self.plot_frame, orient=tk.VERTICAL, command=self.canvas_widget.yview)
        self.scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # Configure the canvas to work with the scrollbar
        self.canvas_widget.configure(yscrollcommand=self.scrollbar.set)
        self.canvas_widget.bind('<Configure>', lambda e: self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all")))

        # Create a frame inside the canvas to hold the plot
        self.plot_container = ttk.Frame(self.canvas_widget)
        self.canvas_widget.create_window((0, 0), window=self.plot_container, anchor="nw")

        # Configure the plot_container to expand
        self.plot_container.bind('<Configure>', lambda e: self.canvas_widget.configure(scrollregion=self.canvas_widget.bbox("all")))

        # Create figure for plotting
        self.fig = plt.figure(figsize=(15, 150))  # Adjust the figure size as needed
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Update plot with loaded data
        self.update_plot()

        # Bind window close event to save data
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.root.destroy()

    def update_plot(self):
        # Clear the figure
        self.fig.clear()

        # Get unique parameters that have data
        df = pd.DataFrame(self.ds.data)
        unique_params = df['Parameter'].unique()

        if len(unique_params) == 0:
            return

        # Calculate grid dimensions
        n_params = len(unique_params)
        n_cols = 2  # Number of columns in the grid
        n_rows = (n_params + n_cols - 1) // n_cols  # Calculate number of rows needed
        df['Value'] = df['Value'].astype(float)

        # Create subplots
        for idx, param in enumerate(unique_params):
            ax = self.fig.add_subplot(n_rows, n_cols, idx + 1)
            param_data = df[df['Parameter'] == param].sort_values('Date')
            param_info = self.ps.parameters[param]

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