import requests

urls = [
    "https://iptv-org.github.io/iptv/countries/sk.m3u",
    "https://iptv-org.github.io/iptv/countries/cz.m3u"
]

merged_content = ["#EXTM3U"]

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

print("Playlisty boli úspešne spojené!")
