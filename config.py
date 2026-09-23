import os

# Storage settings
PERSIST_DIRECTORY = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "historical_defects"

# Similarity Thresholds for Duplicate Detection
DUPLICATE_THRESHOLD_HIGH = 0.82  # Likely Duplicate
DUPLICATE_THRESHOLD_MEDIUM = 0.65  # Related Issue

# Embedding Model Configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"