"""Regresyon testleri: dağıtım artefaktı kaynakla aynı olmalı."""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path

import pytest

KOK = Path(__file__).resolve().parents[1]
KAYNAK = KOK / "src"
WHEEL = KOK / "dist" / "ses_grubu_metin-0.1.0-py3-none-any.whl"
SDIST = KOK / "dist" / "ses_grubu_metin-0.1.0.tar.gz"

pytestmark = pytest.mark.skipif(not WHEEL.exists(), reason="dist/ wheel bulunamadı")


def _kaynak_dosyalari() -> list[Path]:
    return sorted(
        p for p in (KAYNAK / "ses_grubu").rglob("*") if p.is_file() and "__pycache__" not in p.parts
    )


def test_wheel_kaynak_dosyalariyla_ayni() -> None:
    """Wheel içindeki her modül/veri dosyası repodaki kaynakla byte-eş olmalı."""
    with zipfile.ZipFile(WHEEL) as z:
        wheel_dosyalar = {n for n in z.namelist() if n.startswith("ses_grubu/")}
        kaynak_dosyalar = {p.relative_to(KAYNAK).as_posix(): p for p in _kaynak_dosyalari()}

        assert wheel_dosyalar == set(kaynak_dosyalar), (
            "Wheel ile kaynak dosya listesi farklı. `python -m build` ile yeniden üretin."
        )
        for rel, yol in kaynak_dosyalar.items():
            assert z.read(rel) == yol.read_bytes(), f"{rel} kaynakla aynı değil"


def test_sdist_kaynak_dosyalariyla_ayni() -> None:
    """sdist içindeki her modül/veri dosyası repodaki kaynakla byte-eş olmalı."""
    if not SDIST.exists():
        pytest.skip("dist/ sdist bulunamadı")

    with tarfile.open(SDIST) as t:
        uyeler = {m.name: m for m in t.getmembers() if m.isfile()}
        onek = "ses_grubu_metin-0.1.0/"
        for yol in _kaynak_dosyalari():
            rel = yol.relative_to(KAYNAK).as_posix()
            uye = uyeler.get(onek + "src/" + rel)
            assert uye is not None, f"{rel} sdist'te yok. `python -m build` ile yeniden üretin."
            dosya = t.extractfile(uye)
            assert dosya is not None
            assert dosya.read() == yol.read_bytes(), f"{rel} kaynakla aynı değil"


def _cli_calistir(pythonpath: Path, args: list[str], cwd: Path) -> str:
    ortam = os.environ.copy()
    ortam["PYTHONPATH"] = str(pythonpath)
    # Alt süreç çıktısı her platformda UTF-8 olmalı (Windows varsayılanı cp1254).
    ortam["PYTHONIOENCODING"] = "utf-8"
    sonuc = subprocess.run(
        [sys.executable, "-m", "ses_grubu.cli", *args],
        cwd=cwd,
        env=ortam,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert sonuc.returncode == 0, sonuc.stderr
    return "\n".join(satir for satir in sonuc.stdout.splitlines() if not satir.startswith("Tarih:"))


def test_alt_surec_ciktisi_utf8_okunur(monkeypatch: pytest.MonkeyPatch) -> None:
    """Alt sürecin stdout kodlaması açıkça UTF-8'e sabitlenmeli (Windows cp1254)."""
    yakalanan: dict[str, object] = {}

    class _Sonuc:
        returncode = 0
        stdout = "alt süreç çıktısı: ışık\n"
        stderr = ""

    def _sahte_run(*args: object, **kwargs: object) -> _Sonuc:
        yakalanan.update(kwargs)
        return _Sonuc()

    monkeypatch.delenv("PYTHONIOENCODING", raising=False)
    monkeypatch.setattr(subprocess, "run", _sahte_run)
    cikti = _cli_calistir(KAYNAK, ["--profil", "elakin"], KOK)

    ortam = yakalanan.get("env")
    assert isinstance(ortam, dict)
    assert ortam.get("PYTHONIOENCODING") == "utf-8"
    assert yakalanan.get("encoding") == "utf-8"
    assert "ışık" in cikti


def test_kurulan_wheel_kaynakla_ayni_cikti(tmp_path: Path) -> None:
    """Wheel'den çalıştırılan CLI, kaynaktan çalıştırılanla aynı çıktıyı vermeli."""
    with zipfile.ZipFile(WHEEL) as z:
        z.extractall(tmp_path)

    args = ["--profil", "elakin", "--en-cok-hece", "2"]
    wheel_cikti = _cli_calistir(tmp_path, args, tmp_path)
    kaynak_cikti = _cli_calistir(KAYNAK, args, KOK)

    assert wheel_cikti == kaynak_cikti
    assert "Harfler: A E İ K L N" in wheel_cikti
