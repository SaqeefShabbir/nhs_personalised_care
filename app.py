# app.py - Vercel entrypoint
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from nhs_care_server import NHSCareApp
    app = NHSCareApp().app
except ImportError as e:
    print(f"Error importing app: {e}")
    # Fallback to a minimal app if import fails
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return {
            "message": "NHS Personalised Care API",
            "status": "deployed",
            "error": str(e)
        }