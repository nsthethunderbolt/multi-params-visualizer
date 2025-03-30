import os
import json
from tkinter import messagebox

class ParamStore:
        def __init__(self, params_file):
             self.params_file = params_file
        def load_parameters(self):
             self.parameters=self.load_parameters_priv()
        def load_parameters_priv(self):
            try:
                if not os.path.exists(self.params_file):
                    error_msg = f"Parameters file not found at: {self.params_file}\n"
                    error_msg += f"Current working directory: {os.getcwd()}\n"
                    error_msg += f"Script directory: {self.script_dir}"
                    messagebox.showerror("Error", error_msg)
                    return None
                    
                with open(self.params_file, 'r') as f:
                    data = json.load(f)
                    
                if 'parameters' not in data:
                    messagebox.showerror("Error", "Invalid parameters file format.")
                    return None
                    
                return data['parameters']
                
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid JSON format in parameters file.")
                return None
            except Exception as e:
                messagebox.showerror("Error", f"Error loading parameters: {str(e)}")
                return None
            