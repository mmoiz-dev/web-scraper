#!/usr/bin/env python3
"""
Islamic Books Scraper for Internet Archive
Downloads Islamic books in Arabic and English from archive.org
"""

import requests
import sqlite3
import os
import time
import json
from urllib.parse import urljoin, urlparse
from pathlib import Path
import logging

# Import configuration
try:
    from config import *
except ImportError:
    # Default configuration if config.py doesn't exist
    SEARCH_QUERY = "Islamic books"
    LANGUAGES = ["Arabic", "English", "ar", "en"]
    ROWS_PER_PAGE = 100
    DOWNLOAD_DIR = "downloads"
    DATABASE_PATH = "books.db"
    BASE_URL = "https://archive.org/advancedsearch.php"
    METADATA_BASE_URL = "https://archive.org/metadata"
    DOWNLOAD_BASE_URL = "https://archive.org/download"
    API_DELAY = 1
    BOOK_PROCESSING_DELAY = 2
    DOWNLOAD_TIMEOUT = 60
    CHUNK_SIZE = 8192
    PROGRESS_UPDATE_INTERVAL = 1024 * 1024
    LOG_LEVEL = "INFO"
    LOG_FILE = "scraper.log"
    PDF_EXTENSIONS = ['.pdf']

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class IslamicBooksScraper:
    def __init__(self, download_dir=DOWNLOAD_DIR, db_path=DATABASE_PATH):
        self.base_url = BASE_URL
        self.download_dir = Path(download_dir)
        self.db_path = db_path
        self.session = requests.Session()
        
        # Create download directory if it doesn't exist
        self.download_dir.mkdir(exist_ok=True)
        
        # Initialize database
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite database with downloads table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                identifier TEXT UNIQUE,
                file_name TEXT,
                download_url TEXT,
                local_path TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Database initialized: {self.db_path}")
    
    def query_archive_page(self, page_number, rows=ROWS_PER_PAGE):
        """Query Internet Archive's Advanced Search API for a specific page."""
        params = {
            'q': SEARCH_QUERY,
            'fl[]': ['identifier', 'title', 'language'],
            'output': 'json',
            'rows': rows,
            'page': page_number,
            'sort[]': 'downloads desc'
        }
        
        try:
            response = self.session.get(self.base_url, params=params, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error querying page {page_number}: {e}")
            return None
    
    def get_all_books(self):
        """Fetch all books using pagination."""
        all_books = []
        page = 1
        total_results = None
        max_pages = 100  # Limit to prevent infinite loops
        consecutive_errors = 0
        max_consecutive_errors = 3
        
        logger.info("Starting to fetch all Islamic books...")
        
        while page <= max_pages:
            logger.info(f"Fetching page {page}...")
            data = self.query_archive_page(page)
            
            if not data or 'response' not in data:
                logger.error(f"Invalid response for page {page}")
                consecutive_errors += 1
                if consecutive_errors >= max_consecutive_errors:
                    logger.error(f"Too many consecutive errors, stopping at page {page}")
                    break
                page += 1
                time.sleep(API_DELAY * 2)  # Longer delay on errors
                continue
            
            consecutive_errors = 0  # Reset error counter on success
            
            docs = data['response'].get('docs', [])
            if not docs:
                logger.info("No more results found")
                break
            
            # Get total results count on first page
            if total_results is None:
                total_results = data['response'].get('numFound', 0)
                logger.info(f"Total results found: {total_results}")
            
            # Filter for specified languages
            page_books = 0
            for doc in docs:
                languages = doc.get('language', [])
                if isinstance(languages, str):
                    languages = [languages]
                
                # Check if book is in specified languages
                if any(lang.lower() in [lang.lower() for lang in LANGUAGES] for lang in languages):
                    all_books.append({
                        'identifier': doc.get('identifier'),
                        'title': doc.get('title', 'Unknown Title')
                    })
                    page_books += 1
            
            logger.info(f"Page {page}: Found {len(docs)} items, filtered to {page_books} {', '.join(LANGUAGES)} books")
            
            page += 1
            time.sleep(API_DELAY)  # Be respectful to the API
        
        logger.info(f"Total {', '.join(LANGUAGES)} Islamic books found: {len(all_books)}")
        return all_books
    
    def get_pdf_links(self, identifier):
        """Get PDF file links for a given identifier."""
        pdf_urls = []
        
        try:
            # Try to get file list from metadata API
            metadata_url = f"{METADATA_BASE_URL}/{identifier}"
            response = self.session.get(metadata_url, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            metadata = response.json()
            files = metadata.get('files', {})
            
            # Handle both dict and list formats for files
            if isinstance(files, dict):
                for filename, file_info in files.items():
                    if any(filename.lower().endswith(ext) for ext in PDF_EXTENSIONS):
                        pdf_url = f"{DOWNLOAD_BASE_URL}/{identifier}/{filename}"
                        pdf_urls.append({
                            'url': pdf_url,
                            'filename': filename,
                            'size': file_info.get('size', 0) if isinstance(file_info, dict) else 0
                        })
            elif isinstance(files, list):
                # Handle list format
                for file_info in files:
                    if isinstance(file_info, dict):
                        filename = file_info.get('name', '')
                        if any(filename.lower().endswith(ext) for ext in PDF_EXTENSIONS):
                            pdf_url = f"{DOWNLOAD_BASE_URL}/{identifier}/{filename}"
                            pdf_urls.append({
                                'url': pdf_url,
                                'filename': filename,
                                'size': file_info.get('size', 0)
                            })
            
            # If no PDFs found in metadata, try scraping the download page
            if not pdf_urls:
                download_page_url = f"{DOWNLOAD_BASE_URL}/{identifier}/"
                response = self.session.get(download_page_url, timeout=DOWNLOAD_TIMEOUT)
                
                if response.status_code == 200:
                    # Simple HTML parsing to find PDF links
                    content = response.text
                    import re
                    pdf_pattern = r'href="([^"]*\.pdf)"'
                    pdf_matches = re.findall(pdf_pattern, content, re.IGNORECASE)
                    
                    for pdf_match in pdf_matches:
                        if pdf_match.startswith('/'):
                            pdf_url = f"https://archive.org{pdf_match}"
                        else:
                            pdf_url = urljoin(download_page_url, pdf_match)
                        
                        filename = os.path.basename(pdf_match)
                        if any(filename.lower().endswith(ext) for ext in PDF_EXTENSIONS):
                            pdf_urls.append({
                                'url': pdf_url,
                                'filename': filename,
                                'size': 0  # Unknown size
                            })
            
        except requests.RequestException as e:
            logger.error(f"Error getting PDF links for {identifier}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error getting PDF links for {identifier}: {e}")
        
        return pdf_urls
    
    def is_already_downloaded(self, identifier, filename):
        """Check if a file is already downloaded and logged in database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT local_path FROM downloads 
            WHERE identifier = ? AND file_name = ?
        ''', (identifier, filename))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            local_path = result[0]
            return os.path.exists(local_path)
        
        return False
    
    def download_pdf(self, url, filename, identifier):
        """Download a PDF file with streaming."""
        local_path = self.download_dir / filename
        
        try:
            logger.info(f"Downloading: {filename}")
            response = self.session.get(url, stream=True, timeout=DOWNLOAD_TIMEOUT)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Progress update for large files
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            if downloaded_size % PROGRESS_UPDATE_INTERVAL == 0:  # Every MB
                                logger.info(f"Downloaded {downloaded_size}/{total_size} bytes ({progress:.1f}%)")
            
            logger.info(f"Successfully downloaded: {filename}")
            return str(local_path)
            
        except requests.RequestException as e:
            logger.error(f"Error downloading {filename}: {e}")
            # Clean up partial download
            if local_path.exists():
                local_path.unlink()
            return None
    
    def store_metadata(self, title, identifier, filename, download_url, local_path):
        """Store download metadata in SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO downloads 
                (title, identifier, file_name, download_url, local_path)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, identifier, filename, download_url, local_path))
            
            conn.commit()
            logger.info(f"Stored metadata for {filename}")
            
        except sqlite3.Error as e:
            logger.error(f"Database error storing metadata for {filename}: {e}")
        finally:
            conn.close()
    
    def process_book(self, book_info):
        """Process a single book: get PDFs, download them, and store metadata."""
        identifier = book_info['identifier']
        title = book_info['title']
        
        # Handle Unicode titles safely
        try:
            safe_title = title.encode('utf-8', errors='ignore').decode('utf-8')
            logger.info(f"Processing book: {safe_title} ({identifier})")
        except Exception as e:
            logger.info(f"Processing book: [Title encoding error] ({identifier})")
        
        try:
            pdf_links = self.get_pdf_links(identifier)
            
            if not pdf_links:
                logger.warning(f"No PDF files found for {identifier}")
                return
            
            downloaded_count = 0
            skipped_count = 0
            
            for pdf_info in pdf_links:
                filename = pdf_info['filename']
                download_url = pdf_info['url']
                
                # Check if already downloaded
                if self.is_already_downloaded(identifier, filename):
                    logger.info(f"Skipping {filename} - already downloaded")
                    skipped_count += 1
                    continue
                
                # Download the PDF
                local_path = self.download_pdf(download_url, filename, identifier)
                
                if local_path:
                    # Store metadata in database
                    self.store_metadata(title, identifier, filename, download_url, local_path)
                    downloaded_count += 1
                else:
                    logger.error(f"Failed to download {filename}")
            
            logger.info(f"Book {identifier}: Downloaded {downloaded_count}, Skipped {skipped_count}")
            
        except Exception as e:
            logger.error(f"Error processing book {identifier}: {e}")
            # Continue with next book instead of crashing
    
    def run(self):
        """Main method to run the complete scraping process."""
        logger.info("Starting Islamic Books Scraper")
        
        # Get all books
        books = self.get_all_books()
        
        if not books:
            logger.error("No books found")
            return
        
        total_books = len(books)
        processed_count = 0
        
        logger.info(f"Processing {total_books} books...")
        
        try:
            for book_info in books:
                processed_count += 1
                logger.info(f"Processing book {processed_count} of {total_books} ({(processed_count/total_books)*100:.1f}%)")
                
                try:
                    self.process_book(book_info)
                except Exception as e:
                    logger.error(f"Error processing book {book_info['identifier']}: {e}")
                
                # Be respectful to the server
                time.sleep(BOOK_PROCESSING_DELAY)
                
        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user. Progress saved.")
        
        logger.info("Scraping completed!")
        
        # Print final statistics
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM downloads")
        total_downloads = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"Total files downloaded and logged: {total_downloads}")


def main():
    """Main function to run the scraper."""
    scraper = IslamicBooksScraper()
    scraper.run()


if __name__ == "__main__":
    main() 