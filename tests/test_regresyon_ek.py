"""Regression tests: published CLI and template API contract."""

from pathlib import Path

import pytest

from ses_grubu.cikti import html_cikti
from ses_grubu.cli import PROFILLER, main
from ses_grubu.cumle import cumle_olustur
from ses_grubu.suz import SuzmeSonucu


def test_tohum_cli_uretime_aktarilir(capsys: pytest.CaptureFixture[str]) -> None:
    args = ["--harfler", "aeikloruyz", "--cumle-sayisi", "8", "--tohum", "7"]
    assert main(args) == 0
    ilk = capsys.readouterr().out.split("ÖRNEK CÜMLELER")[1]
    assert main(args) == 0
    assert capsys.readouterr().out.split("ÖRNEK CÜMLELER")[1] == ilk
    assert main([*args[:-1], "8"]) == 0
    assert capsys.readouterr().out.split("ÖRNEK CÜMLELER")[1] != ilk


def test_negatif_cumle_cikis_iki() -> None:
    with pytest.raises(SystemExit) as hata:
        main(["--harfler", "elakin", "--cumle-sayisi", "-1"])
    assert hata.value.code == 2


@pytest.mark.parametrize("bicim,uzanti", [("txt", ".HTML"), ("html", ".TXT")])
def test_format_celiskisi_dosya_yazmaz(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], bicim: str, uzanti: str
) -> None:
    yol = tmp_path / f"liste{uzanti}"
    yol.write_text("sentetik içerik", encoding="utf-8")
    assert main(["--harfler", "elakin", "--format", bicim, "-o", str(yol)]) == 2
    assert "çelişiyor" in capsys.readouterr().err
    assert yol.read_text(encoding="utf-8") == "sentetik içerik"


@pytest.mark.parametrize("uzanti", [".txt", ".html"])
def test_cikti_yazma_hatasi_anlasilir(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], uzanti: str
) -> None:
    yol = tmp_path / "olmayan" / f"liste{uzanti}"
    assert main(["--harfler", "elakin", "-o", str(yol)]) == 1
    mesaj = capsys.readouterr()
    assert "çıktı dosyası yazılamadı" in mesaj.err
    assert "Çıktı yazıldı" not in mesaj.out


def test_bozuk_utf8_sozluk_hatasi(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    yol = tmp_path / "sentetik.txt"
    yol.write_bytes(b"el\n\xff\n")
    assert main(["--harfler", "elakin", "--sozluk", str(yol)]) == 1
    assert "UTF-8" in capsys.readouterr().err


def test_sozluk_okuma_hatasi(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    def okunamaz(*_args: object) -> list[str]:
        raise PermissionError("sentetik izin hatası")

    monkeypatch.setattr("ses_grubu.cli.sozluk_yukle", okunamaz)
    assert main(["--harfler", "elakin"]) == 1
    assert "sözlük dosyası okunamadı" in capsys.readouterr().err


def test_bos_kelime_havuzunda_cumle_uyarisi(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    yol = tmp_path / "sentetik.txt"
    yol.write_text("", encoding="utf-8")
    assert main(["--harfler", "elakin", "--sozluk", str(yol), "--cumle-sayisi", "1"]) == 0
    assert "Uyarı: Cümle oluşturulamadı" in capsys.readouterr().err


def test_yayin_sablon_api_ve_turkce_buyuk_harf() -> None:
    from ses_grubu.cumle import SABLONLAR

    assert "hayvan-yuklem" in {s.adi for s in SABLONLAR}
    assert [c.metin for c in cumle_olustur(["inek", "uyur"], "eiknruy", 3, 1)] == ["İnek uyur."]


def test_yayin_nesne_ve_emir_sablonlari() -> None:
    assert "Ali elma yer." in {
        c.metin for c in cumle_olustur(["ali", "elma", "yer"], "aeilmyr", 10, 1)
    }
    assert {c.metin for c in cumle_olustur(["elma", "ye"], "aelmy", 10, 1)} == {
        "Elma ye.",
        "Ye.",
    }


def test_html_siralama_etiketi_kacislanir() -> None:
    etiket = '<img src=x onerror="sentetik">&'
    sonuc = SuzmeSonucu([], {}, "elakin", 0, siralama=etiket)
    cikti = html_cikti(sonuc)
    assert etiket not in cikti
    assert "&lt;img src=x onerror=&quot;sentetik&quot;&gt;&amp;" in cikti


def test_maarif_son_grupta_yumusak_g() -> None:
    assert PROFILLER["phvgfj"] == "phvğfj"
