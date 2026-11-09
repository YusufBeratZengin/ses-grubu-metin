"""Testler: ``scripts/sir-tara.sh`` sır tarama betiği.

Betik kabuk tarafında çalıştığı için testler geçici git depoları kurar ve
betiği oraya kopyalayarak gerçek çıkış kodlarını doğrular. Kabuk yoksa
(ör. yalın Windows kurulumu) testler atlanır.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

BASH = shutil.which("bash")
PROJE_KOKU = Path(__file__).resolve().parents[1]
BETIK = PROJE_KOKU / "scripts" / "sir-tara.sh"

pytestmark = pytest.mark.skipif(BASH is None, reason="bash bulunamadı")


def _git(repo: Path, *argumanlar: str) -> None:
    """Geçici depoda git komutu çalıştırır."""
    subprocess.run(["git", *argumanlar], cwd=repo, check=True, capture_output=True)


def _depo_kur(klasor: Path, *, git: bool = True) -> Path:
    """Betiği içeren geçici bir çalışma klasörü hazırlar."""
    (klasor / "scripts").mkdir(parents=True, exist_ok=True)
    shutil.copy2(BETIK, klasor / "scripts" / "sir-tara.sh")
    if git:
        _git(klasor, "init", "-q")
    return klasor


def _betik(repo: Path, *argumanlar: str) -> subprocess.CompletedProcess[str]:
    """Betiği depo kökünden çalıştırır."""
    return subprocess.run(
        [str(BASH), "scripts/sir-tara.sh", *argumanlar],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def _sahte_anahtar() -> str:
    """Kalıba uyan ama açıkça uydurma bir anahtar üretir.

    Parçalar bilinçli olarak birleştirilir: bu test dosyasının kendisi sır
    taramasından geçerken yanlış pozitif üretmemeli.
    """
    return "AKIA" + "Q" * 16


def _yaz(yol: Path, icerik: str) -> None:
    yol.write_text(icerik, encoding="utf-8")


class TestSirTarama:
    """Sır tarama betiğinin davranışı."""

    def test_temiz_depo_sifir_doner(self, tmp_path: Path) -> None:
        repo = _depo_kur(tmp_path)
        _yaz(repo / "notlar.txt", "merhaba dünya\n")
        _git(repo, "add", "notlar.txt")

        sonuc = _betik(repo)

        assert sonuc.returncode == 0, sonuc.stderr
        assert "temiz" in sonuc.stdout

    def test_bosluklu_dosya_adindaki_sir_yakalanir(self, tmp_path: Path) -> None:
        """Dosya adındaki boşluk sözcük bölmesine kurban gitmemeli."""
        repo = _depo_kur(tmp_path)
        _yaz(repo / "giz li notlar.txt", f"anahtar = {_sahte_anahtar()}\n")
        _git(repo, "add", "giz li notlar.txt")

        sonuc = _betik(repo)

        assert sonuc.returncode == 1, sonuc.stdout + sonuc.stderr
        assert "giz li notlar.txt" in sonuc.stderr
        assert "BAŞARISIZ" in sonuc.stderr

    def test_bosluklu_temiz_dosya_atlanmaz(self, tmp_path: Path) -> None:
        """Boşluklu adlı dosya atlanmamalı; diğer dosyalar taranmaya devam etmeli."""
        repo = _depo_kur(tmp_path)
        _yaz(repo / "giz li notlar.txt", "merhaba dünya\n")
        _yaz(repo / "sir.txt", f"anahtar = {_sahte_anahtar()}\n")
        _git(repo, "add", "giz li notlar.txt", "sir.txt")

        sonuc = _betik(repo)

        assert sonuc.returncode == 1
        assert "sir.txt" in sonuc.stderr

    def test_git_deposu_degilse_basarisiz_olur(self, tmp_path: Path) -> None:
        """Depo dışında tarama 'temiz' diyemez; hata koduyla dönmeli."""
        klasor = _depo_kur(tmp_path / "depo-degil", git=False)
        _yaz(klasor / "notlar.txt", "merhaba\n")

        sonuc = _betik(klasor)

        assert sonuc.returncode != 0, sonuc.stdout
        assert "temiz" not in sonuc.stdout

    def test_staged_yoksa_sifir_doner(self, tmp_path: Path) -> None:
        repo = _depo_kur(tmp_path)
        _yaz(repo / "izlenmeyen.txt", "merhaba\n")

        sonuc = _betik(repo, "--staged")

        assert sonuc.returncode == 0, sonuc.stderr
        assert "commit edilecek dosya yok" in sonuc.stdout

    def test_staged_sir_yakalanir(self, tmp_path: Path) -> None:
        repo = _depo_kur(tmp_path)
        _yaz(repo / "ayar.txt", f"token: {_sahte_anahtar()}\n")
        _git(repo, "add", "ayar.txt")

        sonuc = _betik(repo, "--staged")

        assert sonuc.returncode == 1
        assert "ayar.txt" in sonuc.stderr


class TestBetikSozlesmesi:
    """Betiğin depo içindeki kullanım sözleşmesi."""

    def test_dosya_listesi_nul_ayracli(self) -> None:
        icerik = BETIK.read_text(encoding="utf-8")
        assert "git ls-files -z" in icerik
        assert "read -r -d ''" in icerik

    def test_siki_kabuk_ayarlari(self) -> None:
        icerik = BETIK.read_text(encoding="utf-8")
        assert "set -uo pipefail" in icerik

    def test_grep_argumanlari_guvenli(self) -> None:
        """Dosya adları grep'e '--' sonrası verilmeli (tire ile başlayan adlar)."""
        icerik = BETIK.read_text(encoding="utf-8")
        assert 'grep -nIE -e "$KALIPLAR" -- "$dosya"' in icerik
