import os
import logging
import json
import uuid
import tempfile
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify, send_file
from resume_parser import ResumeParser

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure upload settings
ALLOWED_EXTENSIONS = {'pdf'}
UPLOAD_FOLDER = tempfile.gettempdir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size

def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and resume parsing"""
    if 'resume' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('index'))
    
    file = request.files['resume']
    
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('index'))
    
    if file and allowed_file(file.filename):
        try:
            # Create a unique filename
            unique_filename = f"{uuid.uuid4()}_{secure_filename(file.filename)}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Save the file temporarily
            file.save(filepath)
            logger.debug(f"File saved temporarily at {filepath}")
            
            # Parse the resume
            parser = ResumeParser(filepath)
            resume_data = parser.parse()
            
            # Fix the experience key to match the expected key in templates
            if 'experience' in resume_data and 'work_experience' not in resume_data:
                resume_data['work_experience'] = resume_data.pop('experience')
            
            # Store parsed data in session
            session['resume_data'] = resume_data
            session['temp_file'] = filepath
            
            # Redirect to result page
            return redirect(url_for('show_result'))
        
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            flash(f"Error parsing resume: {str(e)}", 'danger')
            return redirect(url_for('index'))
    else:
        flash('Invalid file format. Please upload a PDF file.', 'danger')
        return redirect(url_for('index'))

@app.route('/result')
def show_result():
    """Display parsed resume data"""
    resume_data = session.get('resume_data')
    
    if not resume_data:
        flash('No resume data found. Please upload a resume first.', 'warning')
        return redirect(url_for('index'))
    
    return render_template('result.html', resume_data=resume_data)

@app.route('/download-json')
def download_json():
    """Generate and download resume data as JSON"""
    resume_data = session.get('resume_data')
    
    if not resume_data:
        flash('No resume data found. Please upload a resume first.', 'warning')
        return redirect(url_for('index'))
    
    # Create a temporary file for the JSON data
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as temp_file:
        json.dump(resume_data, temp_file, indent=4)
        temp_filepath = temp_file.name
    
    # Send the file for download
    return send_file(temp_filepath, 
                     mimetype='application/json',
                     as_attachment=True, 
                     download_name='resume_data.json')

@app.route('/error')
def error():
    """Error page"""
    return render_template('error.html')

@app.after_request
def cleanup(response):
    """Clean up temporary files after request"""
    temp_file = session.get('temp_file')
    if temp_file and os.path.exists(temp_file):
        try:
            os.remove(temp_file)
            logger.debug(f"Temporary file {temp_file} removed")
            session.pop('temp_file', None)
        except Exception as e:
            logger.error(f"Error removing temporary file: {str(e)}")
    return response

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
