import pywhatkit
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WhatsAppBot:
    def __init__(self):
        # Wait time for WhatsApp Web to load
        self.wait_time = 15
        
    def send_message(self, phone_number, message):
        """Send a message to a specific phone number"""
        try:
            # Remove any spaces or special characters from phone number
            phone_number = ''.join(filter(str.isdigit, phone_number))
            # Add country code if not present
            if not phone_number.startswith('1'):
                phone_number = '1' + phone_number
                
            # Get current time
            now = datetime.now()
            # Schedule message for 1 minute from now
            hour = now.hour
            minute = now.minute + 1
            if minute >= 60:
                hour += 1
                minute = 0
                
            # Send message
            pywhatkit.sendwhatmsg(phone_number, message, hour, minute, self.wait_time)
            print(f"Message scheduled to be sent to {phone_number}")
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
            
    def send_message_to_group(self, group_id, message):
        """Send a message to a WhatsApp group"""
        try:
            pywhatkit.sendwhatmsg_to_group(group_id, message, 
                                         datetime.now().hour,
                                         datetime.now().minute + 1,
                                         self.wait_time)
            print(f"Message scheduled to be sent to group {group_id}")
            return True
        except Exception as e:
            print(f"Error sending message to group: {e}")
            return False
            
    def send_image(self, phone_number, image_path, caption=""):
        """Send an image with optional caption"""
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
                
            phone_number = ''.join(filter(str.isdigit, phone_number))
            if not phone_number.startswith('1'):
                phone_number = '1' + phone_number
                
            now = datetime.now()
            hour = now.hour
            minute = now.minute + 1
            if minute >= 60:
                hour += 1
                minute = 0
                
            pywhatkit.sendwhats_image(phone_number, image_path, caption, hour, minute, self.wait_time)
            print(f"Image scheduled to be sent to {phone_number}")
            return True
        except Exception as e:
            print(f"Error sending image: {e}")
            return False

def main():
    # Example usage
    bot = WhatsAppBot()
    
    # Send a message
    phone_number = "1234567890"  # Replace with actual phone number
    message = "Hello from WhatsApp Bot!"
    bot.send_message(phone_number, message)
    
    # Send a message to a group
    group_id = "ABC123"  # Replace with actual group ID
    group_message = "Hello group!"
    bot.send_message_to_group(group_id, group_message)
    
    # Send an image
    image_path = "path/to/your/image.jpg"  # Replace with actual image path
    bot.send_image(phone_number, image_path, "Check this out!")

if __name__ == "__main__":
    main() 