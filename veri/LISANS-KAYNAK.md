# Sözlük Verisi Lisans ve Kaynak Bilgisi

## Veri Kaynağı
Bu projede kullanılan Türkçe kelime listesi, aşağıdaki açık kaynaklı veri setinden elde edilmiştir:

**Turkish Dictionary Dataset & NLP Analysis Reports**
- Depo: https://github.com/ahakanacar/turkish-dictionary-dataset-and-statistics
- Lisans: MIT License
- Açıklama: TDK Güncel Türkçe Sözlük'ten toplanan, Zemberek NLP ile zenginleştirilmiş 64,000+ kelimelik veri seti.

## Lisans (Orijinal MIT Bildirimi)
```
MIT License

Copyright (c) 2021 a-hakan-acar

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Kara Liste (Profanity Filter) Kaynağı
Uygunsuz kelime filtresi için kullanılan kara listesi:

**turkce-kufur-karaliste** (ooguz)
- Depo: https://github.com/ooguz/turkce-kufur-karaliste
- Lisans: Creative Commons Attribution-ShareAlike 4.0 International (CC-BY-SA 4.0)
- Lisans metni: https://github.com/ooguz/turkce-kufur-karaliste/blob/master/LICENSE
- Dosya: `veri/profanity.txt` (karaliste.json'dan dönüştürülmüştür)

## Heceleme
Türkçe heceleme, ünlü sayısı ve ünsüz dağılımı kurallarına göre proje içinde
(`src/ses_grubu/hece.py`) uygulanır; harici bir heceleme kütüphanesi kullanılmaz.

## Proje Kodu Lisansı
Bu projenin kaynak kodu (Python modülleri, CLI, testler, dokümantasyon) MIT lisansı altındadır. Detaylar için kök dizindeki `LICENSE` dosyasına bakın.

## Notlar
- Veri seti TDK Güncel Türkçe Sözlük'ten toplanmıştır; bu nedenle resmî bir onay veya bağlantı değildir.
- Kara liste topluluk kaynaklıdır; eksik veya yanlış girişler olabilir. Öğretmen kontrolü önerilir.
- Bu proje MEB (Milli Eğitim Bakanlığı) resmi bir uygulaması **değildir**.