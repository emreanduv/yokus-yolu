#!/usr/bin/env python3
"""App Store 1.0.0'ı incelemeye hazır hale getirir (göndermez):
yaş derecelendirmesi, içerik hakları, fiyat 1,99 $ + bölgeler (Çin hariç), inceleme bilgileri, derleme seçimi.
Son adım (App Privacy 'Veri toplanmıyor' ve 'Add for Review') Emre'nindir."""
import os, time, jwt, requests, json
B='https://api.appstoreconnect.apple.com'
APP=os.environ['APP_ID']; SURUM=os.environ.get('SURUM','1.0.0')
def H():
    t=jwt.encode({'iss':os.environ['ASC_ISSUER_ID'],'iat':int(time.time()),'exp':int(time.time())+900,'aud':'appstoreconnect-v1'},os.environ['P8'],algorithm='ES256',headers={'kid':os.environ['ASC_KEY_ID'],'typ':'JWT'})
    return {'Authorization':'Bearer '+t,'Content-Type':'application/json'}
def get(p,**q):
    r=requests.get(p if p.startswith('http') else B+p,headers=H(),params=q); r.raise_for_status(); return r.json()
def send(m,p,body):
    r=requests.request(m,B+p,headers=H(),json=body)
    ok=r.status_code<400; print(('✓' if ok else '✗'),m,p.split('?')[0],r.status_code,'' if ok else r.text[:500]); return r
rapor=[]
# --- sürüm
v=[x for x in get(f'/v1/apps/{APP}/appStoreVersions',**{'filter[platform]':'IOS','limit':10})['data'] if x['attributes']['appStoreState'] in ('PREPARE_FOR_SUBMISSION','DEVELOPER_REJECTED','REJECTED','METADATA_REJECTED')]
if not v: raise SystemExit('Düzenlenebilir sürüm yok')
vid=v[0]['id']; print('sürüm',v[0]['attributes']['versionString'],vid)
a={'copyright':'2026 Mr. Anduv!','releaseType':'AFTER_APPROVAL'}
if v[0]['attributes']['versionString']!=SURUM: a['versionString']=SURUM
send('PATCH',f'/v1/appStoreVersions/{vid}',{'data':{'type':'appStoreVersions','id':vid,'attributes':a}})
# --- içerik hakları
send('PATCH',f'/v1/apps/{APP}',{'data':{'type':'apps','id':APP,'attributes':{'contentRightsDeclaration':'DOES_NOT_USE_THIRD_PARTY_CONTENT'}}})
# --- yaş derecelendirmesi (her şey yok/hayır → 4+)
infos=get(f'/v1/apps/{APP}/appInfos')['data']
info=[i for i in infos if i['attributes'].get('appStoreState') not in ('READY_FOR_SALE',)] or infos
iid=info[0]['id']
ard=get(f'/v1/appInfos/{iid}/ageRatingDeclaration')['data']
print('yaş alanları:',json.dumps(ard['attributes'],ensure_ascii=False))
atla={'kidsAgeBand','ageRatingOverride','ageRatingOverrideV2','koreaAgeRatingOverride','developerAgeRatingInfoUrl','gracRatingClassificationNumber'}
BOOL={'advertising','gambling','lootBox','messagingAndChat','parentalControls','ageAssurance','unrestrictedWebAccess','userGeneratedContent','healthOrWellnessTopics','socialMedia','socialMediaAgeRestricted','sharedLocation','datingAndRelationships'}
deg={k:(False if k in BOOL else 'NONE') for k in ard['attributes'] if k not in atla}
for tur in range(8):
    r=requests.patch(f"{B}/v1/ageRatingDeclarations/{ard['id']}",headers=H(),json={'data':{'type':'ageRatingDeclarations','id':ard['id'],'attributes':deg}})
    if r.status_code<400: print('✓ yaş derecelendirmesi', r.status_code); break
    errs=r.json().get('errors',[]); degisti=False
    for e in errs:
        k=(e.get('source',{}).get('pointer','') or '').split('/')[-1]
        if k in deg and e['code'].endswith('TYPE'): deg[k]=(False if deg[k]=='NONE' else 'NONE'); degisti=True
        elif k in deg and e['code'].endswith('REQUIRED'): pass
        elif k and k not in deg and e['code'].endswith('REQUIRED'): deg[k]=False; degisti=True
        elif k in deg and 'INVALID' in e['code']: deg.pop(k); degisti=True
    print('yaş denemesi',tur,r.status_code,[ (e['code'],e.get('source',{}).get('pointer')) for e in errs][:12])
    if not degisti: rapor.append('Yaş derecelendirmesi otomatik doldurulamadı'); break
# --- uygulama fiyatı: ücretsiz (Mr. Anduv! kuralı: mağaza fiyatı 0, Tam Sürüm uygulama içinde)
url=f'{B}/v1/apps/{APP}/appPricePoints'; q={'filter[territory]':'USA','limit':200}; pp=None
while url and not pp:
    d=get(url,**q); q={}
    for x in d['data']:
        if x['attributes'].get('customerPrice') in ('0','0.0','0.00'): pp=x['id']; break
    url=d.get('links',{}).get('next')
print('fiyat noktası',pp)
if pp:
    send('POST','/v1/appPriceSchedules',{'data':{'type':'appPriceSchedules','relationships':{'app':{'data':{'type':'apps','id':APP}},'baseTerritory':{'data':{'type':'territories','id':'USA'}},'manualPrices':{'data':[{'type':'appPrices','id':'${p1}'}]}}},
     'included':[{'type':'appPrices','id':'${p1}','attributes':{'startDate':None},'relationships':{'appPricePoint':{'data':{'type':'appPricePoints','id':pp}}}}]})
else: rapor.append('Ücretsiz fiyat noktası bulunamadı')
# --- bölgeler: hepsi, Çin anakarası hariç (oyun lisansı ister)
ters=[]; url=f'{B}/v1/territories'; q={'limit':200}
while url:
    d=get(url,**q); q={}; ters+= [t['id'] for t in d['data']]; url=d.get('links',{}).get('next')
inc=[]; refs=[]
for i,t in enumerate(ters):
    refs.append({'type':'territoryAvailabilities','id':f'${{t{i}}}'})
    inc.append({'type':'territoryAvailabilities','id':f'${{t{i}}}','attributes':{'available':t!='CHN'},'relationships':{'territory':{'data':{'type':'territories','id':t}}}})
r=send('POST','/v2/appAvailabilities',{'data':{'type':'appAvailabilities','attributes':{'availableInNewTerritories':True},'relationships':{'app':{'data':{'type':'apps','id':APP}},'territoryAvailabilities':{'data':refs}}},'included':inc})
if r.status_code==409: print('bölgeler zaten ayarlı')
# --- inceleme bilgileri (iletişim Malazgirt'ten)
notes=('Yokuş Yolu is a single-player, offline hill climbing game with 1923 levels. No account or login, no ads, no data collection. '
 'The first 100 levels are free; the one-time non-consumable in-app purchase "Tam Sürüm / Full Version" (com.anduv.yokusyolu.tamsurum) unlocks levels 101-1923. '
 'It can be bought from the star button in the main menu or Settings, and restored with "Restore purchases" in the same places. '
 'On first launch the game asks for the language (Turkish/English). Tap "Yola çık / Hit the road" and hold the right pedal (GAS); the left pedal is BRAKE. '
 'Vehicles and upgrades are bought only with in-game coins (akçe) earned by playing. '
 'Settings (gear icon) contains How to Play, Rate, Feedback (opens mail), Recommend to a friend and Delete my data.')
at={'notes':notes,'demoAccountRequired':False}
mal=get('/v1/apps',**{'filter[bundleId]':'com.anduv.malazgirt'})['data']
if mal:
    for mv in get(f"/v1/apps/{mal[0]['id']}/appStoreVersions",limit=5)['data']:
        try:
            d=get(f"/v1/appStoreVersions/{mv['id']}/appStoreReviewDetail")['data']
            if d and d['attributes'].get('contactEmail'):
                for k in ('contactFirstName','contactLastName','contactPhone','contactEmail'): at[k]=d['attributes'][k]
                break
        except Exception as e: pass
try: rd=get(f'/v1/appStoreVersions/{vid}/appStoreReviewDetail')['data']
except Exception: rd=None
if rd: send('PATCH',f"/v1/appStoreReviewDetails/{rd['id']}",{'data':{'type':'appStoreReviewDetails','id':rd['id'],'attributes':at}})
else: send('POST','/v1/appStoreReviewDetails',{'data':{'type':'appStoreReviewDetails','attributes':at,'relationships':{'appStoreVersion':{'data':{'type':'appStoreVersions','id':vid}}}}})
if 'contactEmail' not in at: rapor.append('İnceleme iletişim bilgisi kopyalanamadı (App Review bölümünde elle)')
# --- derleme seç (beklenen derleme görünüp işlenene kadar bekle)
MIN=int(open('store/DERLEME').read().strip()) if os.path.exists('store/DERLEME') else 0
for _ in range(60):
    nb=get('/v1/builds',**{'filter[app]':APP,'filter[preReleaseVersion.version]':SURUM,'sort':'-uploadedDate','limit':1})['data']
    if nb and int(nb[0]['attributes']['version'])<MIN: print('derleme',MIN,'bekleniyor…'); time.sleep(60); continue
    if not nb or nb[0]['attributes']['processingState']!='PROCESSING': break
    print('derleme işleniyor…'); time.sleep(60)
bs=[b for b in get('/v1/builds',**{'filter[app]':APP,'filter[preReleaseVersion.version]':SURUM,'sort':'-uploadedDate','limit':5})['data'] if b['attributes']['processingState']=='VALID']
if bs:
    send('PATCH',f'/v1/appStoreVersions/{vid}/relationships/build',{'data':{'type':'builds','id':bs[0]['id']}})
    print('derleme seçildi:',bs[0]['attributes']['version'])
else: rapor.append('Seçilecek işlenmiş derleme yok')
# --- Tam Sürüm (tek seferlik, iade edilemez olmayan: NON_CONSUMABLE) 1,99 $
PID='com.anduv.yokusyolu.tamsurum'
iaps=get(f'/v1/apps/{APP}/inAppPurchasesV2',limit=50)['data']
iap=[x for x in iaps if x['attributes']['productId']==PID]
if iap: iid2=iap[0]['id']; print('IAP var',iid2,iap[0]['attributes'].get('state'))
else:
    r=send('POST','/v2/inAppPurchases',{'data':{'type':'inAppPurchases','attributes':{'name':'Tam Sürüm','productId':PID,'inAppPurchaseType':'NON_CONSUMABLE','familySharable':False,
      'reviewNote':'Unlocks levels 101-1923. Offered after level 100 and from the star button in the main menu / Settings. Restore purchases is in the same places.'},'relationships':{'app':{'data':{'type':'apps','id':APP}}}}})
    iid2=r.json()['data']['id'] if r.status_code<400 else None
if iid2:
    have={x['attributes']['locale'] for x in get(f'/v2/inAppPurchases/{iid2}/inAppPurchaseLocalizations')['data']}
    for loc,nm,ds in [('tr','Tam Sürüm','1923 bölümün hepsini ve 10 sahneyi açar'),('en-US','Full Version','Unlocks all 1923 levels and 10 stages')]:
        if loc not in have: send('POST','/v1/inAppPurchaseLocalizations',{'data':{'type':'inAppPurchaseLocalizations','attributes':{'locale':loc,'name':nm,'description':ds},'relationships':{'inAppPurchaseV2':{'data':{'type':'inAppPurchases','id':iid2}}}}})
    url=f'{B}/v2/inAppPurchases/{iid2}/pricePoints'; q={'filter[territory]':'USA','limit':200}; ipp=None
    while url and not ipp:
        d=get(url,**q); q={}
        for x in d['data']:
            if x['attributes'].get('customerPrice') in ('1.99','1.990'): ipp=x['id']; break
        url=d.get('links',{}).get('next')
    if ipp:
        send('POST','/v1/inAppPurchasePriceSchedules',{'data':{'type':'inAppPurchasePriceSchedules','relationships':{'inAppPurchase':{'data':{'type':'inAppPurchases','id':iid2}},'baseTerritory':{'data':{'type':'territories','id':'USA'}},'manualPrices':{'data':[{'type':'inAppPurchasePrices','id':'${ip}'}]}}},
         'included':[{'type':'inAppPurchasePrices','id':'${ip}','attributes':{'startDate':None},'relationships':{'inAppPurchasePricePoint':{'data':{'type':'inAppPurchasePricePoints','id':ipp}}}}]})
    else: rapor.append('Tam Sürüm 1,99 $ fiyat noktası bulunamadı')
    r=send('POST','/v1/inAppPurchaseAvailabilities',{'data':{'type':'inAppPurchaseAvailabilities','attributes':{'availableInNewTerritories':True},'relationships':{'inAppPurchase':{'data':{'type':'inAppPurchases','id':iid2}},'availableTerritories':{'data':[{'type':'territories','id':t} for t in ters if t!='CHN']}}}})
    # inceleme ekran görüntüsü
    try:
        ex=None
        try: ex=get(f'/v2/inAppPurchases/{iid2}/appStoreReviewScreenshot')['data']
        except Exception: ex=None
        if not ex:
            import hashlib
            data=open('store/iap-inceleme.png','rb').read()
            r=send('POST','/v1/inAppPurchaseAppStoreReviewScreenshots',{'data':{'type':'inAppPurchaseAppStoreReviewScreenshots','attributes':{'fileName':'tam-surum.png','fileSize':len(data)},'relationships':{'inAppPurchaseV2':{'data':{'type':'inAppPurchases','id':iid2}}}}})
            sd=r.json()['data']
            for op in sd['attributes']['uploadOperations']:
                hd={h['name']:h['value'] for h in op.get('requestHeaders',[])}
                part=data[op['offset']:op['offset']+op['length']]
                requests.request(op['method'],op['url'],headers=hd,data=part).raise_for_status()
            send('PATCH',f"/v1/inAppPurchaseAppStoreReviewScreenshots/{sd['id']}",{'data':{'type':'inAppPurchaseAppStoreReviewScreenshots','id':sd['id'],'attributes':{'uploaded':True,'sourceFileChecksum':hashlib.md5(data).hexdigest()}}})
    except Exception as e: rapor.append(f'Tam Sürüm inceleme görseli yüklenemedi: {e}')
    try: print('Tam Sürüm durumu:',get(f'/v2/inAppPurchases/{iid2}')['data']['attributes'].get('state'))
    except Exception: pass
else: rapor.append('Tam Sürüm (uygulama içi satın alım) oluşturulamadı')
# --- TestFlight beta inceleme durumu
for b in get('/v1/builds',**{'filter[app]':APP,'sort':'-uploadedDate','limit':3})['data']:
    try: s=get(f"/v1/builds/{b['id']}/betaAppReviewSubmission")['data']; print('TestFlight derleme',b['attributes']['version'],'beta inceleme:',s and s['attributes'].get('betaReviewState'))
    except Exception as e: print('beta durumu okunamadı',e)
print('\n== RAPOR ==')
print('\n'.join(rapor) if rapor else 'Otomatik adımların hepsi tamam.')
print('Emre: App Privacy → Veri toplamıyoruz → Yayınla; sürüm sayfasında In-App Purchases bölümüne Tam Sürüm eklenir; sonra Add for Review.')
