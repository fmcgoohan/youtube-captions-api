import re
import requests
import logging

def monkey_patch_requests():
    """Monkey-patch requests.get to use a browser-like User-Agent."""
    original_get = requests.get

    def custom_get(url, **kwargs):
        headers = kwargs.get("headers", {})
        headers.setdefault(
            "User-Agent",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/115.0 Safari/537.36"
        )
        kwargs["headers"] = headers
        return original_get(url, **kwargs)

    requests.get = custom_get

def get_public_ip():
    """Query an external service to get the public IP address."""
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
        if response.status_code == 200:
            ip = response.json().get("ip", "unknown")
            logging.debug(f"Public IP: {ip}")
            return ip
        else:
            logging.error(f"Failed to get public IP, status code: {response.status_code}")
    except Exception as e:
        logging.exception("Error while retrieving public IP")
    return "unknown"

def extract_video_id(url: str) -> str:
    """Extract the YouTube video ID from a URL."""
    patterns = [
        r'v=([\w-]+)',         # Matches v=video_id
        r'/v/([\w-]+)',        # Matches /v/video_id
        r'youtu\.be/([\w-]+)',  # Matches youtu.be/video_id
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            logging.debug(f"Extracted video id: {video_id}")
            return video_id
    logging.error("Could not extract video id from URL")
    return None
