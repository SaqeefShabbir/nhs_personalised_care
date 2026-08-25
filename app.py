import sys
import os
from flask import Flask, jsonify, send_from_directory, render_template_string, request

app = Flask(__name__, static_folder='static', template_folder='templates')

with open('templates/index.html', 'r', encoding='utf-8') as f:
    DASHBOARD_HTML = f.read()

@app.route('/')
def home():
    return DASHBOARD_HTML

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "deployment": "vercel",
        "python_version": sys.version
    })

@app.route('/api/person/<nhs_number>')
def get_person(nhs_number):
    # Your API logic here
    return jsonify({"success": True, "data": {"nhs_number": nhs_number, "name": "Test User"}})

@app.route('/api/goals/<person_id>')
def get_goals(person_id):
    return jsonify({"success": True, "data": []})

@app.route('/api/outcomes/<person_id>')
def get_outcomes(person_id):
    return jsonify({"success": True, "data": []})

@app.route('/api/pam/<person_id>')
def get_pam(person_id):
    return jsonify({"success": True, "data": []})

@app.route('/api/notes/<person_id>')
def get_notes(person_id):
    return jsonify({"success": True, "data": []})

@app.route('/api/insights/<person_id>')
def get_insights(person_id):
    return jsonify({"success": True, "data": {"risk_assessment": {"risk_level": "low"}}})

@app.route('/api/population')
def get_population():
    return jsonify({"success": True, "data": {"total_patients": 3, "average_pam": 65}})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)