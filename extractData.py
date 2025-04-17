import json
import os
import xmltodict
import re
import csv
import argparse
import pandas as pd
import shutil
header_added = False
tbody_added = False

def convert_xml_to_json(xml_file_path):
    try:
        with open(xml_file_path, 'r') as xml_file:
            xml_content = xml_file.read()
            parsed_data = xmltodict.parse(xml_content)
    except Exception:
        raise Exception("Error: Could not parse XML file")
    
    json_file_path = xml_file_path.replace('.XML', '.json')
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(parsed_data, json_file, indent=4)
    except Exception:
        raise Exception("Error: Could not write JSON file")
    
    return json_file_path


def extract_to_csv(json_file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, json_file_path)
    op_csv = json_file_path.replace('.json', '.csv')
    if not os.path.isfile(json_file_path):
        raise FileNotFoundError(f"The file {json_file_path} does not exist.")

    with open(json_file_path, 'r') as file:
        data = json.load(file)

    def extract_thead_tbody(data, collected=None):
        if collected is None:
            collected = {'thead': [], 'tbody': []}
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == 'thead':
                    collected['thead'].append(value)
                elif key == 'tbody':
                    collected['tbody'].append(value)
                else:
                    extract_thead_tbody(value, collected)
        elif isinstance(data, list):
            for item in data:
                extract_thead_tbody(item, collected)
        
        return collected

    extracted = extract_thead_tbody(data)
    df=pd.DataFrame(extracted)
    headers=[]
    rows=[]
    def fixtd(td):
        if isinstance(td,list):
            td[0] =td[0]['#text']
            del td[3]
            del td[4]
            del td[4]
            if len(td) == 4:
                td[3] = str(td[3]).split()[0]

    for index,row in enumerate(df['thead']):
        th = row['tr']['th']
        if 'Component' in th:
            headers.append(th[0:5])
            values=df['tbody'][index]['tr']
            if isinstance(values, list):
                for l in values:
                    fixtd(l['td'])
                    rows.append(l['td'])
            elif isinstance(values, dict):
                fixtd(values['td'])
                rows.append(values['td'])
    del headers[0][3]

    with open(op_csv, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(headers[0])  # Write the header row
        writer.writerows(rows[0:])  # Write the data rows
    return op_csv

def populate_stored_csv(op_csv, param_list):
    df = pd.read_csv(op_csv)
    df=df.sort_values(by='Analysis Time')
    df=df[df['Component'].isin(param_list)]
    df=df[['Analysis Time','Value','Component']]
    df.columns=['Date','Value','Parameter']
    shutil.copy('stored_data.csv', 'stored_data.csv.bak')
    df.to_csv('stored_data.csv', index=False)

def populate_params_json(op_csv, param_list):
    df = pd.read_csv(op_csv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, 'parameters.json')
    df=df[df['Component'].isin(param_list)]
    df=df.sort_values(by='Component')
    toGetNormalValues=df.groupby(['Component']).first()
    parameters={}
    def isdot(s):
        return s=='.'
    for item in toGetNormalValues['Ref Range'].items():
        unitSet=False
        parameters[item[0]] = { "unit": "", "min":item[1],"max": item[1]}
        if isinstance(item[1], str):
            spl=item[1].split(' - ')
            if len(spl)>1:
                furtherspl = spl[1].split()
                if len(furtherspl)>1:
                    parameters[item[0]] = { "unit": furtherspl[1], "min":spl[0],"max": furtherspl[0]}
                    unitSet=True
        if not unitSet:
            if item[1] == '(none)' or item[1] == 'N/A' or item[1] == None:
                parameters[item[0]] = { "unit": "", "min":0,"max": 0}
            elif isinstance(item[1], str) and '<' in item[1]:
                num_part = ''.join(filter(lambda c: isdot(c) or c.isdigit(), item[1]))
                if num_part:
                    integer_num = float(num_part)
                    parameters[item[0]] = { "unit": "", "min":-1,"max": integer_num}
            elif isinstance(item[1], str) and '>' in item[1]:
                num_part = ''.join(filter(str.isdigit, item[1]))
                if num_part:
                    integer_num = int(num_part)
                    parameters[item[0]] = { "unit": "", "min":integer_num,"max": 10000}
            
    json_params={'parameters': parameters}
    shutil.copy(json_file_path, json_file_path + '.bak')
    try:
        with open(json_file_path, 'w') as json_file:
            json.dump(json_params, json_file, indent=4)
    except Exception:
        raise Exception("Error: Could not write JSON file")


def read_txt_to_param_list(file_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, file_path)
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        # Remove newline characters from each line
        return [line.strip() for line in lines]
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Convert XML to JSON and extract data to CSV.")
    parser.add_argument("input_xml", type=str, help="Path to the input XML file")
    args = parser.parse_args()
    param_list = read_txt_to_param_list('parameters_to_track.txt')
    # Process the input XML file
    input_xml = args.input_xml
    op_json = convert_xml_to_json(input_xml)
    op_csv = extract_to_csv(op_json)
    print(f"Data extracted to {op_csv}")
    populate_params_json(op_csv, param_list)
    print(f"Parameters are stored in parameters.json and backup in parameters.json.bak")
    populate_stored_csv(op_csv, param_list)
    print(f"Data is stored in stored_data.csv and backup in stored_data.csv.bak")
    print("All done! To open the application with latest data run the following command:")
    print("python3 MultiParamsVisualizer.py")
