# Yokuş Yolu — Yayın durumu (18 Kasım 2026)

Kimlik: `com.anduv.yokusyolu` (iOS + Android) · SKU `yokus-yolu` · Ücretli 1,99 $ · Yalnız yatay
Gizlilik: https://emreanduv.github.io/yokus-yolu/gizlilik.html · Mağaza metinleri: `store/magaza-metinleri.md`, `store/appstore-metadata/`
Görseller: `store/screenshots/{tr,en}/{iphone69,ipad13,play}` (`python3 araclar/magaza-gorselleri.py`), `store/play-icon-512.png`, `store/play-feature-1024x500.png`

## Durum
- [x] Oyun 1.0.0 (6 sahne, 5 araç, garaj, 1923 m hedefi, rehber, yardım, puan, paylaş, görüş, verilerimi sil, ekran uyanık)
- [x] Capacitor iOS + Android projesi, simge ve açılış ekranı
- [x] İş akışları: `ios.yml` (TestFlight), `android.yml` (AAB), `appstore-surum.yml` (metin+görsel), `asc-bundle-id.yml`
- [x] Gizlilik sayfası yayında
- [x] Repo açıldı (emreanduv/yokus-yolu). Derleme tetiği: store/TETIK-IOS ve store/TETIK-ANDROID dosyasını değiştirip main'e gönder
- [ ] Emre: repo sırları/değişkeni (ASC_KEY_P8, ANDROID_KEYSTORE_B64, ANDROID_KEYSTORE_PASSWORD, FEEDBACK_MAIL)
- [ ] Emre: App Store Connect'te "Yeni Uygulama" (Bundle ID listede) + fiyat 1,99 $
- [ ] Emre: Play Console'da "Uygulama oluştur" (ücretli) + kapalı test listesi
- [ ] TestFlight + Play kapalı test → cihazda doğrulama → incelemeye gönder
- [ ] Steam (Electron) ve Meta Horizon (WebXR/Quest) paketleri

## Android yükleme anahtarı — KAYBETME
`yokusyolu-upload.jks`, alias `yokusyolu`, şifre `SIFRE-OKU.txt` (git dışında; Google Drive "Yokuş Yolu — Yedekler" klasörüne de koy)
SHA-256: 35:CD:EC:03:CB:4F:0A:97:B2:E4:D4:F9:58:1A:B6:10:29:A0:9D:9E:26:BE:7F:52:74:8F:E3:5B:9C:1D:65:7A
