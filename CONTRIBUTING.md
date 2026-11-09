# Contributing to ses-grubu-metin

Teşekkürler! Katkılarınız bu projeyi daha iyi hale getiriyor.

## Nasıl Katkı Sağlayabilirsiniz?

### 1. Hata Bildirimi
- [GitHub Issues](https://github.com/YusufBeratZengin/ses-grubu-metin/issues) sayfasını kontrol edin
- Yeni bir issue açarken: Python sürümü, işletim sistemi, hata mesajı ve yeniden üretim adımlarını ekleyin

### 2. Özellik Önerisi
- "Feature Request" etiketiyle issue açın
- Kullanım senaryosunu ve beklenen davranışı açıklayın

### 3. Kod Katkısı (Pull Request)

#### Geliştirme Ortamı
```bash
git clone https://github.com/YusufBeratZengin/ses-grubu-metin.git
cd ses-grubu-metin
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

#### Kod Standartları
- **Lint**: `ruff check src tests` (otomatik düzeltme: `ruff check --fix`)
- **Tip kontrolü**: `mypy src/ses_grubu`
- **Testler**: `pytest -q` (kapsama ≥%85)
- **Format**: `ruff format src tests`

#### Pull Request Süreci
1. Fork yapın ve feature branch oluşturun (`git checkout -b feature/amazing-feature`)
2. Değişikliklerinizi yapın, testler geçmeli
3. Commit mesajları İngilizce, imperative mood: "Add syllable grouping for Turkish"
4. Push yapın ve PR açın

#### Commit Mesaj Formatı
```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### 4. Kelime Listesi / Kara Liste Güncellemesi
- `veri/sozcukler.txt` ve `veri/profanity.txt` dosyaları haricen yönetilir
- Güncellemeler için upstream kaynağından (TDK/Zemberek) çekin
- Lisans uyumluluğunu kontrol edin (MIT/CC-BY-SA)

### 5. Yeni Profil Ekleme
- MEB müfredatı değişikliklerinde `src/ses_grubu/cli.py` dosyasındaki `PROFILLER` sözlüğünü güncelleyin
- Test ekleyin: `tests/test_cli.py::TestProfiller`

## Kod Yapısı

```
src/ses_grubu/
├── __init__.py      # Public API exports
├── cli.py           # CLI entry point
├── hece.py          # Syllable counting (Turkish rules)
├── sozluk.py        # Dictionary loading, pedagogical filtering
├── suz.py           # Core filtering engine (letter-set → words)
├── cumle.py         # Template-based sentence generation
└── cikti.py         # HTML/Text output rendering
```

## Test Yazma Kılavuzu

- Testler `tests/` klasöründe, modül başına bir dosya: `test_hece.py`, `test_suz.py`, vb.
- `pytest` parametrize kullanın, edge case'leri kapsayın
- Her yeni özellik için en az bir integration test

## Lisans

Katkılarınız MIT lisansı altında kabul edilir. `LICENSE` dosyasına bakın.

## İletişim

- Issues: GitHub Issues
- Güvenlik: `SECURITY.md` dosyasına bakın