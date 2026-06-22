import requests

# Zdrojové URL adresy z iptv-org
urls = [
    "https://iptv-org.github.io/iptv/countries/sk.m3u",
    "https://iptv-org.github.io/iptv/countries/cz.m3u"
]

# Oficiálne a funkčné EPG príručky priamo od iptv-org
epg_sk = "https://iptv-org.github.io/epg/guides/sk.xml"
epg_cz = "https://iptv-org.github.io/epg/guides/cz.xml"

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
                    merged_content.append(line)
        else:
            print(f"Chyba pri sťahovaní {url}: Status {response.status_code}")
    except Exception as e:
        print(f"Zlyhalo spojenie s {url}: {e}")

with open("sk_cz_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content))

print("Playlist s oficiálnym EPG bol úspešne spojený!")
