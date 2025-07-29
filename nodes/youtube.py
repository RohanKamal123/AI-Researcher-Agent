from nodes.base import BaseNode
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

class YouTubeFetcher(BaseNode):
    def __init__(self):
        super().__init__("YouTubeFetcher")

    async def execute(self, store):
        video_id = store.get("processed_input")
        if not video_id:
            print("Error: No video ID found in store for YouTubeFetcher.")
            store.set("error", "No YouTube video ID provided.")
            return "error"

        print(f"Attempting to fetch transcript for video ID: {video_id}")
        try:
            # This is the crucial line:
            yt_api_instance = YouTubeTranscriptApi()
            transcript_list = yt_api_instance.fetch(video_id)
            full_transcript = " ".join([item.text for item in transcript_list])
            store.set("transcript", full_transcript)
            print(f"Successfully fetched transcript for {video_id}. Length: {len(full_transcript)} characters.")
            return "success"

        except NoTranscriptFound:
            print(f"Error: No transcript found for video ID: {video_id}.")
            store.set("error", f"No transcript found for video ID: {video_id}.")
            return "no_transcript_found"
        except TranscriptsDisabled:
            print(f"Error: Transcripts are disabled for video ID: {video_id}.")
            store.set("error", f"Transcripts are disabled for video ID: {video_id}.")
            return "transcripts_disabled"
        except Exception as e:
            print(f"An unexpected error occurred while fetching transcript: {e}")
            store.set("error", f"Failed to fetch transcript: {e}")
            return "fetch_failed"