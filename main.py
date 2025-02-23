from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from youtube_transcript_api import YouTubeTranscriptApi

app = FastAPI()

# Define the request body model
class CaptionRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    """
    Extracts the video ID from a YouTube URL.
    Supports formats like:
    - https://www.youtube.com/watch?v=video_id
    - https://www.youtube.com/v/video_id
    - https://youtu.be/video_id
    """
    patterns = [
        r'v=([\w-]+)',         # Matches v=video_id
        r'/v/([\w-]+)',        # Matches /v/video_id
        r'youtu\.be/([\w-]+)',  # Matches youtu.be/video_id
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(vid_id: str) -> str:
    """
    Retrieves English captions for a given video ID using youtube-transcript-api.
    Returns the concatenated text or None if no captions are available.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=['en'])
        transcript_text = ' '.join([item['text'] for item in transcript])
        return transcript_text
    except Exception:
        # Handles cases like TranscriptsDisabled or NoTranscriptFound
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
        return {"status": False, "message": "No captions available"}
