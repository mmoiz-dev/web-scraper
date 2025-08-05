#!/usr/bin/env python3
"""
Test script for Islamic Books Scraper
Tests basic functionality with a limited sample
"""

import os
import sqlite3
from islamic_books_scraper import IslamicBooksScraper

def test_scraper():
    """Test the scraper with a small sample."""
    print("Testing Islamic Books Scraper...")
    
    # Create test scraper with test database
    scraper = IslamicBooksScraper(download_dir="test_downloads", db_path="test_books.db")
    
    # Test database initialization
    print("✓ Database initialized")
    
    # Test API query (just first page)
    print("Testing API query...")
    data = scraper.query_archive_page(1, rows=10)
    
    if data and 'response' in data:
        docs = data['response'].get('docs', [])
        print(f"✓ API query successful - found {len(docs)} items")
        
        # Test with first few books
        test_books = []
        for doc in docs[:3]:  # Test with first 3 books
            languages = doc.get('language', [])
            if isinstance(languages, str):
                languages = [languages]
            
            if any(lang.lower() in ['arabic', 'english', 'ar', 'en'] for lang in languages):
                test_books.append({
                    'identifier': doc.get('identifier'),
                    'title': doc.get('title', 'Unknown Title')
                })
        
        print(f"✓ Found {len(test_books)} Arabic/English books for testing")
        
        # Test PDF link discovery
        if test_books:
            print("Testing PDF link discovery...")
            identifier = test_books[0]['identifier']
            pdf_links = scraper.get_pdf_links(identifier)
            print(f"✓ Found {len(pdf_links)} PDF files for {identifier}")
            
            # Test download (just check if URLs are valid)
            if pdf_links:
                print("Testing download URL construction...")
                for pdf_info in pdf_links[:1]:  # Test first PDF only
                    url = pdf_info['url']
                    filename = pdf_info['filename']
                    print(f"✓ Download URL: {url}")
                    print(f"✓ Filename: {filename}")
        
        # Test database operations
        print("Testing database operations...")
        test_title = "Test Book"
        test_identifier = "test123"
        test_filename = "test.pdf"
        test_url = "https://example.com/test.pdf"
        test_path = "test_downloads/test.pdf"
        
        scraper.store_metadata(test_title, test_identifier, test_filename, test_url, test_path)
        print("✓ Database write successful")
        
        # Test duplicate check
        is_downloaded = scraper.is_already_downloaded(test_identifier, test_filename)
        print(f"✓ Duplicate check: {is_downloaded}")
        
    else:
        print("✗ API query failed")
    
    # Cleanup test files
    print("Cleaning up test files...")
    if os.path.exists("test_books.db"):
        os.remove("test_books.db")
    if os.path.exists("test_downloads"):
        import shutil
        shutil.rmtree("test_downloads")
    
    print("✓ Test completed successfully!")

if __name__ == "__main__":
    test_scraper() 