"""Testler: çıktı modülü."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ses_grubu.cikti import html_cikti, metin_cikti
from ses_grubu.cumle import Cumle
from ses_grubu.suz import SuzmeSonucu


class TestHtmlCikti:
    """HTML çıktı testleri."""

    @pytest.fixture
    def ornek_sonuc(self) -> SuzmeSonucu:
        return SuzmeSonucu(
            kelimeler=["kale", "elek", "inek", "kalkan", "el", "al", "il"],
            hece_gruplari={
                1: ["el", "al", "il"],
                2: ["kale", "elek", "inek"],
                3: ["kalkan"],
            },
            izinli_harfler="aeikln",
            toplam_kelime=7,
        )

    @pytest.fixture
    def ornek_cumleler(self) -> list[Cumle]:
        return [
            Cumle(
                metin="Ali kale yar.", kelimeler=["ali", "kale", "yar"], sablon_adi="isim+isim+fiil"
            ),
            Cumle(
                metin="Ela elma yer.", kelimeler=["ela", "elma", "yer"], sablon_adi="isim+isim+fiil"
            ),
        ]

    def test_html_icerik(self, ornek_sonuc: SuzmeSonucu, ornek_cumleler: list[Cumle]) -> None:
        html = html_cikti(ornek_sonuc, ornek_cumleler, max_hece=3)
        assert "<!DOCTYPE html>" in html
        assert '<html lang="tr">' in html
        assert "Ses Grubu Kelime Listesi" in html
        assert "A E İ K L N" in html  # Türkçe büyük harf (i -> İ)
        assert "Toplam Kelime" in html
        assert "7" in html
        assert "Max Heceler" in html
        assert "3" in html
        assert "kale" in html
        assert "elek" in html
        assert "Ali kale yar." in html
        assert "Ela elma yer." in html

    def test_html_dosya_yazma(self, ornek_sonuc: SuzmeSonucu, ornek_cumleler: list[Cumle]) -> None:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_yol = f.name

        try:
            sonuc = html_cikti(ornek_sonuc, ornek_cumleler, temp_yol, max_hece=3)
            assert sonuc == ""  # Dosya yazıldığında boş string döner

            icerik = Path(temp_yol).read_text(encoding="utf-8")
            assert "kale" in icerik
            assert "Ali kale yar." in icerik
        finally:
            Path(temp_yol).unlink()

    def test_html_cumle_yok(self, ornek_sonuc: SuzmeSonucu) -> None:
        html = html_cikti(ornek_sonuc, [], max_hece=3)
        assert "Örnek Cümleler" not in html


class TestMetinCikti:
    """Metin çıktı testleri."""

    @pytest.fixture
    def ornek_sonuc(self) -> SuzmeSonucu:
        return SuzmeSonucu(
            kelimeler=["kale", "elek", "inek", "kalkan"],
            hece_gruplari={
                2: ["kale", "elek", "inek"],
                3: ["kalkan"],
            },
            izinli_harfler="aeikln",
            toplam_kelime=4,
        )

    @pytest.fixture
    def ornek_cumleler(self) -> list[Cumle]:
        return [
            Cumle(metin="Ali kale yar.", kelimeler=["ali", "kale", "yar"], sablon_adi="test"),
        ]

    def test_metin_icerik(self, ornek_sonuc: SuzmeSonucu, ornek_cumleler: list[Cumle]) -> None:
        metin = metin_cikti(ornek_sonuc, ornek_cumleler, max_hece=3)
        assert "SES GRUBU KELİME LİSTESİ" in metin
        assert "A E İ K L N" in metin  # Türkçe büyük harf (i -> İ)
        assert "Toplam Kelime: 4" in metin
        assert "Max Heceler: 3" in metin
        assert "2 Heceli" in metin
        assert "3 Heceli" in metin
        assert "kale" in metin
        assert "Ali kale yar." in metin

    def test_metin_dosya_yazma(self, ornek_sonuc: SuzmeSonucu, ornek_cumleler: list[Cumle]) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_yol = f.name

        try:
            sonuc = metin_cikti(ornek_sonuc, ornek_cumleler, temp_yol, max_hece=3)
            assert sonuc == ""

            icerik = Path(temp_yol).read_text(encoding="utf-8")
            assert "kale" in icerik
            assert "Ali kale yar." in icerik
        finally:
            Path(temp_yol).unlink()

    def test_metin_cumle_yok(self, ornek_sonuc: SuzmeSonucu) -> None:
        metin = metin_cikti(ornek_sonuc, [], max_hece=3)
        assert "ÖRNEK CÜMLELER" not in metin
