"""Testler: süzme motoru modülü."""

from __future__ import annotations

import pytest

from ses_grubu.suz import SuzmeSonucu, harfleri_normalize, kelime_uygun_mu, kelimeleri_suz


class TestHarfNormalizasyon:
    """Harf normalize etme testleri."""

    @pytest.mark.parametrize(
        "giris, beklenen",
        [
            ("elakin", "aeikln"),
            ("ELAKİN", "aeikln"),
            ("ElAkIn", "aeklnı"),  # I -> ı (noktasız ı)
            ("eelakkin", "aeikln"),  # tekrar edenler
            ("aneTİL", "aeilnt"),
            ("omutuy", "motuy"),
            ("üsöydz", "dsyzöü"),  # Unicode sıralaması
        ],
    )
    def test_harfleri_normalize(self, giris: str, beklenen: str) -> None:
        assert harfleri_normalize(giris) == beklenen


class TestKelimeUygunMu:
    """Kelime uygunluk kontrolü testleri."""

    def test_sadece_izinli_harfler(self) -> None:
        assert kelime_uygun_mu("kale", "aeikln") is True
        assert kelime_uygun_mu("elek", "aeikln") is True
        assert kelime_uygun_mu("inek", "aeikln") is True
        assert kelime_uygun_mu("kalkan", "aeikln") is True
        assert kelime_uygun_mu("kale", "aeikln") is True

    def test_izinsiz_harf_iceren(self) -> None:
        assert kelime_uygun_mu("kalem", "aeikln") is False  # m izinsiz
        assert kelime_uygun_mu("elma", "aeikln") is False  # m izinsiz
        assert kelime_uygun_mu("armut", "aeikln") is False  # r,m,u,t izinsiz

    def test_bos_kelime(self) -> None:
        assert kelime_uygun_mu("", "aeikln") is False
        assert kelime_uygun_mu(" ", "aeikln") is False

    def test_sayi_ve_ozel_karakter(self) -> None:
        assert kelime_uygun_mu("kal3", "aeikln") is False
        assert kelime_uygun_mu("kal!", "aeikln") is False

    def test_kara_liste(self) -> None:
        kara = {"aptal", "salak"}
        assert kelime_uygun_mu("aptal", "aaltp", kara_liste=kara) is False
        assert kelime_uygun_mu("salak", "aaltp", kara_liste=kara) is False
        assert kelime_uygun_mu("kale", "aeikln", kara_liste=kara) is True


class TestKelimeleriSuz:
    """Kelime süzme testleri."""

    @pytest.fixture
    def ornek_kelimeler(self) -> list[str]:
        return [
            "kale",
            "elek",
            "inek",
            "kalkan",
            "kalem",
            "elma",
            "kitap",
            "masa",
            "sandalye",
            "araba",
            "anne",
            "baba",
            "çocuk",
            "okul",
            "ev",
            "kapı",
            "pencere",
            "el",
            "al",
            "il",
            "in",
            "ka",
            "ke",
            "la",
            "le",
            "li",
        ]

    def test_elakin_grubu(self, ornek_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(ornek_kelimeler, "elakin", max_hece=3)
        assert sonuc.izinli_harfler == "aeikln"
        assert sonuc.toplam_kelime > 0

        # Tüm kelimeler sadece e,l,a,k,i,n harflerinden oluşmalı
        for kelime in sonuc.kelimeler:
            assert all(h in "aeikln" for h in kelime), f"İzinsiz harf: {kelime}"

    def test_hece_siniri(self, ornek_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(ornek_kelimeler, "elakin", max_hece=2)
        for kelime in sonuc.kelimeler:
            from ses_grubu.hece import hece_sayisi

            assert hece_sayisi(kelime) <= 2, f"Fazla hece: {kelime}"

    def test_hece_gruplari(self, ornek_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(ornek_kelimeler, "elakin", max_hece=3, sirala="alfabetik")
        # Her hece grubu alfabetik sıralı olmalı
        for hece_sayisi, kelimeler in sonuc.hece_gruplari.items():
            assert kelimeler == sorted(kelimeler), f"Grup {hece_sayisi} sıralı değil"

    def test_kara_liste_uygulanir(self, ornek_kelimeler: list[str]) -> None:
        kara = {"kale", "elek"}
        sonuc = kelimeleri_suz(ornek_kelimeler, "elakin", max_hece=3, kara_liste=kara)
        assert "kale" not in sonuc.kelimeler
        assert "elek" not in sonuc.kelimeler

    def test_sonuc_tipi(self, ornek_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(ornek_kelimeler, "elakin")
        assert isinstance(sonuc, SuzmeSonucu)
        assert hasattr(sonuc, "kelimeler")
        assert hasattr(sonuc, "hece_gruplari")
        assert hasattr(sonuc, "izinli_harfler")
        assert hasattr(sonuc, "toplam_kelime")
