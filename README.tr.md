# ses-grubu-metin

**İlk okuma yazma öğretimi için ses grubuna göre kelime ve cümle üretici**

Öğrencilerin henüz öğrendiği harflerle yazılabilen kelimeleri ve basit cümleleri
açık lisanslı sözlükten süzen öğretmen aracı. Herhangi bir harf kümesiyle
çalışır; MEB müfredatına uygun hazır profiller de içerir.

## Özellikler

- **Harf kümesi süzme**: istediğiniz harfleri (örn. `elakin`) girin, yalnız o
  harflerden oluşan kelimeleri alın
- **Hece gruplandırma**: kelimeler hece sayısına göre (1, 2, 3) gruplanır
- **Sıklık sırası**: kelimeler en sık kullanılandan başlar (OpenSubtitles
  derlemi); `--sirala` ile alfabetik ya da dosya sırası seçilebilir
- **Küfür/uygunsuz kelime filtresi**: yerleşik kara liste ile elenir
- **Hazır profiller**: klasik (ELAKİN, OMUTÜY) ve Türkiye Yüzyılı Maarif Modeli
  grupları (anetil, okurım, üsöydz, çbgcş, phvğfj)
- **Şablonlu cümle üretimi**: sözcük türü *ve* fiil çekimiyle etiketlenmiş küçük
  bir çekirdek sözlükten kurulan cümleler; özne yalnız 3. tekil fiille, nesne
  yalnız eşleşen fiille birleşir — *isteğe bağlı*
- **HTML/Metin çıktısı**: yazdırmaya uygun HTML veya düz metin
- **Tekrarlanabilir çıktı**: `--tohum` ile cümle seçimi sabitlenir

## Kurulum

```bash
pipx install ses-grubu-metin
# veya
pip install ses-grubu-metin
```

Python 3.10+ gerekir. Heceleme yerleşik Türkçe kurallarıyla yapılır;
çalışma zamanı bağımlılığı yoktur.

## 30 Saniyelik Hızlı Başlangıç

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

Varsayılan üç hece sınırında (`--harfler "elakin"`) sayılar şöyledir:

```text
Harfler: A E İ K L N
Toplam Kelime: 191
1 Heceli (34 kelime):
2 Heceli (104 kelime):
3 Heceli (53 kelime):
```

Bitişik ünlüler ayrı sayılır: `aile` üç hecelidir ve iki hecelik örnekte yer almaz.

```bash
# Yazdırmaya hazır HTML
$ ses-grubu-metin --profil elakin --cumle-sayisi 10 -o liste.html
Çıktı yazıldı: liste.html
```

```bash
# Maarif Modeli (2024) profili
$ ses-grubu-metin --profil anetil --en-cok-hece 3 -o maarif.html
```

```bash
# Tekrarlanabilir cümleler (klasik 1-3. gruplar): aynı tohum aynı çıktı
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

## Cümle Üretimi

Cümle üretimi isteğe bağlıdır (`--cumle-sayisi N`; tekrarlanabilirlik için
`--tohum N`). Bir cümle yalnız `veri/cekirdek_sozcukler.txt` içinde bulunan,
seçilen harf süzgecinden geçen ve küfür kara listesinde yer almayan sözcükleri
kullanabilir.

Çekirdek sözlükteki her giriş sınıfı ve fiil çekimiyle etiketlidir:

| Etiket grubu | Örnekler | Cümledeki yeri |
|--------------|----------|----------------|
| `kisi` / `hayvan` | `ali`, `anne`, `kedi`, `kuş` | özne (hayvanlar okuma/yazma yapmaz) |
| `yiyecek` / `icecek` / `okunacak` / `esya` | `elma`, `süt`, `kitap`, `top` | nesne |
| `fiil` / `gidis` / `yeme` / `icme` / `okuma` / `yazma` / `tutma` / `atma` / `sevme` | `uyur`, `gider`, `yer` | 3. tekil yüklem |
| `emir` / `emir_gidis` / `emir_yeme` / ... | `otur`, `gel`, `oku` | emir yüklemi |

Şablonlar yalnız uyumlu etiketleri birleştirir; bu yüzden özne emir kipiyle,
hayvan okuma fiiliyle eşleşmez.

Uygulamada: Türkçede 3. tekil kişi eki `-r`'dir (`okur`, `gider`). Bu nedenle
`elakin` gibi erken harf kümelerinde özne + fiil cümlesi kurulamaz; klasik 3.
gruptan itibaren havuz genişler. Hiç cümle kurulamazsa CLI stderr'e uyarı yazar
ve yine de `0` ile çıkar (asıl çıktı kelime listesidir).

## Kütüphane API'si

CLI, kütüphanenin ince bir katmanıdır; aynı süzgeçler Python'dan da kullanılabilir
(ek bağımlılık yok, dosya yazmak gerekmez):

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
print(sonuc.toplam_kelime)         # 138
print(sonuc.hece_gruplari[2][:5])  # ['ile', 'iki', 'anne', 'alan', 'kalan']
print(metin_cikti(sonuc, max_hece=2))
```

- `cocuk_sozlugu_olustur(ham_kelimeler, max_hece=3, min_uzunluk=2, max_uzunluk=10)`
  CLI'ın kullandığı pedagojik uzunluk ve alt dize kara liste süzgeçlerini uygular.
- `kelimeleri_suz(kelimeler, izinli_harfler, max_hece=3, kara_liste=None, sirala="siklik", siklik=None)`
  bir `SuzmeSonucu` döndürür (`kelimeler`, `hece_gruplari`, `toplam_kelime`, `izinli_harfler`);
  doğrudan `sozluk_yukle()` üzerinde çağrıldığında yalnız tam eşleşme kara listesini uygular.
- `cumle_olustur(kelimeler, izinli_harfler, max_cumle=10, rastgele_tohum=None, cekirdek=None, kara_liste=None)`
  hem harf kümesini hem küfür kara listesini denetleyerek şablonlu cümleler üretir.
- `harfleri_dogrula()` / `harfleri_normalize()` harf kümesini doğrular ve normalize
  eder (`"ELAKİN"` -> `"aeikln"`; noktalı/noktasız i korunur).
- `html_cikti()` / `metin_cikti()` sonucu metin olarak ya da dosyaya yazar.

Harf kümesi her genel giriş noktasında doğrulanır: yalnız Türk alfabesinin 29 harfi
kabul edilir; `"elakin!"`, `"ela kin"` ve Kiril harfleri sessizce boş liste üretmek
yerine `ValueError` verir. HTML çıktısı gömülen her dinamik değeri (sayfa başlığı
dahil) kaçışlar (`&lt;`, `&amp;`, tırnaklar).

## Gerçek Kullanım Senaryoları

1. **Haftalık okuma kâğıdı**: o haftanın harf grubuyla kelime listesi
2. **Dikte çalışması**: yalnız öğrenilmiş harflerle dikte sözcükleri
3. **Yetişkin okuma yazma kursu**: kursiyerin bulunduğu harf kümesine uygun materyal

## CLI Kullanımı

```bash
ses-grubu-metin --harfler "elakin" [seçenekler]
ses-grubu-metin --profil elakin [seçenekler]
```

### Zorunlu (tam olarak bir tanesi):
- `--harfler "harfler"` — özel harf kümesi (örn. `elakin`, `anetil`); büyük/küçük harf fark etmez
- `--profil AD` — hazır profil (aşağıdaki tablo)
- `--lisans` — veri lisans bilgisini yazdırır
- `--profil-listesi` — mevcut profilleri listeler

### Seçenekler:
- `--en-cok-hece N` — maksimum hece sayısı (1, 2, 3; varsayılan: 3)
- `--cumle-sayisi N` — örnek cümle sayısı (varsayılan: 0; negatif olamaz)
- `--tohum N` — cümle seçimi için rastgele tohum (verilmezse her çalıştırmada farklı)
- `-o, --cikti DOSYA` — çıktı dosyası (varsayılan: stdout)
- `--format html|txt` — çıktı biçimi; verilmezse uzantıdan çıkarılır (`.html` →
  html, diğerleri txt). `--format` ile uzantı çelişirse komut sessizce yanlış
  biçim üretmek yerine hata verir
- `--sirala siklik|alfabetik|giris` — kelime sırası: derlem sıklığı (varsayılan),
  alfabetik veya sözlük dosyasındaki sıra
- `--sozluk DOSYA` — özel kelime listesi (her satırda bir kelime)
- `--version` — sürümü gösterir

Çıkış kodları: `0` başarılı, `1` geçersiz girdi, okunamayan sözlük dosyası veya
yazılamayan çıktı dosyası, `2` komut satırı kullanım hatası (argparse, çelişen
`--format` ve uzantı).

## Profiller (MEB Müfredatı)

| Profil | Harfler | Kaynak |
|--------|---------|--------|
| `elakin` | e l a k i n | Klasik 1. grup |
| `omutuy` | o m u t ü y | Klasik 2. grup |
| `anetil` | a n e t i l | Maarif Modeli 1. grup |
| `okurim` | o k u r ı m | Maarif Modeli 2. grup |
| `usoydz` | ü s ö y d z | Maarif Modeli 3. grup |
| `cbgcs` | ç b g c ş | Maarif Modeli 4. grup |
| `phvgfj` | p h v ğ f j | Maarif Modeli 5. grup |

Türkçedeki noktalı/noktasız i ayrımına dikkat: 1. grup **i**, 2. grup **ı**
harfini öğretir. Profiller kolaylık içindir; resmî MEB ürünü değildir.

## Veri Kaynakları ve Lisanslar

- **Sözlük**: [Turkish Dictionary Dataset](https://github.com/ahakanacar/turkish-dictionary-dataset-and-statistics) (MIT)
- **Sıklık sıralaması** (`veri/siklik.txt`): [FrequencyWords](https://github.com/hermitdave/FrequencyWords)
  Türkçe OpenSubtitles 2018 listesi (CC-BY-SA 4.0); yalnız projedeki sözlükte
  de bulunan sözcükler alınmıştır
- **Küfür filtresi**: [turkce-kufur-karaliste](https://github.com/ooguz/turkce-kufur-karaliste) (CC-BY-SA 4.0)
- **Heceleme**: yerleşik Türkçe hece kuralları
- **Çekirdek cümle sözlüğü** (`veri/cekirdek_sozcukler.txt`): bu proje için yazıldı (MIT)
- **Proje kodu**: MIT

Ayrıntılar: `veri/LISANS-KAYNAK.md`.

## Sınırlamalar

- Resmî bir MEB uygulaması **değildir**; pedagojik onay iddiası yoktur
- Harf kümesi Türk alfabesiyle sınırlıdır; `q`, `w`, `x` gibi harfleri içeren
  sözcükler özel sözlükten bile istenemez
- Sözlük ~62.000 girdi içerir; seyrek ve alıntı sözcükler de bulunur (`kail`,
  `klan` gibi). Özellikle ilk sınıflarda öğretmen gözden geçirmesi beklenir
- Sıklık dereceleri film/dizi alt yazılarından gelir; bu yüzden işlev sözcükleri
  (`ne`, `ki`, `en`) listenin başında görünür ve ~62.000 sözcüğün ~34.000'inin
  sırası vardır, kalanı alfabetik olarak sona eklenir. Yansız sıra için
  `--sirala alfabetik` kullanın
- Küfür kara listesi topluluk kaynaklıdır ve tam olduğu iddia edilemez
- Cümleler yalnız çekirdek sözlükten ve harf süzgecinden geçen sözcüklerle
  kurulur. Şablonlar özne sınıfını, nesne sınıfını ve fiil çekimini denetler;
  "Ali gel." gibi çekim uyumsuzluğu ya da "İnek kitap okur." gibi sınıf hatası
  oluşamaz. Anlam doğallığı yine de garanti edilmez ("Kedi uçar."), çekirdek
  sözlük bilinçli olarak küçüktür. Cümle üretimi varsayılan olarak kapalıdır
- Bitişik ünlüler dahil her Türkçe ünlü bir hece sayılır

## Geliştirme

```bash
python -m venv .venv
source .venv/Scripts/activate      # Windows (Git Bash); Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"

# Hepsi: ruff lint, ruff biçim, mypy, pytest, >=%85 kapsam eşiği
bash scripts/check.sh

# Tek tek
pytest -q
ruff check src tests
mypy src/ses_grubu
```

`scripts/check.sh` proje kökünde `.venv` varsa onu kendiliğinden kullanır
(etkinleştirme gerekmez); çalışma zamanı veya geliştirme bağımlılıkları eksikse
açıkça hata verir ve hiçbir kontrolü sessizce atlamaz.

## Proje Yapısı

```
src/ses_grubu/
├── __init__.py      # Paket dışa aktarımları
├── cli.py           # Komut satırı arayüzü
├── hece.py          # Hece sayımı (Türkçe kurallar)
├── sozluk.py        # Sözlük ve çekirdek sözlük yükleme, pedagojik filtreler
├── suz.py           # Harf kümesi süzme motoru
├── cumle.py         # Şablonlu cümle üretimi
├── cikti.py         # HTML/Metin çıktı biçimlendirme
├── turkce.py        # Türkçe büyük/küçük harf yardımcıları
└── veri/            # Paketlenen veri (kelime listesi, sıklık sırası, kara liste,
                     # çekirdek sözlük, lisanslar)

veri/                # Aynı dosyalar depo kökünde (testler eşitliği doğrular)
├── sozcukler.txt
├── siklik.txt
├── profanity.txt
├── cekirdek_sozcukler.txt
└── LISANS-KAYNAK.md
```
