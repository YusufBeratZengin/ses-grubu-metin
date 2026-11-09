"""Türkçe büyük/küçük harf dönüşüm yardımcıları."""

from __future__ import annotations

# Türkçe büyük-küçük harf eşleştirmesi
_TURKCE_BUYUK_KUCUK = {
    "İ": "i",  # U+0130 -> U+0069
    "I": "ı",  # U+0049 -> U+0131
    "Ğ": "ğ",
    "Ü": "ü",
    "Ş": "ş",
    "Ö": "ö",
    "Ç": "ç",
}

_TURKCE_KUCUK_BUYUK = {v: k for k, v in _TURKCE_BUYUK_KUCUK.items()}


def turkce_lower(metin: str) -> str:
    """Türkçe kurallarına göre küçük harfe çevirir.

    Standart .lower() İ->i ve I->ı'yı yanlış işler.
    Bu fonksiyon İ->i, I->ı doğru şekilde dönüştürür.

    Args:
        metin: Dönüştürülecek metin.

    Returns:
        Küçük harfe çevrilmiş metin.
    """
    # Özel Türkçe harfleri ÖNCE değiştir
    sonuc = []
    for harf in metin:
        sonuc.append(_TURKCE_BUYUK_KUCUK.get(harf, harf.lower()))
    return "".join(sonuc)


def turkce_upper(metin: str) -> str:
    """Türkçe kurallarına göre büyük harfe çevirir.

    Standart .upper() i->İ ve ı->I'yi yanlış işler.
    Bu fonksiyon i->İ, ı->I doğru şekilde dönüştürür.

    Args:
        metin: Dönüştürülecek metin.

    Returns:
        Büyük harfe çevrilmiş metin.
    """
    sonuc = []
    for harf in metin:
        sonuc.append(_TURKCE_KUCUK_BUYUK.get(harf, harf.upper()))
    return "".join(sonuc)


#: Veri kümesinde geçen Türkçe harfler. â/î/û gibi yazım işaretleri listede
#: bulunmadığı için kabul edilmez; Kiril/Yunan gibi yabancı alfabeler de reddedilir.
TURKCE_HARFLER = "abcçdefgğhıijklmnoöprsştuüvyz"


def harfleri_dogrula(harfler: str) -> str:
    """Harf kümesini doğrular ve kenar boşluklarını temizler.

    Doğrulama, harf kümesinin dışa aktarılan her yoldan (CLI, kütüphane API'si,
    HTML başlığı) güvenli olmasını sağlar. Büyük harf serbesttir
    (``"ELAKİN"``); karşılaştırma Türkçe küçük harfe çevrilerek yapılır.

    Args:
        harfler: Ham harf dizisi.

    Returns:
        Kenar boşlukları temizlenmiş girdi.

    Raises:
        ValueError: Girdi boşsa ya da Türkçe alfabede olmayan bir karakter
            içeriyorsa. Hata iletisi sorunlu karakteri ``repr`` ile gösterir.
    """
    temiz = harfler.strip()
    if not temiz:
        raise ValueError("Harf kümesi boş olamaz.")

    for harf in turkce_lower(temiz):
        if harf not in TURKCE_HARFLER:
            raise ValueError(
                f"Harf kümesinde sadece Türkçe harf olmalı, geçersiz karakter: {harf!r}"
            )
    return temiz


def harfleri_normalize(harfler: str) -> str:
    """Harf kümesini normalize eder (küçük harf, benzersiz, alfabetik).

    Türkçe karakterleri korur: ı, ğ, ü, ş, ö, ç
    Büyük İ -> küçük i, Büyük I -> küçük ı

    Args:
        harfler: Ham harf dizisi (örn. "ELAKİN" veya "elakin").

    Returns:
        Normalize edilmiş harf kümesi (örn. "aeikln").
    """
    harfler = turkce_lower(harfleri_dogrula(harfler))
    # Benzersiz ve alfabetik (Unicode code point sırası)
    return "".join(sorted(set(harfler)))


# Kara listedeki kelimelere eklenebilecek çekim ekleri. Yalnızca tam kelime
# veya gerçek çekim ekiyle türemiş hâller elenir; alt dize eşleşmesi yapılmaz.
# Böylece "anahtar", "kanal", "temiz", "hassas" gibi masum kelimeler korunur.
CEKIM_EKLERI = frozenset(
    {
        # Çoğul
        "lar",
        "ler",
        # Çoğul + hâl
        "ları",
        "leri",
        "lara",
        "lere",
        "larda",
        "lerde",
        "lardan",
        "lerden",
        "ların",
        "lerin",
        "larla",
        "lerle",
        # Tekil hâl ekleri
        "yı",
        "yi",
        "yu",
        "yü",
        "ya",
        "ye",
        "da",
        "de",
        "ta",
        "te",
        "nda",
        "nde",
        "dan",
        "den",
        "tan",
        "ten",
        "ndan",
        "nden",
        "ın",
        "in",
        "un",
        "ün",
        "nın",
        "nin",
        "nun",
        "nün",
        "la",
        "le",
        "yla",
        "yle",
        # İyelik
        "sı",
        "si",
        "su",
        "sü",
        "mız",
        "miz",
        "muz",
        "müz",
        "nız",
        "niz",
        "nuz",
        "nüz",
        # Bildirme ve kişi ekleri
        "dır",
        "dir",
        "dur",
        "dür",
        "tır",
        "tir",
        "tur",
        "tür",
        "ım",
        "im",
        "um",
        "üm",
        "sın",
        "sin",
        "sun",
        "sün",
        "sınız",
        "siniz",
        "sunuz",
        "sünüz",
    }
)


# Kök + ek gibi görünse de sözlükte bağımsız bir kelime olan istisnalar.
# "malum", kara listedeki "mal" + "um" sanılarak yanlışlıkla elenmemeli.
KARA_LISTE_ISTISNALARI = frozenset({"malum"})


def kara_listede_mi(kelime: str, kara_liste: set[str] | None) -> bool:
    """Kelimenin kara listede veya kara liste kökünün çekimli hâli olup olmadığını söyler.

    Alt dize eşleşmesi yerine kök + geçerli çekim eki kontrolü yapılır. Böylece
    "ana" kökü "anane"/"analı" gibi masum kelimeleri elemez; yalnızca "analar"
    gibi gerçek çekimli hâller elenir.

    Args:
        kelime: Kontrol edilecek kelime.
        kara_liste: Kara liste kümesi. Boş/None ise hiçbir şey elenmez.

    Returns:
        Kelime elenmeli ise True.
    """
    if not kara_liste:
        return False

    kelime = turkce_lower(kelime.strip())
    if kelime in kara_liste:
        return True
    if kelime in KARA_LISTE_ISTISNALARI:
        return False

    for ek in CEKIM_EKLERI:
        # Tek harflik ekler ("ana" + "e" -> "anae") çok fazla yanlış eşleşme
        # ürettiği için yalnızca en az iki harflik gerçek çekim ekleri denenir.
        if len(ek) < 2 or not kelime.endswith(ek):
            continue
        kok = kelime[: -len(ek)]
        # Kısa köklerde (ör. "am") ek kontrolü "ama" gibi masum kelimeleri eler.
        if len(kok) >= 3 and kok in kara_liste:
            return True
    return False


def kelime_uygun_mu(kelime: str, izinli_harfler: str, kara_liste: set[str] | None = None) -> bool:
    """Kelimenin yalnız izinli harflerden oluşup oluşmadığını kontrol eder.

    Args:
        kelime: Kontrol edilecek kelime.
        izinli_harfler: Normalize edilmiş izinli harfler.
        kara_liste: İsteğe bağlı kara listesi.

    Returns:
        Kelime uygunsa True, değilse False.
    """
    if not kelime or not kelime.isalpha():
        return False

    kelime = turkce_lower(kelime)
    izinli = set(izinli_harfler)

    # Kara listesi kontrolü (tam kelime veya gerçek çekim eki)
    if kara_listede_mi(kelime, kara_liste):
        return False

    # Tüm harfler izinli mi?
    return all(harf in izinli for harf in kelime)
