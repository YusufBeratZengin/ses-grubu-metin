"""Testler: CLI modülü."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from ses_grubu.cli import PROFILLER, arg_parser_olustur, main
from ses_grubu.sozluk import cocuk_sozlugu_olustur, sozluk_yukle
from ses_grubu.suz import harflere_uyanlar, kelimeleri_suz


class TestArgParser:
    """Argüman parser testleri."""

    def test_harfler_arg(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin"])
        assert args.harfler == "elakin"
        assert args.profil is None

    def test_profil_arg(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--profil", "elakin"])
        assert args.profil == "elakin"
        assert args.harfler is None

    def test_hece_siniri(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin", "--en-cok-hece", "2"])
        assert args.en_cok_hece == 2

    def test_cumle_sayisi(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin", "--cumle-sayisi", "15"])
        assert args.cumle_sayisi == 15

    def test_cikti_dosyasi(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin", "-o", "cikti.html"])
        assert args.cikti == "cikti.html"

    def test_format_secimi(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin", "--format", "txt"])
        assert args.format == "txt"

    def test_format_varsayilan_uzantidan(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin"])
        assert args.format is None

    def test_cumle_sayisi_default_zero(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--harfler", "elakin"])
        assert args.cumle_sayisi == 0

    def test_harfler_ve_profil_birlikte_hata(self) -> None:
        parser = arg_parser_olustur()
        with pytest.raises(SystemExit):
            parser.parse_args(["--harfler", "elakin", "--profil", "elakin"])

    def test_hicbiri_yok_hata(self) -> None:
        parser = arg_parser_olustur()
        with pytest.raises(SystemExit):
            parser.parse_args([])

    def test_lisans_flag(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--lisans"])
        assert args.lisans is True

    def test_profil_listesi_flag(self) -> None:
        parser = arg_parser_olustur()
        args = parser.parse_args(["--profil-listesi"])
        assert args.profil_listesi is True

    def test_harfler_dogrulama_bos(self) -> None:
        """Boş harf girdisi hata vermeli."""
        from ses_grubu.cli import _harfleri_dogrula

        with pytest.raises(ValueError, match="boş olamaz"):
            _harfleri_dogrula("")

    def test_harfler_dogrulama_gecersiz_karakter(self) -> None:
        """Sayı veya özel karakter içeren girdi hata vermeli."""
        from ses_grubu.cli import _harfleri_dogrula

        with pytest.raises(ValueError, match="geçersiz karakter"):
            _harfleri_dogrula("elakin1")

        with pytest.raises(ValueError, match="geçersiz karakter"):
            _harfleri_dogrula("elakin!")

        with pytest.raises(ValueError, match="geçersiz karakter"):
            _harfleri_dogrula("ela kin")  # boşluk


class TestProfiller:
    """Profil listesi testleri."""

    def test_profiller_var(self) -> None:
        assert "elakin" in PROFILLER
        assert "omutuy" in PROFILLER
        assert "anetil" in PROFILLER
        assert "okurim" in PROFILLER
        assert "usoydz" in PROFILLER
        assert "cbgcs" in PROFILLER
        assert "phvgfj" in PROFILLER

    def test_profil_harfler_kucuk(self) -> None:
        for harfler in PROFILLER.values():
            assert harfler == harfler.lower()
            assert all(c.isalpha() or c in "ğüşöçı" for c in harfler)

    def test_profil_harf_kumeleri_dogrula(self) -> None:
        """Profil harf kümeleri MEB ses gruplarıyla eşleşmeli."""
        beklenen = {
            "elakin": "elakin",  # e, l, a, k, i, n
            "omutuy": "omutüy",  # o, m, u, t, ü, y
            "anetil": "anetil",
            "okurim": "okurım",
            "usoydz": "üsöydz",
            "cbgcs": "çbgcş",
            "phvgfj": "phvğfj",
        }
        for anahtar, harfler in beklenen.items():
            assert PROFILLER[anahtar] == harfler, (
                f"Profil {anahtar}: beklenen {harfler}, gelen {PROFILLER[anahtar]}"
            )


class TestCLIEntegrasyon:
    """CLI entegrasyon testleri."""

    def test_elakin_html_cikti(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_yol = f.name

        try:
            import os

            sozluk_yolu = "veri/sozcukler.txt"
            if not os.path.exists(sozluk_yolu):
                pytest.skip("Sözlük dosyası yok")

            exit_code = main(
                [
                    "--harfler",
                    "elakin",
                    "--en-cok-hece",
                    "2",
                    "--cumle-sayisi",
                    "5",
                    "-o",
                    temp_yol,
                    "--format",
                    "html",
                    "--sozluk",
                    sozluk_yolu,
                ]
            )
            assert exit_code == 0

            icerik = Path(temp_yol).read_text(encoding="utf-8")
            assert "kale" in icerik or "elek" in icerik or "inek" in icerik
            assert "SES GRUBU" in icerik or "Ses Grubu" in icerik
            assert "Max Heceler" in icerik
            assert "2" in icerik
        finally:
            if Path(temp_yol).exists():
                Path(temp_yol).unlink()

    def test_elakin_txt_cikti(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_yol = f.name

        try:
            import os

            sozluk_yolu = "veri/sozcukler.txt"
            if not os.path.exists(sozluk_yolu):
                pytest.skip("Sözlük dosyası yok")

            exit_code = main(
                [
                    "--harfler",
                    "elakin",
                    "--en-cok-hece",
                    "2",
                    "--cumle-sayisi",
                    "0",
                    "-o",
                    temp_yol,
                    "--format",
                    "txt",
                    "--sozluk",
                    sozluk_yolu,
                ]
            )
            assert exit_code == 0

            icerik = Path(temp_yol).read_text(encoding="utf-8")
            assert "kale" in icerik or "elek" in icerik or "inek" in icerik
            assert "Max Heceler: 2" in icerik
        finally:
            if Path(temp_yol).exists():
                Path(temp_yol).unlink()

    def test_profil_kullanimi(self) -> None:
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_yol = f.name

        try:
            import os

            sozluk_yolu = "veri/sozcukler.txt"
            if not os.path.exists(sozluk_yolu):
                pytest.skip("Sözlük dosyası yok")

            exit_code = main(
                [
                    "--profil",
                    "elakin",
                    "--en-cok-hece",
                    "2",
                    "--cumle-sayisi",
                    "3",
                    "-o",
                    temp_yol,
                    "--sozluk",
                    sozluk_yolu,
                ]
            )
            assert exit_code == 0

            icerik = Path(temp_yol).read_text(encoding="utf-8")
            assert "A E İ K L N" in icerik
        finally:
            if Path(temp_yol).exists():
                Path(temp_yol).unlink()

    def test_lisans_cikti(self, capsys) -> None:
        import os

        sozluk_yolu = "veri/sozcukler.txt"
        if not os.path.exists(sozluk_yolu):
            pytest.skip("Sözlük dosyası yok")

        exit_code = main(["--lisans", "--sozluk", sozluk_yolu])
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "MIT" in captured.out or "Apache" in captured.out or "CC-BY" in captured.out

    def test_profil_listesi_cikti(self, capsys) -> None:
        exit_code = main(["--profil-listesi"])
        assert exit_code == 0

        captured = capsys.readouterr()
        assert "elakin" in captured.out
        assert "anetil" in captured.out
        assert "MEB" in captured.out

    def test_gecersiz_harfler_hata(self) -> None:
        """Geçersiz harf girdisiyle CLI hata vermeli."""
        exit_code = main(["--harfler", "elakin1"])
        assert exit_code == 1

    def test_html_kacis_etkili(self) -> None:
        """HTML çıktısında özel karakterler kaçışlı olmalı."""
        with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
            temp_yol = f.name

        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".txt", delete=False, encoding="utf-8"
            ) as sf:
                sf.write("kale\n<script>alert(1)</script>\n")
                sozluk_yolu = sf.name

            main(
                [
                    "--harfler",
                    "aeliknsctrip",
                    "--en-cok-hece",
                    "3",
                    "-o",
                    temp_yol,
                    "--format",
                    "html",
                    "--sozluk",
                    sozluk_yolu,
                ]
            )
            icerik = Path(temp_yol).read_text(encoding="utf-8")
            assert "<script>" not in icerik
            assert "&lt;script&gt;" not in icerik  # etiket sözlükten hiç geçmemeli
        finally:
            if Path(temp_yol).exists():
                Path(temp_yol).unlink()


class TestReadmeOrnekleri:
    """README.md ve README.tr.md içindeki sayısal ve tam komut örneklerinin doğrulanması."""

    def test_hizli_baslangic_elakin_ornegi(self, capsys) -> None:
        """README Hızlı Başlangıç örneği gerçek CLI çıktısıyla birebir uyuşmalı."""
        assert main(["--harfler", "elakin", "--en-cok-hece", "2"]) == 0
        cikti = capsys.readouterr().out
        satirlar = cikti.splitlines()

        assert satirlar[0] == "SES GRUBU KELİME LİSTESİ"
        assert "Harfler: A E İ K L N" in satirlar
        assert "Toplam Kelime: 138" in satirlar
        assert "Max Heceler: 2" in satirlar
        assert "Sıralama: Sıklık (en sık kullanılan önce)" in satirlar

        bir_hece_idx = satirlar.index("1 Heceli (34 kelime):")
        assert [s.strip() for s in satirlar[bir_hece_idx + 2 : bir_hece_idx + 8]] == [
            "ne",  # ne: 1 hece
            "ki",  # ki: 1 hece
            "en",  # en: 1 hece
            "in",  # in: 1 hece
            "ilk",  # ilk: 1 hece
            "al",  # al: 1 hece
        ]

        # aile: a-i-le, 3 hece; iki heceli grupta bulunamaz.
        assert "  aile" not in satirlar
        iki_hece_idx = satirlar.index("2 Heceli (104 kelime):")
        assert [s.strip() for s in satirlar[iki_hece_idx + 2 : iki_hece_idx + 7]] == [
            "ile",  # i-le: 2 hece
            "iki",  # i-ki: 2 hece
            "anne",  # an-ne: 2 hece
            "alan",  # a-lan: 2 hece
            "kalan",  # ka-lan: 2 hece
        ]

    def test_tekrarlanabilir_cumle_ornegi(self, capsys) -> None:
        """README'deki tohumlu cümle örneği aynı 6 cümleyi üretmeli."""
        assert main(["--harfler", "elakinomutüyörıdsb", "--cumle-sayisi", "6", "--tohum", "3"]) == 0
        cikti = capsys.readouterr().out
        satirlar = cikti.splitlines()
        baslik_idx = satirlar.index("ÖRNEK CÜMLELER")
        cumleler = [s.strip() for s in satirlar[baslik_idx + 2 :]]
        assert cumleler == [
            "Ela okur.",
            "Kedi yer.",
            "Dede elma yer.",
            "Kedi armut yer.",
            "Ela kalem tutar.",
            "Ali kalem atar.",
        ]

    def test_kutuphane_api_ornegi_ve_belge_sayilari_tutarli(self) -> None:
        """Kütüphane API örneği ve README/README.tr sayıları aynı gerçek sonuçla eşleşmeli."""
        import re

        adaylar = cocuk_sozlugu_olustur(harflere_uyanlar(sozluk_yukle(), "ELAKİN"), max_hece=2)
        sonuc = kelimeleri_suz(adaylar, "ELAKİN", max_hece=2)
        assert sonuc.toplam_kelime == 138
        assert len(sonuc.hece_gruplari[1]) == 34
        assert len(sonuc.hece_gruplari[2]) == 104
        assert "aile" not in sonuc.kelimeler  # a-i-le: 3 hece
        assert sonuc.hece_gruplari[2][:5] == [
            "ile",  # i-le: 2 hece
            "iki",  # i-ki: 2 hece
            "anne",  # an-ne: 2 hece
            "alan",  # a-lan: 2 hece
            "kalan",  # ka-lan: 2 hece
        ]

        kok = Path(__file__).resolve().parents[1]
        for belge_adi in ("README.md", "README.tr.md"):
            icerik = (kok / belge_adi).read_text(encoding="utf-8")
            assert f"Toplam Kelime: {sonuc.toplam_kelime}" in icerik
            yorum_sayisi = re.search(r"print\(sonuc\.toplam_kelime\)\s*#\s*(\d+)", icerik)
            assert yorum_sayisi is not None, f"{belge_adi} içinde API toplam_kelime örneği yok"
            assert int(yorum_sayisi.group(1)) == sonuc.toplam_kelime, (
                f"{belge_adi} API yorumu ({yorum_sayisi.group(1)}) "
                f"gerçek sonuçla ({sonuc.toplam_kelime}) eşleşmiyor"
            )
