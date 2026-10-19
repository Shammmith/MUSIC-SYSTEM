from flask import Flask, render_template, jsonify, request, redirect, url_for
import subprocess
import os

app = Flask(__name__)  # Fixed __name__

# Map EXE names to their relative paths
ALLOWED_EXES = {
    'file_upload': os.path.join('exe', 'file_upload.exe'),
    'audio_based': os.path.join('exe', 'audio_based.exe'),  # Case-sensitive name
    'music_recommendation': os.path.join('exe', 'MRS.exe')
}

# Developer information (use relative paths for images in static/images)
DEVELOPERS = [
    {"name": "VENKAT", "pic": "images/venkat.jpg"},
    {"name": "SHAMMITH", "pic": "images/me.jpg"},
    {"name": "VISWANATH", "pic": "images/vishwa.jpg"},
    {"name": "JOTIBA", "pic": "images/jo.jpg"}
]


@app.route('/')
def index():
    return render_template('index.html', exes=ALLOWED_EXES, developers=DEVELOPERS)

@app.route('/classification')
def classification():
    return render_template('classification.html', exes=ALLOWED_EXES, developers=DEVELOPERS)

@app.route('/run/<exe_name>')
def run_exe(exe_name):
    if exe_name not in ALLOWED_EXES:
        return jsonify({"error": "Invalid option!"}), 400

    # Get absolute path to the EXE
    exe_path = os.path.abspath(ALLOWED_EXES[exe_name])
    
    if not os.path.exists(exe_path):
        return jsonify({"error": f"Executable not found: {exe_path}"}), 404

    try:
        # Get working directory (parent directory of the EXE)
        working_directory = os.path.dirname(exe_path)
        
        # Command to open new terminal and run EXE
        cmd = f'start cmd /k "cd /d \"{working_directory}\" && \"{exe_path}\""'
        
        subprocess.Popen(cmd, shell=True)
        return jsonify({"message": f"{exe_name} launched successfully!"}), 200
    except Exception as ex:
        return jsonify({"error": f"Error: {str(ex)}"}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # (Authentication logic would be added here)
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # (User registration logic would be added here)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/help')
def help_page():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True)
