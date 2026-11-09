"""Türkçe heceleme ve hece sayımı."""

from __future__ import annotations

from itertools import pairwise

from .turkce import turkce_lower

UNLULER = frozenset("aeıioöuü")


def hecele(kelime: str) -> list[str]:
    """Türkçe kurallarına göre kelimeyi hecelere ayırır.

    Her hecede tam olarak bir ünlü bulunur. Ünlüler arasında tek ünsüz varsa
    o ünsüz sonraki hecenin başına, birden çok ünsüz varsa sonuncusu sonraki
    hecenin başına geçer. Yan yana gelen ünlüler ayrı hecelere bölünür; bu
    sayede "aile" -> ["a", "i", "le"], "ait" -> ["a", "it"] olur.

    Args:
        kelime: Hecelemek için kelime (Türkçe).

    Returns:
        Heceler listesi. Örn: "elma" -> ["el", "ma"].
        Boş girdi için boş liste döner.
    """
    kelime = kelime.strip()
    if not kelime:
        return []

    # Büyük harfli girdilerde (KALE, İSTASYON) ünlü tespiti için Türkçe
    # küçük harfe çeviri kullanılır: I -> ı, İ -> i.
    unlu_indeksleri = [i for i, harf in enumerate(kelime) if turkce_lower(harf) in UNLULER]
    if not unlu_indeksleri:
        # Ünlüsü olmayan girdi hece oluşturmaz (ör. kısaltma "bh").
        return []

    sinirlar = []
    for onceki, sonraki in pairwise(unlu_indeksleri):
        if sonraki - onceki == 1:
            # Bitişik ünlüler: her ünlü kendi hecesinde.
            sinirlar.append(sonraki)
        else:
            # Aradaki son ünsüz sonraki hecenin başına geçer.
            sinirlar.append(sonraki - 1)

    heceler = []
    baslangic = 0
    for sinir in sinirlar:
        heceler.append(kelime[baslangic:sinir])
        baslangic = sinir
    heceler.append(kelime[baslangic:])
    return heceler


def hece_sayisi(kelime: str) -> int:
    """Kelimenin hece sayısını döndürür.

    Args:
        kelime: Hece sayısı hesaplanacak kelime.

    Returns:
        Hecelerin sayısı. Boş girdi için 0.
    """
    return len(hecele(kelime))
