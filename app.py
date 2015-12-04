#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

from flask import Flask
from flask_socketio import SocketIO, emit,  disconnect

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)


@app.route('/js/<path:path>')
def send_js(path):
    return app.send_static_file('js' + '/' + path)


@socketio.on('action event', namespace='/test')
def action_message(message):
    print(len(message['data']))
    emit('action', [
         {'act': 'fill',
          'type': 'id',
          'label': 'userInput',
          'value': 'name'},
         {'act': 'fill',
          'type': 'id',
          'label': 'passwordInput',
          'value': '123456'},
         {'act': 'click',
          'type': 'class',
          'label': 'col-sm-4 col-sm-offset-4 btn btn-primary',
          'index': 0}]
         )


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', debug=True)
