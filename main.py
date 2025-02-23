import requests
import logging
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

class CaptionRequest(BaseModel):
    url: str

# Monkey-patch requests.get to add a browser-like User-Agent
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
        response = original_get("https://api.ipify.org?format=json", timeout=5)
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

def get_transcript(vid_id: str) -> str:
    # Log the public IP address for diagnostic purposes
    public_ip = get_public_ip()
    logging.debug(f"Attempting to fetch transcript for video {vid_id} from IP {public_ip}")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=['en'])
        transcript_text = ' '.join([item['text'] for item in transcript])
        logging.debug(f"Transcript text: {transcript_text[:100]}...")
        return transcript_text
    except Exception as e:
        # Log more details: try to capture any response content if available
        logging.exception(f"Error fetching transcript for video {vid_id}: {e}")
        return None

@app.post("/captions")
async def get_captions(request: CaptionRequest):
    vid_id = extract_video_id(request.url)
    if not vid_id:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    captions = get_transcript(vid_id)
    if captions:
        return {"status": True, "captions": captions}
    else:
        # Return a more detailed message in case of failure
        return {"status": False, "message": "No captions available. Check logs for details."}
