from flask import Flask, request, Response
import subprocess
import os

app = Flask(__name__)

# Dictionary to store the process reference
processes = {}

def start_streamlink_http_server(url):
    proxy_url = 'http://192.168.1.123:7086'
    
    # Set environment variables for proxy
    env = os.environ.copy()
    env['HTTP_PROXY'] = proxy_url
    env['HTTPS_PROXY'] = proxy_url
    env['http_proxy'] = proxy_url  # Lowercase fallback
    env['https_proxy'] = proxy_url  # Lowercase fallback
    env['NO_PROXY'] = ''  # Ensure no exclusions bypass the proxy
    env['STREAMLINK_ARGS'] = f'--http-proxy={proxy_url} --https-proxy={proxy_url}'  # Additional safeguard

    # Streamlink command to output HLS stream to stdout
    command = [
        'streamlink',
        '--http-no-ssl-verify',        # Disable SSL verification if needed
        '--http-proxy', proxy_url,     # Explicit proxy for HTTP
        '--https-proxy', proxy_url,    # Explicit proxy for HTTPS
        '--hls-live-edge', '10',       # Smaller edge size to reduce delay
        '--hls-segment-stream-data',   # Enable HLS segment streaming
        '--hls-live-restart',          # Restart on live stream interruptions
        url, 'best',
        '-o', '-'  # Output to stdout
    ]

    # Start the Streamlink process
    proc = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def stop_streamlink_http_server(proc):
    # Terminate the Streamlink process and clean up
    if proc:
        proc.terminate()
        proc.wait()
        # Optionally send a kill signal if the process does not terminate
        try:
            proc.kill()
        except Exception as e:
            print(f"Error killing process: {e}")

def stream_generator(proc):
    """Generator to stream data from the process stdout"""
    while True:
        data = proc.stdout.read(1024)  # Read in chunks
        if not data:
            break
        yield data

@app.route('/stream')
def stream():
    url = request.args.get('url')
    
    if not url:
        return "No URL provided.", 400
    
    # Stop any currently running Streamlink process
    if 'proc' in processes:
        stop_streamlink_http_server(processes['proc'])
        del processes['proc']  # Remove reference to the old process
    
    # Start the new Streamlink process
    proc = start_streamlink_http_server(url)
    processes['proc'] = proc

    # Return a streaming response directly to the client
    return Response(stream_generator(proc), mimetype='video/mp4')

@app.route('/stop')
def stop():
    # Stop the currently running Streamlink process
    if 'proc' in processes:
        stop_streamlink_http_server(processes['proc'])
        del processes['proc']
    
    return "Stream stopped.", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7085)
