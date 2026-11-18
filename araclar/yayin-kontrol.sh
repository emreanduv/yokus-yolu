#!/usr/bin/env bash
# Yayın öncesi kontrol: mağazaya giden her derleme bundan geçer. Bir şey eksikse derleme DURUR.
set -u
hata=0
dal="${GITHUB_REF_NAME:-$(git rev-parse --abbrev-ref HEAD)}"
if [ "$dal" != "main" ]; then echo "::error::Mağaza derlemesi yalnız main dalından alınır (bu dal: $dal)"; hata=1; fi
kontrol() { if ! grep -q -- "$2" "$1"; then echo "::error::Eksik: $3 ($1 içinde '$2' yok)"; hata=1; else echo "✓ $3"; fi; }
kontrol www/index.html 'Bir Mr. Anduv! yapımıdır.' 'Ana ekranda imza'
kontrol www/index.html 'id="lang"' 'Açılışta dil sorusu'
kontrol www/index.html 'id="bHelp"' 'Nasıl Oynanır (ana menü)'
kontrol www/index.html 'id="pHelp"' 'Nasıl Oynanır (mola)'
kontrol www/index.html 'id="bShare"' 'Arkadaşına öner'
kontrol www/index.html 'id="setRate"' 'Puan ver (Ayarlar)'
kontrol www/index.html 'id="setFeed"' 'Bize yaz (Ayarlar)'
kontrol www/index.html 'id="setErase"' 'Verilerimi sil (Ayarlar)'
kontrol www/index.html 'function coachTick' 'Rehber (ipucu kartları)'
kontrol www/index.html 'InAppReview' 'Uygulama içi puan'
kontrol www/index.html 'navigator.wakeLock' 'Ekran uyanık (web)'
kontrol www/index.html 'PANOLAR' 'Mr. Anduv! ortak pano seti'
kontrol www/index.html "'KeyD'" 'Klavye WASD'
kontrol package.json '@capacitor-community/in-app-review' 'In-App Review eklentisi'
kontrol package.json '@capacitor/share' 'Paylaş eklentisi'
kontrol ios/App/App/AppDelegate.swift 'isIdleTimerDisabled = true' 'Ekran uyanık (iOS)'
kontrol android/app/src/main/java/com/anduv/yokusyolu/MainActivity.java 'FLAG_KEEP_SCREEN_ON' 'Ekran uyanık (Android)'
if [ -n "${CI:-}" ] && ! grep -q "@" www/iletisim.js; then echo "::warning::Görüş adresi boş: repo Settings → Variables → FEEDBACK_MAIL ekleyin (Bize yaz adressiz açılır)"; fi
if [ -n "${SURUM:-}" ] && [ -f store/SON-SURUM ]; then
  son=$(cat store/SON-SURUM)
  if [ "$(printf '%s\n%s\n' "$son" "$SURUM" | sort -V | head -1)" != "$son" ]; then echo "::error::Sürüm geri gidiyor: $SURUM < $son"; hata=1; else echo "✓ Sürüm $SURUM ≥ $son"; fi
fi
if python3 araclar/turkce-yazi-kontrol.py www; then :; else hata=1; fi
[ $hata -eq 0 ] && echo "Yayın kontrolü geçti." || { echo "Yayın kontrolü BAŞARISIZ — derleme durduruldu."; exit 1; }
