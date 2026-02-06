import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the src directory to the Python path so relative imports work
backend_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(backend_dir, 'src')
sys.path.insert(0, src_dir)

# Add the backend directory to the path so modules can find each other
sys.path.insert(0, backend_dir)

# Set the PYTHONPATH environment variable to include the src directory
os.environ['PYTHONPATH'] = src_dir + os.pathsep + os.environ.get('PYTHONPATH', '')

import uvicorn
from src.main import app

if __name__ == "__main__":
    print("Starting the backend server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)