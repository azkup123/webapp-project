
from flask import Flask, request, jsonify, render_template, send_file
import os
import math
import csv
import pandas as pd
import datetime

def calculate_total_distance_and_speed(filepath):
        def distance(point1, point2):
            try:
                return math.sqrt(
                    (point2[0] - point1[0])**2 +
                    (point2[1] - point1[1])**2 +
                    (point2[2] - point1[2])**2
                )
            except:
                return 0

        total_distance = 0.0
        current_position = [0.0, 0.0, 0.0]
        current_speed = 0.0
        speeds = []

        with open(filepath, 'r') as file:
            for line in file:
                if line.startswith(';'):  
                    continue
                if "G1" in line or "G0" in line:
                    parts = line.split()
                    new_position = current_position[:]
                    for part in parts:
                        if part.startswith('X'):
                            new_position[0] = float(part[1:])
                        elif part.startswith('Y'):
                            new_position[1] = float(part[1:])
                        elif part.startswith('Z'):
                            try:
                                new_position[2] = float(part[1:])
                            except:
                                pass
                        elif part.startswith('F'):
                            current_speed = float(part[1:])
                    
                    total_distance += distance(current_position, new_position)
                    if current_speed:
                        speeds.append(current_speed)
                    current_position = new_position

        return total_distance, sum(speeds)/len(speeds), total_distance/(sum(speeds)/len(speeds))

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads/'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    
    return render_template('upload.html')

@app.route('/download')
def download():
    try:
        return send_file("data.csv", as_attachment=True)
    except Exception as e:
        return f"download failed"
        
    

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        distance, average, time = calculate_total_distance_and_speed(filepath)
        time = round(time,1)
        with open("data.csv", "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([datetime.datetime.now(),filepath,time]) 
	 #Distance and average speed are unused
        return f"Print duration: {time} minutes"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)

