"""Sözlük yükleme ve yönetimi."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from types import MappingProxyType

from .hece import hece_sayisi
from .turkce import kara_listede_mi, turkce_lower

VERI_PAKETI = files("ses_grubu.veri")


def _read_text_resource(filename: str) -> str:
    """Paket içinden metin dosyası okur."""
    return VERI_PAKETI.joinpath(filename).read_text(encoding="utf-8")


def _read_lines_resource(filename: str) -> list[str]:
    """Paket içinden metin dosyasını satır satır okur."""
    return _read_text_resource(filename).splitlines()


def sozluk_yukle(dosya_yolu: str | Path | None = None) -> list[str]:
    """Sözlük dosyasından kelimeleri yükler.

    Args:
        dosya_yolu: Özel sözlük dosyası yolu. None ise varsayılan kullanılır.

    Returns:
        Kelimeler listesi (küçük harf, benzersiz, alfabetik).
    """
    if dosya_yolu:
        yol = Path(dosya_yolu)
        if not yol.exists():
            raise FileNotFoundError(f"Sözlük dosyası bulunamadı: {yol}")
        satirlar = yol.read_text(encoding="utf-8").splitlines()
    else:
        satirlar = _read_lines_resource("sozcukler.txt")

    kelimeler = []
    for satir in satirlar:
        kelime = satir.strip()
        kelime = turkce_lower(kelime)
        if kelime and kelime.isalpha():
            kelimeler.append(kelime)

    # Benzersiz ve alfabetik
    return sorted(set(kelimeler))


def kara_liste_yukle(dosya_yolu: str | Path | None = None) -> set[str]:
    """Küfür/uygunsuz kelime kara listesini yükler.

    Args:
        dosya_yolu: Özel kara listesi dosyası yolu. None ise varsayılan kullanılır.

    Returns:
        Kara liste kümesi (küçük harf).

    Raises:
        FileNotFoundError: Varsayılan kara listesi dosyası bulunamazsa.
    """
    if dosya_yolu:
        yol = Path(dosya_yolu)
        if not yol.exists():
            raise FileNotFoundError(f"Kara listesi dosyası bulunamadı: {yol}")
        satirlar = yol.read_text(encoding="utf-8").splitlines()
    else:
        try:
            satirlar = _read_lines_resource("profanity.txt")
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "Varsayılan kara listesi (profanity.txt) pakette bulunamadı. "
                "Paket kurulumunda veri dosyalarının dahil edildiğini doğrulayın."
            ) from e

    kara = set()
    for satir in satirlar:
        kelime = satir.strip()
        kelime = turkce_lower(kelime)
        if kelime:
            kara.add(kelime)
    return kara


def lisans_bilgisi() -> str:
    """Veri lisans bilgisini döndürür."""
    try:
        return _read_text_resource("LISANS-KAYNAK.md").strip()
    except FileNotFoundError:
        return "Lisans bilgisi bulunamadı."


def cocuk_sozlugu_olustur(
    ham_kelimeler: Iterable[str],
    max_hece: int = 3,
    min_uzunluk: int = 2,
    max_uzunluk: int = 10,
) -> list[str]:
    """İlkokul 1. sınıf seviyesine uygun kelime havuzu oluşturur.

    Filtreler:
    - Sadece harf içeren kelimeler
    - 2-10 karakter arası
    - En fazla max_hece heceli
    - Kara liste dışında

    Args:
        ham_kelimeler: Ham kelime listesi.
        max_hece: Maksimum hece sayısı (varsayılan 3).
        min_uzunluk: Minimum kelime uzunluğu.
        max_uzunluk: Maksimum kelime uzunluğu.

    Returns:
        Filtrelenmiş, sıralı kelime listesi.
    """
    kara_liste = kara_liste_yukle()
    uygun = []

    for kelime in ham_kelimeler:
        kelime = kelime.strip()
        kelime = turkce_lower(kelime)
        if not kelime or not kelime.isalpha():
            continue
        if len(kelime) < min_uzunluk or len(kelime) > max_uzunluk:
            continue
        if kara_listede_mi(kelime, kara_liste):
            continue
        if hece_sayisi(kelime) <= max_hece:
            uygun.append(kelime)

    return sorted(set(uygun))


@lru_cache(maxsize=1)
def _varsayilan_siklik() -> Mapping[str, int]:
    """Paket içindeki sıklık listesini bir kez okuyup önbelleğe alır."""
    satirlar = _read_lines_resource("siklik.txt")
    return MappingProxyType(
        {turkce_lower(satir.strip()): sira for sira, satir in enumerate(satirlar) if satir.strip()}
    )


def siklik_yukle(dosya_yolu: str | Path | None = None) -> Mapping[str, int]:
    """Sözcük sıklık sırasını yükler.

    Dosya, en sık kullanılan sözcükten en seyreğe doğru her satırda bir sözcük
    içerir; satır numarası sıra numarasıdır (0 = en sık). Paket içindeki liste
    yalnız ``sozcukler.txt`` içinde de geçen sözcükleri kapsar.

    Args:
        dosya_yolu: Özel sıklık dosyası. None ise paket içindeki ``veri/siklik.txt``
            kullanılır.

    Returns:
        Sözcükten sıra numarasına salt okunur eşleme.

    Raises:
        FileNotFoundError: Dosya bulunamazsa.
    """
    if dosya_yolu:
        yol = Path(dosya_yolu)
        if not yol.exists():
            raise FileNotFoundError(f"Sıklık dosyası bulunamadı: {yol}")
        satirlar = yol.read_text(encoding="utf-8").splitlines()
        return MappingProxyType(
            {
                turkce_lower(satir.strip()): sira
                for sira, satir in enumerate(satirlar)
                if satir.strip()
            }
        )
    return _varsayilan_siklik()


CEKIRDEK_TURLERI = (
    "kisi",
    "hayvan",
    "yiyecek",
    "icecek",
    "okunacak",
    "esya",
    "zarf",
    "fiil",
    "gidis",
    "yeme",
    "icme",
    "okuma",
    "yazma",
    "tutma",
    "atma",
    "sevme",
    "emir",
    "emir_gidis",
    "emir_yeme",
    "emir_icme",
    "emir_okunacak",
    "emir_esya",
)


def cekirdek_sozluk_yukle(dosya_yolu: str | Path | None = None) -> dict[str, list[str]]:
    """Cümle şablonlarında kullanılan etiketli çekirdek sözlüğü yükler.

    Dosya biçimi: her satırda ``<tür> <kelime>``; ``#`` ile başlayan satırlar
    ve boş satırlar yorum sayılır.

    Args:
        dosya_yolu: Özel çekirdek sözlük dosyası. None ise paket içindeki
            ``veri/cekirdek_sozcukler.txt`` kullanılır.

    Returns:
        Tür adından kelime listesine eşleme. Türler :data:`CEKIRDEK_TURLERI`
        içinde listelenir; ``fiil``/``gidis`` ve nesne sınıfına bağlı
        ``yeme``/``icme``/... 3. tekil, ``emir*`` ise emir kipidir.

    Raises:
        FileNotFoundError: Dosya bulunamazsa.
        ValueError: Bilinmeyen tür etiketi veya eksik alan varsa.
    """
    if dosya_yolu:
        yol = Path(dosya_yolu)
        if not yol.exists():
            raise FileNotFoundError(f"Çekirdek sözlük bulunamadı: {yol}")
        satirlar = yol.read_text(encoding="utf-8").splitlines()
    else:
        satirlar = _read_lines_resource("cekirdek_sozcukler.txt")

    gruplar: dict[str, list[str]] = {tur: [] for tur in CEKIRDEK_TURLERI}
    gorulen: dict[str, int] = {}
    for numara, satir in enumerate(satirlar, 1):
        satir = satir.strip()
        if not satir or satir.startswith("#"):
            continue
        parcalar = satir.split()
        if len(parcalar) != 2:
            raise ValueError(
                f"Çekirdek sözlük {numara}. satır: '<tür> <kelime>' bekleniyor: {satir!r}"
            )
        tur, kelime = parcalar
        if tur not in gruplar:
            raise ValueError(
                f"Çekirdek sözlük {numara}. satır: bilinmeyen tür {tur!r}; "
                f"geçerli türler: {', '.join(CEKIRDEK_TURLERI)}"
            )
        kelime = turkce_lower(kelime)
        # Aynı kelime iki türde olamaz: şablonlar tür üzerinden seçim yapar.
        onceki = gorulen.get(kelime)
        if onceki is not None:
            raise ValueError(
                f"Çekirdek sözlük {numara}. satır: {kelime!r} kelimesi "
                f"{onceki}. satırda zaten tanımlı"
            )
        gorulen[kelime] = numara
        gruplar[tur].append(kelime)

    # Tekrarları at, okunabilirlik için sırala
    return {tur: sorted(set(kelimeler)) for tur, kelimeler in gruplar.items()}
