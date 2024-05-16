from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return 'No file part'
        
        file = request.files['file']
        
        if file.filename == '':
            return 'No selected file'
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the file
            df = pd.read_csv(filepath)
            
            grouped_data = df.groupby("Employee Export Code").agg({
                "Employee Export Code": "first",
                "Date": "max",  # Get the latest date
                "Total Cost": "sum",
                "Total Hours": "sum",
            })

            grouped_data["Invoice Currency"] = "USD"
            grouped_data["Invoice Type"] = "ONCYCLE"

            grouped_data.rename(
                columns={
                    "Employee Export Code": "User ID",
                    "Date": "Date",
                    "Total Cost": "Amount",
                    "Total Hours": "Work Unit Total"
                },
                inplace=True,
            )

            output_filename = request.form['output_filename']
            output_filepath = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            grouped_data.to_csv(output_filepath, index=False)

            return f'CSV file with employee timesheet summary created successfully! Download it <a href="/download/{output_filename}">here</a>.'
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
