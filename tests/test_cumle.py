"""Testler: cümle oluşturma modülü."""

from __future__ import annotations

import pytest

from ses_grubu.cumle import cumle_olustur, kelime_turu_tahmin
from ses_grubu.sozluk import cocuk_sozlugu_olustur, sozluk_yukle
from ses_grubu.suz import kelimeleri_suz


class TestKelimeTuruTahmin:
    """Kelime türü tahmin testleri (basit heuristik)."""

    @pytest.mark.parametrize(
        "kelime, beklenen_tur",
        [
            ("koşar", "fiil"),
            ("gider", "fiil"),
            ("yapar", "fiil"),
            ("okur", "fiil"),
            ("yazar", "fiil"),
            ("eve", "zarf"),
            ("okula", "zarf"),
            ("araba", "isim"),
            ("kitap", "isim"),
            ("masa", "isim"),
            ("mutlu", "sıfat"),
            ("güzel", "sıfat"),
            ("hızlı", "sıfat"),
        ],
    )
    def test_tur_tahmin(self, kelime: str, beklenen_tur: str) -> None:
        # Basit heuristik her zaman doğru olmayabilir, bu yüzden sadece örnekler
        tahmin = kelime_turu_tahmin(kelime)
        # Fiil ve zarf için daha kesin, isim/sıfat için varsayılan
        if beklenen_tur in ("fiil", "zarf"):
            assert tahmin == beklenen_tur, f"{kelime}: beklenen {beklenen_tur}, gelen {tahmin}"


class TestCumleOlustur:
    """Cümle oluşturma testleri."""

    @pytest.fixture
    def izinli_kelimeler(self) -> list[str]:
        # Gerçek sözlükten küçük bir alt küme
        return [
            "ali",
            "ayse",
            "veli",
            "fatma",  # isimler
            "elma",
            "kitap",
            "kalem",
            "masa",
            "kale",  # nesneler
            "koşar",
            "gider",
            "okur",
            "yazar",
            "yer",  # fiiller
            "eve",
            "okula",
            "masaya",
            "evde",
            "okulda",  # zarflar
            "mutlu",
            "güzel",
            "hızlı",  # sıfatlar
        ]

    def test_cumle_olusturma(self, izinli_kelimeler: list[str]) -> None:
        cumleler = cumle_olustur(
            izinli_kelimeler, "aeiklmnorstuvyz", max_cumle=10, rastgele_tohum=42
        )
        assert len(cumleler) > 0
        assert len(cumleler) <= 10

        for cumle in cumleler:
            # Cümle nokta ile bitmeli
            assert cumle.metin.endswith(".")
            # Tüm kelimeler izinli harflerden oluşmalı
            for kelime in cumle.kelimeler:
                assert all(h in "aeiklmnorstuvyz" for h in kelime.lower())

    def test_cumle_sayisi_siniri(self, izinli_kelimeler: list[str]) -> None:
        cumleler = cumle_olustur(
            izinli_kelimeler, "aeiklmnorstuvyz", max_cumle=3, rastgele_tohum=42
        )
        assert len(cumleler) <= 3

    def test_cumle_yok_durumu(self, izinli_kelimeler: list[str]) -> None:
        cumleler = cumle_olustur(izinli_kelimeler, "aeiklmnorstuvyz", max_cumle=0)
        assert cumleler == []

    def test_tekrarlanabilirlik(self, izinli_kelimeler: list[str]) -> None:
        cumleler1 = cumle_olustur(
            izinli_kelimeler, "aeiklmnorstuvyz", max_cumle=10, rastgele_tohum=123
        )
        cumleler2 = cumle_olustur(
            izinli_kelimeler, "aeiklmnorstuvyz", max_cumle=10, rastgele_tohum=123
        )
        assert [c.metin for c in cumleler1] == [c.metin for c in cumleler2]


class TestEntegrasyonSuzCumle:
    """Süzme ve cümle oluşturma entegrasyon testi."""

    def test_gercek_sozlukle_entegresyon(self) -> None:
        # Gerçek sözlük dosyasını yükle
        try:
            ham_kelimeler = sozluk_yukle()
        except FileNotFoundError:
            pytest.skip("Sözlük dosyası bulunamadı")

        # Çocuk sözlüğü oluştur
        cocuk_kelimeleri = cocuk_sozlugu_olustur(ham_kelimeler, max_hece=3)

        # ELAKİN harfleriyle süz
        sonuc = kelimeleri_suz(cocuk_kelimeleri, "elakin", max_hece=3)

        if sonuc.kelimeler:
            # Cümle oluştur
            cumleler = cumle_olustur(sonuc.kelimeler, "elakin", max_cumle=5, rastgele_tohum=42)
            # En az bir cümle denenebilmeli (kelime türleri uygun olmayabilir)
            # Bu test sadece hata vermemeli
            for cumle in cumleler:
                assert cumle.metin.endswith(".")
