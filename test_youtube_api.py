from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

video_id = "cTD6I4nWWIo" # The video ID from your last attempt

print(f"Attempting to fetch transcript for video ID: {video_id} using standalone script.")
try:
    # Corrected: Pass video_id as a positional argument, not a keyword argument 'video_ids'
    yt_api_instance = YouTubeTranscriptApi()
    transcript_list = yt_api_instance.fetch(video_id)
    full_transcript = " ".join([item['text'] for item in transcript_list])
    print(f"SUCCESS: Transcript fetched successfully. Length: {len(full_transcript)} characters.")
    # print("First 200 characters of transcript:")
    # print(full_transcript[:200]) # Uncomment to see part of the transcript
except NoTranscriptFound:
    print(f"ERROR: No transcript found for video ID: {video_id}.")
except TranscriptsDisabled:
    print(f"ERROR: Transcripts are disabled for video ID: {video_id}.")
except Exception as e:
    print(f"UNEXPECTED ERROR: {e}")

