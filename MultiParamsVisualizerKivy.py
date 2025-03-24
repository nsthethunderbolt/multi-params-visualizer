from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.core.window import Window
import matplotlib.pyplot as plt
from datetime import datetime
import pandas as pd
import os
import json
import numpy as np

class MultiParamsVisualizerKivy(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Data storage
        self.data = {'Date': [], 'Value': [], 'Parameter': []}
        
        # Get the directory where the script is located
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # File paths using absolute paths
        self.data_file = os.path.join(self.script_dir, 'stored_data.csv')
        self.params_file = os.path.join(self.script_dir, 'parameters.json')
        
        # Load parameters
        self.parameters = self.load_parameters()
        if not self.parameters:
            return
        
        # Load existing data if available
        self.load_data()
        
        # Create input section
        self.create_input_section()
        
        # Create plot section
        self.create_plot_section()
        
        # Update plot with loaded data
        self.update_plot()

    def create_input_section(self):
        # Input container
        input_container = BoxLayout(orientation='vertical', size_hint_y=None, height=200)
        
        # Parameter selection
        param_layout = BoxLayout(size_hint_y=None, height=40)
        param_layout.add_widget(Label(text='Select Parameter:'))
        self.parameter_spinner = Spinner(
            text='Select Parameter',
            values=list(self.parameters.keys()),
            size_hint=(None, None),
            size=(200, 40),
            pos_hint={'center_x': .5, 'center_y': .5})
        self.parameter_spinner.bind(text=self.update_unit_label)
        param_layout.add_widget(self.parameter_spinner)
        input_container.add_widget(param_layout)
        
        # Date input
        date_layout = BoxLayout(size_hint_y=None, height=40)
        date_layout.add_widget(Label(text='Date (YYYY-MM-DD):'))
        self.date_input = TextInput(multiline=False)
        date_layout.add_widget(self.date_input)
        input_container.add_widget(date_layout)
        
        # Value input
        value_layout = BoxLayout(size_hint_y=None, height=40)
        self.value_label = Label(text='Value:')
        value_layout.add_widget(self.value_label)
        self.value_input = TextInput(multiline=False)
        value_layout.add_widget(self.value_input)
        input_container.add_widget(value_layout)
        
        # Add button
        self.add_button = Button(
            text='Add Data Point',
            size_hint_y=None,
            height=40,
            pos_hint={'center_x': .5, 'center_y': .5})
        self.add_button.bind(on_press=self.add_data)
        input_container.add_widget(self.add_button)
        
        self.add_widget(input_container)

    def create_plot_section(self):
        # Create scrollable plot area
        scroll = ScrollView()
        self.plot_container = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.plot_container.bind(minimum_height=self.plot_container.setter('height'))
        
        # Create figure
        self.fig = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvasKivyAgg(self.fig)
        self.plot_container.add_widget(self.canvas)
        
        scroll.add_widget(self.plot_container)
        self.add_widget(scroll)

    def load_parameters(self):
        try:
            if not os.path.exists(self.params_file):
                print(f"Parameters file not found at: {self.params_file}")
                return None
                
            with open(self.params_file, 'r') as f:
                data = json.load(f)
                
            if 'parameters' not in data:
                print("Invalid parameters file format.")
                return None
                
            return data['parameters']
            
        except Exception as e:
            print(f"Error loading parameters: {str(e)}")
            return None

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                df = pd.read_csv(self.data_file)
                df['Date'] = pd.to_datetime(df['Date'])
                self.data = df.to_dict('list')
        except Exception as e:
            print(f"Error loading data: {str(e)}")

    def save_data(self):
        try:
            df = pd.DataFrame(self.data)
            df.to_csv(self.data_file, index=False)
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def update_unit_label(self, spinner, text):
        if text in self.parameters:
            param_info = self.parameters[text]
            self.value_label.text = f"Value ({param_info['unit']}):"

    def add_data(self, instance):
        try:
            if not self.parameter_spinner.text or self.parameter_spinner.text == 'Select Parameter':
                return
                
            date = datetime.strptime(self.date_input.text, '%Y-%m-%d')
            value = float(self.value_input.text)
            parameter = self.parameter_spinner.text
            
            self.data['Date'].append(date)
            self.data['Value'].append(value)
            self.data['Parameter'].append(parameter)
            
            self.update_plot()
            self.save_data()
            
            # Clear inputs
            self.date_input.text = ''
            self.value_input.text = ''
            
        except ValueError:
            print("Please enter valid date (YYYY-MM-DD) and numeric value")

    def update_plot(self):
        # Clear the figure
        self.fig.clear()
        
        # Get unique parameters that have data
        df = pd.DataFrame(self.data)
        unique_params = df['Parameter'].unique()
        
        if len(unique_params) == 0:
            return
            
        # Create subplots
        for idx, param in enumerate(unique_params):
            ax = self.fig.add_subplot(len(unique_params), 1, idx + 1)
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

class MultiParamsVisualizerApp(App):
    def build(self):
        return MultiParamsVisualizerKivy()

if __name__ == '__main__':
    MultiParamsVisualizerApp().run() 