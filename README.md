# ses-grubu-metin

**Turkish phonics-based word/sentence generator for 1st grade literacy teachers**

Generate word lists and simple sentences using only the letters students have
learned so far. Built for Turkish first-grade literacy teaching (MEB curriculum),
usable with any custom letter set.

## Features

- **Letter-set filtering**: give any letter set (e.g. `elakin`) and get only words
  spelled with those letters
- **Syllable grouping**: words grouped by syllable count (1, 2, 3)
- **Frequency ordering**: words come most-frequent first (OpenSubtitles corpus
  ranking), or alphabetical / file order via `--sirala`
- **Profanity filtering**: built-in blacklist drops inappropriate words
- **Curriculum profiles**: classic (ELAKİN, OMUTÜY) and Türkiye Yüzyılı Maarif
  Modeli groups (anetil, okurım, üsöydz, çbgcş, phvğfj)
- **Sentence generation**: template sentences built from a small curated
  vocabulary tagged by word class *and* verb form, so subjects only pair with
  3rd-person verbs and objects only with matching verbs — *opt-in*
- **HTML/Text output**: print-ready HTML or plain text
- **CLI**: one command, no configuration
- **Reproducible output**: `--tohum` makes sentence selection repeatable

## Installation

```bash
pipx install ses-grubu-metin
# or
pip install ses-grubu-metin
```

Requires Python 3.10+. Syllables are counted with built-in Turkish rules;
there are no runtime dependencies.

## Quick Start (30 seconds)

```bash
$ ses-grubu-metin --harfler "elakin" --en-cok-hece 2
SES GRUBU KELİME LİSTESİ
========================================
Harfler: A E İ K L N
Toplam Kelime: 138
Max Heceler: 2
Sıralama: Sıklık (en sık kullanılan önce)
Tarih: 05.11.2026 05:22


1 Heceli (34 kelime):
------------------------------
  ne
  ki
  en
  in
  ilk
  al
  ...

2 Heceli (104 kelime):
------------------------------
  ile
  iki
  anne
  alan
  kalan
  ...
```

With the default three-syllable limit (`--harfler "elakin"`), the counts are:

```text
Harfler: A E İ K L N
Toplam Kelime: 191
1 Heceli (34 kelime):
2 Heceli (104 kelime):
3 Heceli (53 kelime):
```

Adjacent vowels count separately: `aile` has three syllables and therefore
does not appear in the two-syllable example.

```bash
# Print-ready HTML for the current letter group
$ ses-grubu-metin --profil elakin --cumle-sayisi 10 -o liste.html
Çıktı yazıldı: liste.html
```

```bash
# Maarif Modeli (2024) profile
$ ses-grubu-metin --profil anetil --en-cok-hece 3 -o maarif.html
```

```bash
# Reproducible sentences (classic groups 1-3): the same seed, the same output
$ ses-grubu-metin --harfler "elakinomutüyörıdsb" --cumle-sayisi 6 --tohum 3
...
ÖRNEK CÜMLELER
========================================
  Ela okur.
  Kedi yer.
  Dede elma yer.
  Kedi armut yer.
  Ela kalem tutar.
  Ali kalem atar.
```

## Sentence Generation

Sentence generation is opt-in (`--cumle-sayisi N`, `--tohum N` for reproducibility).
A sentence can only use words that are in `veri/cekirdek_sozcukler.txt`, pass the
letter filter for the chosen letters, and are not on the profanity blacklist.

The core vocabulary tags every entry with its class and verb form:

| Tag group | Examples | Used as |
|-----------|----------|---------|
| `kisi` / `hayvan` | `ali`, `anne`, `kedi`, `kuş` | subject (animals never read or write) |
| `yiyecek` / `icecek` / `okunacak` / `esya` | `elma`, `süt`, `kitap`, `top` | object |
| `fiil` / `gidis` / `yeme` / `icme` / `okuma` / `yazma` / `tutma` / `atma` / `sevme` | `uyur`, `gider`, `yer` | 3rd-person singular predicate |
| `emir` / `emir_gidis` / `emir_yeme` / ... | `otur`, `gel`, `oku` | imperative predicate |

Templates combine only compatible tags, which is why a subject is never paired with
an imperative and why an animal never gets a reading verb.

Practical consequence: Turkish 3rd-person forms end in `-r` (`okur`, `gider`), so
early letter sets such as `elakin` cannot form subject sentences yet; from the third
classic group onwards the pool widens. If no sentence can be built, the CLI prints a
warning to stderr and still exits `0` (the word list is the main output).

## Library API

The CLI is a thin layer over the library, so the same filters are available from
Python (no extra dependencies, no file output required):

```python
from ses_grubu import (
    cocuk_sozlugu_olustur,
    harflere_uyanlar,
    kelimeleri_suz,
    metin_cikti,
    sozluk_yukle,
)

adaylar = cocuk_sozlugu_olustur(harflere_uyanlar(sozluk_yukle(), "ELAKİN"), max_hece=2)
sonuc = kelimeleri_suz(adaylar, "ELAKİN", max_hece=2)
print(sonuc.toplam_kelime)        # 138
print(sonuc.hece_gruplari[2][:5])  # ['ile', 'iki', 'anne', 'alan', 'kalan']
print(metin_cikti(sonuc, max_hece=2))
```

- `cocuk_sozlugu_olustur(ham_kelimeler, max_hece=3, min_uzunluk=2, max_uzunluk=10)`
  applies the pedagogical word-length and profanity-substring filters used by the CLI.
- `kelimeleri_suz(kelimeler, izinli_harfler, max_hece=3, kara_liste=None, sirala="siklik", siklik=None)`
  returns a `SuzmeSonucu` (`kelimeler`, `hece_gruplari`, `toplam_kelime`, `izinli_harfler`);
  calling it directly on `sozluk_yukle()` applies only exact-match blacklist filtering.
- `cumle_olustur(kelimeler, izinli_harfler, max_cumle=10, rastgele_tohum=None, cekirdek=None, kara_liste=None)`
  builds template sentences while enforcing both the letter filter and the profanity blacklist.
- `harfleri_dogrula()` / `harfleri_normalize()` normalise a letter set
  (`"ELAKİN"` -> `"aeikln"`, Turkish dotted/dotless i preserved).
- `html_cikti()` / `metin_cikti()` render the result, to a string or a file.

Letter sets are validated at every public entry point: only the 29 letters of the
Turkish alphabet are accepted, so `"elakin!"`, `"ela kin"` and Cyrillic input raise
`ValueError` instead of silently yielding an empty list. HTML output escapes every
dynamic value it embeds (`&lt;`, `&amp;`, quotes), including the page title.

## Real-world Scenarios

1. **Weekly reading sheets**: word list for the letter group of the week
2. **Dictation practice**: words limited to letters already taught
3. **Adult literacy courses**: material at the learner's current letter set

## CLI Reference

```bash
ses-grubu-metin --harfler "elakin" [options]
ses-grubu-metin --profil elakin [options]
```

### Required (exactly one):
- `--harfler "letters"` — custom letter set (e.g. `elakin`, `anetil`); case-insensitive
- `--profil NAME` — predefined profile (see table below)
- `--lisans` — print data license information
- `--profil-listesi` — list available profiles

### Options:
- `--en-cok-hece N` — max syllables (1, 2 or 3; default: 3)
- `--cumle-sayisi N` — number of example sentences (default: 0 = none; must be >= 0)
- `--tohum N` — random seed for sentence selection (default: random each run)
- `-o, --cikti FILE` — output file (default: stdout)
- `--format html|txt` — output format; when omitted it is inferred from the
  file extension (`.html` → html, otherwise txt). A conflicting
  `--format`/extension pair is rejected instead of silently ignored
- `--sirala siklik|alfabetik|giris` — word order: corpus frequency (default),
  alphabetical, or the order used in the dictionary file
- `--sozluk FILE` — custom word list (one word per line)
- `--version` — print version

Exit codes: `0` success, `1` invalid input, unreadable dictionary file or
unwritable output file, `2` command-line usage error (argparse, conflicting
`--format` and extension).

## Profiles (MEB Curriculum)

| Profile | Letters | Source |
|---------|---------|--------|
| `elakin` | e l a k i n | Classic group 1 |
| `omutuy` | o m u t ü y | Classic group 2 |
| `anetil` | a n e t i l | Maarif Modeli group 1 |
| `okurim` | o k u r ı m | Maarif Modeli group 2 |
| `usoydz` | ü s ö y d z | Maarif Modeli group 3 |
| `cbgcs` | ç b g c ş | Maarif Modeli group 4 |
| `phvgfj` | p h v ğ f j | Maarif Modeli group 5 |

Note the Turkish dotted/dotless i: group 1 teaches **i**, group 2 teaches **ı**.
Profiles are convenience presets, not an official MEB product.

## Data Sources & Licenses

- **Word list**: [Turkish Dictionary Dataset](https://github.com/ahakanacar/turkish-dictionary-dataset-and-statistics) (MIT)
- **Frequency ranking** (`veri/siklik.txt`): [FrequencyWords](https://github.com/hermitdave/FrequencyWords)
  Turkish OpenSubtitles 2018 list (CC-BY-SA 4.0); restricted to words that are
  already in the project word list
- **Profanity filter**: [turkce-kufur-karaliste](https://github.com/ooguz/turkce-kufur-karaliste) (CC-BY-SA 4.0)
- **Syllabification**: built-in Turkish syllable rules
- **Core sentence vocabulary** (`veri/cekirdek_sozcukler.txt`): written for this project (MIT)
- **Project code**: MIT

See `veri/LISANS-KAYNAK.md` for details.

## Limitations

- Not an official MEB application; no pedagogical endorsement
- Letter sets are limited to the Turkish alphabet; words containing `q`, `w`, `x`
  or other non-Turkish letters cannot be requested even from a custom dictionary
- The word list holds ~62K entries, including rare and loan words — teacher review
  is expected, especially for early grades
- Frequency ranks come from film/TV subtitles, so function words (`ne`, `ki`, `en`)
  lead the list and ~34K of the ~62K words have a rank; the rest follow
  alphabetically. Use `--sirala alfabetik` when you want a neutral order
- The profanity blacklist is community-sourced and cannot be exhaustive
- Sentences are built only from the curated core vocabulary and only from words
  that pass the letter filter. Templates check subject class, object class and verb
  form, so agreement errors ("Ali gel.") and category errors ("İnek kitap okur.")
  cannot occur; semantic naturalness is still not guaranteed ("Kedi uçar.") and the
  vocabulary is deliberately small. Sentence generation is off by default
- Each Turkish vowel counts as one syllable, including adjacent vowels

## Development

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash); Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

# Everything: ruff lint, ruff format check, mypy, pytest, >=85% coverage gate
bash scripts/check.sh

# Individual steps
pytest -q
ruff check src tests
mypy src/ses_grubu
```

`scripts/check.sh` uses `.venv` automatically when it exists (no activation
needed), fails loudly if runtime or dev dependencies are missing, and never
silently skips a check.

## Project Structure

```
src/ses_grubu/
├── __init__.py      # Package exports
├── cli.py           # Command-line interface
├── hece.py          # Syllable counting (Turkish rules)
├── sozluk.py        # Dictionary + core vocabulary loading, pedagogical filters
├── suz.py           # Letter-set filtering engine
├── cumle.py         # Template-based sentence generation
├── cikti.py         # HTML/Text output formatting
├── turkce.py        # Turkish case conversion helpers
└── veri/            # Packaged data (word list, frequency ranks, blacklist,
                     # core vocabulary, licenses)

veri/                # Same data files at repository root (kept in sync by tests)
├── sozcukler.txt
├── siklik.txt
├── profanity.txt
├── cekirdek_sozcukler.txt
└── LISANS-KAYNAK.md
```
