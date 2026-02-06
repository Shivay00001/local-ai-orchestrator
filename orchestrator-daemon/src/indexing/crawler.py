import os
import pathspec
from typing import List, Generator

def load_gitignore_spec(root_path: str) -> pathspec.PathSpec:
    gitignore_path = os.path.join(root_path, ".gitignore")
    patterns = []
    
    # Defaults
    patterns.append(".git/")
    patterns.append("__pycache__/")
    patterns.append(".env")
    patterns.append("node_modules/")
    patterns.append("target/") # Rust
    patterns.append("dist/")
    patterns.append("build/")
    
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8") as f:
                patterns.extend(f.readlines())
        except Exception:
            pass
            
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)

def crawl_project(root_path: str) -> Generator[str, None, None]:
    """
    Yields absolute file paths that are NOT ignored.
    """
    spec = load_gitignore_spec(root_path)
    
    for root, dirs, files in os.walk(root_path):
        # Filter directories in-place to prevent recursion into ignored dirs
        dirs[:] = [d for d in dirs if not spec.match_file(os.path.join(os.path.relpath(os.path.join(root, d), root_path)))]
        
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, root_path)
            
            if not spec.match_file(rel_path):
                yield abs_path
