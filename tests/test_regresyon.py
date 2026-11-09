"""Regresyon testleri: profil, kara liste, hece ve cümle."""

from __future__ import annotations

import contextlib
import io
import re
from pathlib import Path

import pytest

from ses_grubu.cli import main
from ses_grubu.cumle import FIIL_FORMLARI, cumle_olustur, kelime_turu_tahmin
from ses_grubu.hece import UNLULER, hece_sayisi
from ses_grubu.sozluk import (
    cekirdek_sozluk_yukle,
    cocuk_sozlugu_olustur,
    kara_liste_yukle,
    sozluk_yukle,
)
from ses_grubu.suz import kelimeleri_suz
from ses_grubu.turkce import kara_listede_mi, turkce_lower

KOK = Path(__file__).resolve().parents[1]


def _cli_cikti(args: list[str]) -> str:
    """CLI'yı çalıştırır, tarih satırını ayıklayarak stdout'u döndürür."""
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        kod = main(args)
    assert kod == 0
    satirlar = [s for s in tampon.getvalue().splitlines() if not s.startswith("Tarih:")]
    return "\n".join(satirlar)


@pytest.fixture(scope="module")
def ham_kelimeler() -> list[str]:
    return sozluk_yukle()


@pytest.fixture(scope="module")
def cocuk_kelimeler(ham_kelimeler: list[str]) -> list[str]:
    return cocuk_sozlugu_olustur(ham_kelimeler, max_hece=3)


class TestProfilHarflerTutarliligi:
    """--profil ve --harfler aynı kelime kümesini üretmeli."""

    @pytest.mark.parametrize("hece", [1, 2, 3])
    def test_elakin_profil_ve_harfler_ayni(self, hece: int) -> None:
        profil = _cli_cikti(["--profil", "elakin", "--en-cok-hece", str(hece)])
        harfler = _cli_cikti(["--harfler", "elakin", "--en-cok-hece", str(hece)])
        assert profil == harfler

    def test_elakin_temel_kelimeler_bulunur(self, cocuk_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(cocuk_kelimeler, "elakin", max_hece=3)
        for kelime in ("aile", "inek", "ekin"):
            assert kelime in sonuc.kelimeler, f"{kelime} elakin çıktısında yok"

    def test_klasik_ikinci_grup_umlu_icerir(self) -> None:
        from ses_grubu.cli import PROFILLER

        assert set(PROFILLER["elakin"]) == set("elakin")
        assert set(PROFILLER["omutuy"]) == set("omutüy")


class TestKaraListeYanlisEslestirme:
    """Alt dize eşleşmesi masum kelimeleri elenmemeli."""

    MASUM = ("kanal", "acemi", "temiz", "anlamlı", "hassas", "anahtar", "analiz")

    def test_masum_kelimeler_cocuk_sozlugunde(
        self, cocuk_kelimeler: list[str], ham_kelimeler: list[str]
    ) -> None:
        assert set(self.MASUM) <= set(ham_kelimeler)
        for kelime in self.MASUM:
            assert kelime in cocuk_kelimeler, f"{kelime} yanlışlıkla elendi"

    def test_kanal_elakin_ciktisinda(self, cocuk_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(cocuk_kelimeler, "elakin", max_hece=2)
        assert "kanal" in sonuc.kelimeler

    def test_gercek_kufur_hala_elenir(self) -> None:
        kara = kara_liste_yukle()
        assert kara_listede_mi("aptal", kara)
        assert kara_listede_mi("aptallar", kara)
        assert kara_listede_mi("orospular", kara)
        assert not kara_listede_mi("ama", kara)


class TestHeceSayisi:
    """Bitişik ünlülerde hece sayısı doğru olmalı."""

    @pytest.mark.parametrize(
        ("kelime", "beklenen"),
        [("aile", 3), ("kaide", 3), ("ait", 2), ("aidat", 3)],
    )
    def test_bitisik_unluler(self, kelime: str, beklenen: int) -> None:
        assert hece_sayisi(kelime) == beklenen

    def test_tum_sozlukte_unlu_sayisiyla_tutarli(self, ham_kelimeler: list[str]) -> None:
        for kelime in ham_kelimeler:
            unlu = sum(1 for harf in kelime if harf in UNLULER)
            assert hece_sayisi(kelime) == unlu, f"{kelime}: {hece_sayisi(kelime)} != {unlu}"


class TestCumleAnlamliligi:
    """Cümleler anlamlı özne + çekimli fiil içermeli, tohum etkili olmalı."""

    KELIMELER = [
        "ali",
        "ayse",
        "veli",
        "fatma",
        "elma",
        "kitap",
        "kalem",
        "masa",
        "kale",
        "koşar",
        "gider",
        "okur",
        "yazar",
        "yer",
        "eve",
        "okula",
        "masaya",
        "evde",
        "okulda",
        "mutlu",
        "güzel",
        "hızlı",
    ]
    HARFLER = "aeiklmnorstuvyz"

    def test_ozne_ve_cekimli_fiil(self) -> None:
        cumleler = cumle_olustur(self.KELIMELER, self.HARFLER, max_cumle=10, rastgele_tohum=7)
        assert cumleler
        for cumle in cumleler:
            assert cumle.metin.endswith(".")
            parcalar = turkce_lower(cumle.metin[:-1]).split()
            assert len(parcalar) >= 2, cumle.metin
            ozne, fiil = parcalar[0], parcalar[-1]
            assert fiil in FIIL_FORMLARI, f"çekimli fiil değil: {fiil}"
            assert ozne not in FIIL_FORMLARI
            assert kelime_turu_tahmin(ozne) == "isim"
            cekirdek = cekirdek_sozluk_yukle()
            assert ozne in {*cekirdek["kisi"], *cekirdek["hayvan"]}, cumle.metin

    def test_tohum_tekrarlanabilir_ve_etkili(self) -> None:
        a = [c.metin for c in cumle_olustur(self.KELIMELER, self.HARFLER, 10, 7)]
        b = [c.metin for c in cumle_olustur(self.KELIMELER, self.HARFLER, 10, 7)]
        c = [c.metin for c in cumle_olustur(self.KELIMELER, self.HARFLER, 10, 8)]
        assert a == b
        assert a != c

    def test_isimler_fiil_sayilmaz(self) -> None:
        for kelime in ("elenti", "kedi", "anahtar", "ait", "masa", "elma"):
            assert kelime_turu_tahmin(kelime) != "fiil", kelime


class TestBaslikVeReadme:
    """Türkçe büyük harf ve README sayıları gerçek çıktıyla eşleşmeli."""

    def test_baslik_turkce_buyuk_harf(self) -> None:
        cikti = _cli_cikti(["--profil", "elakin", "--en-cok-hece", "2", "--format", "txt"])
        assert "Harfler: A E İ K L N" in cikti
        assert "Harfler: A E I K L N" not in cikti

    def test_readme_sayilari_guncel(self) -> None:
        cikti = _cli_cikti(["--harfler", "elakin"])
        toplam = re.search(r"Toplam Kelime: (\d+)", cikti)
        gruplar = re.findall(r"(\d+) Heceli \((\d+) kelime\)", cikti)
        assert toplam is not None
        assert gruplar

        beklenen_satirlar = [f"Toplam Kelime: {toplam.group(1)}"]
        beklenen_satirlar += [f"{h} Heceli ({n} kelime):" for h, n in gruplar]
        beklenen_satirlar.append("Harfler: A E İ K L N")

        for dosya in ("README.md", "README.tr.md"):
            icerik = (KOK / dosya).read_text(encoding="utf-8")
            for satir in beklenen_satirlar:
                assert satir in icerik, f"{dosya} içinde eksik: {satir}"


class TestCumleCekimliFiil:
    """Kelime "acar" çekimli fiil sayılmamalı, "ali acar." üretilmemeli."""

    def test_acar_fiil_listesinde_degil(self) -> None:
        assert "acar" not in FIIL_FORMLARI
        # Doğru çekim ("açar") listede kalmalı.
        assert "açar" in FIIL_FORMLARI

    def test_aliacar_ciktisinda_ali_acar_yok(self, cocuk_kelimeler: list[str]) -> None:
        sonuc = kelimeleri_suz(cocuk_kelimeler, "aliacr", max_hece=3)
        cumleler = cumle_olustur(sonuc.kelimeler, "aliacr", max_cumle=10, rastgele_tohum=0)
        metinler = [c.metin for c in cumleler]
        assert all("acar" not in c.kelimeler for c in cumleler), metinler

        cikti = _cli_cikti(["--harfler", "aliacr", "--cumle-sayisi", "10"])
        cumle_satirlari = [
            satir.strip() for satir in cikti.splitlines() if satir.strip().endswith(".")
        ]
        assert not any(satir == "ali acar." for satir in cumle_satirlari), cumle_satirlari


class TestKaraListeMalum:
    """Kelime "malum" masum kelime; gerçek kara liste kelimeleri elenmeye devam etmeli."""

    def test_malum_korunur(self, ham_kelimeler: list[str]) -> None:
        kara = kara_liste_yukle()
        assert "malum" in ham_kelimeler
        assert kara_listede_mi("malum", kara) is False
        assert "malum" in cocuk_sozlugu_olustur(ham_kelimeler, max_hece=3)
        assert "malum" in kelimeleri_suz(ham_kelimeler, "malum", max_hece=3).kelimeler

    def test_gercek_kara_liste_hala_elenir(self) -> None:
        kara = kara_liste_yukle()
        for kelime in ("mal", "mallar", "aptal", "aptallar", "orospular"):
            assert kara_listede_mi(kelime, kara) is True, kelime


class TestBuyukHarfHece:
    """Büyük harfli (I/İ) kelimelerde hece sayısı doğru olmalı."""

    @pytest.mark.parametrize(
        ("kelime", "beklenen"),
        [
            ("KALE", 2),  # KA-LE: 2 hece
            ("ISIK", 2),  # I-SIK: 2 hece
            ("İSTASYON", 3),  # İS-TAS-YON: 3 hece
            ("IŞIK", 2),  # I-ŞIK: 2 hece
            ("İNEK", 2),  # İ-NEK: 2 hece
        ],
    )
    def test_buyuk_harf_hece_sayisi(self, kelime: str, beklenen: int) -> None:
        assert hece_sayisi(kelime) == beklenen

    def test_buyuk_harf_suzmede_hece_ile_elenir(self) -> None:
        sonuc = kelimeleri_suz(["KALE"], "elakin", max_hece=1)
        assert sonuc.kelimeler == []
        assert 0 not in sonuc.hece_gruplari


class TestSozlukKelimeleri:
    """Emlak ile ilgili beş kelime sözlükte bulunmalı."""

    KELIMELER = ("emlak", "emlakçı", "emlakçılık", "gayrimenkul", "gayrimenkullük")

    def test_kelimeler_dosyada_ve_pakette(self) -> None:
        dosya = (KOK / "veri" / "sozcukler.txt").read_text(encoding="utf-8").splitlines()
        paket = set(sozluk_yukle())
        for kelime in self.KELIMELER:
            assert kelime in {satir.strip() for satir in dosya}, f"{kelime} veri dosyasında yok"
            assert kelime in paket, f"{kelime} paket sözlüğünde yok"

    def test_emlak_ciktida_gorunur(self) -> None:
        cikti = _cli_cikti(["--harfler", "emlak"])
        assert "  emlak\n" in cikti


@pytest.mark.parametrize("metin", ["Ali okur.", "Ali kitap okur.", "Ali eve gider."])
def test_ozne_fiil_kontrolu_gecerli_cumleleri_kabul_eder(
    monkeypatch: pytest.MonkeyPatch, metin: str
) -> None:
    from ses_grubu.cumle import Cumle

    monkeypatch.setattr(
        "test_regresyon.cumle_olustur",
        lambda *_args, **_kwargs: [Cumle(metin, metin[:-1].lower().split(), "sentetik")],
    )
    TestCumleAnlamliligi().test_ozne_ve_cekimli_fiil()


@pytest.mark.parametrize(
    "metin", ["Okur.", "Ali.", "Kitap okur.", "Ali kitap.", "Ali acar.", "Ali kitap oku."]
)
def test_ozne_fiil_kontrolu_eksik_ve_gecersiz_ogeleri_reddeder(
    monkeypatch: pytest.MonkeyPatch, metin: str
) -> None:
    from ses_grubu.cumle import Cumle

    monkeypatch.setattr(
        "test_regresyon.cumle_olustur",
        lambda *_args, **_kwargs: [Cumle(metin, metin[:-1].lower().split(), "sentetik")],
    )
    with pytest.raises(AssertionError):
        TestCumleAnlamliligi().test_ozne_ve_cekimli_fiil()
