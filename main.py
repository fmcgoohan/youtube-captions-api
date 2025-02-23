import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from utils import monkey_patch_requests, extract_video_id
from youtube import get_transcript
from cache import cache  # import the global shelve instance

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create FastAPI app and add GZip middleware for response compression
app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Apply the monkey-patch to requests
monkey_patch_requests()

# Pydantic model for incoming caption requests
class CaptionRequest(BaseModel):
    url: str
    force: bool = False  # Parameter to force cache overwrite

@app.post("/captions")
async def get_captions(request: CaptionRequest):
    vid_id = extract_video_id(request.url)
    if not vid_id:
        raise HTTPException(status_code=400, detail="Invalid URL")
    
    captions = get_transcript(vid_id, force=request.force)
    if captions:
        return {"status": True, "captions": captions}
    else:
        return {"status": False, "message": "No captions available. Check logs for details."}

@app.on_event("shutdown")
def shutdown_event():
    # Close the shelve to flush all cached data to disk
    cache.close()
    logging.debug("Persistent cache closed on shutdown.")
