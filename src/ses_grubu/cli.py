"""Komut satırı arayüzü."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .cikti import html_cikti, metin_cikti
from .cumle import cumle_olustur
from .sozluk import cocuk_sozlugu_olustur, lisans_bilgisi, sozluk_yukle
from .suz import SIRALAMALAR, harflere_uyanlar, kelimeleri_suz
from .turkce import harfleri_dogrula

#: Uzantıdan çıkarılabilen çıktı biçimleri.
_UZANTI_BICIMLERI = {".html": "html", ".txt": "txt"}


def _harfleri_dogrula(harfler: str) -> str:
    """CLI harf girdisini doğrular.

    Kural tek yerde tutulur (:func:`ses_grubu.turkce.harfleri_dogrula`), böylece
    kütüphane API'si ile CLI aynı girdiyi kabul eder.

    Args:
        harfler: Kullanıcı girdisi.

    Returns:
        Temizlenmiş harf dizisi.

    Raises:
        ValueError: Girdi boşsa ya da Türkçe alfabede olmayan karakter varsa.
    """
    return harfleri_dogrula(harfler)


def _negatif_olmayan(deger: str) -> int:
    """argparse türü: negatif olmayan tam sayı.

    Raises:
        argparse.ArgumentTypeError: Değer tam sayı değilse veya negatifse.
    """
    try:
        sayi = int(deger)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"tam sayı bekleniyor: {deger!r}") from exc
    if sayi < 0:
        raise argparse.ArgumentTypeError(f"negatif olamaz: {sayi}")
    return sayi


def _bicim_coz(secim: str | None, cikti_yolu: Path | None) -> str:
    """Çıktı biçimini belirler.

    ``--format`` verilmediyse uzantıya bakılır (``.html`` -> html, ``.txt`` ->
    txt, diğerleri -> txt). İkisi birlikte verilip çelişirse kullanıcı sessizce
    yanlış biçim almaz; hata verilir.

    Args:
        secim: ``--format`` değeri ya da None.
        cikti_yolu: Çıktı dosyası yolu ya da None (stdout).

    Returns:
        ``html`` veya ``txt``.

    Raises:
        ValueError: ``--format`` ile dosya uzantısı çelişiyorsa.
    """
    uzanti = cikti_yolu.suffix if cikti_yolu is not None else ""
    uzantidan = _UZANTI_BICIMLERI.get(uzanti.lower())
    if secim and uzantidan and secim != uzantidan:
        raise ValueError(
            f"--format {secim} ile dosya uzantısı {uzanti!r} çelişiyor. "
            f"Uzantıyı .{secim} yapın veya --format seçeneğini kaldırın."
        )
    return secim or uzantidan or "txt"


def arg_parser_olustur() -> argparse.ArgumentParser:
    """Argüman parser'ı oluşturur."""
    parser = argparse.ArgumentParser(
        prog="ses-grubu-metin",
        description="İlk okuma yazma öğretimi için ses grubuna göre kelime ve cümle listesi üretir.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  ses-grubu-metin --harfler "elakin"
  ses-grubu-metin --harfler "elakinomu" --en-cok-hece 2 -o liste.html
  ses-grubu-metin --harfler "anetil" --cumle-sayisi 15 --format txt -o cikti.txt
  ses-grubu-metin --profil elakin --cumle-sayisi 10
        """,
    )

    # Ana işlem modu: harfler, profil, lisans, profil-listesi (karşılıklı dışlayıcı)
    mod_grup = parser.add_mutually_exclusive_group(required=True)
    mod_grup.add_argument(
        "--harfler",
        type=str,
        help="İzinli harfler (örn. 'elakin', 'anetil'). Büyük/küçük harf fark etmez.",
    )
    mod_grup.add_argument(
        "--profil",
        type=str,
        choices=["elakin", "omutuy", "anetil", "okurim", "usoydz", "cbgcs", "phvgfj"],
        help="Hazır ses grubu profili (MEB müfredatından). --harfler ile birlikte kullanılamaz.",
    )
    mod_grup.add_argument(
        "--lisans",
        action="store_true",
        help="Veri lisans bilgisini gösterir ve çıkar.",
    )
    mod_grup.add_argument(
        "--profil-listesi",
        action="store_true",
        help="Mevcut profilleri listeler ve çıkar.",
    )

    parser.add_argument(
        "--en-cok-hece",
        type=int,
        default=3,
        choices=[1, 2, 3],
        help="Maksimum hece sayısı (varsayılan: 3).",
    )

    parser.add_argument(
        "--cumle-sayisi",
        type=_negatif_olmayan,
        default=0,
        help="Oluşturulacak örnek cümle sayısı (varsayılan: 0 = cümle yok, deneysel).",
    )

    parser.add_argument(
        "--tohum",
        type=int,
        default=None,
        help=(
            "Cümle seçimi için rastgele tohum. Aynı tohum aynı cümleleri üretir; "
            "verilmezse her çalıştırmada farklı cümleler seçilir."
        ),
    )

    parser.add_argument(
        "-o",
        "--cikti",
        type=str,
        help=(
            "Çıktı dosyası yolu. .html uzantısı HTML, .txt uzantısı düz metin üretir; "
            "belirtilmezse stdout'a yazılır."
        ),
    )

    parser.add_argument(
        "--format",
        type=str,
        choices=["html", "txt"],
        default=None,
        help=(
            "Çıktı formatı. Verilmezse dosya uzantısından çıkarılır "
            "(.html -> html, .txt -> txt); uzantı tanınmıyorsa txt. "
            "--format ile uzantı çelişirse komut hata verir."
        ),
    )

    parser.add_argument(
        "--sirala",
        type=str,
        choices=list(SIRALAMALAR),
        default="siklik",
        help=(
            "Sözcük sırası: siklik (varsayılan, en sık kullanılan önce), "
            "alfabetik veya giris (sözlük dosyasındaki sıra)."
        ),
    )

    parser.add_argument(
        "--sozluk",
        type=str,
        help="Özel sözlük dosyası yolu (varsayılan: paket içi veri/sozcukler.txt).",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1.0",
    )

    return parser


PROFILLER = {
    "elakin": "elakin",  # Klasik 1. Grup (e-l-a-k-i-n)
    "omutuy": "omutüy",  # Klasik 2. Grup (o-m-u-t-ü-y)
    "anetil": "anetil",  # Maarif Modeli 1. Grup
    "okurim": "okurım",  # Maarif Modeli 2. Grup
    "usoydz": "üsöydz",  # Maarif Modeli 3. Grup
    "cbgcs": "çbgcş",  # Maarif Modeli 4. Grup
    "phvgfj": "phvğfj",  # Maarif Modeli 5. Grup
}


def profilleri_listele() -> None:
    """Profilleri listeler."""
    print("Mevcut Ses Grubu Profilleri:")
    print("-" * 50)
    for anahtar, harfler in PROFILLER.items():
        print(f"  {anahtar:10} -> {harfler}")
    print()
    print("Kaynak: MEB 2024 Türkiye Yüzyılı Maarif Modeli ve klasik program.")


def main(argv: list[str] | None = None) -> int:
    """Ana CLI giriş noktası."""
    parser = arg_parser_olustur()
    args = parser.parse_args(argv)

    if args.profil_listesi:
        profilleri_listele()
        return 0

    if args.lisans:
        print(lisans_bilgisi())
        return 0

    # Harfleri belirle ve doğrula
    if args.profil:
        # argparse choices sayesinde anahtar her zaman geçerli
        harfler = PROFILLER[args.profil]
    else:
        try:
            harfler = _harfleri_dogrula(args.harfler or "")
        except ValueError as e:
            print(f"Hata: {e}", file=sys.stderr)
            return 1

    # Sözlüğü yükle
    try:
        ham_kelimeler = sozluk_yukle(args.sozluk)
    except FileNotFoundError as e:
        print(f"Hata: {e}", file=sys.stderr)
        print(
            "İpucu: Paket kurulumunda veri dosyalarının dahil edildiğini doğrulayın.",
            file=sys.stderr,
        )
        return 1
    except UnicodeDecodeError as e:
        print(
            f"Hata: sözlük dosyası UTF-8 olarak çözülemedi ({e.reason}, bayt {e.start}). "
            "Dosyayı UTF-8 olarak kaydedin.",
            file=sys.stderr,
        )
        return 1
    except OSError as e:
        print(f"Hata: sözlük dosyası okunamadı: {e}", file=sys.stderr)
        return 1

    # Çıktı biçimi: --format ve dosya uzantısı çelişmemeli
    cikti_yolu = Path(args.cikti) if args.cikti else None
    try:
        bicim = _bicim_coz(args.format, cikti_yolu)
    except ValueError as e:
        print(f"Hata: {e}", file=sys.stderr)
        return 2

    # Ucuz harf ön süzgeci: 60 bin kelimeyi hecelemeden önce ~3 bine indirir.
    # Filtreler birbirinden bağımsız olduğu için sonuç kümesi değişmez.
    aday_kelimeler = harflere_uyanlar(ham_kelimeler, harfler)

    # Çocuk sözlüğü oluştur (pedagojik filtre: uzunluk, kara liste, hece)
    cocuk_kelimeleri = cocuk_sozlugu_olustur(aday_kelimeler, max_hece=args.en_cok_hece)

    # Kelimeleri süz (hece grupları burada oluşur)
    sonuc = kelimeleri_suz(
        cocuk_kelimeleri,
        harfler,
        max_hece=args.en_cok_hece,
        sirala=args.sirala,
    )

    # Cümleler oluştur (isteğe bağlı, deneysel)
    cumleler = []
    if args.cumle_sayisi > 0:
        if sonuc.kelimeler:
            cumleler = cumle_olustur(
                sonuc.kelimeler,
                harfler,
                max_cumle=args.cumle_sayisi,
                rastgele_tohum=args.tohum,
            )
        if not cumleler:
            print(
                "Uyarı: Cümle oluşturulamadı (çekirdek sözlükle eşleşen kelime yok).",
                file=sys.stderr,
            )

    # Çıktı
    if cikti_yolu is not None:
        try:
            if bicim == "html":
                html_cikti(sonuc, cumleler, cikti_yolu, max_hece=args.en_cok_hece)
            else:
                metin_cikti(sonuc, cumleler, cikti_yolu, max_hece=args.en_cok_hece)
        except OSError as e:
            print(f"Hata: çıktı dosyası yazılamadı: {cikti_yolu} ({e})", file=sys.stderr)
            return 1
        print(f"Çıktı yazıldı: {cikti_yolu}")
    else:
        # Stdout'a yaz
        if bicim == "html":
            print(html_cikti(sonuc, cumleler, max_hece=args.en_cok_hece))
        else:
            print(metin_cikti(sonuc, cumleler, max_hece=args.en_cok_hece))

    return 0


if __name__ == "__main__":
    sys.exit(main())
