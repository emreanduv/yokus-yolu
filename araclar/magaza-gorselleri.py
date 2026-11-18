#!/usr/bin/env python3
# Mağaza ekran görüntüleri (App Store iPhone 6.9", iPad 13", Google Play telefon) TR + EN.
# Kullanım: python3 araclar/magaza-gorselleri.py   (www/index.html'i oynatıp kareleri store/ altına yazar)
import asyncio, os
from playwright.async_api import async_playwright
KOK=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES={'iphone69':(956,440,3),'ipad13':(1376,1032,2),'play':(960,540,2)}
CAP={'tr':['Kapadokya’dan Issık Göl’e tepe tırmanma','Havada takla at, akçeleri topla','5 efsane araç: Devran 61’den Tagg T10’a','Karlı Ağrı Dağı’nda kaygan yokuşlar','Kazak bozkırında uçsuz yollar','Garajda aracını geliştir'],
     'en':['Hill climbing from Cappadocia to Issyk-Kul','Flip in the air, collect akçe','5 legendary rides, Devran 61 to Tagg T10','Slippery climbs at snowy Mount Ararat','Endless roads on the Kazakh steppe','Upgrade your ride in the garage']}
SCENES=[('kapadokya','devran',420,'g'),('pamukkale','anadal',900,'air'),('karadeniz','tagg',430,'g'),('agri','toprak',800,'g'),('bozkir','sahan',1500,'air'),(None,None,0,'garage')]
SIM=r'''([st,car,steps,mode])=>{SAVE.coins=12450;Object.assign(SAVE.cars,{sahan:1,anadal:1,toprak:1,tagg:1});STAGES.forEach(s=>SAVE.stages[s.id]=1);SAVE.tips={gas:1,air:1,fuel:1,coin:1};
 SAVE.sel.stage=st;SAVE.sel.car=car;SAVE.best[st]=1923;SAVE.muted=true;startRun();input.gas=1;
 for(let i=0;i<steps;i++){update(1/60);if(game.crashed)break;}
 if(mode==='air'){for(let i=0;i<1500;i++){update(1/60);if(game.air>.35&&Math.abs(game.car.a)<1.2&&!game.crashed)break;}}
 for(let i=0;i<30&&mode==='g';i++)update(1/60);
 input.gas=0;state='paused';show(null);coachHide();return [game.dist|0,game.crashed];}'''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        for lang in ['tr','en']:
            for k,(w,h,d) in SIZES.items():
                out=os.path.join(KOK,'store','screenshots',lang,k);os.makedirs(out,exist_ok=True)
                pg=await b.new_page(viewport={'width':w,'height':h},device_scale_factor=d)
                await pg.goto('file://'+KOK+'/www/index.html');await pg.wait_for_timeout(600)
                await pg.click(f'#lang .btn[data-l={lang}]');await pg.wait_for_timeout(300)
                for i,(st,car,steps,mode) in enumerate(SCENES):
                    if mode=='garage':
                        await pg.evaluate("()=>{state='menu';show('menu');tab='garage';SAVE.sel.car='tagg';SAVE.upg.tagg={engine:3,susp:2,tires:2,tank:1};renderMenu();}")
                        await pg.wait_for_timeout(400)
                    else:
                        n=steps
                        while True:
                            r=await pg.evaluate(SIM,[st,car,n,mode])
                            ok=await pg.evaluate("()=>!game.crashed&&Math.abs(Math.sin(game.car.a))<0.75&&Math.cos(game.car.a)>0")
                            if ok or n<120: break
                            n=int(n*0.8)
                        await pg.wait_for_timeout(250)
                    await pg.evaluate("""(t)=>{let e=document.getElementById('shotcap');if(!e){e=document.createElement('div');e.id='shotcap';document.body.appendChild(e);}
                      e.style.cssText='position:fixed;left:50%;transform:translateX(-50%);bottom:'+(document.getElementById('menu').classList.contains('on')?'auto;top:6px':'18px')+';z-index:20;padding:8px 22px;border-radius:8px;background:linear-gradient(180deg,rgba(29,49,87,.94),rgba(11,18,32,.94));border:2px solid #f3c04d;color:#fff;font:800 '+Math.round(Math.min(innerWidth,innerHeight)*.065)+'px \"Barlow Condensed\";letter-spacing:.02em;white-space:nowrap;box-shadow:0 8px 24px rgba(0,0,0,.5)';e.textContent=t;}""",CAP[lang][i])
                    await pg.wait_for_timeout(150)
                    await pg.screenshot(path=os.path.join(out,f'0{i+1}.png'))
                    await pg.evaluate("()=>{const e=document.getElementById('shotcap');if(e)e.remove();}")
                await pg.close()
        await b.close()
asyncio.run(main())
