# Islamic Books Scraper

A Python script that scrapes Islamic books in Arabic and English from the Internet Archive (archive.org).

## Features

- **Advanced Search API Integration**: Uses Internet Archive's Advanced Search API to find Islamic books
- **Language Filtering**: Automatically filters for Arabic and English books
- **Pagination Support**: Fetches all matching results, not just the first 100
- **PDF Download**: Downloads PDF files with streaming for large files
- **SQLite Database**: Stores metadata about downloaded files
- **Duplicate Prevention**: Skips already downloaded files
- **Progress Tracking**: Shows download progress and status updates
- **Error Handling**: Robust error handling with logging

## Requirements

- Python 3.7+
- `requests` library
- Internet connection

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings:

```bash
python scraper.py
```

### Check Progress

Check the current progress and statistics:

```bash
python check_progress.py
```

### Test the Scraper

Test the scraper functionality:

```bash
python test_scraper.py
```

### Custom Configuration

You can modify the `config.py` file to customize:

- Download directory (default: `downloads/`)
- Database file path (default: `books.db`)
- Search query (currently set to "Islamic books")
- Language filters (currently Arabic and English)
- Rate limiting delays
- Download timeouts

## Output

The script creates:

1. **`downloads/` directory**: Contains all downloaded PDF files
2. **`books.db`**: SQLite database with download metadata
3. **`scraper.log`**: Detailed log file with progress and errors

### Database Schema

The `downloads` table contains:
- `id`: Auto-increment primary key
- `title`: Book title from metadata
- `identifier`: Archive.org identifier
- `file_name`: PDF filename
- `download_url`: Original download URL
- `local_path`: Local file path
- `created_at`: Timestamp of when record was created

## How It Works

1. **Search Phase**: Queries Internet Archive's Advanced Search API with pagination
2. **Filtering**: Filters results for Arabic and English books
3. **PDF Discovery**: For each book, finds available PDF files via metadata API
4. **Download**: Downloads PDFs with streaming and progress tracking
5. **Database Storage**: Stores metadata in SQLite database
6. **Duplicate Check**: Skips files already downloaded

## API Endpoints Used

- **Advanced Search**: `https://archive.org/advancedsearch.php`
- **Metadata API**: `https://archive.org/metadata/{identifier}`
- **Download API**: `https://archive.org/download/{identifier}/{filename}`

## Rate Limiting

The script includes built-in delays to be respectful to archive.org:
- 1 second delay between API requests
- 2 second delay between book processing

## Error Handling

- Network timeouts and connection errors
- Invalid API responses
- File download failures
- Database errors
- Missing PDF files

## Logging

The script provides detailed logging:
- Console output for real-time progress
- Log file (`scraper.log`) for detailed debugging
- Error tracking and reporting

## Example Output

```
2024-01-15 10:30:00 - INFO - Starting Islamic Books Scraper
2024-01-15 10:30:01 - INFO - Database initialized: books.db
2024-01-15 10:30:02 - INFO - Starting to fetch all Islamic books...
2024-01-15 10:30:03 - INFO - Fetching page 1...
2024-01-15 10:30:04 - INFO - Total results found: 1250
2024-01-15 10:30:05 - INFO - Page 1: Found 100 items, filtered to 45 Arabic/English books
2024-01-15 10:30:06 - INFO - Processing book 1 of 45
2024-01-15 10:30:07 - INFO - Processing book: The Holy Quran (quran_arabic)
2024-01-15 10:30:08 - INFO - Downloading: quran_arabic.pdf
2024-01-15 10:30:15 - INFO - Successfully downloaded: quran_arabic.pdf
2024-01-15 10:30:16 - INFO - Stored metadata for quran_arabic.pdf
2024-01-15 10:30:17 - INFO - Book quran_arabic: Downloaded 1, Skipped 0
```

## Troubleshooting

### Common Issues

1. **Network Errors**: Check your internet connection
2. **Permission Errors**: Ensure write permissions for downloads directory
3. **Database Errors**: Check if SQLite is properly installed
4. **Large Downloads**: The script handles large files with streaming
5. **Unicode Errors**: Fixed with UTF-8 encoding support
6. **API Errors**: Added retry logic and error handling
7. **Server Errors**: Added pagination limits and error recovery

### Recent Fixes

- ✅ **Unicode Support**: Fixed Arabic text encoding issues
- ✅ **Metadata API**: Added support for both dict and list file formats
- ✅ **Error Recovery**: Added retry logic and graceful error handling
- ✅ **Progress Tracking**: Added percentage progress and better logging
- ✅ **Resume Capability**: Progress is saved and can be resumed
- ✅ **Rate Limiting**: Improved delays to respect server limits

### Debug Mode

For detailed debugging, modify the logging level in `config.py`:

```python
LOG_LEVEL = "DEBUG"
```

## License

This script is provided as-is for educational and research purposes. Please respect archive.org's terms of service and rate limits.

## Contributing

Feel free to submit issues or pull requests to improve the script.