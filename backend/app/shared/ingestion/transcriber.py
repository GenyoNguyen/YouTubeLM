"""Audio transcription using GroqCloud Whisper API."""

import os
from typing import List, Dict, Any
from groq import Groq


def transcribe_audio(
    audio_path: str,
    api_key: str,
    model: str = "whisper-large-v3-turbo"
) -> Dict[str, Any]:
    """
    Transcribe audio file using GroqCloud Whisper API.
    
    Returns:
        Dict with keys: text, segments (list of dicts with start, end, text)
    """
    client = Groq(api_key=api_key)
    
    with open(audio_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            file=audio_file,
            model=model,
            response_format="verbose_json",
            # timestamp_granularities=["word"],
        )
        print(transcript)
    
    # Extract segments with timestamps
    segments = []
    if hasattr(transcript, 'words') and transcript.words:
        current_segment = {
            'start': transcript.words[0].start,
            'end': transcript.words[0].end,
            'text': transcript.words[0].word,
        }
        
        for word in words[1:]:
            # Group words into segments (roughly by sentence or time gap)
            time_gap = word.start - current_segment['end']
            if time_gap > 2.0:  # New segment if gap > 2 seconds
                segments.append(current_segment)
                current_segment = {
                    'start': word.start,
                    'end': word.end,
                    'text': word.word,
                }
            else:
                current_segment['end'] = word.end
                current_segment['text'] += ' ' + word.word
        
        if current_segment:
            segments.append(current_segment)
    else:
        # Fallback: single segment with full text
        full_text = transcript.text if hasattr(transcript, 'text') else str(transcript)
        segments = [{
            'start': 0.0,
            'end': 0.0,
            'text': full_text,
        }]
    
    return {
        'text': transcript.text if hasattr(transcript, 'text') else str(transcript),
        'segments': segments,
    }

