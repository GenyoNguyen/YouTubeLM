"""Text chunking utilities."""

from typing import List, Dict, Any


def chunk_transcript(
    segments: List[Dict[str, Any]],
    window_size: int = 60,
    overlap: int = 10
) -> List[Dict[str, Any]]:
    """
    Chunk transcript into time windows.
    
    Args:
        segments: List of segments with start, end, text
        window_size: Chunk size in seconds
        overlap: Overlap between chunks in seconds
    
    Returns:
        List of chunks with start_time, end_time, text
    """
    if not segments:
        return []
    
    chunks = []
    current_start = segments[0]['start']
    current_text = []
    current_end = current_start
    
    for segment in segments:
        segment_start = segment['start']
        segment_end = segment['end']
        segment_text = segment['text']
        
        # If adding this segment would exceed window, create a chunk
        if segment_end - current_start > window_size:
            if current_text:
                chunks.append({
                    'start_time': current_start,
                    'end_time': current_end,
                    'text': ' '.join(current_text),
                })
            
            # Start new chunk with overlap
            overlap_start = max(current_start, current_end - overlap)
            # Find segments that overlap with the overlap window
            current_text = []
            current_start = overlap_start
            current_end = overlap_start
        
        current_text.append(segment_text)
        current_end = segment_end
    
    # Add final chunk
    if current_text:
        chunks.append({
            'start_time': current_start,
            'end_time': current_end,
            'text': ' '.join(current_text),
        })
    
    return chunks

