"""Harf kümesine göre kelime süzme motoru."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from .hece import hece_sayisi
from .sozluk import kara_liste_yukle, siklik_yukle
from .turkce import harfleri_normalize, kelime_uygun_mu

#: Desteklenen sıralamalar: sıklık (varsayılan), alfabetik, giriş sırası.
SIRALAMALAR = ("siklik", "alfabetik", "giris")


@dataclass(frozen=True)
class SuzmeSonucu:
    """Süzme işlemi sonucu."""

    kelimeler: list[str]
    hece_gruplari: dict[int, list[str]]
    izinli_harfler: str
    toplam_kelime: int
    siralama: str = "siklik"


def harflere_uyanlar(kelimeler: Iterable[str], izinli_harfler: str) -> list[str]:
    """Yalnız izinli harflerden oluşan kelimeleri döndürür (ucuz ön süzgeç).

    Hece hesabı ve kara liste kontrolü yapılmaz; pahalı adımlardan (heceleme)
    önce aday havuzunu küçültmek için kullanılır. Sonuç kümesi
    :func:`kelimeleri_suz` ile aynıdır, yalnız daha erken elenir.

    Args:
        kelimeler: Ham kelime listesi.
        izinli_harfler: İzinli harfler (normalize edilmemiş de olabilir).

    Returns:
        İzinli harflere uyan kelimeler (giriş sırasıyla).

    Raises:
        ValueError: ``izinli_harfler`` boşsa ya da Türkçe alfabede olmayan
            karakter içeriyorsa.
    """
    izinli = harfleri_normalize(izinli_harfler)
    return [k.strip() for k in kelimeler if kelime_uygun_mu(k.strip(), izinli)]


def _sirala(
    kelimeler: Iterable[str],
    sirala: str,
    siklik: Mapping[str, int],
) -> list[str]:
    """Kelime listesini istenen ölçüte göre sıralar.

    Args:
        kelimeler: Sıralanacak kelimeler.
        sirala: ``siklik``, ``alfabetik`` veya ``giris``.
        siklik: Sözcükten sıklık sırasına eşleme; listede olmayan kelimeler
            sıralı olanların ardından alfabetik gelir.

    Returns:
        Sıralanmış yeni liste.

    Raises:
        ValueError: ``sirala`` desteklenen bir değer değilse.
    """
    if sirala == "giris":
        return list(kelimeler)
    if sirala == "alfabetik":
        return sorted(kelimeler)
    if sirala == "siklik":
        bilinmeyen = len(siklik)
        return sorted(kelimeler, key=lambda k: (siklik.get(k, bilinmeyen), k))
    raise ValueError(f"Geçersiz sıralama: {sirala!r}; geçerli değerler: {', '.join(SIRALAMALAR)}")


def kelimeleri_suz(
    kelimeler: Iterable[str],
    izinli_harfler: str,
    max_hece: int = 3,
    kara_liste: set[str] | None = None,
    sirala: str = "siklik",
    siklik: Mapping[str, int] | None = None,
) -> SuzmeSonucu:
    """Kelime listesini izinli harflere ve hece sayısına göre süzer.

    Args:
        kelimeler: Giriş kelime listesi.
        izinli_harfler: İzinli harfler (normalize edilmemiş de olabilir).
        max_hece: Maksimum hece sayısı (varsayılan 3).
        kara_liste: İsteğe bağlı kara listesi.
        sirala: Çıktı sırası: ``siklik`` (varsayılan), ``alfabetik`` veya
            ``giris``.
        siklik: İsteğe bağlı sözcük sıklık eşlemesi. None ise paket içindeki
            liste kullanılır (yalnız ``sirala="siklik"`` iken okunur).

    Returns:
        Süzme sonucu (kelimeler, hece grupları, istatistikler).

    Raises:
        ValueError: ``sirala`` desteklenen bir değer değilse ya da
            ``izinli_harfler`` geçersizse (boş veya Türkçe alfabe dışı).
    """
    if sirala not in SIRALAMALAR:
        raise ValueError(
            f"Geçersiz sıralama: {sirala!r}; geçerli değerler: {', '.join(SIRALAMALAR)}"
        )

    izinli = harfleri_normalize(izinli_harfler)
    kara = kara_liste if kara_liste is not None else kara_liste_yukle()
    tablo: Mapping[str, int] = {}
    if sirala == "siklik":
        tablo = siklik if siklik is not None else siklik_yukle()

    uygun: list[str] = []
    hece_gruplari: dict[int, list[str]] = defaultdict(list)

    for kelime in kelimeler:
        kelime = kelime.strip()
        # Harf ve kara liste kontrolü hecelemeden önce: heceleme pahalı
        if not kelime_uygun_mu(kelime, izinli, kara):
            continue
        hs = hece_sayisi(kelime)
        if hs <= max_hece:
            uygun.append(kelime)
            hece_gruplari[hs].append(kelime)

    return SuzmeSonucu(
        kelimeler=_sirala(uygun, sirala, tablo),
        hece_gruplari={hs: _sirala(grup, sirala, tablo) for hs, grup in hece_gruplari.items()},
        izinli_harfler=izinli,
        toplam_kelime=len(uygun),
        siralama=sirala,
    )
