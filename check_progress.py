#!/usr/bin/env python3
"""
Check Progress Script for Islamic Books Scraper
Shows current progress and statistics
"""

import sqlite3
import os
from pathlib import Path

def check_progress():
    """Check the current progress of the scraper."""
    db_path = "books.db"
    download_dir = Path("downloads")
    
    print("=== Islamic Books Scraper Progress Report ===\n")
    
    # Check database
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get total downloads
        cursor.execute("SELECT COUNT(*) FROM downloads")
        total_downloads = cursor.fetchone()[0]
        
        # Get unique books
        cursor.execute("SELECT COUNT(DISTINCT identifier) FROM downloads")
        unique_books = cursor.fetchone()[0]
        
        # Get total file size (calculate from actual files)
        total_size = 0
        cursor.execute("SELECT local_path FROM downloads")
        local_paths = cursor.fetchall()
        for (local_path,) in local_paths:
            if os.path.exists(local_path):
                total_size += os.path.getsize(local_path)
        
        # Get recent downloads
        cursor.execute("""
            SELECT title, identifier, file_name, created_at 
            FROM downloads 
            ORDER BY created_at DESC 
            LIMIT 5
        """)
        recent_downloads = cursor.fetchall()
        
        conn.close()
        
        print(f"📊 Database Statistics:")
        print(f"   Total files downloaded: {total_downloads}")
        print(f"   Unique books: {unique_books}")
        print(f"   Total size: {total_size / (1024*1024):.1f} MB")
        
        if recent_downloads:
            print(f"\n📥 Recent Downloads:")
            for title, identifier, filename, created_at in recent_downloads:
                print(f"   • {filename} ({identifier})")
                print(f"     Title: {title[:50]}...")
                print(f"     Date: {created_at}")
                print()
        
    else:
        print("❌ Database not found. Run the scraper first.")
    
    # Check download directory
    if download_dir.exists():
        pdf_files = list(download_dir.glob("*.pdf"))
        print(f"📁 Download Directory:")
        print(f"   PDF files: {len(pdf_files)}")
        print(f"   Directory size: {sum(f.stat().st_size for f in pdf_files) / (1024*1024):.1f} MB")
        
        if pdf_files:
            print(f"\n📄 Sample Files:")
            for pdf_file in pdf_files[:5]:
                size_mb = pdf_file.stat().st_size / (1024*1024)
                print(f"   • {pdf_file.name} ({size_mb:.1f} MB)")
    else:
        print("❌ Download directory not found.")
    
    # Check log file
    log_file = "scraper.log"
    if os.path.exists(log_file):
        log_size = os.path.getsize(log_file) / 1024  # KB
        print(f"\n📝 Log File:")
        print(f"   Size: {log_size:.1f} KB")
        
        # Get last few log entries
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                print(f"   Last entries:")
                for line in lines[-3:]:
                    print(f"     {line.strip()}")
    else:
        print("❌ Log file not found.")

if __name__ == "__main__":
    check_progress() 