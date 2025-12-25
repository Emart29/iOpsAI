# backend/test_server.py - Test if server is working
import requests
import time

def test_server():
    max_retries = 5
    retry_delay = 2
    
    for i in range(max_retries):
        try:
            print(f"Attempt {i+1}/{max_retries} to connect to server...")
            response = requests.get("http://localhost:8000/health", timeout=5)
            
            if response.status_code == 200:
                print("✅ Server is running!")
                print("Response:", response.json())
                return True
            else:
                print(f"❌ Server responded with status: {response.status_code}")
                
        except requests.ConnectionError:
            print("❌ Cannot connect to server. Make sure it's running on port 8000.")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if i < max_retries - 1:
            print(f"Waiting {retry_delay} seconds before retry...")
            time.sleep(retry_delay)
    
    print("\n🚨 Failed to connect to server. Please start the backend:")
    print("cd backend && python -m uvicorn main:app --reload --port 8000")
    return False

if __name__ == "__main__":
    test_server()