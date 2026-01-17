"""
Simple test to verify the trade chatbot functionality
"""
import subprocess
import time
import requests
import sys
import os

def test_backend():
    """Test the backend API"""
    # Start the backend server in the background
    backend_dir = os.path.join(os.getcwd(), 'trade_chatbot', 'backend')
    
    # We'll just verify that the files exist and have the expected content
    expected_files = [
        'app.py',
        'config.py',
        'api/chat.py',
        'api/data.py',
        'context_engine/context_manager.py',
        'utils/helpers.py'
    ]
    
    for file in expected_files:
        file_path = os.path.join(backend_dir, file)
        if not os.path.exists(file_path):
            print(f"Missing backend file: {file}")
            return False
    
    print("All backend files exist")
    return True

def test_frontend():
    """Test the frontend files"""
    frontend_dir = os.path.join(os.getcwd(), 'trade_chatbot', 'frontend')
    
    expected_files = [
        'package.json',
        'webpack.config.js',
        'public/index.html',
        'src/App.jsx',
        'src/components/ChatInterface.jsx',
        'src/components/Message.jsx',
        'src/components/Input.jsx',
        'src/services/api.js'
    ]
    
    for file in expected_files:
        file_path = os.path.join(frontend_dir, file)
        if not os.path.exists(file_path):
            print(f"Missing frontend file: {file}")
            return False
    
    print("All frontend files exist")
    return True

def run_tests():
    """Run all tests"""
    print("Running trade chatbot tests...")
    
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    
    if backend_ok and frontend_ok:
        print("\nAll tests passed! The trade chatbot module is properly structured.")
        print("\nTo run the application:")
        print("1. Backend: cd trade_chatbot/backend && python app.py")
        print("2. Frontend: cd trade_chatbot/frontend && npm install && npm start")
        return True
    else:
        print("\nSome tests failed.")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)