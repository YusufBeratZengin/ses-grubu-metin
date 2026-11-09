"""Şablonlu basit cümle üretimi (özne + nesne/zarf + yüklem).

Cümleler yalnız izinli harflerden oluşan ve etiketli çekirdek sözlükte
(``veri/cekirdek_sozcukler.txt``) tanımlı kelimelerden kurulur. Etiketler hem
sözcük sınıfını hem çekim biçimini taşır:

- ``kisi`` / ``hayvan``: özne sınıfı (hayvanlar okuma/yazma eylemleri almaz)
- ``yiyecek`` / ``icecek`` / ``okunacak`` / ``esya``: nesne sınıfı
- ``fiil`` / ``gidis`` / ``yeme`` ... : 3. tekil kişi
- ``emir`` / ``emir_gidis`` / ``emir_yeme`` ... : emir kipi

Şablonlar yalnız uyumlu etiketleri bir araya getirdiği için "Ali gel." ya da
"İnek kitap okur." gibi biçimce ya da anlamca bozuk cümleler kurulmaz. Yine de
mutlak anlam garantisi verilmez; öğretmen gözden geçirmelidir.
"""

from __future__ import annotations

import random
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from .sozluk import CEKIRDEK_TURLERI, cekirdek_sozluk_yukle, kara_liste_yukle
from .turkce import harfleri_normalize, kelime_uygun_mu, turkce_lower, turkce_upper


@dataclass(frozen=True)
class Cumle:
    """Oluşturulan cümle."""

    metin: str
    kelimeler: list[str]
    sablon_adi: str


# Cümlelerde özne olarak kullanılabilecek, anlamlı cümle kuran kelimeler.
# Harf kümesi dışında kalanlar üretim sırasında elenir.
OZNE_ADAYLARI = (
    "ali",
    "ayşe",
    "ayse",
    "veli",
    "fatma",
    "ela",
    "ece",
    "can",
    "deniz",
    "kedi",
    "kuş",
    "kus",
    "çocuk",
    "cocuk",
    "anne",
    "baba",
    "kardeş",
    "kardes",
    "öğretmen",
    "ogretmen",
    "bebek",
    "arkadaş",
    "arkadas",
    "insan",
    "kumru",
    "kurt",
    "köpek",
    "kopek",
    "balık",
    "balik",
    "arı",
    "ari",
    "keçi",
    "keci",
    "kuzu",
    "tavşan",
    "tavsan",
    "fare",
    "aslan",
    "kaplan",
    "horoz",
    "tavuk",
    "ördek",
    "ordek",
    "güvercin",
    "guvercin",
)

# Üçüncü tekil şahıs çekimli (geniş/şimdiki zaman) yaygın fiiller.
# Heuristik ek kontrolü yerine kapalı bir liste kullanılır; böylece "elenti",
# "kedi", "anahtar" gibi kelimeler yanlışlıkla fiil sayılmaz.
FIIL_FORMLARI = frozenset(
    """
    açar alır anlar atar ayırır azar başlar bakar biner biter bozar bulur
    büyür böler çeker çıkar çizer dinler doğar döker döner durur düşer eker
    geçer gelir gezer gider görür gösterir güler içer iner ister iter kanar
    kaçar kalkar kapanır kazar keser kırar koşar kovar kurar okur olur oturur
    oynar öder öğrenir ölçer ölür örter pişer saklar sanır satar sayar sever
    sezer siler söyler süzer taşır toplar tutar uçar uyur üzer vurur yakar
    yapar yatar yazar yener yer yıkar yürür
    """.split()
)

# Yer bildiren çekimli zarflar; "masa"/"araba" gibi isimlerle karışmaması
# için tek harflik "-a/-e" kuralı kullanılmaz.
ZARF_FORMlari = frozenset(
    {
        "eve",
        "okula",
        "masaya",
        "evde",
        "okulda",
        "sana",
        "bana",
        "ona",
        "buraya",
        "oraya",
        "şimdi",
        "simdi",
        "sonra",
        "dün",
        "dun",
        "bugün",
        "bugun",
        "yarın",
        "yarin",
    }
)

SIFAT_FORMlari = frozenset(
    {
        "mutlu",
        "güzel",
        "guzel",
        "hızlı",
        "hizli",
        "iyi",
        "kötü",
        "kotu",
        "büyük",
        "buyuk",
        "küçük",
        "kucuk",
        "yeni",
        "eski",
        "sıcak",
        "sicak",
        "soğuk",
        "soguk",
        "uzun",
        "kısa",
        "kisa",
    }
)

SIFAT_SONLARI = ("lı", "li", "lu", "lü", "sız", "siz", "suz", "süz")


def kelime_turu_tahmin(kelime: str) -> str:
    """Kelime türünü kapalı listeler ve dar bir sıfat kuralıyla tahmin eder.

    Fiil tespiti ek tahminiyle değil, bilinen çekimli fiil listesiyle yapılır.
    Bu sayede "-ti", "-di", "-ar" ile biten isimler fiil sanılmaz.

    Returns:
        "fiil", "isim", "sıfat", "zarf" veya "bilinmiyor"
    """
    kelime = turkce_lower(kelime.strip())

    if kelime in FIIL_FORMLARI:
        return "fiil"
    if kelime in ZARF_FORMlari:
        return "zarf"
    if kelime in SIFAT_FORMlari:
        return "sıfat"
    if len(kelime) > 4 and kelime.endswith(SIFAT_SONLARI):
        return "sıfat"
    if kelime.isalpha():
        return "isim"
    return "bilinmiyor"


def kelimeleri_turlerine_gore_ayir(kelimeler: Iterable[str]) -> dict[str, list[str]]:
    """Kelimeleri tahmini türlerine göre gruplar."""
    gruplar: dict[str, list[str]] = {
        "isim": [],
        "fiil": [],
        "sıfat": [],
        "zarf": [],
        "bilinmiyor": [],
    }
    for kelime in kelimeler:
        tur = kelime_turu_tahmin(kelime)
        gruplar[tur].append(kelime)
    return gruplar


@dataclass(frozen=True)
class Sablon:
    """Bir cümle şablonu: özne, ara öge ve yüklem etiketleri.

    Boş alan o cümle metninde o ögenin bulunmadığı anlamına gelir; böylece
    emir cümleleri öznesiz kurulabilir.
    """

    adi: str
    ozne: tuple[str, ...] = ()
    ara: tuple[str, ...] = ()
    yuklem: tuple[str, ...] = ()


# İnsan öznelerin kullanabileceği 3. tekil yüklemler
_KISI_YUKLEMLERI = (
    "fiil",
    "gidis",
    "yeme",
    "icme",
    "okuma",
    "yazma",
    "tutma",
    "atma",
    "sevme",
)
# Hayvanlar okuma/yazma/tutma/atma yapmaz
_HAYVAN_YUKLEMLERI = ("fiil", "gidis", "yeme", "icme", "sevme")
# Öznesiz (emir) yüklemler
_EMIR_YUKLEMLERI = (
    "emir",
    "emir_gidis",
    "emir_yeme",
    "emir_icme",
    "emir_okunacak",
    "emir_esya",
)

# Şablonlar yalnız biçimce ve anlamca uyumlu etiketleri birleştirir:
#   özne + yüklem                     -> "Ali koşar.", "Kedi uyur."
#   özne + nesne + eşleşen yüklem     -> "Ayşe elma yer.", "Ali kitap okur."
#   özne + yer zarfı + gidiş fiili    -> "Kuş eve uçar."
#   emir / nesne + emir / zarf + emir -> "Oku.", "Elma ye.", "Eve koş."
SABLONLAR: list[Sablon] = [
    Sablon("kisi-yuklem", ("kisi",), (), _KISI_YUKLEMLERI),
    Sablon("hayvan-yuklem", ("hayvan",), (), _HAYVAN_YUKLEMLERI),
    Sablon("kisi-yiyecek-yeme", ("kisi",), ("yiyecek",), ("yeme",)),
    Sablon("hayvan-yiyecek-yeme", ("hayvan",), ("yiyecek",), ("yeme",)),
    Sablon("kisi-yiyecek-sevme", ("kisi",), ("yiyecek",), ("sevme",)),
    Sablon("hayvan-yiyecek-sevme", ("hayvan",), ("yiyecek",), ("sevme",)),
    Sablon("kisi-icecek-icme", ("kisi",), ("icecek",), ("icme",)),
    Sablon("hayvan-icecek-icme", ("hayvan",), ("icecek",), ("icme",)),
    Sablon("kisi-okunacak-okuma", ("kisi",), ("okunacak",), ("okuma",)),
    Sablon("kisi-okunacak-yazma", ("kisi",), ("okunacak",), ("yazma",)),
    Sablon("kisi-esya-tutma", ("kisi",), ("esya",), ("tutma",)),
    Sablon("kisi-esya-atma", ("kisi",), ("esya",), ("atma",)),
    Sablon("kisi-esya-sevme", ("kisi",), ("esya",), ("sevme",)),
    Sablon("kisi-zarf-gidis", ("kisi",), ("zarf",), ("gidis",)),
    Sablon("hayvan-zarf-gidis", ("hayvan",), ("zarf",), ("gidis",)),
    Sablon("emir", (), (), _EMIR_YUKLEMLERI),
    Sablon("emir-yiyecek", (), ("yiyecek",), ("emir_yeme",)),
    Sablon("emir-icecek", (), ("icecek",), ("emir_icme",)),
    Sablon("emir-okunacak", (), ("okunacak",), ("emir_okunacak",)),
    Sablon("emir-esya", (), ("esya",), ("emir_esya",)),
    Sablon("emir-zarf", (), ("zarf",), ("emir_gidis",)),
]


def _sablonlari_dogrula(sablonlar: Sequence[Sablon]) -> None:
    """Şablonların yalnız tanımlı çekirdek sözlük etiketlerini kullandığını doğrular.

    Raises:
        ValueError: Şablon bilinmeyen bir etiket içeriyorsa (kod hatası).
    """
    gecerli = set(CEKIRDEK_TURLERI)
    for sablon in sablonlar:
        for tip in (*sablon.ozne, *sablon.ara, *sablon.yuklem):
            if tip not in gecerli:
                raise ValueError(
                    f"Şablon {sablon.adi!r} bilinmeyen etiket kullanıyor: {tip!r}; "
                    f"geçerli etiketler: {', '.join(CEKIRDEK_TURLERI)}"
                )


_sablonlari_dogrula(SABLONLAR)

# Çeşitlilik ile maliyet dengesi
_SABLON_BASINA_ADAY = 12
_OZNE_SAYISI = 5
_ARA_SAYISI = 3
_YUKLEM_SAYISI = 3


def _sec(adaylar: Sequence[str], adet: int, rng: random.Random) -> list[str]:
    """Adaylardan rastgele en fazla ``adet`` tanesini seçer.

    Aday sayısı istenen sayıdan azsa tüm adaylar karıştırılmış sırayla döner.
    """
    if not adaylar or adet <= 0:
        return []
    if len(adaylar) <= adet:
        secilen = list(adaylar)
        rng.shuffle(secilen)
        return secilen
    return rng.sample(adaylar, adet)


def _cumle_kur(kelimeler: Sequence[str]) -> str:
    """Kelimeleri cümle metnine çevirir ve ilk harfi büyütür."""
    metin = " ".join(kelimeler)
    return turkce_upper(metin[0]) + metin[1:] + "."


def _havuz(tipler: Sequence[str], gruplar: dict[str, list[str]]) -> list[str]:
    """Verilen etiketlerin kelimelerini tek havuzda toplar."""
    return [kelime for tip in tipler for kelime in gruplar.get(tip, [])]


def _sablon_adaylari(
    sablon: Sablon,
    gruplar: dict[str, list[str]],
    rng: random.Random,
) -> list[Cumle]:
    """Tek bir şablon için aday cümleler üretir."""
    ozne_havuzu = _havuz(sablon.ozne, gruplar)
    ara_havuzu = _havuz(sablon.ara, gruplar)
    yuklem_havuzu = _havuz(sablon.yuklem, gruplar)

    if not yuklem_havuzu:
        return []
    # Şablonun istediği öge için aday yoksa şablon atlanır
    if sablon.ozne and not ozne_havuzu:
        return []
    if sablon.ara and not ara_havuzu:
        return []

    ozneler = _sec(ozne_havuzu, _OZNE_SAYISI, rng) if sablon.ozne else []
    aralar = _sec(ara_havuzu, _ARA_SAYISI, rng) if sablon.ara else []
    yuklemler = _sec(yuklem_havuzu, _YUKLEM_SAYISI, rng)

    ozne_secenekleri: list[str | None] = list(ozneler) if ozneler else [None]
    adaylar: list[Cumle] = []
    for ozne in ozne_secenekleri:
        for yuklem in yuklemler:
            orta = rng.choice(aralar) if aralar else None
            kelimeler = [k for k in (ozne, orta, yuklem) if k is not None]
            adaylar.append(
                Cumle(
                    metin=_cumle_kur(kelimeler),
                    kelimeler=kelimeler,
                    sablon_adi=sablon.adi,
                )
            )
            if len(adaylar) >= _SABLON_BASINA_ADAY:
                return adaylar
    return adaylar


def cumle_olustur(
    kelimeler: Iterable[str],
    izinli_harfler: str,
    max_cumle: int = 10,
    rastgele_tohum: int | None = None,
    cekirdek: dict[str, list[str]] | None = None,
    kara_liste: set[str] | None = None,
) -> list[Cumle]:
    """İzinli kelimelerden basit cümleler oluşturur.

    Yalnız ``kelimeler`` içinde bulunan, izinli harflerden oluşan, kara listede
    yer almayan ve çekirdek sözlükte etiketi olan kelimeler kullanılır.
    Şablonlar çekim biçimini, özne sınıfını ve nesne-yüklem eşleşmesini gözetir
    (bkz. :data:`SABLONLAR`).

    Seçimler rastgeledir; aynı ``rastgele_tohum`` ile aynı liste üretilir.
    Global ``random`` durumu değiştirilmez.

    Args:
        kelimeler: Süzülmüş kelime listesi.
        izinli_harfler: İzinli harfler (kontrol için).
        max_cumle: Maksimum oluşturulacak cümle sayısı (<=0 ise boş liste).
        rastgele_tohum: Tekrarlanabilir sonuç için tohum (None = her çalıştırmada farklı).
        cekirdek: İsteğe bağlı çekirdek sözlük (varsayılan: paket içi dosya).
        kara_liste: İsteğe bağlı uygunsuz kelime kara listesi (None ise paket
            içindeki ``profanity.txt`` yüklenir).

    Returns:
        Oluşturulan cümleler listesi (şablonlar arasında dönüşümlü, tekrarsız).

    Raises:
        FileNotFoundError: Varsayılan çekirdek sözlük veya kara liste bulunamazsa.
        ValueError: Çekirdek sözlük biçimi bozuksa ya da ``izinli_harfler``
            Türkçe alfabede olmayan bir karakter içeriyorsa.
    """
    if max_cumle <= 0:
        return []

    rng = random.Random(rastgele_tohum)

    izinli = harfleri_normalize(izinli_harfler)
    kara = (
        {turkce_lower(k.strip()) for k in kara_liste if k.strip()}
        if kara_liste is not None
        else kara_liste_yukle()
    )
    kullanilabilir = {
        temiz
        for k in kelimeler
        if (temiz := turkce_lower(k.strip())) and kelime_uygun_mu(temiz, izinli, kara)
    }

    kaynak = cekirdek if cekirdek is not None else cekirdek_sozluk_yukle()
    gruplar = {
        tur: [temiz for k in tur_kelimeleri if (temiz := turkce_lower(k.strip())) in kullanilabilir]
        for tur, tur_kelimeleri in kaynak.items()
    }

    sablon_havuzlari = [_sablon_adaylari(sablon, gruplar, rng) for sablon in SABLONLAR]

    # Şablonlar arasında sırayla dönerek çeşitlilik sağla
    cumleler: list[Cumle] = []
    gorulen: set[str] = set()
    sira = 0
    while len(cumleler) < max_cumle:
        eklendi = False
        for havuz in sablon_havuzlari:
            if len(cumleler) >= max_cumle:
                break
            if sira >= len(havuz):
                continue
            aday = havuz[sira]
            if aday.metin in gorulen:
                continue
            gorulen.add(aday.metin)
            cumleler.append(aday)
            eklendi = True
        if not eklendi and all(sira >= len(h) for h in sablon_havuzlari):
            break
        sira += 1

    return cumleler[:max_cumle]
