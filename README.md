# Purpose

This is a multi-threaded Python-based image scraper with a graphical user interface. It's designed to download images from websites, particularly from oldbookillustrations.com.

## Features

- Web scraping using Selenium and BeautifulSoup
- Multithreaded image downloading for improved performance
- Simple GUI for easy operation
- Automatic navigation through multiple pages of image galleries
- Downloads high-resolution "Raw Scan" versions of images when available

## Requirements

- Python 3.7+
- Chrome browser (for Selenium WebDriver)
- ChromeDriver (compatible with your Chrome version)

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/image-scraper.git
   cd image-scraper
   ```

2. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

3. Download the appropriate version of ChromeDriver for your system and ensure it's in your PATH.

## Usage

1. Run the script:

   ```
   python main.py
   ```

2. Enter the URL of the gallery you want to scrape in the input field.

3. Click "Scan URL" to start the scraping process.

4. The program will scan for images, then download them to a folder named "downloaded_images" in the same directory as the script.

## Configuration

You can adjust the number of concurrent download threads by modifying the `max_workers` parameter in the `ThreadPoolExecutor` within the `download_images` method of the `ImageScraper` class.

## Disclaimer

This tool is for educational purposes only. Be sure to comply with the terms of service.
