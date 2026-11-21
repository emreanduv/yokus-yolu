#!/usr/bin/env python3
"""Hazırlanmış App Store sürümünü (SURUM) incelemeye gönderir. Yalnız Emre "gönder" dedikten sonra tetiklenir (store/TETIK-GONDER)."""
import os, time, jwt, requests
B='https://api.appstoreconnect.apple.com'
APP=os.environ['APP_ID']; SURUM=os.environ['SURUM']
def H():
    t=jwt.encode({'iss':os.environ['ASC_ISSUER_ID'],'iat':int(time.time()),'exp':int(time.time())+900,'aud':'appstoreconnect-v1'},os.environ['P8'],algorithm='ES256',headers={'kid':os.environ['ASC_KEY_ID'],'typ':'JWT'})
    return {'Authorization':'Bearer '+t,'Content-Type':'application/json'}
def get(p,**q):
    r=requests.get(B+p,headers=H(),params=q); r.raise_for_status(); return r.json()
def send(m,p,body=None):
    r=requests.request(m,B+p,headers=H(),json=body)
    ok=r.status_code<400; print(('✓' if ok else '✗'),m,p,r.status_code,'' if ok else r.text[:800]); return r
v=[x for x in get(f'/v1/apps/{APP}/appStoreVersions',**{'filter[platform]':'IOS','filter[versionString]':SURUM})['data']]
if not v: raise SystemExit('Sürüm yok: '+SURUM)
st=v[0]['attributes']['appStoreState']; vid=v[0]['id']; print('sürüm',SURUM,st)
if st not in ('PREPARE_FOR_SUBMISSION','DEVELOPER_REJECTED','REJECTED','METADATA_REJECTED'): raise SystemExit('Gönderilecek durumda değil: '+st)
b=get(f'/v1/appStoreVersions/{vid}/build')['data']; print('derleme', b and b['attributes']['version'])
if not b: raise SystemExit('Derleme seçili değil')
# açık bir gönderim varsa onu kullan
subs=get('/v1/reviewSubmissions',**{'filter[app]':APP,'filter[platform]':'IOS','filter[state]':'READY_FOR_REVIEW'})['data']
if subs: sid=subs[0]['id']
else:
    r=send('POST','/v1/reviewSubmissions',{'data':{'type':'reviewSubmissions','attributes':{'platform':'IOS'},'relationships':{'app':{'data':{'type':'apps','id':APP}}}}})
    if r.status_code>=400: raise SystemExit(1)
    sid=r.json()['data']['id']
r=send('POST','/v1/reviewSubmissionItems',{'data':{'type':'reviewSubmissionItems','relationships':{'reviewSubmission':{'data':{'type':'reviewSubmissions','id':sid}},'appStoreVersion':{'data':{'type':'appStoreVersions','id':vid}}}}})
if r.status_code>=400 and 'already' not in r.text.lower(): raise SystemExit(1)
r=send('PATCH',f'/v1/reviewSubmissions/{sid}',{'data':{'type':'reviewSubmissions','id':sid,'attributes':{'submitted':True}}})
if r.status_code>=400: raise SystemExit(1)
time.sleep(10)
print('durum:',get(f'/v1/appStoreVersions/{vid}')['data']['attributes']['appStoreState'])
