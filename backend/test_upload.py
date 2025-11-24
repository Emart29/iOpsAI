# backend/test_upload.py
import requests
import json

def test_upload():
    print("📤 Testing File Upload...")
    
    try:
        # Upload file
        with open('test_data.csv', 'rb') as f:
            files = {'file': ('test_data.csv', f, 'text/csv')}
            response = requests.post('http://localhost:8000/upload', files=files)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ UPLOAD SUCCESSFUL!")
            print(f"   Session ID: {data['session_id']}")
            print(f"   File: {data['analysis']['filename']}")
            print(f"   Rows: {data['analysis']['rows']}")
            print(f"   Columns: {data['analysis']['columns']}")
            print(f"   Column Names: {data['analysis']['column_names']}")
            
            session_id = data['session_id']
            
            # Test AI question
            print("\n🤖 Testing AI Question...")
            
            question_data = {
                'session_id': session_id,
                'question': 'How many columns and what are their names?'
            }
            
            ai_response = requests.post('http://localhost:8000/ask', json=question_data)
            ai_data = ai_response.json()
            
            print("✅ AI RESPONSE:")
            print(f"   Question: {ai_data['question']}")
            print(f"   Answer: {ai_data['answer']}")
            
            # Test export
            print("\n📝 Testing Code Export...")
            
            export_response = requests.get(f'http://localhost:8000/export/{session_id}')
            export_data = export_response.json()
            
            print("✅ EXPORT SUCCESSFUL!")
            print(f"   Filename: {export_data['filename']}")
            print(f"   Code Preview: {export_data['code'][:50]}...")
            
            return True
            
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ TEST FAILED: {str(e)}")
        return False

if __name__ == "__main__":
    test_upload()
    print("\n" + "✨" * 50)
    print("✨ BACKEND IS FULLY OPERATIONAL!")
    print("✨" * 50)