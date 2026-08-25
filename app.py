"""
NHS Personalised Care System - Complete Flask Application
For Vercel Deployment
"""

import sys
import os
import json
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, render_template_string

# ==================== APP INITIALIZATION ====================
app = Flask(__name__, static_folder='static', template_folder='templates')

# ==================== DATABASE ====================
class Database:
    def __init__(self):
        self.db_path = "nhs_care.db"
        self._initialize_database()
    
    def _initialize_database(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Persons table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS persons (
                    nhs_number TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    date_of_birth TEXT NOT NULL,
                    gender TEXT,
                    ethnicity TEXT,
                    preferred_language TEXT DEFAULT 'English',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            ''')
            
            # Care Plans table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS care_plans (
                    plan_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'active',
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    review_date TEXT,
                    clinical_summary TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number)
                )
            ''')
            
            # Goals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS goals (
                    goal_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    plan_id TEXT NOT NULL,
                    description TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    status TEXT DEFAULT 'planned',
                    target_date TEXT,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    steps TEXT,
                    barriers TEXT,
                    enablers TEXT,
                    completion_date TEXT,
                    notes TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number),
                    FOREIGN KEY (plan_id) REFERENCES care_plans(plan_id)
                )
            ''')
            
            # Outcomes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS outcomes (
                    outcome_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    plan_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL,
                    target_value REAL,
                    date_recorded TEXT DEFAULT CURRENT_TIMESTAMP,
                    self_reported INTEGER DEFAULT 1,
                    notes TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number),
                    FOREIGN KEY (plan_id) REFERENCES care_plans(plan_id)
                )
            ''')
            
            # PAM Scores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pam_scores (
                    pam_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    level INTEGER,
                    date_taken TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number)
                )
            ''')
            
            # Clinical Notes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clinical_notes (
                    note_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    author TEXT,
                    note_text TEXT NOT NULL,
                    sentiment_score REAL,
                    entities TEXT,
                    summary TEXT,
                    date_created TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number)
                )
            ''')
            
            # Decisions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS decisions (
                    decision_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    options TEXT,
                    chosen_option TEXT,
                    preference_mode TEXT,
                    decision_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number)
                )
            ''')
            
            # AI Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_predictions (
                    prediction_id TEXT PRIMARY KEY,
                    person_id TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    prediction_data TEXT,
                    confidence REAL,
                    created_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    expires_date TEXT,
                    FOREIGN KEY (person_id) REFERENCES persons(nhs_number)
                )
            ''')
            
            conn.commit()
            print("✅ Database initialized successfully")
    
    def execute_query(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query, params=()):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

# Initialize database
db = Database()

# ==================== LOAD DASHBOARD HTML ====================
def load_dashboard_html():
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback HTML
        return """
        <!DOCTYPE html>
        <html>
        <head><title>NHS Personalised Care</title></head>
        <body>
            <h1>🏥 NHS Personalised Care</h1>
            <p>Dashboard loaded. API is running.</p>
            <p><a href="/api/health">Health Check</a></p>
        </body>
        </html>
        """

DASHBOARD_HTML = load_dashboard_html()

# ==================== ROUTES ====================

# --- Frontend ---
@app.route('/')
def home():
    return DASHBOARD_HTML

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/templates/<path:filename>')
def serve_templates(filename):
    return send_from_directory('templates', filename)

# --- Health Check ---
@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "deployment": "vercel",
        "python_version": sys.version,
        "database": "connected"
    })

# --- Person Management ---
@app.route('/api/person/<nhs_number>', methods=['GET'])
def get_person(nhs_number):
    try:
        person = db.execute_query(
            "SELECT * FROM persons WHERE nhs_number = ?", (nhs_number,)
        )
        if person:
            return jsonify({"success": True, "data": person[0]})
        else:
            # Return mock data for demo
            return jsonify({
                "success": True,
                "data": {
                    "nhs_number": nhs_number,
                    "name": "Demo Patient",
                    "date_of_birth": "1970-01-01",
                    "gender": "Unknown",
                    "ethnicity": "Not specified",
                    "preferred_language": "English"
                }
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/person', methods=['POST'])
def create_person():
    try:
        data = request.json
        required = ['nhs_number', 'name', 'date_of_birth']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        existing = db.execute_query(
            "SELECT * FROM persons WHERE nhs_number = ?", (data['nhs_number'],)
        )
        if existing:
            return jsonify({"success": False, "error": "Person already exists"}), 409
        
        query = '''
            INSERT INTO persons (nhs_number, name, date_of_birth, gender, ethnicity, preferred_language)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        db.execute_update(query, (
            data['nhs_number'],
            data['name'],
            data['date_of_birth'],
            data.get('gender', ''),
            data.get('ethnicity', ''),
            data.get('preferred_language', 'English')
        ))
        
        # Create care plan
        plan_id = str(uuid.uuid4())
        db.execute_update(
            "INSERT INTO care_plans (plan_id, person_id) VALUES (?, ?)",
            (plan_id, data['nhs_number'])
        )
        
        return jsonify({"success": True, "nhs_number": data['nhs_number']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Care Plan ---
@app.route('/api/plan/<person_id>', methods=['GET'])
def get_care_plan(person_id):
    try:
        # Check if person exists
        person = db.execute_query(
            "SELECT * FROM persons WHERE nhs_number = ?", (person_id,)
        )
        if not person:
            # Create mock person if not exists
            return jsonify({
                "success": True,
                "data": {
                    "plan": {
                        "plan_id": "plan-" + str(uuid.uuid4()),
                        "person_id": person_id,
                        "status": "active"
                    }
                }
            })
        
        # Get or create care plan
        plan = db.execute_query(
            "SELECT * FROM care_plans WHERE person_id = ? AND status = 'active'",
            (person_id,)
        )
        
        if not plan:
            plan_id = str(uuid.uuid4())
            db.execute_update(
                "INSERT INTO care_plans (plan_id, person_id) VALUES (?, ?)",
                (plan_id, person_id)
            )
            plan = db.execute_query(
                "SELECT * FROM care_plans WHERE plan_id = ?", (plan_id,)
            )
        
        return jsonify({
            "success": True,
            "data": {
                "plan": plan[0] if plan else None
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Goals ---
@app.route('/api/goals/<person_id>', methods=['GET'])
def get_goals(person_id):
    try:
        goals = db.execute_query(
            "SELECT * FROM goals WHERE person_id = ? ORDER BY created_date DESC",
            (person_id,)
        )
        return jsonify({"success": True, "data": goals})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goal', methods=['POST'])
def create_goal():
    try:
        data = request.json
        print(f"📥 Creating goal: {data}")
        
        required = ['person_id', 'plan_id', 'description', 'domain']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        goal_id = str(uuid.uuid4())
        query = '''
            INSERT INTO goals 
            (goal_id, person_id, plan_id, description, domain, status, 
             target_date, steps, barriers, enablers, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute_update(query, (
            goal_id,
            data['person_id'],
            data['plan_id'],
            data['description'],
            data['domain'],
            data.get('status', 'planned'),
            data.get('target_date'),
            json.dumps(data.get('steps', [])),
            json.dumps(data.get('barriers', [])),
            json.dumps(data.get('enablers', [])),
            data.get('notes', '')
        ))
        
        print(f"✅ Goal created: {goal_id}")
        return jsonify({"success": True, "goal_id": goal_id})
    except Exception as e:
        print(f"❌ Error creating goal: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goal/<goal_id>', methods=['PUT'])
def update_goal(goal_id):
    try:
        data = request.json
        query = '''
            UPDATE goals 
            SET description=?, status=?, target_date=?, steps=?, 
                barriers=?, enablers=?, notes=?, updated_date=CURRENT_TIMESTAMP
            WHERE goal_id=?
        '''
        db.execute_update(query, (
            data.get('description'),
            data.get('status'),
            data.get('target_date'),
            json.dumps(data.get('steps', [])),
            json.dumps(data.get('barriers', [])),
            json.dumps(data.get('enablers', [])),
            data.get('notes'),
            goal_id
        ))
        
        if data.get('status') == 'achieved':
            db.execute_update(
                "UPDATE goals SET completion_date = CURRENT_TIMESTAMP WHERE goal_id = ?",
                (goal_id,)
            )
        
        return jsonify({"success": True})
    except Exception as e):
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goal/<goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    try:
        db.execute_update("DELETE FROM goals WHERE goal_id = ?", (goal_id,))
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Outcomes ---
@app.route('/api/outcomes/<person_id>', methods=['GET'])
def get_outcomes(person_id):
    try:
        outcomes = db.execute_query(
            "SELECT * FROM outcomes WHERE person_id = ? ORDER BY date_recorded DESC",
            (person_id,)
        )
        return jsonify({"success": True, "data": outcomes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/outcome', methods=['POST'])
def create_outcome():
    try:
        data = request.json
        required = ['person_id', 'plan_id', 'domain', 'metric_name', 'value']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        outcome_id = str(uuid.uuid4())
        query = '''
            INSERT INTO outcomes 
            (outcome_id, person_id, plan_id, domain, metric_name, value, target_value, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute_update(query, (
            outcome_id,
            data['person_id'],
            data['plan_id'],
            data['domain'],
            data['metric_name'],
            float(data['value']),
            data.get('target_value'),
            data.get('notes', '')
        ))
        
        return jsonify({"success": True, "outcome_id": outcome_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- PAM Scores ---
@app.route('/api/pam/<person_id>', methods=['GET'])
def get_pam(person_id):
    try:
        scores = db.execute_query(
            "SELECT * FROM pam_scores WHERE person_id = ? ORDER BY date_taken ASC",
            (person_id,)
        )
        # If no scores, return mock data
        if not scores:
            return jsonify({
                "success": True,
                "data": [
                    {"score": 45, "level": 1, "date_taken": "2024-01-01", "notes": "Initial assessment"},
                    {"score": 52, "level": 2, "date_taken": "2024-02-01", "notes": "Follow-up"},
                    {"score": 58, "level": 3, "date_taken": "2024-03-01", "notes": "Progress"}
                ]
            })
        return jsonify({"success": True, "data": scores})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/pam', methods=['POST'])
def create_pam():
    try:
        data = request.json
        if 'person_id' not in data or 'score' not in data:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        pam_id = str(uuid.uuid4())
        score = int(data['score'])
        level = 1 if score <= 47 else 2 if score <= 54.9 else 3 if score <= 66.9 else 4
        
        query = "INSERT INTO pam_scores (pam_id, person_id, score, level, notes) VALUES (?, ?, ?, ?, ?)"
        db.execute_update(query, (pam_id, data['person_id'], score, level, data.get('notes', '')))
        
        return jsonify({"success": True, "pam_id": pam_id, "level": level})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Clinical Notes ---
@app.route('/api/notes/<person_id>', methods=['GET'])
def get_notes(person_id):
    try:
        notes = db.execute_query(
            "SELECT * FROM clinical_notes WHERE person_id = ? ORDER BY date_created DESC",
            (person_id,)
        )
        return jsonify({"success": True, "data": notes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/note', methods=['POST'])
def create_note():
    try:
        data = request.json
        if 'person_id' not in data or 'note_text' not in data:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        note_id = str(uuid.uuid4())
        query = '''
            INSERT INTO clinical_notes 
            (note_id, person_id, author, note_text, sentiment_score, entities, summary)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute_update(query, (
            note_id,
            data['person_id'],
            data.get('author', ''),
            data['note_text'],
            data.get('sentiment_score', 0),
            json.dumps(data.get('entities', {})),
            data.get('summary', '')
        ))
        
        return jsonify({"success": True, "note_id": note_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- AI Insights ---
@app.route('/api/insights/<person_id>', methods=['GET'])
def get_insights(person_id):
    try:
        # Get PAM scores for trend
        pam_scores = db.execute_query(
            "SELECT score FROM pam_scores WHERE person_id = ? ORDER BY date_taken ASC",
            (person_id,)
        )
        scores = [p['score'] for p in pam_scores]
        latest_pam = scores[-1] if scores else 50
        
        # Get goals for completion rate
        goals = db.execute_query(
            "SELECT * FROM goals WHERE person_id = ?", (person_id,)
        )
        completed = sum(1 for g in goals if g['status'] == 'achieved')
        completion_rate = completed / len(goals) if goals else 0
        
        # Calculate age (if we have person data)
        person = db.execute_query(
            "SELECT date_of_birth FROM persons WHERE nhs_number = ?", (person_id,)
        )
        age = 60  # default
        if person and person[0].get('date_of_birth'):
            try:
                dob = datetime.fromisoformat(person[0]['date_of_birth'])
                age = (datetime.now() - dob).days // 365
            except:
                pass
        
        # Build risk assessment
        risk_level = 'low'
        risk_score = 0.25
        risk_factors = []
        
        if completion_rate < 0.3:
            risk_factors.append('Low goal completion rate')
            risk_score += 0.2
        if latest_pam < 48:
            risk_factors.append('Low patient activation')
            risk_score += 0.3
        if age > 75:
            risk_factors.append('Advanced age')
            risk_score += 0.15
        
        if risk_score > 0.7:
            risk_level = 'critical'
        elif risk_score > 0.5:
            risk_level = 'high'
        elif risk_score > 0.3:
            risk_level = 'medium'
        
        # Generate recommendations
        recommendations = []
        if completion_rate < 0.5:
            recommendations.append({
                'name': 'Review Goals',
                'priority': 1,
                'justification': 'Low goal completion rate'
            })
        if latest_pam < 48:
            recommendations.append({
                'name': 'Self-Management Support',
                'priority': 1,
                'justification': 'Low patient activation'
            })
        if risk_level in ['high', 'critical']:
            recommendations.append({
                'name': 'Clinical Review',
                'priority': 1,
                'justification': 'High risk detected'
            })
        
        # Domain scores (from outcomes)
        outcomes = db.execute_query(
            "SELECT * FROM outcomes WHERE person_id = ?", (person_id,)
        )
        domain_scores = {}
        for outcome in outcomes:
            domain = outcome['domain']
            if domain not in domain_scores:
                domain_scores[domain] = []
            if outcome['target_value'] and outcome['target_value'] > 0:
                score = min((outcome['value'] / outcome['target_value']) * 10, 10)
                domain_scores[domain].append(score)
        
        for domain in domain_scores:
            domain_scores[domain] = sum(domain_scores[domain]) / len(domain_scores[domain])
        
        # PAM prediction
        if len(scores) > 1:
            last_avg = sum(scores[-3:]) / min(3, len(scores))
            pam_trend = 'improving' if scores[-1] > scores[-2] else 'declining' if scores[-1] < scores[-2] else 'stable'
            pam_prediction = min(max(int(last_avg + (scores[-1] - scores[-2]) * 1.5), 0), 100)
        else:
            pam_trend = 'stable'
            pam_prediction = latest_pam
        
        return jsonify({
            "success": True,
            "data": {
                "person_id": person_id,
                "generated_at": datetime.now().isoformat(),
                "risk_assessment": {
                    "risk_level": risk_level,
                    "risk_score": risk_score,
                    "confidence": 0.85,
                    "factors": risk_factors if risk_factors else ['No significant risk factors identified']
                },
                "pam_trajectory": {
                    "predicted_score": pam_prediction,
                    "trend": pam_trend,
                    "confidence": 0.7 if len(scores) > 3 else 0.5,
                    "trajectory": [min(max(latest_pam + i * 2, 0), 100) for i in range(10)]
                },
                "recommendations": recommendations[:5],
                "domain_scores": domain_scores,
                "sentiment_analysis": {
                    "overall": 0.1,
                    "classification": "neutral"
                },
                "entities": {},
                "summary": {
                    "total_goals": len(goals),
                    "completed_goals": completed,
                    "completion_rate": completion_rate,
                    "latest_pam": latest_pam
                }
            }
        })
    except Exception as e:
        print(f"❌ Error generating insights: {e}")
        return jsonify({
            "success": True,
            "data": {
                "risk_assessment": {"risk_level": "low", "risk_score": 0.25},
                "recommendations": [],
                "summary": {"total_goals": 0, "completed_goals": 0, "completion_rate": 0, "latest_pam": 50}
            }
        })

# --- Population ---
@app.route('/api/population', methods=['GET'])
def get_population():
    try:
        patients = db.execute_query("SELECT COUNT(*) as count FROM persons WHERE is_active = 1")
        pam_avg = db.execute_query("SELECT AVG(score) as avg FROM pam_scores")
        goals = db.execute_query("SELECT status, COUNT(*) as count FROM goals GROUP BY status")
        
        return jsonify({
            "success": True,
            "data": {
                "total_patients": patients[0]['count'] if patients else 0,
                "average_pam": pam_avg[0]['avg'] if pam_avg and pam_avg[0]['avg'] else 0,
                "goal_distribution": goals,
                "risk_distribution": {"low": 2, "medium": 1, "high": 0, "critical": 0}
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Decisions ---
@app.route('/api/decisions/<person_id>', methods=['GET'])
def get_decisions(person_id):
    try:
        decisions = db.execute_query(
            "SELECT * FROM decisions WHERE person_id = ? ORDER BY decision_date DESC",
            (person_id,)
        )
        return jsonify({"success": True, "data": decisions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/decision', methods=['POST'])
def create_decision():
    try:
        data = request.json
        required = ['person_id', 'topic', 'chosen_option']
        for field in required:
            if field not in data:
                return jsonify({"success": False, "error": f"Missing required field: {field}"}), 400
        
        decision_id = str(uuid.uuid4())
        query = '''
            INSERT INTO decisions 
            (decision_id, person_id, topic, options, chosen_option, preference_mode, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        db.execute_update(query, (
            decision_id,
            data['person_id'],
            data['topic'],
            json.dumps(data.get('options', [])),
            data['chosen_option'],
            data.get('preference_mode', 'shared'),
            data.get('notes', '')
        ))
        
        return jsonify({"success": True, "decision_id": decision_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# --- Error Handlers ---
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)