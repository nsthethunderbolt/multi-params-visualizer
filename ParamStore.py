import os
import json

# ParamStore class to manage parameter loading
# This class handles the loading of parameters from a JSON file.
# It checks for the existence of the file and validates its format.
# It also provides methods to load parameters and handle errors.
class ParamStore:
        def __init__(self, params_file):
             self.params_file = params_file
        def load_parameters(self):
             ret = self.load_parameters_priv()
             if ret[0] == True:
                 self.parameters = ret[1]
                 return (True,"")
             else:
                 return ret
        def load_parameters_priv(self):
            try:
                if not os.path.exists(self.params_file):
                    error_msg = f"Parameters file not found at: {self.params_file}\n"
                    error_msg += f"Current working directory: {os.getcwd()}\n"
                    error_msg += f"Script directory: {self.script_dir}"
                    return (False, error_msg)
                    
                with open(self.params_file, 'r') as f:
                    data = json.load(f)
                    
                if 'parameters' not in data:
                    return (False, "Invalid parameters file format.")
                    
                return (True,data['parameters'])
                
            except json.JSONDecodeError:
                return (False, "Invalid JSON format in parameters file.")
            except Exception as e:
                return (False, f"Error loading parameters: {str(e)}")
            