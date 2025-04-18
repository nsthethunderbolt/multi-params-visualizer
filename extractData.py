import json
import os
import xmltodict
import re
import csv
import argparse
import ast
import pandas as pd
import shutil
import config
header_added = False
tbody_added = False

def convert_xml_to_json(xml_file_path):
    try:
        with open(xml_file_path, 'r') as xml_file:
            xml_content = xml_file.read()
            parsed_data = xmltodict.parse(xml_content)
    except Exception:
        raise Exception("Error: Could not parse XML file")
    
    return parsed_data


def process_json_to_csv(data):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    op_csv = os.path.join(script_dir, 'temp.csv')
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

def populate_stored_csv(op_csv, param_list, stored_csv_file, stored_csv_bak_file):
    df = pd.read_csv(op_csv)
    df=df.sort_values(by='Analysis Time')
    df=df[df['Component'].isin(param_list)]
    df=df[['Analysis Time','Value','Component']]
    df.columns=['Date','Value','Parameter']
    df['Value'] = df['Value'].str.replace('<', '')
    df['Value'] = df['Value'].str.replace('>', '')
    df['Value'] = df['Value'].str.replace('+', '')
    df['Value'] = df['Value'].str.replace(',', '')

    df['Value'] = df['Value'].apply(lambda x: ast.literal_eval(x)['content'] if isinstance(x, str) and 'content' in x else x)
    df = df[df.apply(lambda row: row.count() == 3, axis=1)]
    shutil.copy(stored_csv_file, stored_csv_bak_file)
    df.to_csv(stored_csv_file, index=False)

def populate_params_json(op_csv, param_list, params_json_file, params_json_bak_file):
    df = pd.read_csv(op_csv)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_file_path = os.path.join(script_dir, params_json_file)
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
                    parameters[item[0]] = { "unit": furtherspl[1], "min":float(spl[0]),"max": float(furtherspl[0])}
                    unitSet=True
                else:
                    parameters[item[0]] = { "unit": "", "min":float(spl[0]),"max": float(spl[1])}
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
    shutil.copy(json_file_path, params_json_bak_file)
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
    print(f"Parameters to track are picked from {config.parameters_to_track_file}")
    param_list = read_txt_to_param_list(config.parameters_to_track_file)

    # Process the input XML file
    input_xml = args.input_xml
    extracted_json = convert_xml_to_json(input_xml)
    op_csv = process_json_to_csv(extracted_json)
    print(f"Data extracted to {op_csv}")

    populate_params_json(op_csv, param_list, config.param_file, config.param_file_backup)
    print(f"Parameters are stored in {config.param_file} and backup in {config.param_file_backup}")

    populate_stored_csv(op_csv, param_list, config.data_file, config.data_file_backup)
    print(f"Data is stored in {config.data_file} and backup in {config.data_file_backup}")

    # Remove the temporary csv file
    if os.path.exists(op_csv):
        os.remove(op_csv)
        print(f"Temporary file {op_csv} removed.")
    else:
        print(f"Temporary file {op_csv} not found.")
    print("All done! To open the application with latest data run the following command:")
    print("python3 MultiParamsVisualizer.py")
