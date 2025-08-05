#!/usr/bin/env python3
"""
Configuration file for Islamic Books Scraper
Modify these settings to customize the scraper behavior
"""

# Search Configuration
SEARCH_QUERY = "Islamic books"
LANGUAGES = ["Arabic", "English", "ar", "en"]
ROWS_PER_PAGE = 100

# Download Configuration
DOWNLOAD_DIR = "downloads"
DATABASE_PATH = "books.db"

# API Configuration
BASE_URL = "https://archive.org/advancedsearch.php"
METADATA_BASE_URL = "https://archive.org/metadata"
DOWNLOAD_BASE_URL = "https://archive.org/download"

# Rate Limiting (in seconds)
API_DELAY = 1  # Delay between API requests
BOOK_PROCESSING_DELAY = 2  # Delay between processing books

# Download Configuration
DOWNLOAD_TIMEOUT = 60  # Timeout for download requests
CHUNK_SIZE = 8192  # Chunk size for streaming downloads
PROGRESS_UPDATE_INTERVAL = 1024 * 1024  # Update progress every MB

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "scraper.log"

# File Extensions to Download
PDF_EXTENSIONS = ['.pdf']

# Database Schema
DATABASE_SCHEMA = '''
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    identifier TEXT UNIQUE,
    file_name TEXT,
    download_url TEXT,
    local_path TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''' 