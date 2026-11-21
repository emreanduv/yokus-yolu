# Yokuş Yolu — Yayın durumu (19 Kasım 2026)

Kimlik: `com.anduv.yokusyolu` (iOS + Android) · SKU `yokus-yolu` · Mağazada ücretsiz, Tam Sürüm 1,99 $ (`com.anduv.yokusyolu.tamsurum`, ilk 10 bölüm açık) · Yalnız yatay
Gizlilik: https://emreanduv.github.io/yokus-yolu/gizlilik.html · Mağaza metinleri: `store/magaza-metinleri.md`, `store/appstore-metadata/`
Görseller: `store/screenshots/{tr,en}/{iphone69,ipad13,play}` (`python3 araclar/magaza-gorselleri.py`), `store/play-icon-512.png`, `store/play-feature-1024x500.png`

## Durum
- [x] Oyun 1.0.0 (6 sahne, 5 araç, garaj, 1923 m hedefi, rehber, yardım, puan, paylaş, görüş, verilerimi sil, ekran uyanık)
- [x] Capacitor iOS + Android projesi, simge ve açılış ekranı
- [x] İş akışları: `ios.yml` (TestFlight), `android.yml` (AAB), `appstore-surum.yml` (metin+görsel), `asc-bundle-id.yml`
- [x] Gizlilik sayfası yayında
- [x] Repo açıldı (emreanduv/yokus-yolu). Derleme tetiği: store/TETIK-IOS ve store/TETIK-ANDROID dosyasını değiştirip main'e gönder
- [ ] Emre: repo sırları/değişkeni (ASC_KEY_P8, ANDROID_KEYSTORE_B64, ANDROID_KEYSTORE_PASSWORD, FEEDBACK_MAIL)
- [x] App Store Connect kaydı (id 6836515355), TestFlight 1.0.0 (1) beta onaylı, test grubu kuruldu
- [x] App Store 1.0.0: metin + ekran görüntüleri TR/EN, kategori Yarış, yaş 4+, fiyat 1,99 $, bölgeler (Çin hariç), inceleme bilgileri, derleme seçili (`store/TETIK-APPSTORE` → appstore-hazir.yml)
- [x] 1.0.0 (2): 1923 bölüm, 10 sahne, Tam Sürüm, FM2010 menü, Malaklı/Van kedisi; TestFlight'ta (beta inceleme gönderildi); App Store sürümüne derleme 2 seçili; uygulama fiyatı ücretsiz; Tam Sürüm IAP oluşturuldu (yerelleştirme, 1,99 $, bölgeler, inceleme görseli)
- [ ] Emre: TestFlight'ta 1.0.0 (2)'yi dene
- [x] 20 Kas 2026 08:30: App Privacy "Data Not Collected" yayınlandı; iOS 1.0.0 (3) + Tam Sürüm birlikte App Review'a gönderildi (bekleniyor)
- [x] 21 Kas 2026: **1.0.0 App Store'da yayında** (store/SON-SURUM = 1.0.0).
- [x] 21 Kas 2026 12:4x: 1.0.1 (6) (Taros 12, Serbest Sürüş ilk sekme, takla rampaları, menü yerini korur) Emre onayıyla App Review'a gönderildi (appstore-gonder.yml)
- [ ] 1.0.2 (7): beş yeni araç (Marat 124, Egga, Bücek 75, Kersan Jast, Anadal STK-16); çerçeve evren kitabı 4e. 1.0.1 onaylanınca App Store'a gönderilecek.
- Derleme tetikleri: `store/TETIK-IOS` (iOS derle), `store/DERLEME` (beklenen derleme no; TestFlight'a aç), `store/TETIK-APPSTORE` (metin, görsel, fiyat, IAP, derleme seçimi)
- [ ] Emre: Play Console'da "Uygulama oluştur" (ücretli) + kapalı test listesi
- [ ] TestFlight + Play kapalı test → cihazda doğrulama → incelemeye gönder
- [ ] Steam (Electron) ve Meta Horizon (WebXR/Quest) paketleri

## Android yükleme anahtarı — KAYBETME
`yokusyolu-upload.jks`, alias `yokusyolu`, şifre `SIFRE-OKU.txt` (git dışında; Google Drive "Yokuş Yolu — Yedekler" klasörüne de koy)
SHA-256: 35:CD:EC:03:CB:4F:0A:97:B2:E4:D4:F9:58:1A:B6:10:29:A0:9D:9E:26:BE:7F:52:74:8F:E3:5B:9C:1D:65:7A
