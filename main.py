import socketio
import time

sio = socketio.Client()

@sio.on('web_response')
def on_message(data):
    print(f"Received from web app: {data}")

def main():
    sio.connect('http://localhost:5000')
    sio.emit('console_message', "Hello from Console App!")
    sio.emit('get_user_string')
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Exiting...")
        sio.disconnect()
        exit()
        
        
@sio.on('send_input')
def on_input(data):
    user_input = data['input']
    process_input(user_input) 
    
def process_input(user_input):
    print(f"Received input from Flask app: {user_input}")
    
if __name__ == '__main__':
    main()
