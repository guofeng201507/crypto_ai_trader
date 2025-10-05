"""
Context management for the trade chatbot
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ContextManager:
    """
    Manages conversation context for users
    """
    def __init__(self, storage_path: str = "context_storage"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.contexts: Dict[str, List[Dict[str, Any]]] = {}
    
    def get_context(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve context for a specific user
        """
        if user_id in self.contexts:
            return self.contexts[user_id]
        
        # Try to load from file
        context_file = os.path.join(self.storage_path, f"{user_id}_context.json")
        if os.path.exists(context_file):
            with open(context_file, 'r') as f:
                self.contexts[user_id] = json.load(f)
        else:
            self.contexts[user_id] = []
        
        return self.contexts[user_id]
    
    def update_context(self, user_id: str, user_message: str, bot_response: str):
        """
        Update context with a new user message and bot response
        """
        context = self.get_context(user_id)
        new_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response
        }
        context.append(new_entry)
        
        # Keep only the last 20 interactions to prevent memory issues
        if len(context) > 20:
            context = context[-20:]
        
        self.contexts[user_id] = context
        
        # Save to file
        context_file = os.path.join(self.storage_path, f"{user_id}_context.json")
        with open(context_file, 'w') as f:
            json.dump(context, f)
    
    def clear_context(self, user_id: str):
        """
        Clear context for a specific user
        """
        if user_id in self.contexts:
            del self.contexts[user_id]
        
        context_file = os.path.join(self.storage_path, f"{user_id}_context.json")
        if os.path.exists(context_file):
            os.remove(context_file)