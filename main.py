from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re
from youtube_transcript_api import YouTubeTranscriptApi
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = FastAPI()

class CaptionRequest(BaseModel):
    url: str

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
    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=['en'])
        transcript_text = ' '.join([item['text'] for item in transcript])
        logging.debug(f"Transcript text: {transcript_text[:100]}...")  # Print first 100 chars
        return transcript_text
    except Exception as e:
        logging.exception(f"Error fetching transcript for video id {vid_id}: {e}")
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
