from dataclasses import dataclass
from typing import List

@dataclass
class TextChunk:
    filepath: str
    content: str
    start_line: int
    end_line: int

def chunk_file(filepath: str, max_tokens: int = 500, overlap: int = 50) -> List[TextChunk]:
    """
    Splits file content into chunks.
    Naive Line-based chunking for now (approx 1 line = 10 tokens).
    Future: Use a real tokenizer.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        return [] # Skip binary files
    except Exception:
        return []

    chunks = []
    
    # Heuristic: ~50 lines per chunk (~500 tokens)
    LINES_PER_CHUNK = 50
    OVERLAP_LINES = 5
    
    total_lines = len(lines)
    
    for i in range(0, total_lines, LINES_PER_CHUNK - OVERLAP_LINES):
        end = min(i + LINES_PER_CHUNK, total_lines)
        chunk_lines = lines[i:end]
        content = "".join(chunk_lines)
        
        if not content.strip():
            continue
            
        chunks.append(TextChunk(
            filepath=filepath,
            content=content,
            start_line=i + 1,
            end_line=end
        ))
        
        if end == total_lines:
            break
            
    return chunks
