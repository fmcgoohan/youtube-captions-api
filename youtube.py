import logging
from youtube_transcript_api import YouTubeTranscriptApi
from utils import get_public_ip
from cache import get_cached_transcript, set_cached_transcript

def get_transcript(vid_id: str, force: bool = False) -> str:
    """
    Retrieve the transcript for a video.
    If `force` is False, first check the persistent cache.
    Otherwise, fetch a fresh transcript and update the cache.
    """
    if not force:
        cached = get_cached_transcript(vid_id)
        if cached is not None:
            return cached

    public_ip = get_public_ip()
    logging.debug(f"Attempting to fetch transcript for video {vid_id} from IP {public_ip}")

    try:
        transcript = YouTubeTranscriptApi.get_transcript(vid_id, languages=['en'])
        transcript_text = ' '.join([item['text'] for item in transcript])
        set_cached_transcript(vid_id, transcript_text)
        logging.debug(f"Transcript text: {transcript_text[:100]}...")
        return transcript_text
    except Exception as e:
        logging.exception(f"Error fetching transcript for video {vid_id}: {e}")
        return None
