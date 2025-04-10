from mitmproxy import http
import re
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def request(flow: http.HTTPFlow) -> None:
    # Update headers to optimize for streaming
    flow.request.headers.update({
        "Referer": "https://ok.ru/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",  # Removed 'zstd'
        "Origin": "https://ok.ru",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    })

    # Check if the request URL is a decryption key request
    if "wmsxx.php" in flow.request.pretty_url:
        # Extract channel number from the query or Referer URL
        referer = flow.request.headers.get("Referer", "")
        match = re.search(r"premium(\d+)", referer)
        if match:
            channel_number = match.group(1)
            # Modify the query parameters in the request URL
            parsed_url = urlparse(flow.request.url)
            query_params = parse_qs(parsed_url.query)
            if 'name' in query_params:
                query_params['name'] = [f"premium{channel_number}"]
            new_query = urlencode(query_params, doseq=True)
            new_url = urlunparse(parsed_url._replace(query=new_query))
            flow.request.url = new_url

def response(flow: http.HTTPFlow) -> None:
    if "wmsxx.php" in flow.request.pretty_url:
        # Check if the response has an error status code
        if flow.response.status_code in {403, 503, 502}:
            # Log the error for debugging
            print(f"Error {flow.response.status_code} detected. Retrying with updated headers.")

            # Retry the request with new Referer and Origin
            flow.request.headers.update({
                "Referer": "https://vk.ru/",
                "Origin": "https://vk.ru"
            })

            # Replay the modified request
            flow.response = None  # Clear the current response
            flow.intercept()      # Mark for replay
            flow.resume()         # Resume the flow to resend the request

addons = [
    request,
    response
]
