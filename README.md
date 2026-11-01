# Cebir Kaçışı

5. ve 6. sınıf matematik, **2. Tema: İşlemlerle Cebirsel Düşünme** için 3D kovalama oyunu.
Öğrenci karakteri tahtadaki sorunun doğru cevabını toplar, Gri Bıyık onu kovalar.

| Bölüm | Kazanım | Soru türleri |
|---|---|---|
| 1. Sözelden cebire | MAT.6.2.1 | "x TL'den 8 TL fazla", "3 katının 2 fazlası", simit-ayran, dikdörtgen çevresi |
| 2. Denk ifadeler | MAT.6.2.1 | 4a = a + 3a, 3(x + 2) = 3x + 6, katsayı, sabit terim, terim sayısı |
| 3. Örüntüler | MAT.6.2.2 | n. terim kuralı, istenen adımdaki terim, çokgen açıları |
| 4. Algoritma ve değer | MAT.6.2.3 | ifadenin değeri, adım adım algoritma, "aklından bir sayı tut" |

## Karakterler
3D modeller Blender ile `blender/karakterler.py` betiğinden üretilir:

```
blender -b -P blender/karakterler.py -- web/karakterler.glb
```

Sayfa kaynağı `src/template.html` + `src/sorular.js` (6. sınıf) + `src/sorular5.js` (5. sınıf); `python3 src/build.py` ile `web/index.html` oluşturulur.

## Kontroller
Dokunmatik joystick (tablet/telefon) veya ok tuşları / W A S D.

## Bağlantılar
- Oyun (GitHub Pages): https://ekerem.github.io/cebir-kacisi/
- APK indir: https://github.com/Ekerem/cebir-kacisi/releases/latest/download/cebir-kacisi.apk

## Sınıflar
Menüden **5. Sınıf** (İşlemlerle Cebirsel Düşünme: eşitlik ve işlem özellikleri, işlem önceliği, örüntüler, algoritmalar; kolaydan zora) veya **6. Sınıf** (yukarıdaki tablo) seçilir.

## Yeni sürüm
`src/template.html` içindeki `APP_VERSION` ve `web/version.json` aynı anda artırılır, `python3 src/build.py` çalıştırılır ve yeni etiket (ör. `v1.5.1`) gönderilir. APK iş akışı Release'i kendisi oluşturur.

Made by Us
