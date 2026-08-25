"""
NHS Personalised Care - Minimal Vercel Version
No database, uses in-memory storage
"""

import sys
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# In-memory storage (data will reset on each deployment)
mock_data = {
    "persons": {
        "NHS123456": {
            "nhs_number": "NHS123456",
            "name": "Sarah Johnson",
            "date_of_birth": "1965-05-15",
            "gender": "Female"
        },
        "NHS789012": {
            "nhs_number": "NHS789012",
            "name": "James Smith",
            "date_of_birth": "1978-03-22",
            "gender": "Male"
        }
    },
    "goals": {
        "NHS123456": [
            {"goal_id": "1", "description": "Walk 30 minutes daily", "domain": "physical_health", "status": "in_progress"},
            {"goal_id": "2", "description": "Join community walking group", "domain": "social_wellbeing", "status": "planned"}
        ],
        "NHS789012": [
            {"goal_id": "3", "description": "Reduce blood pressure", "domain": "physical_health", "status": "planned"}
        ]
    },
    "outcomes": {
        "NHS123456": [
            {"metric_name": "Blood Pressure", "value": 135, "target_value": 120, "domain": "physical_health"},
            {"metric_name": "Heart Rate", "value": 82, "target_value": 70, "domain": "physical_health"}
        ]
    },
    "pam_scores": {
        "NHS123456": [
            {"score": 45, "level": 1},
            {"score": 52, "level": 2},
            {"score": 58, "level": 3},
            {"score": 62, "level": 3}
        ]
    },
    "notes": {
        "NHS123456": [
            {"note_text": "Feeling more energetic", "author": "Dr. Smith", "sentiment_score": 0.3},
            {"note_text": "Blood pressure slightly elevated", "author": "Dr. Smith", "sentiment_score": -0.1}
        ]
    },
    "plans": {}
}

# ==================== HEALTH CHECK ====================
@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "deployment": "vercel",
        "python_version": sys.version
    })

# ==================== DASHBOARD ====================
@app.route('/')
def home():
    # Return minimal HTML
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NHS Personalised Care</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 20px; background: #f5f7fa; }
            .header { background: #005EB8; color: white; padding: 20px; border-radius: 12px; text-align: center; }
            .card { background: white; padding: 16px; border-radius: 12px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
            .score { font-size: 48px; font-weight: bold; color: #005EB8; text-align: center; }
            .btn { background: #005EB8; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; margin: 4px 0; }
            .btn:hover { opacity: 0.9; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏥 NHS Personalised Care</h1>
            <p>NHS England</p>
        </div>
        <div class="card">
            <h3>Patient Activation Measure</h3>
            <div class="score" id="pamScore">--</div>
            <p style="text-align:center;color:#666;" id="pamLevel">Loading...</p>
        </div>
        <div class="card">
            <h3>🎯 Goals</h3>
            <div id="goalsList">Loading...</div>
        </div>
        <div class="card">
            <button class="btn" onclick="loadData()">🔄 Refresh</button>
        </div>
        <script>
            const API_URL = '';
            let personId = 'NHS123456';
            
            async function loadData() {
                try {
                    // Load PAM
                    const pamRes = await fetch(API_URL + '/api/pam/' + personId);
                    const pamData = await pamRes.json();
                    if (pamData.success && pamData.data && pamData.data.length > 0) {
                        const latest = pamData.data[pamData.data.length - 1];
                        document.getElementById('pamScore').textContent = latest.score;
                        document.getElementById('pamLevel').textContent = 'Level ' + (latest.level || '1');
                    }
                    
                    // Load Goals
                    const goalsRes = await fetch(API_URL + '/api/goals/' + personId);
                    const goalsData = await goalsRes.json();
                    if (goalsData.success && goalsData.data) {
                        const html = goalsData.data.map(g => 
                            '<div style="padding:8px 0;border-bottom:1px solid #eee;">' +
                            '<strong>' + g.description + '</strong>' +
                            '<span style="float:right;color:#666;font-size:12px;">' + g.status + '</span>' +
                            '</div>'
                        ).join('');
                        document.getElementById('goalsList').innerHTML = html || 'No goals set';
                    }
                } catch (e) {
                    console.error('Error:', e);
                    document.getElementById('goalsList').textContent = 'Error loading data';
                }
            }
            
            loadData();
        </script>
    </body>
    </html>
    """

# ==================== PERSON ====================
@app.route('/api/person/<nhs_number>')
def get_person(nhs_number):
    person = mock_data["persons"].get(nhs_number)
    if person:
        return jsonify({"success": True, "data": person})
    return jsonify({"success": True, "data": {"nhs_number": nhs_number, "name": "Demo Patient"}})

@app.route('/api/person', methods=['POST'])
def create_person():
    data = request.json
    nhs_number = data.get('nhs_number')
    if not nhs_number:
        return jsonify({"success": False, "error": "Missing NHS number"}), 400
    
    if nhs_number not in mock_data["persons"]:
        mock_data["persons"][nhs_number] = {
            "nhs_number": nhs_number,
            "name": data.get('name', 'New Patient'),
            "date_of_birth": data.get('date_of_birth', '2000-01-01'),
            "gender": data.get('gender', 'Unknown')
        }
        mock_data["goals"][nhs_number] = []
        mock_data["outcomes"][nhs_number] = []
        mock_data["pam_scores"][nhs_number] = []
        mock_data["notes"][nhs_number] = []
    
    return jsonify({"success": True, "nhs_number": nhs_number})

# ==================== PLAN ====================
@app.route('/api/plan/<person_id>')
def get_plan(person_id):
    if person_id not in mock_data["plans"]:
        mock_data["plans"][person_id] = {
            "plan_id": "plan-" + str(uuid.uuid4()),
            "person_id": person_id,
            "status": "active"
        }
    return jsonify({
        "success": True,
        "data": {"plan": mock_data["plans"][person_id]}
    })

# ==================== GOALS ====================
@app.route('/api/goals/<person_id>')
def get_goals(person_id):
    goals = mock_data["goals"].get(person_id, [])
    return jsonify({"success": True, "data": goals})

@app.route('/api/goal', methods=['POST'])
def create_goal():
    data = request.json
    person_id = data.get('person_id')
    if not person_id:
        return jsonify({"success": False, "error": "Missing person_id"}), 400
    
    goal = {
        "goal_id": str(uuid.uuid4())[:8],
        "description": data.get('description', ''),
        "domain": data.get('domain', 'physical_health'),
        "status": data.get('status', 'planned'),
        "steps": data.get('steps', []),
        "target_date": data.get('target_date'),
        "created_date": datetime.now().isoformat()
    }
    
    if person_id not in mock_data["goals"]:
        mock_data["goals"][person_id] = []
    mock_data["goals"][person_id].append(goal)
    
    return jsonify({"success": True, "goal_id": goal["goal_id"]})

@app.route('/api/goal/<goal_id>', methods=['PUT'])
def update_goal(goal_id):
    data = request.json
    for person_id, goals in mock_data["goals"].items():
        for goal in goals:
            if goal.get("goal_id") == goal_id:
                goal["status"] = data.get("status", goal["status"])
                goal["description"] = data.get("description", goal["description"])
                return jsonify({"success": True})
    return jsonify({"success": False, "error": "Goal not found"}), 404

# ==================== OUTCOMES ====================
@app.route('/api/outcomes/<person_id>')
def get_outcomes(person_id):
    outcomes = mock_data["outcomes"].get(person_id, [])
    return jsonify({"success": True, "data": outcomes})

@app.route('/api/outcome', methods=['POST'])
def create_outcome():
    data = request.json
    person_id = data.get('person_id')
    if not person_id:
        return jsonify({"success": False, "error": "Missing person_id"}), 400
    
    outcome = {
        "outcome_id": str(uuid.uuid4())[:8],
        "metric_name": data.get('metric_name', ''),
        "value": data.get('value', 0),
        "target_value": data.get('target_value'),
        "domain": data.get('domain', 'physical_health'),
        "date_recorded": datetime.now().isoformat()
    }
    
    if person_id not in mock_data["outcomes"]:
        mock_data["outcomes"][person_id] = []
    mock_data["outcomes"][person_id].append(outcome)
    
    return jsonify({"success": True, "outcome_id": outcome["outcome_id"]})

# ==================== PAM ====================
@app.route('/api/pam/<person_id>')
def get_pam(person_id):
    scores = mock_data["pam_scores"].get(person_id, [])
    return jsonify({"success": True, "data": scores})

@app.route('/api/pam', methods=['POST'])
def create_pam():
    data = request.json
    person_id = data.get('person_id')
    score = data.get('score')
    if not person_id or score is None:
        return jsonify({"success": False, "error": "Missing person_id or score"}), 400
    
    level = 1 if score <= 47 else 2 if score <= 54.9 else 3 if score <= 66.9 else 4
    
    pam_entry = {
        "pam_id": str(uuid.uuid4())[:8],
        "score": score,
        "level": level,
        "date_taken": datetime.now().isoformat()
    }
    
    if person_id not in mock_data["pam_scores"]:
        mock_data["pam_scores"][person_id] = []
    mock_data["pam_scores"][person_id].append(pam_entry)
    
    return jsonify({"success": True, "pam_id": pam_entry["pam_id"], "level": level})

# ==================== NOTES ====================
@app.route('/api/notes/<person_id>')
def get_notes(person_id):
    notes = mock_data["notes"].get(person_id, [])
    return jsonify({"success": True, "data": notes})

@app.route('/api/note', methods=['POST'])
def create_note():
    data = request.json
    person_id = data.get('person_id')
    if not person_id:
        return jsonify({"success": False, "error": "Missing person_id"}), 400
    
    note = {
        "note_id": str(uuid.uuid4())[:8],
        "note_text": data.get('note_text', ''),
        "author": data.get('author', 'Unknown'),
        "sentiment_score": data.get('sentiment_score', 0),
        "date_created": datetime.now().isoformat()
    }
    
    if person_id not in mock_data["notes"]:
        mock_data["notes"][person_id] = []
    mock_data["notes"][person_id].append(note)
    
    return jsonify({"success": True, "note_id": note["note_id"]})

# ==================== INSIGHTS ====================
@app.route('/api/insights/<person_id>')
def get_insights(person_id):
    scores = mock_data["pam_scores"].get(person_id, [])
    latest_pam = scores[-1]["score"] if scores else 50
    
    goals = mock_data["goals"].get(person_id, [])
    completed = len([g for g in goals if g["status"] == "achieved"])
    completion_rate = completed / len(goals) if goals else 0
    
    return jsonify({
        "success": True,
        "data": {
            "risk_assessment": {
                "risk_level": "low",
                "risk_score": 0.25,
                "confidence": 0.85,
                "factors": ["No significant risk factors identified"]
            },
            "pam_trajectory": {
                "predicted_score": min(latest_pam + 5, 100),
                "trend": "improving" if len(scores) > 1 and scores[-1]["score"] > scores[-2]["score"] else "stable",
                "confidence": 0.7
            },
            "recommendations": [
                {"name": "Review Goals", "priority": 1, "justification": "Low goal completion rate"} if completion_rate < 0.5 else None,
                {"name": "Self-Management Support", "priority": 2, "justification": "Consider activation level"} if latest_pam < 55 else None
            ],
            "domain_scores": {"physical_health": 6.5, "mental_health": 7.0},
            "summary": {
                "total_goals": len(goals),
                "completed_goals": completed,
                "completion_rate": completion_rate,
                "latest_pam": latest_pam
            }
        }
    })

# ==================== POPULATION ====================
@app.route('/api/population')
def get_population():
    total_patients = len(mock_data["persons"])
    all_scores = []
    for scores in mock_data["pam_scores"].values():
        if scores:
            all_scores.append(scores[-1]["score"])
    
    avg_pam = sum(all_scores) / len(all_scores) if all_scores else 0
    
    return jsonify({
        "success": True,
        "data": {
            "total_patients": total_patients,
            "average_pam": avg_pam,
            "goal_distribution": [{"status": "planned", "count": 2}, {"status": "in_progress", "count": 1}],
            "risk_distribution": {"low": 2, "medium": 0, "high": 0, "critical": 0}
        }
    })

# ==================== ERROR HANDLING ====================
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)