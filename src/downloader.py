"""
downloader.py - Downloads Excel files from XM (Colombian electricity market operator)
"""

import requests
import pandas as pd
from pathlib import Path
import time
from tqdm import tqdm
import urllib.parse
import os

class XMDataDownloader:
    """
    Downloads historical energy demand data from XM
    """
    
    def __init__(self, raw_data_path="data/raw/"):
        self.raw_path = Path(raw_data_path)
        self.raw_path.mkdir(parents=True, exist_ok=True)
        
        # List of URLs for each year (based on actual XM structure)
        self.file_urls = {
            2000: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2000.xlsx",
            2001: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2001.xlsx",
            2002: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2002.xlsx",
            2003: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2003.xlsx",
            2004: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2004.xlsx",
            2005: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2005.xlsx",
            2006: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2006.xlsx",
            2007: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2007.xlsx",
            2008: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2008.xlsx",
            2009: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2009.xlsx",
            2010: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2010.xlsx",
            2011: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2011.xlsx",
            2012: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2012.xlsx",
            2013: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2013.xlsx",
            2014: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2014.xlsx",
            2015: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2015.xlsx",
            2016: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2016.xlsx",
            2017: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2017.xlsx",
            2018: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2018.xlsx",
            2019: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2019.xlsx",
            2020: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2020.xlsx",
            2021: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2021.xlsx",
            2022: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2022.xlsx",
            2023: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2023.xlsx",
            2024: "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2024.xlsx",
        }
        
        # Session to maintain cookies
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def download_file(self, year, url):
        """Download a single Excel file"""
        output_path = self.raw_path / f"Demanda_Energia_SIN_{year}.xlsx"
        
        # Skip if already downloaded
        if output_path.exists():
            print(f"File for {year} already exists, skipping...")
            return str(output_path)
        
        try:
            print(f"Downloading {year} from {url}...")
            response = self.session.get(url, timeout=60)
            
            if response.status_code == 200:
                # Check if it's an Excel file
                content_type = response.headers.get('Content-Type', '')
                if 'excel' in content_type or 'application/vnd.openxmlformats' in content_type or response.content[:4] == b'PK\x03\x04':
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    print(f"  Successfully downloaded {year}")
                    return str(output_path)
                else:
                    print(f"  Failed: Not an Excel file for {year}. Status: {response.status_code}")
                    return None
            else:
                print(f"  Failed: HTTP {response.status_code} for {year}")
                return None
                
        except Exception as e:
            print(f"  Error downloading {year}: {e}")
            return None
    
    def download_all(self, years=None):
        """Download all available Excel files"""
        if years is None:
            years = list(self.file_urls.keys())
        
        downloaded_files = []
        for year in tqdm(years, desc="Downloading files"):
            url = self.file_urls.get(year)
            if url:
                result = self.download_file(year, url)
                if result:
                    downloaded_files.append(result)
                time.sleep(1)  # Be respectful to the server
        
        print(f"\nDownloaded {len(downloaded_files)} files to {self.raw_path}")
        return downloaded_files


# Test the downloader
if __name__ == "__main__":
    downloader = XMDataDownloader()
    files = downloader.download_all(years=[2000, 2001])  # Test with 2 years
    print(f"Downloaded files: {files}")