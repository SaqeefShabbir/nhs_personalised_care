"""
API Test Suite for NHS Personalised Care System
Uses built-in urllib - no external dependencies needed!
Run: python -m pytest tests/test_api.py -v
Or: python tests/test_api.py
"""

import json
import urllib.request
import urllib.error
from urllib.parse import urljoin
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = "http://localhost:5000"

class APIError(Exception):
    """Custom exception for API errors"""
    pass

def make_request(method, endpoint, data=None):
    """Make HTTP request using urllib"""
    url = urljoin(BASE_URL, endpoint)
    
    try:
        if method == "GET":
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        
        elif method == "POST":
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url, 
                data=data_bytes,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        
        elif method == "PUT":
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=data_bytes,
                headers={'Content-Type': 'application/json'},
                method='PUT'
            )
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        
        elif method == "DELETE":
            req = urllib.request.Request(url, method='DELETE')
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
    
    except urllib.error.URLError as e:
        print(f"❌ Connection error: {e}")
        print(f"   Make sure the server is running at {BASE_URL}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return None

class TestAPI:
    """Test all API endpoints"""
    
    @staticmethod
    def test_health_check():
        """Test health endpoint"""
        print("\n🧪 Testing: Health Check")
        response = make_request("GET", "/api/health")
        
        if response and response.get('status') == 'healthy':
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
    
    @staticmethod
    def test_get_person():
        """Test get person endpoint"""
        print("\n🧪 Testing: Get Person")
        response = make_request("GET", "/api/person/NHS123456")
        
        if response and response.get('success') and response['data']['nhs_number'] == 'NHS123456':
            print("✅ Get person passed")
            return True
        else:
            print("❌ Get person failed")
            return False
    
    @staticmethod
    def test_create_person():
        """Test create person endpoint"""
        print("\n🧪 Testing: Create Person")
        import uuid
        test_nhs = f"NHS{str(uuid.uuid4())[:6].upper()}"
        
        person_data = {
            'nhs_number': test_nhs,
            'name': 'Test Patient',
            'date_of_birth': '1990-01-01',
            'gender': 'Male'
        }
        response = make_request("POST", "/api/person", person_data)
        
        if response and response.get('success') and response.get('nhs_number') == test_nhs:
            print(f"✅ Create person passed (created: {test_nhs})")
            return True
        else:
            print("❌ Create person failed")
            return False
    
    @staticmethod
    def test_get_goals():
        """Test get goals endpoint"""
        print("\n🧪 Testing: Get Goals")
        response = make_request("GET", "/api/goals/NHS123456")
        
        if response and response.get('success') and isinstance(response.get('data'), list):
            print("✅ Get goals passed")
            return True
        else:
            print("❌ Get goals failed")
            return False
    
    @staticmethod
    def test_create_goal():
        """Test create goal endpoint"""
        print("\n🧪 Testing: Create Goal")
        import uuid
        goal_data = {
            'person_id': 'NHS123456',
            'plan_id': f'test-plan-{uuid.uuid4()}',
            'description': 'Test Goal',
            'domain': 'physical_health',
            'status': 'planned'
        }
        response = make_request("POST", "/api/goal", goal_data)
        
        if response and response.get('success') and response.get('goal_id'):
            print("✅ Create goal passed")
            return True
        else:
            print("❌ Create goal failed")
            return False
    
    @staticmethod
    def test_get_outcomes():
        """Test get outcomes endpoint"""
        print("\n🧪 Testing: Get Outcomes")
        response = make_request("GET", "/api/outcomes/NHS123456")
        
        if response and response.get('success') and isinstance(response.get('data'), list):
            print("✅ Get outcomes passed")
            return True
        else:
            print("❌ Get outcomes failed")
            return False
    
    @staticmethod
    def test_create_outcome():
        """Test create outcome endpoint"""
        print("\n🧪 Testing: Create Outcome")
        import uuid
        outcome_data = {
            'person_id': 'NHS123456',
            'plan_id': f'test-plan-{uuid.uuid4()}',
            'domain': 'physical_health',
            'metric_name': 'Test Metric',
            'value': 100,
            'target_value': 120
        }
        response = make_request("POST", "/api/outcome", outcome_data)
        
        if response and response.get('success') and response.get('outcome_id'):
            print("✅ Create outcome passed")
            return True
        else:
            print("❌ Create outcome failed")
            return False
    
    @staticmethod
    def test_get_pam():
        """Test get PAM scores endpoint"""
        print("\n🧪 Testing: Get PAM Scores")
        response = make_request("GET", "/api/pam/NHS123456")
        
        if response and response.get('success') and isinstance(response.get('data'), list):
            print("✅ Get PAM passed")
            return True
        else:
            print("❌ Get PAM failed")
            return False
    
    @staticmethod
    def test_create_pam():
        """Test create PAM score endpoint"""
        print("\n🧪 Testing: Create PAM Score")
        import random
        pam_data = {
            'person_id': 'NHS123456',
            'score': random.randint(50, 80)
        }
        response = make_request("POST", "/api/pam", pam_data)
        
        if response and response.get('success') and response.get('pam_id'):
            print("✅ Create PAM passed")
            return True
        else:
            print("❌ Create PAM failed")
            return False
    
    @staticmethod
    def test_create_note():
        """Test create note endpoint"""
        print("\n🧪 Testing: Create Note")
        note_data = {
            'person_id': 'NHS123456',
            'author': 'Test Doctor',
            'note_text': 'Test clinical note with sentiment analysis'
        }
        response = make_request("POST", "/api/note", note_data)
        
        if response and response.get('success') and response.get('note_id'):
            print("✅ Create note passed")
            if response.get('sentiment'):
                print(f"   Sentiment: {response['sentiment'].get('classification', 'unknown')}")
            return True
        else:
            print("❌ Create note failed")
            return False
    
    @staticmethod
    def test_get_notes():
        """Test get notes endpoint"""
        print("\n🧪 Testing: Get Notes")
        response = make_request("GET", "/api/notes/NHS123456")
        
        if response and response.get('success') and isinstance(response.get('data'), list):
            print("✅ Get notes passed")
            return True
        else:
            print("❌ Get notes failed")
            return False
    
    @staticmethod
    def test_get_insights():
        """Test get insights endpoint"""
        print("\n🧪 Testing: Get Insights")
        response = make_request("GET", "/api/insights/NHS123456")
        
        if response and response.get('success'):
            data = response.get('data', {})
            if 'risk_assessment' in data and 'recommendations' in data:
                print("✅ Get insights passed")
                print(f"   Risk Level: {data['risk_assessment'].get('risk_level', 'unknown')}")
                print(f"   Recommendations: {len(data.get('recommendations', []))}")
                return True
        print("❌ Get insights failed")
        return False
    
    @staticmethod
    def test_get_population():
        """Test get population endpoint"""
        print("\n🧪 Testing: Get Population")
        response = make_request("GET", "/api/population")
        
        if response and response.get('success'):
            data = response.get('data', {})
            if 'total_patients' in data and 'average_pam' in data:
                print("✅ Get population passed")
                print(f"   Total Patients: {data.get('total_patients', 0)}")
                print(f"   Average PAM: {data.get('average_pam', 0):.1f}")
                return True
        print("❌ Get population failed")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("🧪 NHS PERSONALISED CARE - API TEST SUITE")
    print("=" * 60)
    print(f"\n📡 Server: {BASE_URL}")
    print("ℹ️  Make sure the server is running before testing")
    
    try:
        response = make_request("GET", "/api/health")
        if not response:
            print("\n❌ Cannot connect to server!")
            print("   Please start the server first: python nhs_care_server.py")
            return False
    except:
        print("\n❌ Cannot connect to server!")
        print("   Please start the server first: python nhs_care_server.py")
        return False
    
    tests = [
        TestAPI.test_health_check,
        TestAPI.test_get_person,
        TestAPI.test_create_person,
        TestAPI.test_get_goals,
        TestAPI.test_create_goal,
        TestAPI.test_get_outcomes,
        TestAPI.test_create_outcome,
        TestAPI.test_get_pam,
        TestAPI.test_create_pam,
        TestAPI.test_create_note,
        TestAPI.test_get_notes,
        TestAPI.test_get_insights,
        TestAPI.test_get_population,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test error: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    for i, test in enumerate(tests):
        status = "✅" if results[i] else "❌"
        print(f"{status} {test.__name__}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} tests failed")
    
    return passed == total

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)