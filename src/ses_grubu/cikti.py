"""HTML ve metin çıktı modülleri."""

from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path

from .cumle import Cumle
from .suz import SuzmeSonucu
from .turkce import turkce_upper

HTML_SABLON = """<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ses Grubu Kelime Listesi - {harfler}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #fafafa;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 1.8rem;
        }}
        .meta {{
            color: #666;
            margin-bottom: 20px;
            font-size: 0.95rem;
        }}
        .meta span {{
            margin-right: 20px;
        }}
        .hece-grup {{
            margin-bottom: 30px;
        }}
        .hece-grup h2 {{
            color: #34495e;
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #3498db;
        }}
        .kelime-listesi {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .kelime {{
            background: #ecf0f1;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 1.1rem;
            font-weight: 500;
            color: #2c3e50;
            transition: all 0.2s;
        }}
        .kelime:hover {{
            background: #3498db;
            color: white;
        }}
        .cumleler {{
            margin-top: 30px;
        }}
        .cumleler h2 {{
            color: #34495e;
            font-size: 1.3rem;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e74c3c;
        }}
        .cumle {{
            background: #fdf2e9;
            padding: 12px 16px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #e67e22;
            font-size: 1.1rem;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #888;
            font-size: 0.85rem;
            text-align: center;
        }}
        @media print {{
            body {{ background: white; }}
            .container {{ box-shadow: none; padding: 0; }}
            .kelime {{ background: #f0f0f0; }}
            .cumle {{ background: #fafafa; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Ses Grubu Kelime Listesi</h1>
        <div class="meta">
            <span><strong>Harfler:</strong> {harfler_gosterim}</span>
            <span><strong>Toplam Kelime:</strong> {toplam_kelime}</span>
            <span><strong>Max Heceler:</strong> {max_hece}</span>
            <span><strong>Sıralama:</strong> {siralama}</span>
        </div>

        {hece_gruplari_html}

        {cumleler_html}

        <div class="footer">
            Oluşturulma: {tarih} · ses-grubu-metin v0.1.0 · Lisans: MIT
        </div>
    </div>
</body>
</html>
"""


def _kacis(deger: object) -> str:
    """Şablona gömülecek dinamik değeri HTML olarak kaçışlar.

    ``html.escape(quote=True)`` seçilir: değerler yalnız metin düğümlerine
    değil, tırnak içindeki özniteliklere de gömülebilir.
    """
    return html.escape(str(deger), quote=True)


def _harfler_gosterim(sonuc: SuzmeSonucu) -> str:
    """İzinli harfleri okunur biçimde gösterir (örn. "A E İ K L N")."""
    return turkce_upper(" ".join(sonuc.izinli_harfler))


_SIRALAMA_ETIKETLERI = {
    "siklik": "Sıklık (en sık kullanılan önce)",
    "alfabetik": "Alfabetik",
    "giris": "Giriş sırası",
}


def _siralama_gosterim(sonuc: SuzmeSonucu) -> str:
    """Sıralama ölçütünü okunur biçimde gösterir."""
    return _SIRALAMA_ETIKETLERI.get(sonuc.siralama, sonuc.siralama)


def hece_gruplari_html(sonuc: SuzmeSonucu) -> str:
    """Hece gruplarını HTML olarak render eder."""
    if not sonuc.hece_gruplari:
        return "<p>Bu harflerle kelime bulunamadı.</p>"

    parcalar = []
    for hece_sayisi in sorted(sonuc.hece_gruplari.keys()):
        kelimeler = sonuc.hece_gruplari[hece_sayisi]
        hece_etiket = "Heceli" if hece_sayisi == 1 else "Heceli"
        parcalar.append('<div class="hece-grup">')
        parcalar.append(f"<h2>{hece_sayisi} {hece_etiket} ({len(kelimeler)} kelime)</h2>")
        parcalar.append('<div class="kelime-listesi">')
        for kelime in kelimeler:
            guvenli_kelime = html.escape(kelime)
            parcalar.append(f'<span class="kelime">{guvenli_kelime}</span>')
        parcalar.append("</div>")
        parcalar.append("</div>")

    return "\n".join(parcalar)


def cumleler_html(cumleler: list[Cumle]) -> str:
    """Cümleleri HTML olarak render eder."""
    if not cumleler:
        return ""

    parcalar = ['<div class="cumleler">', "<h2>Örnek Cümleler</h2>"]
    for cumle in cumleler:
        guvenli_metin = html.escape(cumle.metin)
        parcalar.append(f'<div class="cumle">{guvenli_metin}</div>')
    parcalar.append("</div>")
    return "\n".join(parcalar)


def html_cikti(
    sonuc: SuzmeSonucu,
    cumleler: list[Cumle] | None = None,
    cikti_yolu: str | Path | None = None,
    max_hece: int = 3,
) -> str:
    """Süzme sonucunu HTML dosyası olarak yazar.

    Args:
        sonuc: Süzme sonucu.
        cumleler: İsteğe bağlı cümle listesi.
        cikti_yolu: Çıktı dosyası yolu. None ise string döndürür.
        max_hece: Maksimum hece sayısı (gösterim için).

    Returns:
        HTML içeriği (dosya yazılırsa boş string).
    """
    harfler_gosterim = " ".join(list(sonuc.izinli_harfler))
    # Türkçe büyük harfe çevir (İ/ı için)
    harfler_gosterim = turkce_upper(harfler_gosterim)

    icerik = HTML_SABLON.format(
        harfler=html.escape(sonuc.izinli_harfler),
        harfler_gosterim=_kacis(harfler_gosterim),
        toplam_kelime=_kacis(sonuc.toplam_kelime),
        max_hece=_kacis(max_hece),
        siralama=_kacis(_siralama_gosterim(sonuc)),
        hece_gruplari_html=hece_gruplari_html(sonuc),
        cumleler_html=cumleler_html(cumleler or []),
        tarih=datetime.now().strftime("%d.%m.%Y %H:%M"),
    )

    if cikti_yolu:
        Path(cikti_yolu).write_text(icerik, encoding="utf-8")
        return ""
    return icerik


def metin_cikti(
    sonuc: SuzmeSonucu,
    cumleler: list[Cumle] | None = None,
    cikti_yolu: str | Path | None = None,
    max_hece: int = 3,
) -> str:
    """Süzme sonucunu düz metin olarak yazar."""
    satirlar = []
    satirlar.append("SES GRUBU KELİME LİSTESİ")
    satirlar.append("=" * 40)
    harfler_gosterim = " ".join(list(sonuc.izinli_harfler))
    harfler_gosterim = turkce_upper(harfler_gosterim)
    satirlar.append(f"Harfler: {harfler_gosterim}")
    satirlar.append(f"Toplam Kelime: {sonuc.toplam_kelime}")
    satirlar.append(f"Max Heceler: {max_hece}")
    satirlar.append(f"Sıralama: {_siralama_gosterim(sonuc)}")
    satirlar.append(f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    satirlar.append("")

    for hece_sayisi in sorted(sonuc.hece_gruplari.keys()):
        kelimeler = sonuc.hece_gruplari[hece_sayisi]
        hece_etiket = "Heceli" if hece_sayisi == 1 else "Heceli"
        satirlar.append(f"\n{hece_sayisi} {hece_etiket} ({len(kelimeler)} kelime):")
        satirlar.append("-" * 30)
        for _i, kelime_item in enumerate(kelimeler, 1):
            satirlar.append(f"  {kelime_item}")
        satirlar.append("")

    if cumleler:
        satirlar.append("\nÖRNEK CÜMLELER")
        satirlar.append("=" * 40)
        for cumle in cumleler:
            satirlar.append(f"  {cumle.metin}")

    metin = "\n".join(satirlar)

    if cikti_yolu:
        Path(cikti_yolu).write_text(metin, encoding="utf-8")
        return ""
    return metin
