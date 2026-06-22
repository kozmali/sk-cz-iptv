import requests
import re

# ==========================================
# TVOJ MAPOVACÍ SLOVNÍK (Ako v PHP)
# Vľavo: Očistený názov z iptv-org
# Vpravo: Presné ID z epgshare01 (zoznam_stanic.txt)
# ==========================================
CHANNEL_MAPPING = {
    "Jednotka": "Jednotka.sk",
    "Dvojka": "Dvojka.sk",
    "Markíza": "Markiza.sk",
    "JOJ": "TV.JOJ.sk",
    "JOJ Plus": "JOJ.Plus.sk",
    "Dajto": "Dajto.sk",
    "ČT1": "CT1.cz",
    "ČT2": "CT2.cz",
    "ČT Sport": "CT.Sport.cz",
    "ČT24": "CT24.cz",
    "Nova": "Nova.cz",
    "Nova Cinema": "Nova.Cinema.cz",
    "Nova Action": "Nova.Action.cz",
    "Prima": "Prima.cz",
    "Prima COOL": "Prima.Cool.cz",
    "History": "History.cz",
    "AXN": "AXN.cz"
    # Ak ti bude chýbať EPG na inej stanici, jednoducho ju sem dopíšeš.
}

# Zdrojové URL adresy z iptv-org
urls = [
    "https://iptv-org.github.io/iptv/countries/sk.m3u",
    "https://iptv-org.github.io/iptv/countries/cz.m3u"
]

# Nové EPG z epgshare01
epg_sk = "https://epgshare01.online/epgshare01/epg_ripper_SK1.xml.gz"
epg_cz = "https://epgshare01.online/epgshare01/epg_ripper_CZ1.xml.gz"

merged_content = [f'#EXTM3U url-tvg="{epg_sk},{epg_cz}"']

for url in urls:
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            lines = response.text.splitlines()
            start_idx = 1 if lines and lines[0].strip().startswith("#EXTM3U") else 0
            
            for line in lines[start_idx:]:
                if line.strip():
                    if line.startswith("#EXTINF"):
                        parts = line.rsplit(",", 1)
                        if len(parts) == 2:
                            inf_part, name_part = parts[0], parts[1]
                            
                            # 1. Vyčistíme balast z názvu stanice
                            cleaned_name = re.sub(r'\s*\(\d+p\)', '', name_part)
                            cleaned_name = re.sub(r'\s*\[.*?\]', '', cleaned_name)
                            cleaned_name = cleaned_name.replace("STV1", "").replace("STV2", "")
                            cleaned_name = " ".join(cleaned_name.split())
                            
                            # 2. Úplne vymažeme staré iptv-org IDčka a názvy
                            inf_part = re.sub(r'tvg-id="[^"]*"', '', inf_part)
                            inf_part = re.sub(r'tvg-name="[^"]*"', '', inf_part)
                            
                            # 3. Zistíme, či máme pre tento názov správne ID v našom slovníku
                            spravne_id = CHANNEL_MAPPING.get(cleaned_name)
                            
                            # 4. Ak sme ho našli, vložíme ho do playlistu
                            if spravne_id:
                                inf_part = inf_part.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{spravne_id}"')
                            
                            line = f"{inf_part},{cleaned_name}"
                    
                    merged_content.append(line)
        else:
            print(f"Chyba pri sťahovaní {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Zlyhalo spojenie s {url}: {e}")

with open("sk_cz_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content))

print("Playlist s presným EPG mapovaním bol úspešne vytvorený!")
