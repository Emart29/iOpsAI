# backend/test_upload_direct.py
import requests

def test_upload():
    url = 'http://localhost:8000/upload'
    
    with open('test_data.csv', 'rb') as f:
        files = {'file': ('test_data.csv', f, 'text/csv')}
        response = requests.post(url, files=files)
    
    print('Status Code:', response.status_code)
    print('Response:', response.text)
    
    if response.status_code == 200:
        data = response.json()
        print('✅ Upload successful!')
        print('Session ID:', data.get('session_id'))
        print('Message:', data.get('message'))
    else:
        print('❌ Upload failed')

if __name__ == '__main__':
    test_upload()
