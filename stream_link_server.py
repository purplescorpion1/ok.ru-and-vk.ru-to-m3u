from flask import Flask, request, redirect
import subprocess
import os

app = Flask(__name__)

# Dictionary to store the process reference
processes = {}

def start_streamlink_http_server(url):
    proxy_url = 'http://192.168.1.25:7086'
    
    # Set environment variables for proxy
    env = os.environ.copy()
    env['HTTP_PROXY'] = proxy_url
    env['HTTPS_PROXY'] = proxy_url

    # Streamlink command to run HTTP server with optimized parameters for live streaming
    command = [
        'streamlink',
        '--http-no-ssl-verify',
        '--http-proxy', proxy_url,
        '--ringbuffer-size', '500M',  # Reduce buffer size to minimize latency
        '--hls-live-edge', '10',  # Smaller edge size to reduce delay
        '--hls-segment-stream-data',
        '--player-external-http',
        '--hls-live-restart',
        '--player-external-http-port', '8889',  # HTTP server port on your machine
        url, 'best'
    ]

    # Start the Streamlink process
    proc = subprocess.Popen(command, env=env)
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

@app.route('/stream')
def stream():
    url = request.args.get('url')
    
    if not url:
        return "No URL provided.", 400
    
    # Stop any currently running Streamlink process
    if 'proc' in processes:
        stop_streamlink_http_server(processes['proc'])
        del processes['proc']  # Remove reference to the old process
    
    # Start the new Streamlink HTTP server
    proc = start_streamlink_http_server(url)
    processes['proc'] = proc

    # Redirect to Streamlink's internal server on the server's IP address
    return redirect("http://192.168.1.123:8889")

@app.route('/stop')
def stop():
    # Stop the currently running Streamlink process
    if 'proc' in processes:
        stop_streamlink_http_server(processes['proc'])
        del processes['proc']
    
    return "Stream stopped.", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7085)
