# app.py - Vercel entrypoint
from nhs_care_server import NHSCareApp

# Create the Flask app instance that Vercel expects
app = NHSCareApp().app