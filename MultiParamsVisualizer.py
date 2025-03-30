import tkinter as tk
from tkinter import ttk, messagebox
import os
from DataStore import DataStore
from ParamStore import ParamStore
from UI import UI

class MultiParamsVisualizer:
    def __init__(self, root):
        self.ds=DataStore()
        
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # File paths using absolute paths
        data_file = os.path.join(self.script_dir, 'stored_data.csv')
        params_file = os.path.join(self.script_dir, 'parameters.json')
        self.ps=ParamStore(params_file)
        # Load parameters
        self.ps.load_parameters()
        if not self.ps.parameters:
            messagebox.showerror("Error", f"Failed to load parameters from {self.ps.params_file}. Application will exit.")
            self.root.destroy()
            return
        
        # Load existing data if available
        self.ds.load_data(data_file)
        self.ui=UI(root, "Multi-Parameter Visualizer", self.ds,self.ps)
        
       
if __name__ == "__main__":
    root = tk.Tk()
    app = MultiParamsVisualizer(root)
    root.mainloop()
