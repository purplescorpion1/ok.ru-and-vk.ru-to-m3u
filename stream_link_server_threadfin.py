from flask import Flask, request, Response
import subprocess
import os
import threading
import logging
import warnings
import time

# Suppress urllib3 warnings
logging.captureWarnings(True)
warnings.filterwarnings("ignore", message=".*InsecureRequestWarning.*")
warnings.filterwarnings("ignore", category=Warning, module="urllib3.*")
logging.getLogger("urllib3").setLevel(logging.CRITICAL)
logging.getLogger("urllib3.connectionpool").setLevel(logging.CRITICAL)

app = Flask(__name__)

# Dictionary to store the process and URL
processes = {}
# Dictionary to track client connections by IP
client_connections = {}
# Lock for thread-safe access
connection_lock = threading.Lock()

def start_streamlink_http_server(url, use_http=False):
    proxy_url = 'http://192.168.1.123:7086'
    
    # Set environment variables for proxy
    env = os.environ.copy()
    env['HTTP_PROXY'] = proxy_url
    env['HTTPS_PROXY'] = proxy_url
    env['http_proxy'] = proxy_url  # Lowercase fallback
    env['https_proxy'] = proxy_url  # Lowercase fallback
    env['NO_PROXY'] = ''  # Ensure no exclusions bypass the proxy
    env['STREAMLINK_ARGS'] = f'--http-proxy={proxy_url} --https-proxy={proxy_url}'  # Additional safeguard

    # Use HTTP if specified
    stream_url = url.replace("https://", "http://") if use_http and url.startswith("https://") else url

    # Streamlink command
    command = [
        'streamlink',
        '--http-no-ssl-verify',
        '--http-proxy', proxy_url,
        '--hls-live-edge', '10',
        '--hls-segment-stream-data',
        '--hls-live-restart',
        '--stream-timeout', '7200',
        '--retry-streams', '3',
        '--retry-max', '2',
        '--loglevel', 'error',
        stream_url, 'best',
        '-o', '-'
    ]

    print(f"Starting Streamlink for URL: {stream_url} (original: {url}) with proxy: {proxy_url}")
    proc = subprocess.Popen(command, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return proc

def log_stderr(proc, url, client_ip):
    """Log Streamlink's stderr and retry with HTTP on TLS or 502 errors"""
    while True:
        line = proc.stderr.readline()
        if not line:
            break
        decoded = line.decode().strip()
        if "InsecureRequestWarning" not in decoded and "streamlinkdeprecation" not in decoded:
            print(f"Streamlink stderr [URL: {url}]: {decoded}")
            # Check for TLS or 502 errors
            if ("tls" in decoded.lower() or 
                "ssl" in decoded.lower() or 
                "certificate" in decoded.lower() or 
                "502" in decoded.lower()):
                print(f"Error detected for {url}, retrying with HTTP")
                with connection_lock:
                    if 'proc' in processes and processes['url'] == url:
                        stop_streamlink_http_server(processes['proc'], url)
                        del processes['proc']
                        del processes['url']
                        proc = start_streamlink_http_server(url, use_http=True)
                        processes['proc'] = proc
                        processes['url'] = url
                        if client_ip in client_connections:
                            client_connections[client_ip]['url'] = url
                        print(f"Retried with HTTP for client {client_ip} on URL: {url}")
                threading.Thread(target=log_stderr, args=(proc, url, client_ip), daemon=True).start()
                break

def stop_streamlink_http_server(proc, url):
    """Stop the Streamlink process with logging"""
    if proc and proc.poll() is None:
        print(f"Stopping Streamlink process for URL: {url}")
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            print(f"Streamlink process forcefully terminated for URL: {url}")
        except Exception as e:
            print(f"Error stopping process for URL {url}: {e}")

def stream_generator(proc, client_ip, url):
    """Generator to stream data and track client activity"""
    try:
        while True:
            data = proc.stdout.read(1024)
            if not data:
                if proc.poll() is not None:
                    print(f"Streamlink process ended for {client_ip} (URL: {url})")
                    break
                time.sleep(0.5)
                continue
            with connection_lock:
                if client_ip in client_connections:
                    client_connections[client_ip]['active'] = True
            yield data
    except Exception as e:
        print(f"Stream error for {client_ip} (URL: {url}): {e}")
    finally:
        with connection_lock:
            client_connections.pop(client_ip, None)
            if not client_connections and 'proc' in processes and processes['url'] == url:
                print(f"No remaining clients for URL {url}, stopping Streamlink.")
                stop_streamlink_http_server(processes['proc'], url)
                del processes['proc']
                del processes['url']

@app.route('/stream')
def stream():
    url = request.args.get('url')
    client_ip = request.remote_addr
    
    if not url:
        return "No URL provided.", 400
    
    with connection_lock:
        if 'proc' in processes:
            print(f"New URL requested ({url}), stopping process for {processes['url']}")
            stop_streamlink_http_server(processes['proc'], processes['url'])
            del processes['proc']
            del processes['url']
            client_connections.clear()
        
        proc = start_streamlink_http_server(url)
        processes['proc'] = proc
        processes['url'] = url
        client_connections[client_ip] = {'active': True, 'url': url}
        print(f"Client {client_ip} connected to URL: {url}")
        threading.Thread(target=log_stderr, args=(proc, url, client_ip), daemon=True).start()

    return Response(stream_generator(proc, client_ip, url), mimetype='video/mp4')

@app.route('/stop')
def stop():
    with connection_lock:
        if 'proc' in processes:
            stop_streamlink_http_server(processes['proc'], processes['url'])
            del processes['proc']
            del processes['url']
        client_connections.clear()
    
    return "Stream stopped.", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7085)
