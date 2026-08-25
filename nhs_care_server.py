"""
NHS Personalised Care PWA - Complete Python Backend Server
Serves the PWA, manages database, AI models, and API endpoints
"""

import os
import sys
import json
import sqlite3
import uuid
import hashlib
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pathlib import Path
import re

# Force UTF-8 encoding for console output
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

# ===================== DEPENDENCIES =====================
try:
    from flask import Flask, request, jsonify, send_from_directory, send_file
    from flask_cors import CORS
    from flask_socketio import SocketIO, emit
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.preprocessing import StandardScaler
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install: pip install flask flask-cors flask-socketio pandas numpy scikit-learn")
    sys.exit(1)

# ===================== LOGGING =====================
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===================== CONSTANTS =====================
class HealthDomain(Enum):
    PHYSICAL = "physical_health"
    MENTAL = "mental_health"
    SOCIAL = "social_wellbeing"
    FINANCIAL = "financial_security"
    OCCUPATIONAL = "occupational_wellbeing"

class GoalStatus(Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    PARTIALLY_ACHIEVED = "partially_achieved"
    ABANDONED = "abandoned"

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ===================== DATABASE =====================
class Database:
    """SQLite database with full schema for PWA"""
    
    def __init__(self, db_path: str = "nhs_care.db"):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Create all tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Persons
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
            
            # Care Plans
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
            
            # Goals
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
            
            # Outcomes
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
            
            # PAM Scores
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
            
            # Clinical Notes
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
            
            # AI Predictions
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
            
            # Decisions
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
            
            # Audit Log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id TEXT PRIMARY KEY,
                    user_id TEXT,
                    action TEXT,
                    resource_type TEXT,
                    resource_id TEXT,
                    details TEXT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results as dict"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute update and return affected rows"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount

# ===================== AI SERVICES =====================
class NLPService:
    """Natural Language Processing for clinical notes"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        self.sentiment_keywords = {
            'positive': ['improved', 'better', 'good', 'excellent', 'hopeful', 'confident',
                        'progress', 'achieved', 'managing', 'coping', 'positive', 'well', 'great'],
            'negative': ['worse', 'declining', 'struggling', 'difficult', 'anxious',
                        'depressed', 'pain', 'tired', 'exhausted', 'frustrated', 'worry',
                        'concerned', 'poor'],
            'neutral': ['stable', 'unchanged', 'same', 'consistent', 'steady']
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract health entities from text"""
        entities = {
            'symptoms': [],
            'medications': [],
            'conditions': [],
            'emotional_state': [],
            'social_factors': [],
            'behaviours': []
        }
        
        text_lower = text.lower()
        
        # Symptoms
        symptom_patterns = [
            r'(pain|ache|discomfort|sore|stiff|swollen)',
            r'(headache|migraine|dizziness|nausea|fatigue|insomnia|fever)',
            r'(shortness of breath|cough|chest pain|palpitations)'
        ]
        for pattern in symptom_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                entities['symptoms'].extend(matches if isinstance(matches, list) else [matches])
        
        # Medications
        med_patterns = [
            r'(metformin|insulin|lisinopril|atorvastatin|omeprazole|paracetamol)',
            r'(taking|prescribed|on) (\w+)\s*(\d+)?\s*(mg|mcg|g)?'
        ]
        for pattern in med_patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                for m in matches:
                    if isinstance(m, tuple) and len(m) > 1:
                        entities['medications'].append(m[1])
                    elif isinstance(m, str):
                        entities['medications'].append(m)
        
        # Emotional state
        for state, keywords in self.sentiment_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    entities['emotional_state'].append(keyword)
        
        # Social factors
        social_indicators = ['living alone', 'carer', 'employed', 'retired', 'volunteer',
                            'family', 'friends', 'support network', 'community', 'widowed']
        for indicator in social_indicators:
            if indicator in text_lower:
                entities['social_factors'].append(indicator)
        
        # Conditions
        conditions = ['diabetes', 'hypertension', 'asthma', 'copd', 'arthritis', 
                     'depression', 'anxiety', 'dementia', 'parkinson', 'stroke']
        for condition in conditions:
            if condition in text_lower:
                entities['conditions'].append(condition)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def analyse_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyse sentiment in clinical note"""
        text_lower = text.lower()
        words = text_lower.split()
        
        sentiment_scores = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for word in words:
            for sentiment, keywords in self.sentiment_keywords.items():
                if word in keywords:
                    sentiment_scores[sentiment] += 1
        
        total = sum(sentiment_scores.values()) or 1
        overall = (sentiment_scores['positive'] - sentiment_scores['negative']) / total
        
        return {
            'positive_ratio': sentiment_scores['positive'] / total,
            'negative_ratio': sentiment_scores['negative'] / total,
            'neutral_ratio': sentiment_scores['neutral'] / total,
            'overall': overall,
            'classification': 'positive' if overall > 0.1 else 'negative' if overall < -0.1 else 'neutral'
        }
    
    def generate_summary(self, notes: List[str]) -> str:
        """Generate clinical summary from notes"""
        if not notes:
            return "No notes available"
        
        full_text = " ".join(notes)
        full_text = re.sub(r'\s+', ' ', full_text)
        
        sentences = re.split(r'[.!?]+', full_text)
        important_sentences = []
        
        clinical_indicators = ['diagnosis', 'treatment', 'medication', 'symptom',
                              'referral', 'appointment', 'follow-up', 'plan', 'goal',
                              'improved', 'worsened', 'stable', 'review']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            weight = sum(1 for indicator in clinical_indicators if indicator in sentence.lower())
            if weight > 0 or len(important_sentences) < 2:
                important_sentences.append((weight, sentence))
        
        important_sentences.sort(reverse=True)
        summary = ". ".join([s[1] for s in important_sentences[:5]])
        
        return summary + "."

class PredictiveAnalytics:
    """AI-powered predictive models"""
    
    def __init__(self):
        self.deterioration_model = RandomForestClassifier(n_estimators=50, random_state=42)
        self.pam_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def train(self, data: pd.DataFrame):
        """Train AI models"""
        if data.empty:
            return
        
        feature_cols = ['age', 'pam_score', 'goal_completion', 'adherence', 
                       'num_medications', 'num_symptoms', 'social_support']
        
        X = data[feature_cols].fillna(0).values
        X_scaled = self.scaler.fit_transform(X)
        
        if 'deteriorated' in data.columns:
            y = data['deteriorated'].fillna(0).values
            self.deterioration_model.fit(X_scaled, y)
        
        if 'future_pam' in data.columns:
            y = data['future_pam'].fillna(50).values
            self.pam_model.fit(X_scaled, y)
        
        self.is_trained = True
        logger.info("AI models trained successfully")
    
    def predict_risk(self, person_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict deterioration risk"""
        if not self.is_trained:
            return {'risk_level': 'medium', 'risk_score': 0.4, 'confidence': 0.3}
        
        features = np.array([[
            person_data.get('age', 60),
            person_data.get('pam_score', 50),
            person_data.get('goal_completion', 0.5),
            person_data.get('adherence', 0.7),
            person_data.get('num_medications', 2),
            person_data.get('num_symptoms', 1),
            person_data.get('social_support', 5)
        ]])
        
        features_scaled = self.scaler.transform(features)
        risk_prob = self.deterioration_model.predict_proba(features_scaled)[0][1]
        
        if risk_prob < 0.3:
            risk_level = 'low'
        elif risk_prob < 0.6:
            risk_level = 'medium'
        elif risk_prob < 0.8:
            risk_level = 'high'
        else:
            risk_level = 'critical'
        
        return {
            'risk_level': risk_level,
            'risk_score': float(risk_prob),
            'confidence': 0.85
        }
    
    def predict_pam(self, historical_scores: List[int]) -> Dict[str, Any]:
        """Predict future PAM score"""
        if len(historical_scores) < 3:
            return {
                'predicted_score': historical_scores[-1] if historical_scores else 50,
                'trend': 'stable',
                'confidence': 0.3
            }
        
        try:
            x = np.array(range(len(historical_scores))).reshape(-1, 1)
            y = np.array(historical_scores)
            
            coeff = np.polyfit(x.flatten(), y, 1)
            future_x = np.array(range(len(historical_scores), len(historical_scores) + 30))
            predicted = coeff[0] * future_x + coeff[1]
            final_prediction = np.clip(predicted[-1], 0, 100)
            
            trend = 'improving' if coeff[0] > 0.5 else 'declining' if coeff[0] < -0.5 else 'stable'
            
            return {
                'predicted_score': int(final_prediction),
                'trend': trend,
                'confidence': 0.7 if len(historical_scores) > 5 else 0.5,
                'trajectory': [int(p) for p in predicted[:10]]
            }
        except Exception as e:
            logger.error(f"PAM prediction error: {e}")
            return {'predicted_score': historical_scores[-1], 'trend': 'stable', 'confidence': 0.3}

# ===================== FLASK APP =====================
class NHSCareApp:
    """Complete Flask application for NHS Personalised Care PWA"""
    
    def __init__(self):
        self.app = Flask(__name__, static_folder='static', template_folder='templates')
        self.app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
        self.app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
        
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self.db = Database()
        self.nlp = NLPService()
        self.predictor = PredictiveAnalytics()
        
        self._setup_routes()
        self._setup_socket_events()
        self._load_models()
        
        logger.info("NHS Personalised Care API Server Initialized")
    
    def _load_models(self):
        """Load or train AI models"""
        try:
            # Load sample training data
            sample_data = pd.DataFrame({
                'age': np.random.randint(20, 90, 200),
                'pam_score': np.random.randint(20, 100, 200),
                'goal_completion': np.random.random(200),
                'adherence': np.random.random(200),
                'num_medications': np.random.randint(0, 8, 200),
                'num_symptoms': np.random.randint(0, 5, 200),
                'social_support': np.random.randint(1, 10, 200),
                'deteriorated': np.random.randint(0, 2, 200),
                'future_pam': np.random.randint(20, 100, 200)
            })
            self.predictor.train(sample_data)
            logger.info("AI models loaded")
        except Exception as e:
            logger.warning(f"Could not train AI models: {e}")
    
    def _setup_routes(self):
        """Setup all API routes"""
        
        # ===== FRONTEND =====
        @self.app.route('/')
        def serve_index():
            """Serve the PWA index page"""
            return send_file('templates/index.html')
        
        @self.app.route('/manifest.json')
        def serve_manifest():
            """Serve the PWA manifest"""
            return send_file('static/manifest.json')
        
        @self.app.route('/sw.js')
        def serve_sw():
            """Serve the service worker"""
            return send_file('static/sw.js')
        
        @self.app.route('/icons/<path:filename>')
        def serve_icons(filename):
            """Serve app icons"""
            return send_from_directory('static/icons', filename)
        
        @self.app.route('/static/<path:filename>')
        def serve_static(filename):
            """Serve static files"""
            return send_from_directory('static', filename)
        
        # ===== AUTH =====
        @self.app.route('/api/auth/login', methods=['POST'])
        def login():
            """Authenticate user"""
            data = request.json
            nhs_number = data.get('nhs_number')
            
            # Check if person exists
            person = self.db.execute_query(
                "SELECT * FROM persons WHERE nhs_number = ?", (nhs_number,)
            )
            
            if not person:
                return jsonify({'error': 'NHS number not found'}), 404
            
            return jsonify({
                'success': True,
                'person': person[0],
                'token': hashlib.sha256(f"{nhs_number}-secret".encode()).hexdigest()
            })
        
        # ===== PERSONS =====
        @self.app.route('/api/person', methods=['POST'])
        def create_person():
            """Register a new person"""
            data = request.json
            
            required = ['nhs_number', 'name', 'date_of_birth']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Check if exists
            existing = self.db.execute_query(
                "SELECT * FROM persons WHERE nhs_number = ?", (data['nhs_number'],)
            )
            if existing:
                return jsonify({'error': 'Person already exists'}), 409
            
            query = '''
                INSERT INTO persons (nhs_number, name, date_of_birth, gender, ethnicity, preferred_language)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            params = (
                data['nhs_number'],
                data['name'],
                data['date_of_birth'],
                data.get('gender', ''),
                data.get('ethnicity', ''),
                data.get('preferred_language', 'English')
            )
            self.db.execute_update(query, params)
            
            # Create care plan
            plan_id = str(uuid.uuid4())
            self.db.execute_update(
                "INSERT INTO care_plans (plan_id, person_id) VALUES (?, ?)",
                (plan_id, data['nhs_number'])
            )
            
            self._log_audit('person_created', data['nhs_number'])
            return jsonify({'success': True, 'nhs_number': data['nhs_number']})
        
        @self.app.route('/api/person/<nhs_number>', methods=['GET'])
        def get_person(nhs_number):
            """Get person details"""
            person = self.db.execute_query(
                "SELECT * FROM persons WHERE nhs_number = ?", (nhs_number,)
            )
            if not person:
                return jsonify({'error': 'Person not found'}), 404
            return jsonify({'success': True, 'data': person[0]})
        
        @self.app.route('/api/person/<nhs_number>', methods=['PUT'])
        def update_person(nhs_number):
            """Update person details"""
            data = request.json
            
            query = '''
                UPDATE persons 
                SET name=?, gender=?, ethnicity=?, preferred_language=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE nhs_number=?
            '''
            params = (
                data.get('name'),
                data.get('gender'),
                data.get('ethnicity'),
                data.get('preferred_language'),
                nhs_number
            )
            rows = self.db.execute_update(query, params)
            if rows == 0:
                return jsonify({'error': 'Person not found'}), 404
            
            self._log_audit('person_updated', nhs_number)
            return jsonify({'success': True})
        
        # ===== CARE PLANS =====
        @self.app.route('/api/plan/<person_id>', methods=['GET'])
        def get_care_plan(person_id):
            """Get active care plan"""
            plan = self.db.execute_query(
                "SELECT * FROM care_plans WHERE person_id = ? AND status = 'active'",
                (person_id,)
            )
            if not plan:
                return jsonify({'error': 'Care plan not found'}), 404
            
            plan_data = plan[0]
            
            # Get goals
            goals = self.db.execute_query(
                "SELECT * FROM goals WHERE person_id = ? AND plan_id = ?",
                (person_id, plan_data['plan_id'])
            )
            
            # Get outcomes
            outcomes = self.db.execute_query(
                "SELECT * FROM outcomes WHERE person_id = ? AND plan_id = ?",
                (person_id, plan_data['plan_id'])
            )
            
            # Get decisions
            decisions = self.db.execute_query(
                "SELECT * FROM decisions WHERE person_id = ?",
                (person_id,)
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'plan': plan_data,
                    'goals': goals,
                    'outcomes': outcomes,
                    'decisions': decisions
                }
            })
        
        # ===== GOALS =====
        @self.app.route('/api/goal', methods=['POST'])
        def create_goal():
            """Create a new goal"""
            data = request.json
            
            required = ['person_id', 'plan_id', 'description', 'domain']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            goal_id = str(uuid.uuid4())
            query = '''
                INSERT INTO goals 
                (goal_id, person_id, plan_id, description, domain, status, 
                 target_date, steps, barriers, enablers)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                goal_id,
                data['person_id'],
                data['plan_id'],
                data['description'],
                data['domain'],
                data.get('status', 'planned'),
                data.get('target_date'),
                json.dumps(data.get('steps', [])),
                json.dumps(data.get('barriers', [])),
                json.dumps(data.get('enablers', []))
            )
            self.db.execute_update(query, params)
            
            self._log_audit('goal_created', goal_id)
            return jsonify({'success': True, 'goal_id': goal_id})
        
        @self.app.route('/api/goal/<goal_id>', methods=['PUT'])
        def update_goal(goal_id):
            """Update a goal"""
            data = request.json
            
            query = '''
                UPDATE goals 
                SET description=?, status=?, target_date=?, steps=?, 
                    barriers=?, enablers=?, notes=?, updated_date=CURRENT_TIMESTAMP
                WHERE goal_id=?
            '''
            params = (
                data.get('description'),
                data.get('status'),
                data.get('target_date'),
                json.dumps(data.get('steps', [])),
                json.dumps(data.get('barriers', [])),
                json.dumps(data.get('enablers', [])),
                data.get('notes'),
                goal_id
            )
            rows = self.db.execute_update(query, params)
            if rows == 0:
                return jsonify({'error': 'Goal not found'}), 404
            
            # If achieved, set completion date
            if data.get('status') == 'achieved':
                self.db.execute_update(
                    "UPDATE goals SET completion_date = CURRENT_TIMESTAMP WHERE goal_id = ?",
                    (goal_id,)
                )
            
            self._log_audit('goal_updated', goal_id)
            return jsonify({'success': True})
        
        @self.app.route('/api/goal/<goal_id>', methods=['DELETE'])
        def delete_goal(goal_id):
            """Delete a goal"""
            rows = self.db.execute_update(
                "DELETE FROM goals WHERE goal_id = ?", (goal_id,)
            )
            if rows == 0:
                return jsonify({'error': 'Goal not found'}), 404
            
            self._log_audit('goal_deleted', goal_id)
            return jsonify({'success': True})
        
        @self.app.route('/api/goals/<person_id>', methods=['GET'])
        def get_goals(person_id):
            """Get all goals for a person"""
            goals = self.db.execute_query(
                "SELECT * FROM goals WHERE person_id = ? ORDER BY created_date DESC",
                (person_id,)
            )
            return jsonify({'success': True, 'data': goals})
        
        # ===== OUTCOMES =====
        @self.app.route('/api/outcome', methods=['POST'])
        def create_outcome():
            """Record an outcome"""
            data = request.json
            
            required = ['person_id', 'plan_id', 'domain', 'metric_name', 'value']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            outcome_id = str(uuid.uuid4())
            query = '''
                INSERT INTO outcomes 
                (outcome_id, person_id, plan_id, domain, metric_name, 
                 value, target_value, self_reported, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                outcome_id,
                data['person_id'],
                data['plan_id'],
                data['domain'],
                data['metric_name'],
                float(data['value']),
                data.get('target_value'),
                data.get('self_reported', 1),
                data.get('notes', '')
            )
            self.db.execute_update(query, params)
            
            self._log_audit('outcome_recorded', outcome_id)
            return jsonify({'success': True, 'outcome_id': outcome_id})
        
        @self.app.route('/api/outcomes/<person_id>', methods=['GET'])
        def get_outcomes(person_id):
            """Get outcomes for a person"""
            outcomes = self.db.execute_query(
                "SELECT * FROM outcomes WHERE person_id = ? ORDER BY date_recorded DESC",
                (person_id,)
            )
            return jsonify({'success': True, 'data': outcomes})
        
        # ===== PAM SCORES =====
        @self.app.route('/api/pam', methods=['POST'])
        def create_pam():
            """Record a PAM score"""
            data = request.json
            
            if 'person_id' not in data or 'score' not in data:
                return jsonify({'error': 'Missing required fields: person_id, score'}), 400
            
            pam_id = str(uuid.uuid4())
            score = int(data['score'])
            
            # Determine level
            if score <= 47:
                level = 1
            elif score <= 54.9:
                level = 2
            elif score <= 66.9:
                level = 3
            else:
                level = 4
            
            query = '''
                INSERT INTO pam_scores (pam_id, person_id, score, level, notes)
                VALUES (?, ?, ?, ?, ?)
            '''
            params = (pam_id, data['person_id'], score, level, data.get('notes', ''))
            self.db.execute_update(query, params)
            
            self._log_audit('pam_recorded', pam_id)
            return jsonify({'success': True, 'pam_id': pam_id, 'level': level})
        
        @self.app.route('/api/pam/<person_id>', methods=['GET'])
        def get_pam_scores(person_id):
            """Get PAM history"""
            scores = self.db.execute_query(
                "SELECT * FROM pam_scores WHERE person_id = ? ORDER BY date_taken ASC",
                (person_id,)
            )
            return jsonify({'success': True, 'data': scores})
        
        # ===== CLINICAL NOTES =====
        @self.app.route('/api/note', methods=['POST'])
        def create_note():
            """Process a clinical note"""
            data = request.json
            
            if 'person_id' not in data or 'note_text' not in data:
                return jsonify({'error': 'Missing required fields'}), 400
            
            # NLP processing
            entities = self.nlp.extract_entities(data['note_text'])
            sentiment = self.nlp.analyse_sentiment(data['note_text'])
            
            # Get historical notes for summary
            historical = self.db.execute_query(
                "SELECT note_text FROM clinical_notes WHERE person_id = ? ORDER BY date_created DESC LIMIT 5",
                (data['person_id'],)
            )
            notes = [n['note_text'] for n in historical]
            notes.append(data['note_text'])
            summary = self.nlp.generate_summary(notes)
            
            note_id = str(uuid.uuid4())
            query = '''
                INSERT INTO clinical_notes 
                (note_id, person_id, author, note_text, sentiment_score, entities, summary)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                note_id,
                data['person_id'],
                data.get('author', ''),
                data['note_text'],
                sentiment['overall'],
                json.dumps(entities),
                summary
            )
            self.db.execute_update(query, params)
            
            # Update care plan summary
            plan = self.db.execute_query(
                "SELECT plan_id FROM care_plans WHERE person_id = ? AND status = 'active'",
                (data['person_id'],)
            )
            if plan:
                self.db.execute_update(
                    "UPDATE care_plans SET clinical_summary = ? WHERE plan_id = ?",
                    (summary, plan[0]['plan_id'])
                )
            
            self._log_audit('note_created', note_id)
            
            # Emit real-time update via WebSocket
            self.socketio.emit('new_note', {
                'person_id': data['person_id'],
                'note_id': note_id,
                'sentiment': sentiment,
                'summary': summary
            })
            
            return jsonify({
                'success': True,
                'note_id': note_id,
                'sentiment': sentiment,
                'entities': entities,
                'summary': summary
            })
        
        @self.app.route('/api/notes/<person_id>', methods=['GET'])
        def get_notes(person_id):
            """Get clinical notes"""
            notes = self.db.execute_query(
                "SELECT * FROM clinical_notes WHERE person_id = ? ORDER BY date_created DESC",
                (person_id,)
            )
            return jsonify({'success': True, 'data': notes})
        
        # ===== AI INSIGHTS =====
        @self.app.route('/api/insights/<person_id>', methods=['GET'])
        def get_insights(person_id):
            """Generate AI insights"""
            # Gather data
            person = self.db.execute_query(
                "SELECT * FROM persons WHERE nhs_number = ?", (person_id,)
            )
            if not person:
                return jsonify({'error': 'Person not found'}), 404
            
            person_data = person[0]
            
            # Get PAM scores
            pam_scores = self.db.execute_query(
                "SELECT score FROM pam_scores WHERE person_id = ? ORDER BY date_taken ASC",
                (person_id,)
            )
            scores = [p['score'] for p in pam_scores]
            latest_pam = scores[-1] if scores else 50
            
            # Get goals
            goals = self.db.execute_query(
                "SELECT * FROM goals WHERE person_id = ?", (person_id,)
            )
            completed = sum(1 for g in goals if g['status'] == 'achieved')
            completion_rate = completed / len(goals) if goals else 0
            
            # Get outcomes
            outcomes = self.db.execute_query(
                "SELECT * FROM outcomes WHERE person_id = ?", (person_id,)
            )
            
            # Get notes for sentiment
            notes = self.db.execute_query(
                "SELECT sentiment_score FROM clinical_notes WHERE person_id = ?",
                (person_id,)
            )
            avg_sentiment = sum(n['sentiment_score'] for n in notes) / len(notes) if notes else 0
            
            # Calculate domain scores
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
            
            # Calculate age
            age = (datetime.now() - datetime.fromisoformat(person_data['date_of_birth'])).days // 365
            
            # Build person profile
            profile = {
                'age': age,
                'pam_score': latest_pam,
                'goal_completion': completion_rate,
                'adherence': 0.7,
                'num_medications': 2,
                'num_symptoms': len(outcomes) // 3,
                'social_support': 5
            }
            
            # Get predictions
            risk = self.predictor.predict_risk(profile)
            pam_prediction = self.predictor.predict_pam(scores)
            
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
            if risk['risk_level'] in ['high', 'critical']:
                recommendations.append({
                    'name': 'Clinical Review',
                    'priority': 1,
                    'justification': 'High risk detected'
                })
            
            # Generate entities summary from notes
            all_entities = {}
            notes_text = self.db.execute_query(
                "SELECT note_text FROM clinical_notes WHERE person_id = ?",
                (person_id,)
            )
            for note in notes_text:
                entities = self.nlp.extract_entities(note['note_text'])
                for key, values in entities.items():
                    if key not in all_entities:
                        all_entities[key] = []
                    all_entities[key].extend(values)
            
            for key in all_entities:
                all_entities[key] = list(set(all_entities[key]))[:5]
            
            insights = {
                'person_id': person_id,
                'generated_at': datetime.now().isoformat(),
                'risk_assessment': risk,
                'pam_trajectory': pam_prediction,
                'recommendations': recommendations[:5],
                'domain_scores': domain_scores,
                'sentiment_analysis': {
                    'overall': avg_sentiment,
                    'classification': 'positive' if avg_sentiment > 0.1 else 'negative' if avg_sentiment < -0.1 else 'neutral'
                },
                'entities': all_entities,
                'summary': {
                    'total_goals': len(goals),
                    'completed_goals': completed,
                    'completion_rate': completion_rate,
                    'latest_pam': latest_pam
                }
            }
            
            # Save prediction
            self.db.execute_update(
                '''INSERT INTO ai_predictions 
                   (prediction_id, person_id, prediction_type, prediction_data, confidence)
                   VALUES (?, ?, ?, ?, ?)''',
                (str(uuid.uuid4()), person_id, 'insights', json.dumps(insights), risk.get('confidence', 0.5))
            )
            
            return jsonify({'success': True, 'data': insights})
        
        # ===== POPULATION =====
        @self.app.route('/api/population', methods=['GET'])
        def get_population():
            """Get population insights"""
            # Count active patients
            patients = self.db.execute_query(
                "SELECT COUNT(*) as count FROM persons WHERE is_active = 1"
            )
            
            # Average PAM
            pam_avg = self.db.execute_query(
                "SELECT AVG(score) as avg FROM pam_scores"
            )
            
            # Goal completion
            goals = self.db.execute_query(
                "SELECT status, COUNT(*) as count FROM goals GROUP BY status"
            )
            
            # Risk distribution
            risk_distribution = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
            
            return jsonify({
                'success': True,
                'data': {
                    'total_patients': patients[0]['count'] if patients else 0,
                    'average_pam': pam_avg[0]['avg'] if pam_avg and pam_avg[0]['avg'] else 0,
                    'goal_distribution': goals,
                    'risk_distribution': risk_distribution,
                    'timestamp': datetime.now().isoformat()
                }
            })
        
        # ===== DECISIONS =====
        @self.app.route('/api/decision', methods=['POST'])
        def create_decision():
            """Record a shared decision"""
            data = request.json
            
            required = ['person_id', 'topic', 'chosen_option']
            for field in required:
                if field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            decision_id = str(uuid.uuid4())
            query = '''
                INSERT INTO decisions 
                (decision_id, person_id, topic, options, chosen_option, 
                 preference_mode, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            '''
            params = (
                decision_id,
                data['person_id'],
                data['topic'],
                json.dumps(data.get('options', [])),
                data['chosen_option'],
                data.get('preference_mode', 'shared'),
                data.get('notes', '')
            )
            self.db.execute_update(query, params)
            
            self._log_audit('decision_created', decision_id)
            return jsonify({'success': True, 'decision_id': decision_id})
        
        @self.app.route('/api/decisions/<person_id>', methods=['GET'])
        def get_decisions(person_id):
            """Get decisions for a person"""
            decisions = self.db.execute_query(
                "SELECT * FROM decisions WHERE person_id = ? ORDER BY decision_date DESC",
                (person_id,)
            )
            return jsonify({'success': True, 'data': decisions})
        
        # ===== AUDIT =====
        @self.app.route('/api/audit/<person_id>', methods=['GET'])
        def get_audit(person_id):
            """Get audit log for a person"""
            logs = self.db.execute_query(
                "SELECT * FROM audit_log WHERE user_id = ? ORDER BY timestamp DESC LIMIT 50",
                (person_id,)
            )
            return jsonify({'success': True, 'data': logs})
        
        # ===== HEALTH CHECK =====
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """API health check"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'database': 'connected',
                'ai_models': 'loaded' if self.predictor.is_trained else 'unavailable'
            })
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(e):
            return jsonify({'error': 'Resource not found'}), 404
        
        @self.app.errorhandler(500)
        def server_error(e):
            return jsonify({'error': 'Internal server error'}), 500
    
    def _setup_socket_events(self):
        """Setup WebSocket events for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            logger.info(f"Client connected: {request.sid}")
            emit('connected', {'status': 'connected'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            logger.info(f"Client disconnected: {request.sid}")
        
        @self.socketio.on('subscribe_person')
        def handle_subscribe(data):
            person_id = data.get('person_id')
            if person_id:
                logger.info(f"Client {request.sid} subscribed to {person_id}")
                emit('subscribed', {'person_id': person_id})
        
        @self.socketio.on('get_realtime_update')
        def handle_realtime_update(data):
            person_id = data.get('person_id')
            if person_id:
                self.socketio.emit('update', {
                    'person_id': person_id,
                    'timestamp': datetime.now().isoformat()
                })
    
    def _log_audit(self, action: str, resource_id: str, user_id: str = 'system'):
        """Log to audit trail"""
        self.db.execute_update(
            '''INSERT INTO audit_log (log_id, user_id, action, resource_type, resource_id)
               VALUES (?, ?, ?, ?, ?)''',
            (str(uuid.uuid4()), user_id, action, 'resource', resource_id)
        )
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Run the application"""
        logger.info(f"Starting NHS Personalised Care API Server on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)

# ===================== FILE GENERATORS =====================
def create_static_files():
    """Create necessary static files for the PWA with UTF-8 encoding"""
    
    # Create directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/icons', exist_ok=True)
    
    # Create HTML template - index.html will be placed separately
    # We'll use the provided index.html file
    
    # Create manifest.json
    manifest = {
        "name": "NHS Personalised Care",
        "short_name": "NHS Care",
        "description": "NHS England Comprehensive Model for Personalised Care",
        "start_url": "/",
        "display": "standalone",
        "orientation": "portrait",
        "background_color": "#005EB8",
        "theme_color": "#005EB8",
        "icons": [
            {"src": "/icons/icon-72.png", "sizes": "72x72", "type": "image/png"},
            {"src": "/icons/icon-96.png", "sizes": "96x96", "type": "image/png"},
            {"src": "/icons/icon-128.png", "sizes": "128x128", "type": "image/png"},
            {"src": "/icons/icon-144.png", "sizes": "144x144", "type": "image/png"},
            {"src": "/icons/icon-152.png", "sizes": "152x152", "type": "image/png"},
            {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any maskable"},
            {"src": "/icons/icon-384.png", "sizes": "384x384", "type": "image/png"},
            {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any maskable"}
        ]
    }
    
    with open('static/manifest.json', 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)
    
    # Create service worker
    sw_content = """
const CACHE_NAME = 'nhs-care-v2';
const ASSETS = ['/', '/manifest.json', '/api/health'];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) { return cache.addAll(ASSETS); })
            .then(function() { return self.skipWaiting(); })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys()
            .then(function(keys) {
                return Promise.all(keys.filter(function(k) { return k !== CACHE_NAME; }).map(function(k) { return caches.delete(k); }));
            })
            .then(function() { return self.clients.claim(); })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) { return response || fetch(event.request); })
            .catch(function() { return new Response('Offline', { status: 503 }); })
    );
});

self.addEventListener('push', function(event) {
    var data = event.data ? event.data.json() : { title: 'NHS Care', body: 'Update available' };
    event.waitUntil(
        self.registration.showNotification(data.title || 'NHS Care', {
            body: data.body || 'You have a new update',
            icon: '/icons/icon-192.png',
            badge: '/icons/icon-72.png'
        })
    );
});
"""
    
    with open('static/sw.js', 'w', encoding='utf-8') as f:
        f.write(sw_content)
    
    # Create placeholder icons (1x1 pixel PNG data)
    png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    
    for size in [72, 96, 128, 144, 152, 192, 384, 512]:
        with open(f'static/icons/icon-{size}.png', 'wb') as f:
            f.write(png_data)
    
    logger.info("Static files created")

# ===================== DATA INITIALIZATION =====================
def initialize_sample_data(db: Database):
    """Populate database with sample data"""
    sample_persons = [
        {
            'nhs_number': 'NHS123456',
            'name': 'Sarah Johnson',
            'date_of_birth': '1965-05-15',
            'gender': 'Female',
            'ethnicity': 'White British',
            'preferred_language': 'English'
        },
        {
            'nhs_number': 'NHS789012',
            'name': 'James Smith',
            'date_of_birth': '1978-03-22',
            'gender': 'Male',
            'ethnicity': 'White British',
            'preferred_language': 'English'
        },
        {
            'nhs_number': 'NHS345678',
            'name': 'Aisha Patel',
            'date_of_birth': '1990-11-08',
            'gender': 'Female',
            'ethnicity': 'Asian British',
            'preferred_language': 'English'
        }
    ]
    
    for person in sample_persons:
        # Check if exists
        existing = db.execute_query(
            "SELECT * FROM persons WHERE nhs_number = ?", (person['nhs_number'],)
        )
        if existing:
            continue
        
        # Insert person
        db.execute_update(
            '''INSERT INTO persons 
               (nhs_number, name, date_of_birth, gender, ethnicity, preferred_language)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (person['nhs_number'], person['name'], person['date_of_birth'],
             person['gender'], person['ethnicity'], person['preferred_language'])
        )
        
        # Create care plan
        plan_id = str(uuid.uuid4())
        db.execute_update(
            "INSERT INTO care_plans (plan_id, person_id) VALUES (?, ?)",
            (plan_id, person['nhs_number'])
        )
        
        # Add sample goals
        goals = [
            ('Walk 30 minutes daily', 'physical_health', ['Start with 10 min', 'Increase gradually']),
            ('Join community walking group', 'social_wellbeing', ['Find local groups', 'Attend first session']),
            ('Reduce blood pressure', 'physical_health', ['Monitor BP daily', 'Reduce salt intake'])
        ]
        for desc, domain, steps in goals:
            goal_id = str(uuid.uuid4())
            db.execute_update(
                '''INSERT INTO goals 
                   (goal_id, person_id, plan_id, description, domain, status, steps)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (goal_id, person['nhs_number'], plan_id, desc, domain, 'planned', json.dumps(steps))
            )
        
        # Add sample PAM scores
        pam_scores = [45, 52, 58, 62, 68]
        for score in pam_scores:
            pam_id = str(uuid.uuid4())
            level = 1 if score <= 47 else 2 if score <= 54.9 else 3 if score <= 66.9 else 4
            db.execute_update(
                '''INSERT INTO pam_scores (pam_id, person_id, score, level)
                   VALUES (?, ?, ?, ?)''',
                (pam_id, person['nhs_number'], score, level)
            )
        
        # Add sample outcomes
        outcomes = [
            ('Blood Pressure', 'physical_health', 135, 120),
            ('Heart Rate', 'physical_health', 82, 70),
            ('Mood Score', 'mental_health', 7, 8)
        ]
        for metric, domain, value, target in outcomes:
            outcome_id = str(uuid.uuid4())
            db.execute_update(
                '''INSERT INTO outcomes 
                   (outcome_id, person_id, plan_id, domain, metric_name, value, target_value)
                   VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (outcome_id, person['nhs_number'], plan_id, domain, metric, value, target)
            )
    
    logger.info("Sample data initialized")

# ===================== MAIN =====================
def main():
    """Main entry point"""
    print("=" * 60)
    print("NHS PERSONALISED CARE - COMPLETE BACKEND SERVER")
    print("=" * 60)
    
    # Create static files
    create_static_files()
    
    # Initialize database
    db = Database()
    initialize_sample_data(db)
    
    # Create and run app
    app = NHSCareApp()
    
    print("\n" + "=" * 60)
    print("SERVER STARTING")
    print("=" * 60)
    print("Access the PWA: http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET  /api/person/<nhs_number>")
    print("  GET  /api/plan/<person_id>")
    print("  GET  /api/goals/<person_id>")
    print("  POST /api/goal")
    print("  GET  /api/pam/<person_id>")
    print("  POST /api/pam")
    print("  POST /api/note")
    print("  GET  /api/insights/<person_id>")
    print("  GET  /api/population")
    print("  GET  /api/health")
    print("=" * 60)
    print("\nTest with:")
    print("  curl http://localhost:5000/api/health")
    print("  curl http://localhost:5000/api/person/NHS123456")
    print("  curl http://localhost:5000/api/pam/NHS123456")
    print("\n" + "=" * 60)
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()