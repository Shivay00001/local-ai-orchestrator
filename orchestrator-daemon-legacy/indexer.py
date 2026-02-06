import os
import pathspec
from typing import List, Dict

class ProjectIndexer:
    def __init__(self, root_path: str):
        self.root_path = root_path
        self.ignore_spec = self._load_gitignore()

    def _load_gitignore(self):
        ignore_patterns = [
            '.git/', 'node_modules/', '__pycache__/', 
            '*.pyc', '.venv/', 'dist/', 'build/', '.DS_Store'
        ]
        gitignore_path = os.path.join(self.root_path, '.gitignore')
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                ignore_patterns.extend(f.readlines())
        
        return pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns)

    def scan_project(self) -> List[Dict]:
        """Scans the project and returns a list of file details."""
        files_to_index = []
        for root, dirs, files in os.walk(self.root_path):
            # Filter directories in-place
            rel_root = os.path.relpath(root, self.root_path)
            if rel_root == '.':
                rel_root = ''
            
            dirs[:] = [d for d in dirs if not self.ignore_spec.match_file(os.path.join(rel_root, d))]
            
            for file in files:
                rel_path = os.path.join(rel_root, file)
                if not self.ignore_spec.match_file(rel_path):
                    full_path = os.path.join(root, file)
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if content.strip():
                                files_to_index.append({
                                    "path": rel_path,
                                    "content": content,
                                    "extension": os.path.splitext(file)[1]
                                })
                    except Exception as e:
                        print(f"Failed to read {rel_path}: {e}")
        
        return files_to_index

    @staticmethod
    def chunk_content(content: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple sliding window chunking."""
        chunks = []
        if not content:
            return chunks
        
        start = 0
        while start < len(content):
            end = start + chunk_size
            chunks.append(content[start:end])
            start += chunk_size - overlap
        return chunks
