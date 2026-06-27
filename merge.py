import requests
import re

# ==========================================
# Mapovanie názvov kanálov -> správne tvg-id z EPG zdrojov
# Kľúč = očistený názov z iptv playlistu
# Hodnota = channel id, ktoré existuje v tvojich EPG XML zdrojoch
# ==========================================
CHANNEL_MAPPING = {
    "Jednotka": "Jednotka.sk",
    "Dvojka": "Dvojka.sk",
    "Markíza": "Markiza.sk",
    "JOJ": "TV.JOJ.sk",
    "JOJ Plus": "JOJ.Plus.sk",
    "Dajto": "Dajto.sk",

    "ČT1": "ČT1.HD.sk",
    "ČT 1": "ČT1.HD.sk",
    "ČT2": "ČT2.HD.sk",
    "ČT 2": "ČT2.HD.sk",
    "ČT24": "ČT24.HD.sk",
    "ČT 24": "ČT24.HD.sk",
    "ČT Sport": "CT.Sport.cz",

    "Nova": "Nova.cz",
    "Nova Cinema": "Nova.Cinema.cz",
    "Nova Action": "Nova.Action.cz",
    "Prima": "Prima.cz",
    "Prima COOL": "Prima.Cool.cz",

    "History": "History.HD.sk",
    "AMC": "AMC.HD.sk",
    "AMC Europe Czech Republic": "AMC.HD.sk",

    "AXN": "AXN.HD.sk",
    "AXN CEE Czech Republic": "AXN.HD.sk",
    "AXN White": "AXN.White.cz",
    "AXN White CzechRepublic": "AXN.White.cz",
    "AXN White Czech Republic": "AXN.White.cz",

    "FilmBox+ One Czech Republic": "Filmbox.HD.sk",
    "FilmBox+ Hits Czech Republic": "Filmbox.Premium.HD.sk",
    "FilmBox+ Emotion Czech Republic": "Filmbox.Extra.HD.sk",
    "FilmBox+ Love & Crime Czech Republic": "Filmbox.Family.sk",

    "Barrandov Krimi": "Barrandov.Krimi.cz",
    ":Šport": "RTVS.Sport.sk",
}

# Zdrojové URL adresy z iptv-org
urls = [
    "https://iptv-org.github.io/iptv/countries/sk.m3u",
    "https://iptv-org.github.io/iptv/countries/cz.m3u"
]

# Zjednotený EPG zdroj z tvojho druhého repozitára
merged_epg_url = "https://raw.githubusercontent.com/kozmali/sk-cz-epg/refs/heads/main/epg.xml.gz"

merged_content = [f'#EXTM3U url-tvg="{merged_epg_url}"']


def clean_channel_name(name: str) -> str:
    name = re.sub(r'\s*\(\d+p\)', '', name)
    name = re.sub(r'\s*\[.*?\]', '', name)
    name = name.replace("STV1", "Jednotka")
    name = name.replace("STV2", "Dvojka")
    name = name.replace("CzechRepublic", "Czech Republic")
    name = " ".join(name.split())
    return name.strip()


for url in urls:
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        lines = response.text.splitlines()
        start_idx = 1 if lines and lines[0].strip().startswith("#EXTM3U") else 0

        for line in lines[start_idx:]:
            if not line.strip():
                continue

            if line.startswith("#EXTINF"):
                parts = line.rsplit(",", 1)
                if len(parts) == 2:
                    inf_part, name_part = parts[0], parts[1]
                    cleaned_name = clean_channel_name(name_part)

                    # odstránenie pôvodných iptv-org identifikátorov
                    inf_part = re.sub(r'\s*tvg-id="[^"]*"', '', inf_part)
                    inf_part = re.sub(r'\s*tvg-name="[^"]*"', '', inf_part)

                    # nájdi správne tvg-id
                    spravne_id = CHANNEL_MAPPING.get(cleaned_name)

                    if spravne_id:
                        inf_part = inf_part.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-id="{spravne_id}" tvg-name="{cleaned_name}"')
                    else:
                        inf_part = inf_part.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-name="{cleaned_name}"')

                    line = f"{inf_part},{cleaned_name}"

            merged_content.append(line)

    except Exception as e:
        print(f"Zlyhalo spojenie s {url}: {e}")

with open("sk_cz_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content))

print("Playlist s presným EPG mapovaním bol úspešne vytvorený!")
