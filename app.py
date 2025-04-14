from flask import Flask
import threading
import sys
from bot import run_bot

app = Flask(__name__)

def start_bot():
    try:
        run_bot()
    except Exception as e:
        print(f"Bot error: {e}")

# Start the bot in a separate thread immediately
bot_thread = threading.Thread(target=start_bot)
bot_thread.daemon = True
bot_thread.start()

if __name__ == '__main__':
    # Enable Flask debug mode which includes auto-reloader
    app.run(debug=True, use_reloader=True) 