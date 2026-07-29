import sys, time, signal, socketio, os

# ==========================================
# CONFIGURATION
# ==========================================
TOKEN_PATH = './token/token.txt'

if not os.path.exists(TOKEN_PATH):
    raise FileNotFoundError('Please create "./token/token.txt" and place your Streamlabs token inside.')

with open(TOKEN_PATH, 'r') as f:
    STREAMLABS_SOCKET_TOKEN = f.read().strip() or None
    # print(STREAMLABS_SOCKET_TOKEN[:-1])

# Create Socket.IO client instance
sio = socketio.Client(
    reconnection=True,
    reconnection_attempts=0,   # Infinite reconnection attempts
    reconnection_delay=2,      # Start retrying after 2 seconds
    reconnection_delay_max=10  # Max delay between retries
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
    event_for = data.get("for")
    print(event_type, event_for)
    # print(event_type, data)
    if event_type == "message":
        messages = data.get("message", [])
        for msg in messages:
            # Safely extract platform string before calling upper()
            raw_platform = msg.get("platform") or "UNKNOWN"
            platform = raw_platform.upper()
            
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
    if not STREAMLABS_SOCKET_TOKEN:
        print("❌ ERROR: 'token.txt' is empty! Please populate it with your Streamlabs Socket Token!")
        sys.exit(1)

    # Register Ctrl+C (SIGINT) signal handler
    signal.signal(signal.SIGINT, handle_exit_signal)

    endpoint_url = f"https://sockets.streamlabs.com?token={STREAMLABS_SOCKET_TOKEN}"

    # Infinite loop to handle initial connection drops/failures
    while True:
        try:
            print("Connecting to Streamlabs...")
            # Added transports=['websocket'] for reliable Streamlabs connection
            sio.connect(endpoint_url, transports=['websocket'])
            sio.wait()  # Blocks and listens indefinitely while connected
        except Exception as err:
            print(f"⚠️ Socket execution error: {err}")
            print("Retrying connection in 5 seconds...\n")
            time.sleep(5)

if __name__ == "__main__":
    main()