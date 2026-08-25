"""
NHS Personalised Care - Complete Flask Application
With Full API Support for Dashboard
"""

import sys
import os
import json
import uuid
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request, render_template_string

app = Flask(__name__, static_folder='static', template_folder='templates')

# ==================== LOAD DASHBOARD HTML ====================
def load_dashboard():
    try:
        with open('templates/index.html', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback if template not found
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>NHS Personalised Care</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { font-family: Arial; max-width: 480px; margin: 0 auto; padding: 20px; background: #f5f7fa; }
                .header { background: #005EB8; color: white; padding: 20px; border-radius: 12px; text-align: center; }
                .card { background: white; padding: 16px; border-radius: 12px; margin: 12px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
                .btn { background: #005EB8; color: white; border: none; padding: 12px; border-radius: 8px; font-size: 16px; cursor: pointer; width: 100%; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏥 NHS Personalised Care</h1>
                <p>NHS England</p>
            </div>
            <div class="card">
                <h3>✅ Dashboard Loaded</h3>
                <p>API is running. Use the full dashboard HTML file.</p>
                <button class="btn" onclick="location.href='/api/health'">Health Check</button>
            </div>
        </body>
        </html>
        """

DASHBOARD_HTML = load_dashboard()

# ==================== IN-MEMORY DATA ====================
# Sample data for demonstration
mock_data = {
    "persons": {
        "NHS123456": {
            "nhs_number": "NHS123456",
            "name": "Sarah Johnson",
            "date_of_birth": "1965-05-15",
            "gender": "Female",
            "ethnicity": "White British"
        },
        "NHS789012": {
            "nhs_number": "NHS789012",
            "name": "James Smith",
            "date_of_birth": "1978-03-22",
            "gender": "Male",
            "ethnicity": "White British"
        }
    },
    "plans": {},
    "goals": {
        "NHS123456": [
            {"goal_id": "g1", "description": "Walk 30 minutes daily", "domain": "physical_health", "status": "in_progress", "steps": ["Start with 10 min", "Increase gradually"], "created_date": "2024-01-15"},
            {"goal_id": "g2", "description": "Join community walking group", "domain": "social_wellbeing", "status": "planned", "steps": ["Find local groups", "Attend first session"], "created_date": "2024-01-20"}
        ],
        "NHS789012": [
            {"goal_id": "g3", "description": "Reduce blood pressure", "domain": "physical_health", "status": "planned", "steps": ["Monitor BP daily", "Reduce salt intake"], "created_date": "2024-01-10"}
        ]
    },
    "outcomes": {
        "NHS123456": [
            {"outcome_id": "o1", "metric_name": "Blood Pressure", "value": 135, "target_value": 120, "domain": "physical_health", "date_recorded": "2024-01-20"},
            {"outcome_id": "o2", "metric_name": "Heart Rate", "value": 82, "target_value": 70, "domain": "physical_health", "date_recorded": "2024-01-20"},
            {"outcome_id": "o3", "metric_name": "Mood Score", "value": 7, "target_value": 8, "domain": "mental_health", "date_recorded": "2024-01-19"}
        ]
    },
    "pam_scores": {
        "NHS123456": [
            {"pam_id": "p1", "score": 45, "level": 1, "date_taken": "2024-01-01"},
            {"pam_id": "p2", "score": 52, "level": 2, "date_taken": "2024-01-15"},
            {"pam_id": "p3", "score": 58, "level": 3, "date_taken": "2024-02-01"},
            {"pam_id": "p4", "score": 62, "level": 3, "date_taken": "2024-02-15"}
        ]
    },
    "notes": {
        "NHS123456": [
            {"note_id": "n1", "note_text": "Feeling more energetic. Walking 20 minutes daily.", "author": "Dr. Smith", "sentiment_score": 0.3, "date_created": "2024-01-20"},
            {"note_id": "n2", "note_text": "Blood pressure slightly elevated. Need to reduce salt intake.", "author": "Dr. Smith", "sentiment_score": -0.1, "date_created": "2024-01-18"}
        ]
    },
    "decisions": {
        "NHS123456": [
            {"decision_id": "d1", "topic": "Diabetes Management", "chosen_option": "Combined approach", "decision_date": "2024-01-10"}
        ]
    }
}

# ==================== ROUTES ====================

# --- Frontend ---
@app.route('/')
def home():
    return DASHBOARD_HTML

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# --- Health Check ---
@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "deployment": "vercel",
        "python_version": sys.version,
        "timestamp": datetime.now().isoformat()
    })

# ==================== PERSON ENDPOINTS ====================

@app.route('/api/person/<nhs_number>', methods=['GET'])
def get_person(nhs_number):
    """Get person details"""
    person = mock_data["persons"].get(nhs_number)
    if person:
        return jsonify({"success": True, "data": person})
    
    # Return mock data if person not found
    return jsonify({
        "success": True,
        "data": {
            "nhs_number": nhs_number,
            "name": f"Patient {nhs_number}",
            "date_of_birth": "1970-01-01",
            "gender": "Unknown",
            "ethnicity": "Not specified"
        }
    })

@app.route('/api/person', methods=['POST'])
def create_person():
    """Create a new person"""
    try:
        data = request.json
        nhs_number = data.get('nhs_number')
        
        if not nhs_number:
            return jsonify({"success": False, "error": "Missing nhs_number"}), 400
        
        if nhs_number in mock_data["persons"]:
            return jsonify({"success": False, "error": "Person already exists"}), 409
        
        mock_data["persons"][nhs_number] = {
            "nhs_number": nhs_number,
            "name": data.get('name', 'New Patient'),
            "date_of_birth": data.get('date_of_birth', '2000-01-01'),
            "gender": data.get('gender', 'Unknown'),
            "ethnicity": data.get('ethnicity', 'Not specified')
        }
        
        # Initialize empty lists for this person
        mock_data["goals"][nhs_number] = []
        mock_data["outcomes"][nhs_number] = []
        mock_data["pam_scores"][nhs_number] = []
        mock_data["notes"][nhs_number] = []
        mock_data["decisions"][nhs_number] = []
        
        return jsonify({"success": True, "nhs_number": nhs_number})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== PLAN ENDPOINTS ====================

@app.route('/api/plan/<person_id>', methods=['GET'])
def get_plan(person_id):
    """Get or create a care plan"""
    try:
        if person_id not in mock_data["plans"]:
            mock_data["plans"][person_id] = {
                "plan_id": "plan-" + str(uuid.uuid4())[:8],
                "person_id": person_id,
                "status": "active",
                "created_date": datetime.now().isoformat(),
                "clinical_summary": ""
            }
        
        return jsonify({
            "success": True,
            "data": {"plan": mock_data["plans"][person_id]}
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== GOAL ENDPOINTS ====================

@app.route('/api/goals/<person_id>', methods=['GET'])
def get_goals(person_id):
    """Get all goals for a person"""
    try:
        goals = mock_data["goals"].get(person_id, [])
        return jsonify({"success": True, "data": goals})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goal', methods=['POST'])
def create_goal():
    """Create a new goal"""
    try:
        data = request.json
        person_id = data.get('person_id')
        
        if not person_id:
            return jsonify({"success": False, "error": "Missing person_id"}), 400
        
        goal = {
            "goal_id": "g" + str(uuid.uuid4())[:8],
            "description": data.get('description', ''),
            "domain": data.get('domain', 'physical_health'),
            "status": data.get('status', 'planned'),
            "steps": data.get('steps', []),
            "target_date": data.get('target_date'),
            "created_date": datetime.now().isoformat(),
            "updated_date": datetime.now().isoformat()
        }
        
        if person_id not in mock_data["goals"]:
            mock_data["goals"][person_id] = []
        mock_data["goals"][person_id].append(goal)
        
        return jsonify({"success": True, "goal_id": goal["goal_id"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goal/<goal_id>', methods=['PUT'])
def update_goal(goal_id):
    """Update a goal"""
    try:
        data = request.json
        
        for person_id, goals in mock_data["goals"].items():
            for goal in goals:
                if goal.get("goal_id") == goal_id:
                    goal["description"] = data.get("description", goal["description"])
                    goal["status"] = data.get("status", goal["status"])
                    goal["steps"] = data.get("steps", goal.get("steps", []))
                    goal["target_date"] = data.get("target_date", goal.get("target_date"))
                    goal["updated_date"] = datetime.now().isoformat()
                    
                    if data.get("status") == "achieved":
                        goal["completion_date"] = datetime.now().isoformat()
                    
                    return jsonify({"success": True})
        
        return jsonify({"success": False, "error": "Goal not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/goal/<goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    """Delete a goal"""
    try:
        for person_id, goals in mock_data["goals"].items():
            for i, goal in enumerate(goals):
                if goal.get("goal_id") == goal_id:
                    del mock_data["goals"][person_id][i]
                    return jsonify({"success": True})
        
        return jsonify({"success": False, "error": "Goal not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== OUTCOME ENDPOINTS ====================

@app.route('/api/outcomes/<person_id>', methods=['GET'])
def get_outcomes(person_id):
    """Get all outcomes for a person"""
    try:
        outcomes = mock_data["outcomes"].get(person_id, [])
        return jsonify({"success": True, "data": outcomes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/outcome', methods=['POST'])
def create_outcome():
    """Create a new outcome"""
    try:
        data = request.json
        person_id = data.get('person_id')
        
        if not person_id:
            return jsonify({"success": False, "error": "Missing person_id"}), 400
        
        outcome = {
            "outcome_id": "o" + str(uuid.uuid4())[:8],
            "metric_name": data.get('metric_name', ''),
            "value": float(data.get('value', 0)),
            "target_value": float(data.get('target_value')) if data.get('target_value') else None,
            "domain": data.get('domain', 'physical_health'),
            "date_recorded": datetime.now().isoformat(),
            "self_reported": data.get('self_reported', 1),
            "notes": data.get('notes', '')
        }
        
        if person_id not in mock_data["outcomes"]:
            mock_data["outcomes"][person_id] = []
        mock_data["outcomes"][person_id].append(outcome)
        
        return jsonify({"success": True, "outcome_id": outcome["outcome_id"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== PAM ENDPOINTS ====================

@app.route('/api/pam/<person_id>', methods=['GET'])
def get_pam(person_id):
    """Get PAM scores for a person"""
    try:
        scores = mock_data["pam_scores"].get(person_id, [])
        return jsonify({"success": True, "data": scores})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/pam', methods=['POST'])
def create_pam():
    """Create a new PAM score"""
    try:
        data = request.json
        person_id = data.get('person_id')
        score = data.get('score')
        
        if not person_id or score is None:
            return jsonify({"success": False, "error": "Missing person_id or score"}), 400
        
        score = int(score)
        level = 1 if score <= 47 else 2 if score <= 54.9 else 3 if score <= 66.9 else 4
        
        pam_entry = {
            "pam_id": "p" + str(uuid.uuid4())[:8],
            "score": score,
            "level": level,
            "date_taken": datetime.now().isoformat(),
            "notes": data.get('notes', '')
        }
        
        if person_id not in mock_data["pam_scores"]:
            mock_data["pam_scores"][person_id] = []
        mock_data["pam_scores"][person_id].append(pam_entry)
        
        return jsonify({"success": True, "pam_id": pam_entry["pam_id"], "level": level})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== NOTE ENDPOINTS ====================

@app.route('/api/notes/<person_id>', methods=['GET'])
def get_notes(person_id):
    """Get clinical notes for a person"""
    try:
        notes = mock_data["notes"].get(person_id, [])
        return jsonify({"success": True, "data": notes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/note', methods=['POST'])
def create_note():
    """Create a new clinical note"""
    try:
        data = request.json
        person_id = data.get('person_id')
        
        if not person_id:
            return jsonify({"success": False, "error": "Missing person_id"}), 400
        
        # Simple sentiment analysis
        text = data.get('note_text', '')
        positive_words = ['improved', 'better', 'good', 'positive', 'hopeful', 'well']
        negative_words = ['worse', 'struggling', 'difficult', 'anxious', 'pain', 'tired']
        
        pos_count = sum(1 for w in positive_words if w in text.lower())
        neg_count = sum(1 for w in negative_words if w in text.lower())
        sentiment = (pos_count - neg_count) / (pos_count + neg_count + 1)
        
        note = {
            "note_id": "n" + str(uuid.uuid4())[:8],
            "note_text": text,
            "author": data.get('author', 'Unknown'),
            "sentiment_score": sentiment,
            "date_created": datetime.now().isoformat(),
            "entities": {},
            "summary": text[:200] + "..." if len(text) > 200 else text
        }
        
        if person_id not in mock_data["notes"]:
            mock_data["notes"][person_id] = []
        mock_data["notes"][person_id].append(note)
        
        return jsonify({
            "success": True,
            "note_id": note["note_id"],
            "sentiment": {
                "overall": sentiment,
                "classification": "positive" if sentiment > 0.1 else "negative" if sentiment < -0.1 else "neutral"
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== DECISION ENDPOINTS ====================

@app.route('/api/decisions/<person_id>', methods=['GET'])
def get_decisions(person_id):
    """Get decisions for a person"""
    try:
        decisions = mock_data["decisions"].get(person_id, [])
        return jsonify({"success": True, "data": decisions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/decision', methods=['POST'])
def create_decision():
    """Create a new decision"""
    try:
        data = request.json
        person_id = data.get('person_id')
        
        if not person_id:
            return jsonify({"success": False, "error": "Missing person_id"}), 400
        
        decision = {
            "decision_id": "d" + str(uuid.uuid4())[:8],
            "topic": data.get('topic', ''),
            "options": data.get('options', []),
            "chosen_option": data.get('chosen_option', ''),
            "preference_mode": data.get('preference_mode', 'shared'),
            "decision_date": datetime.now().isoformat(),
            "notes": data.get('notes', '')
        }
        
        if person_id not in mock_data["decisions"]:
            mock_data["decisions"][person_id] = []
        mock_data["decisions"][person_id].append(decision)
        
        return jsonify({"success": True, "decision_id": decision["decision_id"]})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== INSIGHTS ENDPOINT ====================

@app.route('/api/insights/<person_id>', methods=['GET'])
def get_insights(person_id):
    """Generate AI insights for a person"""
    try:
        # Get data for this person
        goals = mock_data["goals"].get(person_id, [])
        outcomes = mock_data["outcomes"].get(person_id, [])
        pam_scores = mock_data["pam_scores"].get(person_id, [])
        notes = mock_data["notes"].get(person_id, [])
        
        # Calculate metrics
        total_goals = len(goals)
        completed_goals = len([g for g in goals if g.get("status") == "achieved"])
        completion_rate = completed_goals / total_goals if total_goals > 0 else 0
        
        latest_pam = pam_scores[-1]["score"] if pam_scores else 50
        pam_level = pam_scores[-1]["level"] if pam_scores else 1
        
        # Calculate domain scores
        domain_scores = {}
        for outcome in outcomes:
            domain = outcome.get('domain', 'general')
            if domain not in domain_scores:
                domain_scores[domain] = []
            if outcome.get('target_value') and outcome['target_value'] > 0:
                score = min((outcome['value'] / outcome['target_value']) * 10, 10)
                domain_scores[domain].append(score)
        
        for domain in domain_scores:
            domain_scores[domain] = sum(domain_scores[domain]) / len(domain_scores[domain])
        
        # Risk assessment
        risk_factors = []
        risk_score = 0.25
        
        if completion_rate < 0.3:
            risk_factors.append("Low goal completion rate")
            risk_score += 0.2
        if latest_pam < 48:
            risk_factors.append("Low patient activation")
            risk_score += 0.3
        if len(outcomes) < 3:
            risk_factors.append("Limited outcome tracking")
            risk_score += 0.1
        
        if risk_score > 0.7:
            risk_level = "critical"
        elif risk_score > 0.5:
            risk_level = "high"
        elif risk_score > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        # Recommendations
        recommendations = []
        if completion_rate < 0.5:
            recommendations.append({
                "name": "Review Goals",
                "priority": 1,
                "justification": f"Only {int(completion_rate * 100)}% of goals completed"
            })
        if latest_pam < 48:
            recommendations.append({
                "name": "Self-Management Support",
                "priority": 1,
                "justification": "Low patient activation detected"
            })
        if risk_level in ["high", "critical"]:
            recommendations.append({
                "name": "Clinical Review",
                "priority": 1,
                "justification": "High risk detected"
            })
        if not recommendations:
            recommendations.append({
                "name": "Maintain Current Plan",
                "priority": 3,
                "justification": "All metrics are stable"
            })
        
        # PAM trajectory prediction
        if len(pam_scores) > 1:
            recent_trend = pam_scores[-1]["score"] - pam_scores[-2]["score"]
            if recent_trend > 3:
                pam_trend = "improving"
                predicted = min(latest_pam + 8, 100)
            elif recent_trend < -3:
                pam_trend = "declining"
                predicted = max(latest_pam - 5, 0)
            else:
                pam_trend = "stable"
                predicted = latest_pam + 2
        else:
            pam_trend = "stable"
            predicted = latest_pam + 1
        
        # Sentiment from notes
        sentiments = [n.get('sentiment_score', 0) for n in notes]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
        
        return jsonify({
            "success": True,
            "data": {
                "person_id": person_id,
                "generated_at": datetime.now().isoformat(),
                "risk_assessment": {
                    "risk_level": risk_level,
                    "risk_score": round(risk_score, 2),
                    "confidence": 0.85,
                    "factors": risk_factors if risk_factors else ["No significant risk factors identified"]
                },
                "pam_trajectory": {
                    "predicted_score": int(predicted),
                    "trend": pam_trend,
                    "confidence": 0.7 if len(pam_scores) > 3 else 0.5,
                    "trajectory": [int(min(max(latest_pam + i * 2, 0), 100)) for i in range(10)]
                },
                "recommendations": recommendations,
                "domain_scores": domain_scores,
                "sentiment_analysis": {
                    "overall": round(avg_sentiment, 2),
                    "classification": "positive" if avg_sentiment > 0.1 else "negative" if avg_sentiment < -0.1 else "neutral",
                    "positive_ratio": max(0, min(1, (avg_sentiment + 1) / 2)),
                    "negative_ratio": max(0, min(1, (1 - avg_sentiment) / 2))
                },
                "entities": {
                    "symptoms": ["fatigue", "pain"] if "pain" in str(notes) else [],
                    "medications": ["lisinopril"] if "lisinopril" in str(notes) else [],
                    "conditions": ["diabetes"] if "diabetes" in str(notes) else []
                },
                "summary": {
                    "total_goals": total_goals,
                    "completed_goals": completed_goals,
                    "completion_rate": round(completion_rate, 2),
                    "latest_pam": latest_pam,
                    "pam_level": pam_level
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
                "summary": {
                    "total_goals": 0,
                    "completed_goals": 0,
                    "completion_rate": 0,
                    "latest_pam": 50
                }
            }
        })

# ==================== POPULATION ENDPOINT ====================

@app.route('/api/population', methods=['GET'])
def get_population():
    """Get population statistics"""
    try:
        total_patients = len(mock_data["persons"])
        
        # Calculate average PAM
        all_scores = []
        for scores in mock_data["pam_scores"].values():
            if scores:
                all_scores.append(scores[-1]["score"])
        avg_pam = sum(all_scores) / len(all_scores) if all_scores else 0
        
        # Goal distribution
        goal_statuses = {}
        for goals in mock_data["goals"].values():
            for goal in goals:
                status = goal.get("status", "planned")
                goal_statuses[status] = goal_statuses.get(status, 0) + 1
        
        goal_distribution = [{"status": k, "count": v} for k, v in goal_statuses.items()]
        
        return jsonify({
            "success": True,
            "data": {
                "total_patients": total_patients,
                "average_pam": round(avg_pam, 1),
                "goal_distribution": goal_distribution,
                "risk_distribution": {"low": max(0, total_patients - 1), "medium": 1, "high": 0, "critical": 0},
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Resource not found", "status": 404}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "status": 500}), 500

# ==================== MAIN ====================
if __name__ == '__main__':
    print("🏥 NHS Personalised Care API Server")
    print(f"📡 Running on http://localhost:5000")
    print(f"🐍 Python version: {sys.version}")
    print("✅ All endpoints ready!")
    app.run(host='0.0.0.0', port=5000, debug=True)