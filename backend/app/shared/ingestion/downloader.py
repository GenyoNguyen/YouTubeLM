"""YouTube video downloader."""

import os
import yt_dlp
from pathlib import Path
from typing import Optional, Dict, Any
import re


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from URL."""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from URL: {url}")


def download_video(video_url: str, output_dir: str) -> Dict[str, Any]:
    """
    Download YouTube video audio and extract metadata.
    
    Returns:
        Dict with keys: video_id, title, duration, audio_path
    """
    video_id = extract_video_id(video_url)
    output_path = Path(output_dir) / f"{video_id}.%(ext)s"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_path),
        'extractaudio': True,
        'audioformat': 'wav',
        'quiet': True,
        'no_warnings': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Extract info
        info = ydl.extract_info(video_url, download=False)
        title = info.get('title', '')
        duration = info.get('duration', 0)
        
        # Download
        ydl.download([video_url])
    
    # Find the downloaded file
    audio_path = None
    for ext in ['wav', 'm4a', 'webm', 'mp3']:
        potential_path = Path(output_dir) / f"{video_id}.{ext}"
        if potential_path.exists():
            audio_path = str(potential_path)
            break
    
    if not audio_path:
        raise FileNotFoundError(f"Downloaded audio file not found for {video_id}")
    
    return {
        'video_id': video_id,
        'title': title,
        'duration': duration,
        'audio_path': audio_path,
        'url': video_url,
    }

