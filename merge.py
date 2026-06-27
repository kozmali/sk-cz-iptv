import requests
import re

# ==========================================
# Mapovanie názvov kanálov -> správne tvg-id z EPG zdrojov
# Kľúč = očistený názov z iptv playlistu
# Hodnota = channel id, ktoré existuje v tvojich EPG XML zdrojoch
# ==========================================
CHANNEL_MAPPING = {
    "Jednotka": "Jednotka.HD.sk",
    "Dvojka": "Dvojka.HD.sk",
    "Markíza": "Markiza.sk",
    "JOJ": "TV.JOJ.sk",
    "JOJ Plus": "JOJ.Plus.sk",
    "Dajto": "Dajto.sk",

    "ČT1": "ČT1.cz",
    "ČT 1": "ČT1.HD.sk",
    "ČT2": "ČT2.cz",
    "ČT 2": "ČT2.HD.sk",
    "ČT24": "ČT24.HD.sk",
    "ČT 24": "ČT24.HD.sk",

    "Ocko Black": "ÓČKOBlack.cz",
    "Óčko Expres": "ÓČKOEXPRES.cz",
    "Ocko Star": "Óčko.Star.cz",
    "Óčko Gold": "Óčko.Star.cz",
    "Slager Original": "Šláger.Originál.HD.sk",
    "Slager Muzika": "Šláger.Muzika.HD.sk",
    
    "TV Lux": "Lux.TV.HD.sk",
    "Retro Music Television": "RETRO.Music.TV.sk",
    "Televize Seznam": "Televize.Seznam.HD.sk",
    "TV Noe": "TVNOE.cz",
    "Noe+": "Noe+.cz",
    "Východočeská TV": "V1.cz",

    "Nova": "Nova.cz",
    "Nova Cinema": "Nova.Cinema.cz",
    "Nova Action": "Nova.Action.cz",
    "Prima": "Prima.cz",
    "Prima COOL": "Prima.Cool.cz",

    "AMC": "AMC.cz",
    "AMC Europe Czech Republic": "AMC.cz",

    "History": "THEHISTORYCHANNEL.cz",

    "AXN": "AXN.cz",
    "AXN CEE Czech Republic": "AXN.cz",
    "AXN White": "AXNWHITE.cz",
    "AXN White CzechRepublic": "AXN.White.cz",
    "AXN White Czech Republic": "AXN.White.cz",
    "AXN Black Czech Republic": "AXN.Black.cz",
    "AXN CEE CEE Czech Republic": "AXN.cz",

    "FilmBox+ One Czech Republic": "FILMBOX.cz",
    "FilmBox+ Hits Czech Republic": "FILMBOXPREMIUM.cz",
    "FilmBox+ Emotion Czech Republic": "FILMBOXEXTRA.cz",
    "FilmBox+ Love & Crime Czech Republic": "FILMBOXFAMILY.cz",

    "Barrandov Krimi": "BARRANDOVKRIMI.cz",
    "Kino Barrandov": "Kino.Barrandov.HD.sk",
    "Televízia OSEM": "TV.OSEM.cz",
    "ČT:D/ČT art": "ČT:D/ČTart.cz",

    ":Šport": "RTVS.SPORT.cz",
    ":24": ":24.HD.sk",

    "TV Doktor": "TV.Doktor.cz",
    "LifeTv": "LifeTV.cz",
    "Life Tv": "LifeTV.sk",
    "JOJ Šport 2": "JOJŠPORT2.cz",
    "Klasik": "MarkizaKlasik.cz",
    
    "Zapadoslovenska TV": "Západoslovenská.televízia.cz",
    "Polar TV": "POLAR.cz",
    "Plzeň TV": "ČRoPlzeň.cz",
    "TV Brno 1": "TV.Brno.1.cz",
    "Mňau TV": "MŇAU.cz",
    
    "Liptov": "Liptov.sk",
    "MTR": "Mestská.televízia.Ružomberok.cz",
    "TVT": "TVT.cz",
    "Miestna TV Trebišov.sk": "Miestna.TV.Trebišov.sk",
    "TV9 KTV": "TV9.KTV.cz",
    "TV Nitricka": "TV.Nitrička.sk",
    "RTM": "RTM.cz",
    "RTM Plus": "RTM.plus.Liberecko.cz",
    "Régió TV": "Régió.TV.cz",
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
    name = re.sub(r'\s*STV1\b', '', name)   # bolo: name.replace("STV1", "Jednotka")
    name = re.sub(r'\s*STV2\b', '', name)   # bolo: name.replace("STV2", "Dvojka")
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
