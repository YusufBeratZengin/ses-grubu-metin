"""Yayın API ve özne-yüklem uyumu regresyonları."""

import pytest

from ses_grubu.cumle import cumle_olustur
from ses_grubu.suz import kelimeleri_suz


def test_existing_sorting_api():
    result = kelimeleri_suz(["elma"], "elma", sirala="alfabetik")
    assert result.kelimeler == ["elma"]


def test_existing_blacklist_api():
    assert cumle_olustur(["ali", "alır"], "aliır", kara_liste={"alır"}) == []


def test_animal_does_not_read_or_write():
    sentences = cumle_olustur(["kedi", "okur", "yazar"], "adeikoruyz", 10, 0)
    assert not sentences, [s.metin for s in sentences]


def test_cli_sirala(capsys: pytest.CaptureFixture[str]) -> None:
    from ses_grubu.cli import main

    assert main(["--harfler", "elma", "--sirala", "alfabetik"]) == 0
    assert "elma" in capsys.readouterr().out


def test_siklik_ve_giris_sirasi() -> None:
    kelimeler = ["elma", "alma"]
    assert kelimeleri_suz(kelimeler, "elma", sirala="giris").kelimeler == kelimeler
    sonuc = kelimeleri_suz(kelimeler, "elma", siklik={"alma": 0, "elma": 1})
    assert sonuc.kelimeler == ["alma", "elma"]
    assert sonuc.hece_gruplari[2] == ["alma", "elma"]
    assert sonuc.siralama == "siklik"


def test_yayin_disa_aktarimlari_ve_verileri() -> None:
    from ses_grubu import cekirdek_sozluk_yukle, harflere_uyanlar, harfleri_dogrula
    from ses_grubu.sozluk import siklik_yukle

    assert harfleri_dogrula(" ELAKİN ") == "ELAKİN"
    with pytest.raises(ValueError):
        harfleri_dogrula("abcq")
    assert harflere_uyanlar(["elma", "kedi"], "elma") == ["elma"]
    assert "elma" in siklik_yukle()
    assert "kedi" in cekirdek_sozluk_yukle()["hayvan"]


def test_insan_okur_hayvan_uyur() -> None:
    cumleler = cumle_olustur(["ali", "kedi", "okur", "yazar", "uyur"], "adeikloruyz", 100, 0)
    kelimeler = {tuple(c.kelimeler) for c in cumleler}
    assert ("ali", "okur") in kelimeler
    assert ("ali", "yazar") in kelimeler
    assert ("kedi", "uyur") in kelimeler
    assert ("kedi", "okur") not in kelimeler
    assert ("kedi", "yazar") not in kelimeler
