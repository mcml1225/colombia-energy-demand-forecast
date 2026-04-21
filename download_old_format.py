"""
Download 2011 and 2012 in .xls format
"""

import requests
from pathlib import Path

def download_file(url, output_path):
    """Download a file"""
    try:
        print(f"Descargando {output_path.name}...", end=" ")
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        if response.status_code == 200:
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print("✓ OK")
            return True
        else:
            print(f"✗ HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

raw_path = Path("data/raw")
raw_path.mkdir(parents=True, exist_ok=True)

# Try different possible URLs for old format
urls_to_try = [
    ("2011", "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2011.xls"),
    ("2011", "https://sinergox.xm.com.co/dmnd/Historicos/Demanda%20Nacional/Demanda_Energia_SIN_2011.xls"),
    ("2012", "https://sinergox.xm.com.co/dmnd/Histricos/Demanda%20Nacional/Demanda_Energia_SIN_2012.xls"),
    ("2012", "https://sinergox.xm.com.co/dmnd/Historicos/Demanda%20Nacional/Demanda_Energia_SIN_2012.xls"),
]

print("="*50)
print("DESCARGANDO ARCHIVOS 2011 y 2012 (formato .xls)")
print("="*50)

for year, url in urls_to_try:
    output_file = raw_path / f"Demanda_Energia_SIN_{year}.xls"
    
    if output_file.exists():
        print(f"{year} - Ya existe")
        continue
    
    download_file(url, output_file)

print("\n✓ Proceso completado")
print("\nVerifica los archivos en data/raw/")