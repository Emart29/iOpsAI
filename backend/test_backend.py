# backend/test_backend.py
import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health():
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health check passed\n")

def test_upload():
    print("📤 Testing file upload...")
    
    # Create test CSV
    test_csv = "Name,Age,Salary\nJohn,30,50000\nJane,25,60000\nBob,35,70000"
    
    files = {'file': ('test.csv', test_csv, 'text/csv')}
    response = requests.post(f"{BASE_URL}/upload-enhanced", files=files)
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Session ID: {data.get('session_id')}")
    print(f"Rows: {data.get('analysis', {}).get('overview', {}).get('rows')}")
    print(f"Columns: {data.get('analysis', {}).get('overview', {}).get('columns')}")
    
    assert response.status_code == 200
    assert 'session_id' in data
    print("✅ Upload test passed\n")
    
    return data['session_id']

def test_ai_question(session_id):
    print("🤖 Testing AI question...")
    
    response = requests.post(
        f"{BASE_URL}/ask",
        params={'session_id': session_id, 'question': 'How many rows?'}
    )
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Answer: {data.get('answer')}")
    
    assert response.status_code == 200
    print("✅ AI question test passed\n")

def test_chart_data(session_id):
    print("📊 Testing chart data...")
    
    response = requests.get(f"{BASE_URL}/chart-data/{session_id}?chart_type=overview")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Chart type: {data.get('type')}")
    print(f"Data points: {len(data.get('data', []))}")
    
    assert response.status_code == 200
    print("✅ Chart data test passed\n")

def test_sessions():
    print("📋 Testing sessions list...")
    
    response = requests.get(f"{BASE_URL}/sessions")
    
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Total sessions: {data.get('total')}")
    
    assert response.status_code == 200
    print("✅ Sessions list test passed\n")

if __name__ == "__main__":
    print("🧪 Running Backend Tests\n")
    print("="*50 + "\n")
    
    try:
        test_health()
        session_id = test_upload()
        test_ai_question(session_id)
        test_chart_data(session_id)
        test_sessions()
        
        print("="*50)
        print("🎉 ALL TESTS PASSED!")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()