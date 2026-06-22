import requests
import re

# Zdrojové URL adresy z iptv-org
urls = [
    "https://iptv-org.github.io/iptv/countries/sk.m3u",
    "https://iptv-org.github.io/iptv/countries/cz.m3u"
]

# Nové, funkčné EPG príručky z epgshare01
epg_sk = "https://epgshare01.online/epgshare01/epg_ripper_SK1.xml.gz"
epg_cz = "https://epgshare01.online/epgshare01/epg_ripper_CZ1.xml.gz"

# Spojenie oboch EPG do hlavičky (oddelené čiarkou)
merged_content = [f'#EXTM3U url-tvg="{epg_sk},{epg_cz}"']

for url in urls:
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            lines = response.text.splitlines()
            start_idx = 1 if lines and lines[0].strip().startswith("#EXTM3U") else 0
            
            for line in lines[start_idx:]:
                if line.strip():
                    # Ak riadok obsahuje info o stanici, upravíme ho
                    if line.startswith("#EXTINF"):
                        parts = line.rsplit(",", 1)
                        if len(parts) == 2:
                            inf_part, name_part = parts[0], parts[1]
                            
                            # ÚPLNÉ VYMAZANIE TVG-ID, aby ProgDVB musel párovať podľa názvov
                            inf_part = re.sub(r'tvg-id="[^"]*"', '', inf_part)
                            
                            # Odstránime (720p), [Not 24/7], (1080p) atď.
                            cleaned_name = re.sub(r'\s*\(\d+p\)', '', name_part)
                            cleaned_name = re.sub(r'\s*\[.*?\]', '', cleaned_name)
                            cleaned_name = cleaned_name.replace("STV1", "").replace("STV2", "")
                            cleaned_name = " ".join(cleaned_name.split())
                            
                            line = f"{inf_part},{cleaned_name}"
                    
                    merged_content.append(line)
        else:
            print(f"Chyba pri sťahovaní {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Zlyhalo spojenie s {url}: {e}")

with open("sk_cz_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content))

print("Playlist úspešne vytvorený bez problémových ID!")
