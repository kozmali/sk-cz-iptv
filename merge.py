#!/usr/bin/env python3
import requests
import re

# ==========================================
# Mapovanie názvov kanálov -> správne tvg-id z EPG zdrojov
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
    "TV Noe": "Noe.cz",
    "TV Noe+": "Noe+.cz",
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
    "AXN White": "AXN.White.ro",
    "AXN White CzechRepublic": "AXN.White.cz",
    "AXN White Czech Republic": "AXN.White.cz",
    "AXN Black Czech Republic": "AXN.Black.cz",
    "AXN CEE CEE Czech Republic": "AXN.cz",

    "FilmBox+ One Czech Republic": "FILMBOX.cz",
    "FilmBox+ Hits Czech Republic": "FILMBOXPREMIUM.cz",
    "FilmBox+ Emotion Czech Republic": "FILMBOXEXTRA.cz",
    "FilmBox+ Love & Crime Czech Republic": "FILMBOXSTARS.cz",

    "Barrandov Krimi": "BARRANDOVKRIMI.cz",
    "Kino Barrandov": "Kino.Barrandov.HD.sk",
    "Televízia OSEM": "TV.OSEM.cz",
    "ČT:D/ČT art": "ČT:D/ČTart.cz",

    ":Šport": "RTVS.SPORT.cz",
    ":24": ":24.HD.sk",

    "LifeTv": "LifeTV.sk",
    "JOJ Šport 2": "JOJŠPORT2.cz",
    "Klasik": "Markíza.Klasik.HD.sk",

    "Zapadoslovenska TV": "Západoslovenská.televízia.cz",
    "Polar TV": "POLAR.cz",
    "Plzeň TV": "ČRoPlzeň.cz",
    "TV Brno 1": "TV.Brno.1.cz",
    "Mňau TV": "MŇAU.cz",

    "MTR": "Mestská.televízia.Ružomberok.cz",
    "TVT": "TVT.cz",
    "TV Nitricka": "TV.Nitricka.sk",
    "RTM Plus": "RTM.plus.Liberecko.cz",
    "Régió TV": "Régió.TV.cz",
    "TV NRSR": "tv.NRSR.sk",
    "TV LocAll": "TV.LocAll.sk",
    "TV Povazie": "TV.Považie.cz",
    "RTG int.": "RTGINT.ru",
    "TV Ružinov": "TV.Ružinov.cz",
}

# ==========================================
# Globálne číslovanie kanálov — pozícia = tvg-chno
#
# Čísla zodpovedajú tvojmu zoznamu 1–88.
# Kanály preferované z cache-sk (Jednotka, ČT1...) sú tu tiež,
# aby keď sa objavia v iptv-org, dostali správne číslo a nesedeli
# na konci zoznamu v Kodi.
# Kanály mimo tohto slovníka dostanú chno 89, 90, 91...
# ==========================================
CHANNEL_CHNO = {
    # --- cache-sk (ale môžu byť aj v iptv-org, preto im dáme číslo) ---
    "Jednotka":                              1,
    "Dvojka":                                2,
    "Markíza":                               3,
    "JOJ":                                   4,
    "Dajto":                                 5,
    "Krimi":                                 6,
    "Doma":                                  7,
    "Klasik":                                8,
    "JOJ Plus":                              9,
    "JOJ Krimi":                            10,
    "JOJ Family":                           11,
    "JOJ Cinema":                           12,
    "Nova Cinema":                          13,
    # --- sk-cz-iptv ---
    "FilmBox+ One Czech Republic":          14,
    "FilmBox+ Love & Crime Czech Republic": 15,
    "FilmBox+ Hits Czech Republic":         16,
    "FilmBox+ Emotion Czech Republic":      17,
    "AMC Europe Czech Republic":            18,
    "AXN CEE Czech Republic":              19,
    "AXN Black Czech Republic":            20,
    "AXN White Czech Republic":            21,
    "AXN White":                           22,   # RO anglický stream
    # --- cache-sk ---
    "ČT 1":                                23,   # iptv-org má "ČT 1"
    "ČT1":                                 23,   # cache-sk má "ČT1"
    "ČT 2":                                24,
    "ČT2":                                 24,
    # --- sk-cz-iptv ---
    "Barrandov Krimi":                     25,
    # --- cache-sk ---
    "CS Film":                             26,
    "CS History":                          27,
    # --- sk-cz-iptv ---
    "History":                             28,
    # --- cache-sk ---
    "CS Mystery":                          29,
    ":Šport":                              30,   # cache-sk "ŠPORT", iptv-org ":Šport"
    "JOJ Šport":                           31,
    "JOJ Šport 2":                         32,
    # --- sk-cz-iptv ---
    "Sport1":                              33,
    "Sport2":                              34,
    # --- cache-sk ---
    "ČT Sport":                            35,
    # --- sk-cz-iptv ---
    "Sporty TV":                           36,
    "Golf Channel":                        37,
    "Arena Sport 1":                       38,
    "Arena Sport 2":                       39,
    # --- cache-sk ---
    ":24":                                 40,
    "JOJ 24":                              41,
    "TA3":                                 42,
    "ČT24":                                43,
    "CNN Prima News":                      44,
    "Live NRSR":                           45,
    "Jojko":                               46,
    "ČT:D/ČT art":                         47,
    "TV Doktor":                           48,
    "SZTŠ":                                49,
    "Live :O":                             50,
    "Live RTVS":                           51,
    # --- sk-cz-iptv ---
    "Elektrika TV":                        52,
    "Mňau TV":                             53,
    "TV Noe":                              54,
    "TV Noe+":                             55,
    "LifeTv":                              56,
    "Televízia OSEM":                      57,
    "Óčko":                                58,
    # --- cache-sk ---
    "Óčko Expres":                         59,
    # --- sk-cz-iptv ---
    "Ocko Black":                          60,
    "Ocko Star":                           61,
    # --- cache-sk ---
    "Retro Music Television":              62,   # iptv-org názov
    # --- sk-cz-iptv ---
    "Senzi":                               63,
    "Slager Original":                     64,
    "Slager Muzika":                       65,
    "Antik Info TV":                       66,
    "Zapadoslovenska TV":                  67,
    "TV Ružinov":                          68,
    "TV Central":                          69,
    "TV Nitricka":                         70,
    "TV LocAll":                           71,
    "TV Povazie":                          72,
    "TVT":                                 73,
    "TV Liptov":                           74,
    "MTR":                                 75,
    "TV Mistral":                          76,
    "Televízia Močenok":                   77,
    "TV9":                                 78,
    "TV Brno 1":                           79,
    "Jihočeská televize":                  80,
    "JČ1":                                 81,
    "Východočeská TV":                     82,
    "ÚTV":                                 83,
    "Plzeň TV":                            84,
    "Polar TV":                            85,
    "Polar2 TV":                           86,
    "Régió TV":                            87,
    "RTG int.":                            88,
}

# ==========================================
# Zdrojové URL adresy z iptv-org
# ==========================================
urls = [
    "https://iptv-org.github.io/iptv/countries/sk.m3u",
    "https://iptv-org.github.io/iptv/countries/cz.m3u"
]

merged_epg_url = "https://raw.githubusercontent.com/kozmali/sk-cz-epg/refs/heads/main/epg.xml.gz"


def clean_channel_name(name: str) -> str:
    name = re.sub(r'\s*\(\d+p\)', '', name)
    name = re.sub(r'\s*\[.*?\]', '', name)
    name = re.sub(r'\s*STV1\b', '', name)
    name = re.sub(r'\s*STV2\b', '', name)
    name = name.replace("CzechRepublic", "Czech Republic")
    name = " ".join(name.split())
    return name.strip()


# --- zbieranie kanálov ---
channels = []       # list of (cleaned_name, extinf_line, url_line)
seen_names = set()  # deduplication – prvý výskyt vyhráva
pending_extinf = None

for url in urls:
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        lines = response.text.splitlines()
        start_idx = 1 if lines and lines[0].strip().startswith("#EXTM3U") else 0

        for line in lines[start_idx:]:
            stripped = line.strip()
            if not stripped:
                continue

            if stripped.startswith("#EXTINF"):
                parts = stripped.rsplit(",", 1)
                if len(parts) == 2:
                    inf_part, name_part = parts[0], parts[1]
                    cleaned_name = clean_channel_name(name_part)

                    inf_part = re.sub(r'\s*tvg-id="[^"]*"', '', inf_part)
                    inf_part = re.sub(r'\s*tvg-name="[^"]*"', '', inf_part)
                    inf_part = re.sub(r'\s*tvg-chno="[^"]*"', '', inf_part)

                    spravne_id = CHANNEL_MAPPING.get(cleaned_name)
                    if spravne_id:
                        inf_part = inf_part.replace(
                            '#EXTINF:-1',
                            f'#EXTINF:-1 tvg-id="{spravne_id}" tvg-name="{cleaned_name}"'
                        )
                    else:
                        inf_part = inf_part.replace(
                            '#EXTINF:-1',
                            f'#EXTINF:-1 tvg-name="{cleaned_name}"'
                        )
                    pending_extinf = (cleaned_name, f"{inf_part},{cleaned_name}")
                else:
                    pending_extinf = None

            elif not stripped.startswith("#") and pending_extinf:
                cleaned_name, extinf_line = pending_extinf
                if cleaned_name not in seen_names:
                    seen_names.add(cleaned_name)
                    channels.append((cleaned_name, extinf_line, stripped))
                pending_extinf = None
            else:
                pending_extinf = None

    except Exception as e:
        print(f"Zlyhalo spojenie s {url}: {e}")

# --- zoradenie: podľa chno (potom abecedne pre ostatné) ---
max_chno = max(CHANNEL_CHNO.values()) + 1  # = 89
channels.sort(key=lambda item: (
    CHANNEL_CHNO.get(item[0], max_chno),
    item[0]
))

# --- zostavenie výsledného m3u s pevným tvg-chno ---
merged_content = [f'#EXTM3U url-tvg="{merged_epg_url}"']
next_chno = max_chno  # číslovanie pre kanály mimo zoznamu (89, 90, ...)

for cleaned_name, extinf_line, url_line in channels:
    chno = CHANNEL_CHNO.get(cleaned_name, next_chno)
    if chno == next_chno:
        next_chno += 1
    extinf_line = extinf_line.replace('#EXTINF:-1', f'#EXTINF:-1 tvg-chno="{chno}"', 1)
    merged_content.append(extinf_line)
    merged_content.append(url_line)

with open("sk_cz_iptv.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(merged_content))

print(f"Playlist vytvorený: {len(channels)} kanálov, zoradených podľa CHANNEL_CHNO.")
