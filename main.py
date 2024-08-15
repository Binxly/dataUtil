import os
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import concurrent.futures
from urllib.parse import urljoin

class ImageScraper:
    def __init__(self, url):
        self.base_url = url
        self.image_urls = []

    def find_images(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        
        page_num = 1
        while True:
            page_url = f"{self.base_url}page{page_num}/" if page_num > 1 else self.base_url
            driver.get(page_url)

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "ul.gallery"))
                )

                figures = driver.find_elements(By.CSS_SELECTOR, "ul.gallery li figure")
                
                if not figures:
                    break

                for figure in figures:
                    try:
                        a_tag = WebDriverWait(figure, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "a"))
                        )
                        href = a_tag.get_attribute('href')
                        if href:
                            self.image_urls.append(href)
                    except TimeoutException:
                        print(f"Timeout waiting for link in figure: {figure.text}")

                page_num += 1
            except TimeoutException:
                print(f"Timeout waiting for gallery to load on page {page_num}. Stopping.")
                break

        driver.quit()
        return len(self.image_urls)

    def download_image(self, url, download_path, i):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            raw_scan_link = soup.select_one('li.dld-btn.btn-4.hover-border a:contains("Raw Scan")')
            
            if raw_scan_link and 'href' in raw_scan_link.attrs:
                full_img_url = urljoin(self.base_url, raw_scan_link['href'])
                
                img_response = requests.get(full_img_url, headers=headers, timeout=10)
                img_response.raise_for_status()

                filename = os.path.join(download_path, f"image_{i+1}.jpg")
                with open(filename, 'wb') as f:
                    f.write(img_response.content)
                print(f"Downloaded: {filename}")
                return True
            else:
                print(f"Could not find Raw Scan link on page: {url}")
                return False

        except Exception as e:
            print(f"Error downloading image from {url}: {e}")
            return False

    def download_images(self, download_path):
        if not os.path.exists(download_path):
            os.makedirs(download_path)

        downloaded = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.download_image, url, download_path, i): (url, i) for i, url in enumerate(self.image_urls)}
            for future in concurrent.futures.as_completed(future_to_url):
                url, i = future_to_url[future]
                try:
                    if future.result():
                        downloaded += 1
                except Exception as e:
                    print(f"Error processing {url}: {e}")

        return downloaded

class ImageScraperGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Image Scraper")
        self.scraper = None

        self.url_entry = ttk.Entry(master, width=50)
        self.url_entry.pack(pady=10)

        self.scan_button = ttk.Button(master, text="Scan URL", command=self.scan_url)
        self.scan_button.pack(pady=5)

        self.status_label = ttk.Label(master, text="")
        self.status_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=300, mode="indeterminate")
        self.progress_bar.pack(pady=5)

    def scan_url(self):
        url = self.url_entry.get()
        self.scraper = ImageScraper(url)
        
        self.status_label.config(text="Scanning URL...")
        self.progress_bar.start()
        
        self.master.after(100, self.start_scanning)

    def start_scanning(self):
        thread = threading.Thread(target=self.scan_thread)
        thread.start()

    def scan_thread(self):
        try:
            num_images = self.scraper.find_images()
            self.master.after(0, self.update_status, f"Found {num_images} images. Downloading...")
            
            download_path = "downloaded_images"
            downloaded = self.scraper.download_images(download_path)

            self.master.after(0, self.update_status, f"Downloaded {downloaded} images to {download_path}")
            self.master.after(0, self.finish_scanning)
        except Exception as e:
            self.master.after(0, self.update_status, f"Error: {str(e)}")
            self.master.after(0, self.finish_scanning)

    def update_status(self, message):
        self.status_label.config(text=message)

    def finish_scanning(self):
        self.progress_bar.stop()
        self.status_label.config(text="Scan complete.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageScraperGUI(root)
    root.mainloop()