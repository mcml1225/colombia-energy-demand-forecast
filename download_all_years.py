"""
Download all Excel files from XM for years 2000-2024
"""

import requests
from pathlib import Path
import time
import os

def download_file(url, output_path):
    """Download a file from URL"""
    try:
        print(f"Descargando {output_path.name}...", end=" ")
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            # Check if it's an Excel file
            if response.content[:4] == b'PK\x03\x04':
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                print("✓ OK")
                return True
            else:
                print("✗ No es un archivo Excel válido")
                return False
        else:
            print(f"✗ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

# Create raw data directory
raw_path = Path("data/raw")
raw_path.mkdir(parents=True, exist_ok=True)

# Base URL pattern
base_url = "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_{year}.xlsx"

# Download all years
print("="*50)
print("DESCARGANDO ARCHIVOS 2000-2024")
print("="*50)

downloaded = 0
failed = []

for year in range(2000, 2025):
    output_file = raw_path / f"Demanda_Energia_SIN_{year}.xlsx"
    
    # Skip if already exists
    if output_file.exists():
        print(f"{year} - Ya existe, omitiendo")
        downloaded += 1
        continue
    
    url = base_url.format(year=year)
    if download_file(url, output_file):
        downloaded += 1
    else:
        failed.append(year)
    
    # Wait to be nice to the server
    time.sleep(1)

print("\n" + "="*50)
print("RESUMEN DE DESCARGA")
print("="*50)
print(f"Archivos descargados: {downloaded}/25")
if failed:
    print(f"Fallaron: {failed}")
    print("\nPuedes descargar estos años manualmente desde:")
    for year in failed:
        print(f"  {base_url.format(year=year)}")
else:
    print("✓ Todos los archivos descargados exitosamente!")