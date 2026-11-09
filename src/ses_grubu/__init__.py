"""ses-grubu-metin: İlk okuma yazma öğretimi için ses grubu kelime/cümle üretici."""

from __future__ import annotations

from .cikti import html_cikti, metin_cikti
from .cli import main
from .cumle import cumle_olustur
from .hece import hece_sayisi, hecele
from .sozluk import (
    cekirdek_sozluk_yukle,
    cocuk_sozlugu_olustur,
    kara_liste_yukle,
    lisans_bilgisi,
    sozluk_yukle,
)
from .suz import SuzmeSonucu, harflere_uyanlar, kelimeleri_suz
from .turkce import (
    harfleri_dogrula,
    harfleri_normalize,
    kara_listede_mi,
    kelime_uygun_mu,
    turkce_lower,
    turkce_upper,
)

__version__ = "0.1.0"
__author__ = "Yusuf Berat Zengin"
__license__ = "MIT"

__all__ = [
    "main",
    "cumle_olustur",
    "html_cikti",
    "metin_cikti",
    "hece_sayisi",
    "hecele",
    "cekirdek_sozluk_yukle",
    "cocuk_sozlugu_olustur",
    "kara_liste_yukle",
    "lisans_bilgisi",
    "sozluk_yukle",
    "SuzmeSonucu",
    "harfleri_dogrula",
    "harflere_uyanlar",
    "harfleri_normalize",
    "kara_listede_mi",
    "kelime_uygun_mu",
    "kelimeleri_suz",
    "turkce_lower",
    "turkce_upper",
]
