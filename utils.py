import os
import logging
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_temp_directory():
    """
    Create a temporary directory for file uploads
    
    Returns:
        str: Path to the temporary directory
    """
    temp_dir = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
    os.makedirs(temp_dir, exist_ok=True)
    logger.debug(f"Created temporary directory: {temp_dir}")
    return temp_dir

def cleanup_temp_file(file_path):
    """
    Remove a temporary file if it exists
    
    Args:
        file_path (str): Path to the file to remove
    """
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.debug(f"Removed temporary file: {file_path}")
        except Exception as e:
            logger.error(f"Error removing temporary file {file_path}: {str(e)}")

def format_resume_data(resume_data):
    """
    Format resume data for display
    
    Args:
        resume_data (dict): Parsed resume data
        
    Returns:
        dict: Formatted resume data
    """
    # Ensure all expected sections exist
    if not resume_data:
        return {
            "personal_info": {},
            "education": [],
            "skills": {},
            "work_experience": []
        }
    
    # Fill in any missing sections
    if "personal_info" not in resume_data:
        resume_data["personal_info"] = {}
    
    if "education" not in resume_data:
        resume_data["education"] = []
    
    if "skills" not in resume_data:
        resume_data["skills"] = {}
    
    if "work_experience" not in resume_data:
        resume_data["work_experience"] = []
    
    return resume_data
