import os
import openai
from datetime import datetime
from typing import List, Dict
from .db_manager import DatabaseManager

class AIInterpreter:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        openai.api_key = self.openai_api_key
        
    def process_messages(self, batch_size: int = 10):
        """Process messages in batches and update their interpretations"""
        messages = self.db.get_not_interpreted_messages(limit=batch_size)
        if not messages:
            print("No messages to interpret")
            return
            
        print(f"Processing {len(messages)} messages...")
        
        # Group messages by date for better context
        messages_by_date = {}
        for msg in messages:
            date_str = msg.created_at.date().isoformat()
            if date_str not in messages_by_date:
                messages_by_date[date_str] = []
            messages_by_date[date_str].append(msg)
            
        # Process each date's messages
        for date_str, date_messages in messages_by_date.items():
            try:
                interpretation = self._get_interpretation(date_messages)
                # Update each message with its interpretation
                for msg in date_messages:
                    self.db.update_interpretation(msg.message_id, interpretation)
                print(f"Successfully interpreted {len(date_messages)} messages from {date_str}")
            except Exception as e:
                print(f"Error processing messages from {date_str}: {e}")
                
    def _get_interpretation(self, messages: List[Dict]) -> str:
        """Get interpretation from ChatGPT for a batch of messages"""
        # Prepare the prompt
        prompt = "Please provide a brief summary of these Twitter messages:\n\n"
        for msg in messages:
            prompt += f"- {msg.content}\n"
            
        # Get interpretation from ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides concise summaries of Twitter messages."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    def run_interpretation_loop(self, interval_minutes: int = 5):
        """Run the interpretation process periodically"""
        import time
        while True:
            try:
                self.process_messages()
                time.sleep(interval_minutes * 60)  # Convert minutes to seconds
            except Exception as e:
                print(f"Error in interpretation loop: {e}")
                time.sleep(60)  # Wait a minute before retrying 