import requests
import json

def test_all_endpoints():
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Insight Studio API Endpoints...")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Health check: {response.status_code}")
    except:
        print("❌ Cannot connect to server")
        return
    
    # Test upload
    print("\n📤 Testing file upload...")
    try:
        with open("sample_data.csv", "rb") as f:
            files = {"file": ("sample.csv", f, "text/csv")}
            response = requests.post(f"{base_url}/datasets/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data["session_id"]
            print(f"✅ Upload successful - Session: {session_id}")
            
            # Test other endpoints with the session
            print("\n🔍 Testing EDA endpoints...")
            
            # Profile
            profile_response = requests.post(f"{base_url}/eda/profile", json={"session_id": session_id})
            print(f"✅ Profile: {profile_response.status_code}")
            
            # Correlations
            corr_response = requests.post(f"{base_url}/eda/correlations", json={"session_id": session_id})
            print(f"✅ Correlations: {corr_response.status_code}")
            
            # AI QA
            print("\n🤖 Testing AI endpoints...")
            qa_response = requests.post(
                f"{base_url}/ai/qa", 
                json={"session_id": session_id, "question": "How many rows and columns?"}
            )
            print(f"✅ AI QA: {qa_response.status_code}")
            
            # Suggestions
            suggest_response = requests.post(
                f"{base_url}/ai/suggest", 
                json={"session_id": session_id, "goal": "find insights"}
            )
            print(f"✅ Suggestions: {suggest_response.status_code}")
            
            print(f"\n🎉 All tests passed! Session ID: {session_id}")
            
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_all_endpoints()