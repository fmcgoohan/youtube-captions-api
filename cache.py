import shelve
import logging

CACHE_FILENAME = "transcript_cache"

# Open the shelve database; this file will persist across service restarts.
cache = shelve.open(CACHE_FILENAME, writeback=True)

def get_cached_transcript(vid_id: str) -> str:
    """Return the cached transcript for a given video ID, or None if not cached."""
    if vid_id in cache:
        logging.debug(f"Transcript for video {vid_id} retrieved from persistent cache.")
        return cache[vid_id]
    return None

def set_cached_transcript(vid_id: str, transcript_text: str):
    """Cache the transcript for a given video ID and sync to disk."""
    cache[vid_id] = transcript_text
    cache.sync()
