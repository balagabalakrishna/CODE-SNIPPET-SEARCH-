import json
import os
import time
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
import datetime
import streamlit as st
# Add at the very top (with other imports)
from functools import lru_cache
import time  # Add if not already present
# Configuration
PROCESSED_DIR = "data/processed"
EMBEDDINGS_PATH = os.path.join(PROCESSED_DIR, "embeddings.faiss")
METADATA_PATH = os.path.join(PROCESSED_DIR, "metadata.json")
TIMESTAMP_PATH = os.path.join(PROCESSED_DIR, "timestamps.txt")

# Add right after imports, before class definitions
@lru_cache(maxsize=1)
def get_embedding_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def get_snippets_file():
    """Returns the correct path to snippets.json"""
    return Path.home() / "code-snippet-search" / "data" / "snippets.json"

def save_snippet_to_file(new_snippet):
    """Atomic save operation that works on Windows"""
    DATA_FILE = get_snippets_file()
    try:
        # 1. Ensure directory exists
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        # 2. Load existing data
        snippets = []
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                snippets = json.load(f)
        
        # 3. Add new snippet
        snippets.append(new_snippet)
        
        # 4. Write to temporary file first
        temp_path = DATA_FILE.with_suffix('.tmp')
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False)
        
        # 5. Atomic replace
        temp_path.replace(DATA_FILE)
        return True
        
    except Exception as e:
        st.error(f"💾 Save failed: {type(e).__name__}: {str(e)}")
        if 'temp_path' in locals() and temp_path.exists():
            temp_path.unlink()
        return False

class Preprocessor:
    def __init__(self):
        os.makedirs(PROCESSED_DIR, exist_ok=True)
        self.model = get_embedding_model()  # Use cached version
        self._load_or_create_index()  # Add this line
        
        # Keep your existing initialization code if any
        self.last_processed = 0
        self.index = None
        self.metadata = []

    def _load_or_create_index(self):  # Add this new method
        """Optimized index loading/creation"""
        if all(os.path.exists(p) for p in [EMBEDDINGS_PATH, METADATA_PATH]):
            try:
                self.index = faiss.read_index(EMBEDDINGS_PATH)
                with open(METADATA_PATH, 'r') as f:
                    self.metadata = json.load(f)
                return
            except Exception as e:
                print(f"Failed to load index: {e}")
                
        if os.path.exists(get_snippets_file()):
            self.process_data()
        
    def needs_processing(self):
        """Check if raw data is newer than processed data"""
        if not os.path.exists(get_snippets_file()):
            return False
            
        if not all(os.path.exists(p) for p in [EMBEDDINGS_PATH, METADATA_PATH, TIMESTAMP_PATH]):
            return True
            
        with open(TIMESTAMP_PATH) as f:
            last_processed = float(f.read())
            
        return os.path.getmtime(get_snippets_file()) > last_processed
        
    def load_processed_data(self):
        """Load processed data if available"""
        if os.path.exists(EMBEDDINGS_PATH):
            self.index = faiss.read_index(EMBEDDINGS_PATH)
        if os.path.exists(METADATA_PATH):
            with open(METADATA_PATH, 'r') as f:
                self.metadata = json.load(f)
                
    def get_metadata(self):
        """Get current metadata"""
        return self.metadata
        
    def process_data(self):
        """Process raw data and save embeddings + metadata"""
        try:
            with open(get_snippets_file(), 'r', encoding='utf-8') as f:
                snippets = json.load(f)
            
            # Prepare data for embedding
            texts = []
            metadata = []
            for idx, snippet in enumerate(snippets):
                text = f"{snippet['title']} {snippet['code']} {' '.join(snippet.get('tags', []))}"
                texts.append(text)
                metadata.append({
                    'id': idx,
                    'title': snippet['title'],
                    'tags': snippet.get('tags', []),
                    'code': snippet['code'],
                    'language': snippet.get('language', ''),
                    'full_code': snippet['code']  # Store full code for display
                })
            
            # Generate embeddings
            embeddings = self.model.encode(texts, show_progress_bar=False)
            
            # Create FAISS index
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
            self.index.add(embeddings)
            self.metadata = metadata
            
            # Save processed data
            faiss.write_index(self.index, EMBEDDINGS_PATH)
            with open(METADATA_PATH, 'w') as f:
                json.dump(metadata, f)
            with open(TIMESTAMP_PATH, 'w') as f:
                f.write(str(time.time()))
            
            self.last_processed = time.time()
            print(f"Processed {len(snippets)} snippets")
            return True
            
        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            return False
    
    def search(self, query, top_k=5):
        """Search for similar snippets"""
        if self.index is None:
            self.load_processed_data()
            
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in range(top_k):
            if indices[0][i] >= 0:  # Valid index
                result = self.metadata[indices[0][i]]
                result['score'] = float(distances[0][i])
                results.append(result)
        
        return results

class FileWatcher:
    def __init__(self, preprocessor):
        self.preprocessor = preprocessor
        self.observer = Observer()
        
    def run(self):
        event_handler = OptimizedHandler(self.preprocessor)  # Changed to use OptimizedHandler
        self.observer.schedule(event_handler, path=get_snippets_file().parent)
        self.observer.start()
        print(f"Watching for changes in {get_snippets_file()}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()
class OptimizedHandler(FileSystemEventHandler):
    def __init__(self, preprocessor):
        super().__init__()
        self.preprocessor = preprocessor
        self.last_modified = 0  # Tracks last processing time
        
    def on_modified(self, event):
        """Only trigger processing if:
        1. The modified file is snippets.json
        2. At least 30 seconds since last processing
        3. Actually needs processing"""
        
        # 1. Check if right file was modified
        if not event.src_path.endswith(str(get_snippets_file())):
            return
            
        current_time = time.time()
        
        # 2. Debounce check (30-second cooldown)
        if current_time - self.last_modified < 30:
            return
            
        self.last_modified = current_time
        
        # 3. Needs processing check
        if self.preprocessor.needs_processing():
            print("Detected valid changes - processing snippets...")
            self.preprocessor.process_data()

def initialize_preprocessor():
    """Initialize and return preprocessor with loaded data"""
    preprocessor = Preprocessor()
    if preprocessor.needs_processing():
        preprocessor.process_data()
    else:
        preprocessor.load_processed_data()
    return preprocessor
def init_preprocessor():
    """Automatically initialize and process data"""
    preprocessor = Preprocessor()
    if preprocessor.needs_processing():
        preprocessor.process_data()
    return preprocessor

# This will run automatically when imported
preprocessor = init_preprocessor()

# ===== ADD THIS RIGHT HERE =====
def get_auto_preprocessor():
    """For Streamlit Cloud - always ensure fresh embeddings"""
    preprocessor = Preprocessor()
    if preprocessor.needs_processing():
        preprocessor.process_data()
    return preprocessor

# Auto-initialize when imported
preprocessor = get_auto_preprocessor()
if __name__ == "__main__":
    # Test initialization
    preprocessor = Preprocessor()
    
    # Start watcher with optimized handler
    watcher = FileWatcher(preprocessor)
    try:
        watcher.run()
    except KeyboardInterrupt:
        print("Stopping file watcher...")