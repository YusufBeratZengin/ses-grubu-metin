# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-11-03

### Added
- Initial release of ses-grubu-metin
- Letter-set filtering engine (`suz.py`) with Turkish character normalization
- Syllable counting using `syllabreak` library (`hece.py`)
- Dictionary loading with pedagogical filtering (`sozluk.py`)
- Template-based sentence generation (`cumle.py`)
- HTML and plain text output formatting (`cikti.py`)
- Command-line interface with predefined MEB curriculum profiles (`cli.py`)
- Predefined profiles: classic (elakin, omutuy) and Maarif Modeli (anetil, okurim, usoydz, cbgcs, phvgfj)
- Profanity filtering using turkce-kufur-karaliste
- Comprehensive test suite (96 tests, 96% coverage)
- CI/CD pipeline with GitHub Actions (Linux + Windows)
- Documentation: README (EN/TR), CHANGELOG, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT

### Data Sources
- Word list: Turkish Dictionary Dataset (MIT License)
- Profanity blacklist: turkce-kufur-karaliste (CC-BY-SA 4.0)
- Syllabification: syllabreak (MIT License)

[0.1.0]: https://github.com/YusufBeratZengin/ses-grubu-metin/releases/tag/v0.1.0