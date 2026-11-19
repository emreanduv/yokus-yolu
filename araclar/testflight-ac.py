#!/usr/bin/env python3
"""TestFlight: son derlemeyi bekle, dış test grubunu kur, testçileri ekle, derlemeyi ver, Beta incelemesine gönder."""
import os, time, jwt, requests
B='https://api.appstoreconnect.apple.com/v1'
APP=os.environ['APP_ID']; GRUP='Mr. Anduv! Testçileri'
def H():
    t=jwt.encode({'iss':os.environ['ASC_ISSUER_ID'],'iat':int(time.time()),'exp':int(time.time())+900,'aud':'appstoreconnect-v1'},os.environ['P8'],algorithm='ES256',headers={'kid':os.environ['ASC_KEY_ID'],'typ':'JWT'})
    return {'Authorization':'Bearer '+t,'Content-Type':'application/json'}
def get(p,**q):
    r=requests.get(B+p,headers=H(),params=q); r.raise_for_status(); return r.json()
def post(p,body):
    r=requests.post(B+p,headers=H(),json=body)
    if r.status_code>=400: print('!',p,r.status_code,r.text[:600])
    return r
def patch(p,body):
    r=requests.patch(B+p,headers=H(),json=body)
    if r.status_code>=400: print('!',p,r.status_code,r.text[:600])
    return r
# 1) son derleme işlensin
build=None
MIN=int(os.environ.get('MIN_BUILD') or (open('store/DERLEME').read().strip() if os.path.exists('store/DERLEME') else 0) or 0)
print('beklenen derleme no ≥',MIN)
for i in range(70):
    d=get('/builds',**{'filter[app]':APP,'sort':'-uploadedDate','limit':1})['data']
    if d and int(d[0]['attributes']['version'])<MIN: print('derleme',MIN,'henüz görünmüyor'); time.sleep(60); continue
    if d:
        st=d[0]['attributes']['processingState']; print('derleme',d[0]['attributes']['version'],st)
        if st=='VALID': build=d[0]; break
        if st in ('FAILED','INVALID'): raise SystemExit('Derleme işlenemedi: '+st)
    time.sleep(60)
if not build: raise SystemExit('Derleme 70 dakikada işlenmedi')
bid=build['id']
# 2) ihracat uyumu (şifreleme yok)
if build['attributes'].get('usesNonExemptEncryption') is None:
    patch(f'/builds/{bid}',{'data':{'type':'builds','id':bid,'attributes':{'usesNonExemptEncryption':False}}})
# 3) test bilgileri (Malazgirt'ten iletişim bilgisi kopyala)
src=get('/apps',**{'filter[bundleId]':os.environ['KAYNAK_BUNDLE']})['data']
if src:
    try:
        sd=get(f"/apps/{src[0]['id']}/betaAppReviewDetail")['data']['attributes']
        md=get(f'/apps/{APP}/betaAppReviewDetail')['data']
        at={k:sd.get(k) for k in ('contactFirstName','contactLastName','contactPhone','contactEmail')}
        at.update({'demoAccountRequired':False,'notes':'Tek kişilik, çevrimdışı tepe tırmanma oyunu. Hesap/giriş yok. Sağdaki GAZ pedalı ileri, soldaki FREN.'})
        patch(f"/betaAppReviewDetails/{md['id']}",{'data':{'type':'betaAppReviewDetails','id':md['id'],'attributes':at}})
    except Exception as e: print('iletişim kopyalanamadı:',e)
    try:
        sl=get(f"/apps/{src[0]['id']}/betaAppLocalizations")['data']
        ml={x['attributes']['locale']:x for x in get(f'/apps/{APP}/betaAppLocalizations')['data']}
        for s in sl:
            loc=s['attributes']['locale']; a={'feedbackEmail':s['attributes'].get('feedbackEmail'),'description':'Yokuş Yolu: klasik araçlarla fizik tabanlı tepe tırmanma yarışı.'}
            if loc in ml: patch(f"/betaAppLocalizations/{ml[loc]['id']}",{'data':{'type':'betaAppLocalizations','id':ml[loc]['id'],'attributes':a}})
            else: post('/betaAppLocalizations',{'data':{'type':'betaAppLocalizations','attributes':dict(a,locale=loc),'relationships':{'app':{'data':{'type':'apps','id':APP}}}}})
    except Exception as e: print('yerelleştirme kopyalanamadı:',e)
# 4) "Neyi test etmeli"
for loc,txt in [('tr','İlk sürüm: 6 sahne, 5 araç, garaj geliştirmeleri, 1923 m hedefi. Lütfen dil seçimi, sürüş, ipucu kartları, Ayarlar (puan, bize yaz, paylaş, verilerimi sil) ve iPad görünümünü deneyin.'),('en-US','First release: 6 stages, 5 vehicles, garage upgrades, 1923 m goal. Please try language choice, driving, tip cards, Settings and the iPad layout.')]:
    ex=[x for x in get(f'/builds/{bid}/betaBuildLocalizations')['data'] if x['attributes']['locale']==loc]
    if ex: patch(f"/betaBuildLocalizations/{ex[0]['id']}",{'data':{'type':'betaBuildLocalizations','id':ex[0]['id'],'attributes':{'whatsNew':txt}}})
    else: post('/betaBuildLocalizations',{'data':{'type':'betaBuildLocalizations','attributes':{'locale':loc,'whatsNew':txt},'relationships':{'build':{'data':{'type':'builds','id':bid}}}}})
# 5) dış grup
g=[x for x in get(f'/apps/{APP}/betaGroups')['data'] if x['attributes']['name']==GRUP]
if g: gid=g[0]['id']
else:
    r=post('/betaGroups',{'data':{'type':'betaGroups','attributes':{'name':GRUP,'publicLinkEnabled':False},'relationships':{'app':{'data':{'type':'apps','id':APP}}}}}); r.raise_for_status(); gid=r.json()['data']['id']
print('grup',gid)
# 6) testçiler
var={t['attributes']['email'].lower() for t in get(f'/betaGroups/{gid}/betaTesters',limit=200)['data']}
for e in open('store/testflight-testciler.txt').read().split():
    if e.lower() in var: print('✓ zaten var',e); continue
    r=post('/betaTesters',{'data':{'type':'betaTesters','attributes':{'email':e},'relationships':{'betaGroups':{'data':[{'type':'betaGroups','id':gid}]}}}})
    print('testçi',e,r.status_code)
# 7) derlemeyi gruba ver + incelemeye gönder
post(f'/betaGroups/{gid}/relationships/builds',{'data':[{'type':'builds','id':bid}]})
r=post('/betaAppReviewSubmissions',{'data':{'type':'betaAppReviewSubmissions','relationships':{'build':{'data':{'type':'builds','id':bid}}}}})
print('beta incelemesi',r.status_code)
print('✓ Bitti: derleme',build['attributes']['version'],'→',GRUP)
