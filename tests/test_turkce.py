"""Testler: Türkçe büyük/küçük harf dönüşüm modülü."""

from __future__ import annotations

import pytest

from ses_grubu.turkce import harfleri_normalize, kelime_uygun_mu, turkce_lower, turkce_upper


class TestTurkceLower:
    """Türkçe küçük harfe çevirme testleri."""

    @pytest.mark.parametrize(
        "giris, beklenen",
        [
            ("ELAKİN", "elakin"),
            ("İNEK", "inek"),
            ("KIZIL", "kızıl"),
            ("İSTANBUL", "istanbul"),
            ("AĞAÇ", "ağaç"),
            ("GÜL", "gül"),
            ("ŞEHİR", "şehir"),
            ("ÖZEL", "özel"),
            ("ÇOCUK", "çocuk"),
            ("ELMA", "elma"),  # Normal ASCII
            ("elakin", "elakin"),  # Zaten küçük
        ],
    )
    def test_turkce_lower(self, giris: str, beklenen: str) -> None:
        assert turkce_lower(giris) == beklenen


class TestTurkceUpper:
    """Türkçe büyük harfe çevirme testleri."""

    @pytest.mark.parametrize(
        "giris, beklenen",
        [
            ("elakin", "ELAKİN"),
            ("inek", "İNEK"),
            ("kızıl", "KIZIL"),
            ("istanbul", "İSTANBUL"),
            ("ağaç", "AĞAÇ"),
            ("gül", "GÜL"),
            ("şehir", "ŞEHİR"),
            ("özel", "ÖZEL"),
            ("çocuk", "ÇOCUK"),
            ("elma", "ELMA"),  # Normal ASCII
            ("ELAKİN", "ELAKİN"),  # Zaten büyük
        ],
    )
    def test_turkce_upper(self, giris: str, beklenen: str) -> None:
        assert turkce_upper(giris) == beklenen


class TestHarfleriNormalize:
    """Harf normalize etme testleri."""

    @pytest.mark.parametrize(
        "giris, beklenen",
        [
            ("elakin", "aeikln"),
            ("ELAKİN", "aeikln"),
            ("ElAkIn", "aeklnı"),  # I -> ı (noktasız ı)
            ("eelakkin", "aeikln"),  # tekrar edenler
            ("aneTİL", "aeilnt"),
            ("omutüy", "motuyü"),  # ü korunur
            ("üsöydz", "dsyzöü"),  # Unicode sıralaması
            ("okurım", "kmoruı"),
            ("phvgfğ", "fghpvğ"),  # Unicode code point sırası
        ],
    )
    def test_harfleri_normalize(self, giris: str, beklenen: str) -> None:
        assert harfleri_normalize(giris) == beklenen


class TestKelimeUygunMuTurkce:
    """Kelime uygunluk kontrolü Türkçe karakter testleri."""

    def test_turkce_karakterli_kelimeler(self) -> None:
        # İ/ı testi
        assert kelime_uygun_mu("inek", "aeikln") is True
        assert kelime_uygun_mu("İNEK", "aeikln") is True  # Büyük İ
        assert kelime_uygun_mu("kızıl", "ıklz") is True
        assert kelime_uygun_mu("KIZIL", "ıklz") is True  # Büyük I -> ı

        # ğ, ü, ş, ö, ç testi
        assert kelime_uygun_mu("ağaç", "aaçğ") is True
        assert kelime_uygun_mu("gül", "glü") is True
        assert kelime_uygun_mu("şehir", "ehirş") is True
        assert kelime_uygun_mu("özel", "elöz") is True
        assert kelime_uygun_mu("çocuk", "çckou") is True

    def test_izinsiz_turkce_harf(self) -> None:
        assert kelime_uygun_mu("elma", "aeikln") is False  # m izinsiz
        assert kelime_uygun_mu("armut", "aeikln") is False  # r,m,u,t izinsiz
