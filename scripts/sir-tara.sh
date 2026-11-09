#!/usr/bin/env bash
# scripts/sir-tara.sh - Depoda sır/anahtar kalıbı arar.
# Kullanım:
#   bash scripts/sir-tara.sh            # izlenen tüm dosyalar
#   bash scripts/sir-tara.sh --staged   # yalnız commit'e girecek dosyalar
#
# Çıkış kodları:
#   0  tarama temiz (ya da taranacak dosya yok)
#   1  olası sır bulundu; commit etmeyin
#   2  tarama yapılamadı (git deposu yok, dosya listelenemedi, dosya okunamadı)
#
# Git deposu dışında çalıştırılırsa 0 dönmez: "taranamadı" ile "temiz"
# karıştırılmamalıdır.

set -uo pipefail

if ! KOK="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    echo "Hata: git deposu bulunamadı; sır taraması yapılamadı." >&2
    echo "Betiği bir git çalışma ağacı içinde çalıştırın." >&2
    exit 2
fi

if ! cd "$KOK"; then
    echo "Hata: depo köküne girilemedi: $KOK" >&2
    exit 2
fi

GECICI_LISTE="$(mktemp)" || {
    echo "Hata: geçici dosya oluşturulamadı." >&2
    exit 2
}
GECICI_ESLESME="$(mktemp)" || {
    rm -f "$GECICI_LISTE"
    echo "Hata: geçici dosya oluşturulamadı." >&2
    exit 2
}
trap 'rm -f "$GECICI_LISTE" "$GECICI_ESLESME"' EXIT

# Dosya adları NUL ayraçlı okunur; boşluk ve satır sonu içeren adlar bozulmaz.
if [ "${1:-}" = "--staged" ]; then
    if ! git diff --cached --name-only -z --diff-filter=ACM > "$GECICI_LISTE"; then
        echo "Hata: commit'e girecek dosyalar listelenemedi (git diff --cached)." >&2
        exit 2
    fi
    if [ ! -s "$GECICI_LISTE" ]; then
        echo "Sır taraması: commit edilecek dosya yok."
        exit 0
    fi
else
    if ! git ls-files -z > "$GECICI_LISTE"; then
        echo "Hata: izlenen dosyalar listelenemedi (git ls-files)." >&2
        exit 2
    fi
fi

KALIPLAR='-----BEGIN [A-Z ]*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|AIza[0-9A-Za-z_-]{35}|(password|passwd|secret|api[_-]?key|access[_-]?token)[[:space:]]*[:=]'

BULUNDU=0
HATA=0
TARANAN=0

while IFS= read -r -d '' dosya; do
    [ -n "$dosya" ] || continue
    [ -f "$dosya" ] || continue
    case "$dosya" in
        *.png|*.jpg|*.jpeg|*.gif|*.ico|*.pdf|*.whl|*.gz|*.zip|*.db) continue ;;
    esac
    # scripts/sir-tara.sh kendi kalıplarını içerir; kendini taramaz
    [ "$dosya" = "scripts/sir-tara.sh" ] && continue

    TARANAN=$((TARANAN + 1))
    grep -nIE -e "$KALIPLAR" -- "$dosya" > "$GECICI_ESLESME" 2>/dev/null
    DURUM=$?
    if [ "$DURUM" -eq 0 ]; then
        echo "OLASI SIR: $dosya" >&2
        sed 's/^/    /' "$GECICI_ESLESME" | cut -c1-120 >&2
        BULUNDU=1
    elif [ "$DURUM" -gt 1 ]; then
        echo "Hata: dosya taranamadı: $dosya" >&2
        HATA=1
    fi
done < "$GECICI_LISTE"

if [ "$HATA" -ne 0 ]; then
    echo "" >&2
    echo "Sır taraması TAMAMLANAMADI. Okunamayan dosyaları denetleyin." >&2
    exit 2
fi

if [ "$TARANAN" -eq 0 ]; then
    echo "Sır taraması: taranacak metin dosyası yok."
    exit 0
fi

if [ "$BULUNDU" -ne 0 ]; then
    echo "" >&2
    echo "Sır taraması BAŞARISIZ. Değerleri kaldırın veya ortam değişkenine taşıyın." >&2
    exit 1
fi

echo "Sır taraması temiz ($TARANAN dosya)."
exit 0
