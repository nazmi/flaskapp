from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print("Client Connected")

@socketio.on('console_message')
def handle_console_message(message):
    print(f"Received from console: {message}")
    socketio.emit('web_response', "Hello back to console!")


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input')
def input():
    return render_template('input.html')

@socketio.on('get_user_string')
def trigger_socket_event():
    socketio.emit('get_user_string')

@socketio.on('send_input')
def handle_input(data):
    user_input = data
    print(f"Received input: {user_input}")
    socketio.emit('web_response', f"{user_input}")

@app.route('/handle_input', methods=['POST'])
def handle_input():
    user_input = request.form.get('userInput')
    # Do something with the input, for instance:
    print(user_input)
    socketio.emit('web_response', f"{user_input}")
    # Redirect to the main page or wherever you'd like:
    return redirect(url_for('index'))  # Assuming 'index' is the name of the function for your main page.

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
