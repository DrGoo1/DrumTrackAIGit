import sys
import os

# Add the current directory to the path so Python can find the drumtrackkai package
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from drumtrackkit import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)