"""Testler: sözlük modülü."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ses_grubu.sozluk import cocuk_sozlugu_olustur, kara_liste_yukle, lisans_bilgisi, sozluk_yukle


class TestSozlukYukle:
    """Sözlük yükleme testleri."""

    def test_gecerli_dosya(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("elma\nkale\nkitap\n\n  \nkalem\n")
            temp_yol = f.name

        try:
            kelimeler = sozluk_yukle(temp_yol)
            assert kelimeler == ["elma", "kale", "kalem", "kitap"]
        finally:
            Path(temp_yol).unlink()

    def test_olmayan_dosya(self) -> None:
        with pytest.raises(FileNotFoundError):
            sozluk_yukle("olmayan_dosya.txt")

    def test_buyuk_kucuk_harf(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("ELMA\nKale\nKiTaP\n")
            temp_yol = f.name

        try:
            kelimeler = sozluk_yukle(temp_yol)
            assert kelimeler == ["elma", "kale", "kitap"]
        finally:
            Path(temp_yol).unlink()

    def test_tekrar_ve_siralama(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("kale\nelma\nkale\nkitap\nelma\n")
            temp_yol = f.name

        try:
            kelimeler = sozluk_yukle(temp_yol)
            assert kelimeler == ["elma", "kale", "kitap"]
        finally:
            Path(temp_yol).unlink()


class TestKaraListeYukle:
    """Kara liste yükleme testleri."""

    def test_gecerli_dosya(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("aptal\nsalak\n\n  \namk\n")
            temp_yol = f.name

        try:
            kara = kara_liste_yukle(temp_yol)
            assert kara == {"aptal", "salak", "amk"}
        finally:
            Path(temp_yol).unlink()

    def test_olmayan_dosya(self) -> None:
        with pytest.raises(FileNotFoundError):
            kara_liste_yukle("olmayan_dosya.txt")


class TestCocukSozluguOlustur:
    """Çocuk sözlüğü oluşturma testleri."""

    @pytest.fixture
    def ham_kelimeler(self) -> list[str]:
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
            "aptal",
            "salak",  # kara liste kelimeleri
            "a",
            "ab",
            "abcde",
            "abcdefghijk",  # uzunluk testleri
        ]

    def test_temel_filtreleme(self, ham_kelimeler: list[str]) -> None:
        sonuc = cocuk_sozlugu_olustur(ham_kelimeler, max_hece=3)
        # Kara liste kelimeleri olmamalı
        assert "aptal" not in sonuc
        assert "salak" not in sonuc
        # Çok uzun kelimeler olmamalı
        assert "abcdefghijk" not in sonuc
        # Çok kısa kelimeler olmamalı (min 2)
        assert "a" not in sonuc
        # Geçerli kelimeler olmalı
        assert "kale" in sonuc
        assert "elma" in sonuc

    def test_hece_siniri(self, ham_kelimeler: list[str]) -> None:
        sonuc = cocuk_sozlugu_olustur(ham_kelimeler, max_hece=2)
        from ses_grubu.hece import hece_sayisi

        for kelime in sonuc:
            assert hece_sayisi(kelime) <= 2

    def test_uzunluk_sinirlari(self, ham_kelimeler: list[str]) -> None:
        sonuc = cocuk_sozlugu_olustur(ham_kelimeler, min_uzunluk=3, max_uzunluk=5)
        for kelime in sonuc:
            assert 3 <= len(kelime) <= 5

    def test_siralama_ve_benzersizlik(self, ham_kelimeler: list[str]) -> None:
        sonuc = cocuk_sozlugu_olustur(ham_kelimeler)
        assert sonuc == sorted(set(sonuc))


class TestLisansBilgisi:
    """Lisans bilgisi testleri."""

    def test_lisans_dosyasi_var(self) -> None:
        # Gerçek dosya var mı?
        bilgi = lisans_bilgisi()
        assert isinstance(bilgi, str)
        assert len(bilgi) > 0
        assert "MIT" in bilgi or "Apache" in bilgi or "CC-BY" in bilgi
