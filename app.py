from flask import Flask, render_template, request, send_from_directory, flash
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
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            try:
                df = pd.read_csv(filepath)
                
                grouped_data = df.groupby("Employee Export Code").agg({
                    "Employee Export Code": "first",
                    "Date": "max",
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
            except Exception as e:
                print(f"Error processing file: {e}")
                return f"Error processing file: {e}"
    return render_template('index.html')

@app.route('/download/<filename>')
def download(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        print(f"Error downloading file: {e}")
        return f"Error downloading file: {e}"

if __name__ == '__main__':
    app.run(debug=True)
