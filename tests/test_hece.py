"""Testler: heceleme modülü."""

from __future__ import annotations

import pytest

from ses_grubu.hece import hece_sayisi, hecele


class TestHeceleme:
    """Türkçe heceleme testleri."""

    @pytest.mark.parametrize(
        "kelime, beklenen_hece_sayisi",
        [
            ("elma", 2),
            ("kale", 2),
            ("kalkan", 2),
            ("inek", 2),
            ("eleman", 3),
            ("kitap", 2),
            ("okul", 2),
            ("anne", 2),
            ("baba", 2),
            ("çocuk", 2),
            ("araba", 3),
            ("kalem", 2),
            ("masa", 2),
            ("sandalye", 3),
            ("bilgisayar", 4),
            ("a", 1),
            ("ı", 1),
            ("el", 1),
            ("at", 1),
        ],
    )
    def test_hece_sayisi(self, kelime: str, beklenen_hece_sayisi: int) -> None:
        assert hece_sayisi(kelime) == beklenen_hece_sayisi

    @pytest.mark.parametrize(
        "kelime, beklenen_heceler",
        [
            ("elma", ["el", "ma"]),
            ("kale", ["ka", "le"]),
            ("kalkan", ["kal", "kan"]),
            ("inek", ["i", "nek"]),
            ("eleman", ["e", "le", "man"]),
            ("kitap", ["ki", "tap"]),
            ("okul", ["o", "kul"]),
            ("araba", ["a", "ra", "ba"]),
        ],
    )
    def test_hecele(self, kelime: str, beklenen_heceler: list[str]) -> None:
        assert hecele(kelime) == beklenen_heceler
