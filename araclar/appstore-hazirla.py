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
# --- fiyat 1,99 $ (ABD taban)
url=f'{B}/v1/apps/{APP}/appPricePoints'; q={'filter[territory]':'USA','limit':200}; pp=None
while url and not pp:
    d=get(url,**q); q={}
    for x in d['data']:
        if x['attributes'].get('customerPrice') in ('1.99','1.990'): pp=x['id']; break
    url=d.get('links',{}).get('next')
print('fiyat noktası',pp)
if pp:
    send('POST','/v1/appPriceSchedules',{'data':{'type':'appPriceSchedules','relationships':{'app':{'data':{'type':'apps','id':APP}},'baseTerritory':{'data':{'type':'territories','id':'USA'}},'manualPrices':{'data':[{'type':'appPrices','id':'${p1}'}]}}},
     'included':[{'type':'appPrices','id':'${p1}','attributes':{'startDate':None},'relationships':{'appPricePoint':{'data':{'type':'appPricePoints','id':pp}}}}]})
else: rapor.append('1,99 $ fiyat noktası bulunamadı')
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
notes=('Yokuş Yolu is a single-player, offline hill climbing game. No account or login, no ads, no in-app purchases, no data collection. '
 'On first launch the game asks for the language (Turkish/English). Tap "Yola çık / Hit the road" and hold the right pedal (GAS); the left pedal is BRAKE. '
 'All stages and vehicles can be unlocked with in-game coins (akçe) earned by playing; no real money is involved inside the app. '
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
# --- derleme seç
bs=[b for b in get('/v1/builds',**{'filter[app]':APP,'filter[preReleaseVersion.version]':SURUM,'sort':'-uploadedDate','limit':5})['data'] if b['attributes']['processingState']=='VALID']
if bs:
    send('PATCH',f'/v1/appStoreVersions/{vid}/relationships/build',{'data':{'type':'builds','id':bs[0]['id']}})
    print('derleme seçildi:',bs[0]['attributes']['version'])
else: rapor.append('Seçilecek işlenmiş derleme yok')
# --- TestFlight beta inceleme durumu
for b in get('/v1/builds',**{'filter[app]':APP,'sort':'-uploadedDate','limit':3})['data']:
    try: s=get(f"/v1/builds/{b['id']}/betaAppReviewSubmission")['data']; print('TestFlight derleme',b['attributes']['version'],'beta inceleme:',s and s['attributes'].get('betaReviewState'))
    except Exception as e: print('beta durumu okunamadı',e)
print('\n== RAPOR ==')
print('\n'.join(rapor) if rapor else 'Otomatik adımların hepsi tamam.')
print('Emre: App Privacy → "Veri toplamıyoruz" → Yayınla; sonra "Add for Review".')
