#!/usr/bin/env python3
"""
reorder.py  —  správa poradia kanálov v merge.py

Ako používať:
  1. Pridaj nový kanál na správne miesto v zozname CHANNEL_ORDER nižšie
     (presný cleaned_name — rovnaký ako tvg-name v sk_cz_iptv.m3u)
  2. Spusti:  python reorder.py
  3. Skript automaticky prepíše blok CHANNEL_CHNO v merge.py
     so sekvenčnými číslami 1, 2, 3... podľa tohto poradia
  4. Commitni oba súbory (reorder.py + merge.py) do GitHubu

Kanály z cache-sk, ktoré nie sú v iptv-org, sa NEZOBRAZÍ
v sk_cz_iptv.m3u — ale ich číslo tu nastavíš, aby keď sa objavia
v iptv-org, alebo keď cache-sk tiež nasadí tvg-chno, sedeli správne.

Kanály, ktoré nie sú v tomto zozname, dostanú v merge.py
automaticky čísla za posledným (napr. 89, 90, 91...).
"""

CHANNEL_ORDER = [
    # 1–13: Hlavné SK stanice (cache-sk)
    "JOJ Cinema",
    "Nova Cinema",
    # 14–22: Film / Entertainment (sk-cz-iptv)
    "FilmBox+ One Czech Republic",
    "FilmBox+ Love & Crime Czech Republic",
    "FilmBox+ Hits Czech Republic",
    "FilmBox+ Emotion Czech Republic",
    "AMC Europe Czech Republic",
    "AXN CEE Czech Republic",
    "AXN Black Czech Republic",
    "AXN White Czech Republic",
    "AXN White",
    # 23–29: Česká verejnoprávna + CS stanice (cache-sk)
    "ČT 1",
    "ČT 2",
    "Barrandov Krimi",
    "CS Film",
    "CS History",
    "History",
    "CS Mystery",
    # 30–39: Šport (mix)
    ":Šport",
    "JOJ Šport",
    "JOJ Šport 2",
    "Sport1",
    "Sport2",
    "ČT Sport",
    "Sporty TV",
    "Golf Channel",
    "Arena Sport 1",
    "Arena Sport 2",
    # 40–51: Spravodajstvo + špeciálne (mix)
    ":24",
    "JOJ 24",
    "TA3",
    "ČT24",
    "CNN Prima News",
    "Live NRSR",
    "Jojko",
    "ČT:D/ČT art",
    "TV Doktor",
    "SZTŠ",
    "Live :O",
    "Live RTVS",
    # 52–65: Záujmové / Hudba / Náboženské (sk-cz-iptv)
    "Elektrika TV",
    "Mňau TV",
    "TV Noe",
    "TV Noe+",
    "LifeTv",
    "Televízia OSEM",
    "Óčko",
    "Óčko Expres",
    "Ocko Black",
    "Ocko Star",
    "Retro Music Television",
    "Senzi",
    "Slager Original",
    "Slager Muzika",
    # 66–88: Regionálne / Lokálne (sk-cz-iptv)
    "Antik Info TV",
    "Zapadoslovenska TV",
    "TV Ružinov",
    "TV Central",
    "TV Nitricka",
    "TV LocAll",
    "TV Povazie",
    "TVT",
    "TV Liptov",
    "MTR",
    "TV Mistral",
    "Televízia Močenok",
    "TV9",
    "TV Brno 1",
    "Jihočeská televize",
    "JČ1",
    "Východočeská TV",
    "ÚTV",
    "Plzeň TV",
    "Polar TV",
    "Polar2 TV",
    "Régió TV",
    "RTG int.",
]

# ================================================================
# — od tu nadol nemeň nič —
# ================================================================
import re
import os

MERGE_PY = os.path.join(os.path.dirname(__file__), "merge.py")

BLOCK_START = "# <<< CHANNEL_CHNO_START >>>"
BLOCK_END   = "# <<< CHANNEL_CHNO_END >>>"


def generate_chno_block(order: list) -> str:
    lines = [
        "CHANNEL_CHNO = {",
        "    # Generované automaticky cez reorder.py — nemeň ručne",
    ]
    for i, name in enumerate(order, start=1):
        escaped = name.replace('"', '\\"')
        lines.append(f'    "{escaped}": {i},')
    lines.append("}")
    return "\n".join(lines)


def update_merge_py(order: list) -> None:
    with open(MERGE_PY, "r", encoding="utf-8") as f:
        content = f.read()

    new_block = (
        BLOCK_START + "\n"
        + generate_chno_block(order) + "\n"
        + BLOCK_END
    )

    # ak už tam sú markery, nahraď blok medzi nimi
    pattern = re.compile(
        re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END),
        re.DOTALL
    )
    if pattern.search(content):
        new_content = pattern.sub(new_block, content)
    else:
        # prvé spustenie — markery ešte nie sú, vložíme za definíciu merged_epg_url
        # (hľadáme riadok "merged_epg_url = ..." a vložíme za neho)
        insert_after = re.compile(r"(merged_epg_url\s*=\s*\"[^\"]*\"\s*\n)")
        if insert_after.search(content):
            new_content = insert_after.sub(
                r"\1\n" + new_block + "\n",
                content,
                count=1
            )
        else:
            print("CHYBA: Nenašiel som kde vložiť CHANNEL_CHNO do merge.py.")
            print("Uisti sa, že merge.py obsahuje riadok:  merged_epg_url = \"...\"")
            return

    with open(MERGE_PY, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✓ merge.py aktualizovaný — {len(order)} kanálov očíslovaných 1–{len(order)}")
    print(f"  Kanály mimo zoznamu dostanú čísla {len(order)+1}+")


if __name__ == "__main__":
    if not os.path.exists(MERGE_PY):
        print(f"CHYBA: {MERGE_PY} neexistuje. Spusti reorder.py z rovnakého priečinka ako merge.py.")
    else:
        update_merge_py(CHANNEL_ORDER)
