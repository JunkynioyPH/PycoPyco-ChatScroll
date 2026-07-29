import sys
import time
import signal
import socketio

# ==========================================
# CONFIGURATION
# ==========================================
# Obtain this token from Streamlabs Dashboard -> Settings -> API Settings -> API Tokens -> Socket API Token
with open('token.txt','r') as token:
    STREAMLABS_SOCKET_TOKEN = "YOUR_STREAMLABS_SOCKET_TOKEN_HERE"

# Create Socket.IO client instance with automatic ping heartbeats and reconnects
sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,  # Infinite reconnection attempts
    reconnection_delay=2,     # Start retrying after 2 seconds
    reconnection_delay_max=10 # Max delay between retries
)

# ==========================================
# EVENT HANDLERS
# ==========================================
@sio.event
def connect():
    print("✅ Successfully connected to Streamlabs WebSocket API!")
    print(" Listening for merged chat messages from Twitch and YouTube...\n")

@sio.event
def disconnect():
    print("⚠️ Disconnected from Streamlabs. Reconnecting automatically...")

@sio.event
def connect_error(data):
    print(f"❌ Connection error: {data}")

@sio.on("event")
def on_event(data):
    """
    Streamlabs sends a generic 'event' object for all stream actions.
    Filter specifically for type 'message' to capture chat messages.
    """
    event_type = data.get("type")

    if event_type == "message":
        messages = data.get("message", [])
        for msg in messages:
            platform = msg.get("platform", "chat").upper() # 'TWITCH' or 'YOUTUBE'
            username = msg.get("name", "Anonymous")
            comment = msg.get("comment", "")
            
            # Print formatted chat message
            print(f"[{platform}] {username}: {comment}")

# ==========================================
# MAIN EXECUTION & SHUTDOWN HANDLING
# ==========================================
def handle_exit_signal(sig, frame):
    """Handle Ctrl+C cleanly without printing huge stack traces."""
    print("\n🛑 Stop signal received. Disconnecting and shutting down...")
    try:
        sio.disconnect()
    except Exception:
        pass
    sys.exit(0)

def main():
    if STREAMLABS_SOCKET_TOKEN == "YOUR_STREAMLABS_SOCKET_TOKEN_HERE":
        print("❌ ERROR: Please replace STREAMLABS_SOCKET_TOKEN with your actual token!")
        sys.exit(1)

    # Register Ctrl+C (SIGINT) signal handler
    signal.signal(signal.SIGINT, handle_exit_signal)

    endpoint_url = f"https://sockets.streamlabs.com?token={STREAMLABS_SOCKET_TOKEN}"

    # Infinite loop to handle initial connection drops/failures
    while True:
        try:
            print("Connecting to Streamlabs...")
            sio.connect(endpoint_url)
            sio.wait()  # Blocks and listens indefinitely while connected
        except Exception as err:
            print(f"⚠️ Socket execution error: {err}")
            print("Retrying connection in 5 seconds...\n")
            time.sleep(5)

if __name__ == "__main__":
    main()