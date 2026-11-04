#!/usr/bin/env python3
"""Génère une page Hugo par référence à partir de publications.bib.

Usage : python3 scripts/import_publications.py

Lit `publications.bib` (racine du dépôt) et (ré)écrit `content/publications/<clé>/`
(index.en.md en anglais, index.fr.md en français, cite.bib). Les dossiers générés sont
recréés à chaque exécution.

Version anglaise : `publications-en.json` associe à une clé BibTeX soit la traduction
du titre (affichée entre crochets après le titre original), soit {"title": "..."} pour
remplacer tout le titre (recensions, entretiens). Une clé absente laisse le titre tel quel.
Aucune dépendance : bibliothèque standard Python uniquement.

Le champ `keywords` donne la rubrique :
  acl → articles ; ouvrage, direction, numero → ouvrages ; chapitre → chapitres ;
  communication → communications ; cahier → rapports ; revue, diffusion → autres.
"""

import html
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIB = ROOT / "publications.bib"
TRAD = ROOT / "publications-en.json"
OUT = ROOT / "content" / "publications"

RUBRIQUES = {
    "acl": "article",
    "ouvrage": "livre",
    "direction": "livre",
    "numero": "livre",
    "chapitre": "chapitre",
    "communication": "communication",
    "cahier": "rapport",
    "revue": "autre",
    "diffusion": "autre",
}
MOIS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
OWNER = "Peneranda"


# ---------------------------------------------------------------- lecture BibTeX
def read_braced(s, i):
    """s[i] == '{' ; renvoie (contenu, index après l'accolade fermante)."""
    depth, j = 0, i
    while j < len(s):
        c = s[j]
        if c == "\\":
            j += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    raise ValueError("accolade non fermée")


def parse_bib(text):
    entries = []
    for m in re.finditer(r"@(\w+)\s*\{\s*([^,\s]+)\s*,", text):
        etype, key = m.group(1).lower(), m.group(2)
        if etype in ("comment", "string", "preamble"):
            continue
        start = m.start()
        _, end = read_braced(text, text.index("{", m.start()))
        body = text[m.end():end - 1]
        fields, i = {}, 0
        while i < len(body):
            fm = re.compile(r"\s*,?\s*([A-Za-z_][\w-]*)\s*=\s*").match(body, i)
            if not fm:
                break
            name, i = fm.group(1).lower(), fm.end()
            if body[i] == "{":
                val, i = read_braced(body, i)
            elif body[i] == '"':
                k = body.index('"', i + 1)
                val, i = body[i + 1:k], k + 1
            else:
                vm = re.compile(r"[^,\s}]+").match(body, i)
                val, i = vm.group(0), vm.end()
            fields[name] = " ".join(val.split())
        entries.append({"type": etype, "key": key, "fields": fields,
                        "raw": text[start:end]})
    return entries


# ---------------------------------------------------------------- mise en forme
def latex(s, as_html=True):
    s = s.replace("--", "–").replace("\\&", "&")
    out, i = [], 0
    while i < len(s):
        if s.startswith("\\emph{", i) or s.startswith("\\textit{", i):
            inner, i = read_braced(s, s.index("{", i))
            t = latex(inner, as_html)
            out.append(f"<em>{t}</em>" if as_html else t)
            continue
        c = s[i]
        if c in "{}":
            i += 1
            continue
        out.append(html.escape(c, quote=False) if as_html else c)
        i += 1
    return "".join(out)


def short_name(name):
    name = name.strip()
    if name.startswith("{") and name.endswith("}"):
        return latex(name[1:-1], False)
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
        initials = []
        for part in re.split(r"\s+", first):
            pieces = [p for p in part.split("-") if p]
            initials.append("-".join(p if p.endswith(".") else p[0] + "." for p in pieces))
        return f"{latex(last, False)}, {' '.join(initials)}"
    return latex(name, False)


def people(field, bold=True):
    names = [short_name(n) for n in re.split(r"\s+and\s+", field)]
    return ", ".join(
        f"<strong>{html.escape(n)}</strong>" if bold and n.startswith(OWNER + ",")
        else html.escape(n)
        for n in names)


def end_punct(s):
    return s if re.search(r"[?!.…]$", re.sub(r"<[^>]+>", "", s)) else s + "."


# Libellés propres à chaque langue
TXT = {
    "fr": {"no": "n°", "pp": "p.", "ed": "dir.", "eds": "dir.", "colon": " : "},
    "en": {"no": "no.", "pp": "pp.", "ed": "Ed.", "eds": "Eds.", "colon": ": "},
}
NOTES_EN = {
    "entretien": "interview",
    "témoignage": "testimony",
    "numéro thématique": "special issue",
    "collection marcel de corte, dirigée par adrien peneranda":
        "Marcel De Corte collection, series editor A. Peneranda",
}


def note_text(note, lang):
    t = latex(note)
    if lang == "en":
        return NOTES_EN.get(t.lower(), t)
    return t


def vol_num(f, lang):
    v, n = f.get("volume"), f.get("number")
    if v and n:
        return f"{latex(v)} ({latex(n)})"
    if v:
        return latex(v)
    if n:
        return f"{TXT[lang]['no']} {latex(n)}"
    return ""


def editors(field, lang, bold=False):
    many = len(re.split(r"\s+and\s+", field)) > 1
    return f"{people(field, bold=bold)} ({TXT[lang]['eds' if many else 'ed']})"


def title_for(e, lang, tr):
    """Titre HTML : original en français ; en anglais, original + [traduction]
    ou remplacement complet, d'après publications-en.json."""
    f = e["fields"]
    title = latex(f.get("title", ""))
    if lang == "en":
        t = tr.get(e["key"])
        if isinstance(t, dict) and t.get("title"):
            return latex(t["title"])
        if isinstance(t, str) and t:
            return f"{title} [{latex(t)}]"
    return title


def citation(e, lang, title):
    f, t = e["fields"], e["type"]
    L = TXT[lang]
    rub = f.get("keywords", "")
    year = f.get("year", "")
    note = f.get("note", "")
    parts = []

    if t == "book" and rub == "numero":
        head = f"{editors(f['editor'], lang, bold=True)} ({year})."
        vn = vol_num(f, lang)
        venue = f"<em>{latex(f.get('series', ''))}</em>" + (f", {vn}" if vn else "")
        return f"{head} {end_punct(title)} {venue} [{note_text(note, lang).lower()}]."

    who = people(f.get("author") or f.get("editor", ""))
    head = f"{who} ({year})."

    if t == "article":
        bits = [f"<em>{latex(f.get('journal', ''))}</em>"]
        if vol_num(f, lang):
            bits.append(vol_num(f, lang))
        if f.get("pages"):
            bits.append(f"{L['pp']} {latex(f['pages'])}")
        tail = ", ".join(bits)
        if note:
            tail += f" [{note_text(note, lang).lower()}]"
        parts = [end_punct(title), tail + "."]
    elif t == "incollection":
        bits = []
        if f.get("editor"):
            bits.append(f"In {editors(f['editor'], lang)}, <em>{latex(f['booktitle'])}</em>")
        else:
            bits.append(f"In <em>{latex(f['booktitle'])}</em>")
        if f.get("pages"):
            bits.append(f"{L['pp']} {latex(f['pages'])}")
        pub = latex(f.get("publisher", ""))
        if f.get("address"):
            pub = f"{latex(f['address'])}{L['colon']}{pub}"
        parts = [end_punct(title), ", ".join(bits) + ".", end_punct(pub)]
    elif t == "inproceedings":
        loc = f", {latex(f['address'])}" if f.get("address") else ""
        parts = [end_punct(title), f"In <em>{latex(f.get('booktitle', ''))}</em>{loc}."]
    elif t == "book":
        pub = latex(f.get("publisher", ""))
        if f.get("address"):
            pub = f"{latex(f['address'])}{L['colon']}{pub}"
        parts = [end_punct(title), end_punct(pub)]
        if note:
            parts.append(end_punct(note_text(note, lang)))
    elif t == "techreport":
        kind = f"<em>{latex(f.get('type', ''))}</em>"
        if f.get("number"):
            kind += f" {latex(f['number'])}"
        parts = [end_punct(title), f"{kind}, {latex(f.get('institution', ''))}."]
    else:  # misc et autres
        tail = f" [{note_text(note, lang).lower()}]" if note else ""
        parts = [title + tail + "."]
    return " ".join([head] + [p for p in parts if p])


def venue_text(e):
    f = e["fields"]
    for k in ("journal", "booktitle", "series", "publisher", "institution"):
        if f.get(k):
            return latex(f[k], False)
    return ""


def clean_bibtex(raw):
    lines = [l for l in raw.splitlines() if not re.match(r"\s*keywords\s*=", l)]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- écriture
def main():
    entries = parse_bib(BIB.read_text(encoding="utf-8"))
    tr = json.loads(TRAD.read_text(encoding="utf-8")) if TRAD.exists() else {}
    for d in OUT.iterdir():
        if d.is_dir():
            shutil.rmtree(d)
    seen, sans_trad = set(), []
    for e in entries:
        f, key = e["fields"], e["key"]
        if key in seen:
            sys.exit(f"Clé BibTeX en double : {key}")
        seen.add(key)
        rub = f.get("keywords", "").strip()
        if rub not in RUBRIQUES:
            sys.exit(f"{key} : rubrique « {rub} » inconnue (champ keywords)")
        if key not in tr:
            sans_trad.append(key)
        year = int(f["year"])
        month = MOIS.get(f.get("month", "").lower()[:3], 1)
        hal = f.get("hal", "")
        hal_url = f.get("url") or (f"https://hal.science/{hal}" if hal else "")
        bib = clean_bibtex(e["raw"])
        d = OUT / key
        d.mkdir(parents=True)
        (d / "cite.bib").write_text(bib, encoding="utf-8")
        for lang, fname in (("en", "index.en.md"), ("fr", "index.fr.md")):
            titre = title_for(e, lang, tr)
            front = {
                "title": re.sub(r"<[^>]+>", "", html.unescape(titre)),
                "date": f"{year:04d}-{month:02d}-01",
                "key": key,
                "type_pub": RUBRIQUES[rub],
                "rubrique": rub,
                "auteurs": people(f.get("author") or f.get("editor", "")),
                "citation": citation(e, lang, titre),
                "titre_html": titre,
                "lieu": venue_text(e),
                "hal": hal_url,
                "bibtex": bib,
            }
            (d / fname).write_text(json.dumps(front, ensure_ascii=False, indent=2) + "\n",
                                   encoding="utf-8")
    inconnues = sorted(set(tr) - seen)
    print(f"{len(entries)} publications importées depuis {BIB.name}")
    if sans_trad:
        print(f"Sans entrée dans {TRAD.name} (titre laissé tel quel en anglais) : "
              + ", ".join(sans_trad))
    if inconnues:
        print(f"Clés de {TRAD.name} absentes du .bib (ignorées) : " + ", ".join(inconnues))


if __name__ == "__main__":
    main()
