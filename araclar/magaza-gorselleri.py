#!/usr/bin/env python3
# Mağaza ekran görüntüleri (App Store iPhone 6.9", iPad 13", Google Play telefon) TR + EN.
# Kullanım: python3 araclar/magaza-gorselleri.py   (www/index.html'i oynatıp kareleri store/ altına yazar)
import asyncio, os
from playwright.async_api import async_playwright
KOK=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIZES={'iphone69':(956,440,3),'ipad13':(1376,1032,2),'play':(960,540,2)}
CAP={'tr':['1923 bölüm: Kapadokya’dan Altaylar’a','Van Gölü’nde Süphan’a karşı tırman','Semerkant’ın mavi kubbeleri','Karlı Ağrı Dağı’nda kaygan yokuşlar','5 efsane araç: Devran 61’den Tagg T10’a','Her bölüm bir görev, üç yıldız'],
     'en':['1923 levels: Cappadocia to the Altai','Climb beside Lake Van and Mount Süphan','The blue domes of Samarkand','Slippery climbs at snowy Mount Ararat','5 legendary rides, Devran 61 to Tagg T10','Every level a goal, three stars']}
SCENES=[(6,'devran',420,'g'),(1000,'anadal',430,'g'),(1610,'taros',600,'g'),(700,'toprak',800,'g'),(1850,'tagg',430,'g'),(None,None,0,'menu')]
SIM=r'''([n,car,steps,mode])=>{SAVE.coins=12450;Object.assign(SAVE.cars,{sahan:1,anadal:1,toprak:1,tagg:1});SAVE.tips={gas:1,air:1,fuel:1,coin:1,mission:1};SAVE.full=1;SAVE.done={};
 for(let k=1;k<n;k++)SAVE.done[k]=1+(k%3?2:1);SAVE.sel.car=car;SAVE.muted=true;RUN={mode:'bolum',n};startRun();input.gas=1;
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
                    if mode=='menu':
                        await pg.evaluate("()=>{SAVE.done={};for(let k=1;k<37;k++)SAVE.done[k]=1+(k%3?2:1);state='menu';show('menu');tab='bolum';bolStage=null;renderMenu();}")
                        await pg.wait_for_timeout(300)
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
                      e.style.cssText='position:fixed;left:50%;transform:translateX(-50%);bottom:'+(document.getElementById('menu').classList.contains('on')?'auto;top:auto;bottom:'+(innerHeight*.5)+'px':'18px')+';z-index:20;padding:8px 22px;border-radius:8px;background:linear-gradient(180deg,rgba(29,49,87,.94),rgba(11,18,32,.94));border:2px solid #f3c04d;color:#fff;font:800 '+Math.round(Math.min(innerWidth,innerHeight)*.065)+'px \"Barlow Condensed\";letter-spacing:.02em;white-space:nowrap;box-shadow:0 8px 24px rgba(0,0,0,.5)';e.textContent=t;}""",CAP[lang][i])
                    await pg.wait_for_timeout(150)
                    await pg.screenshot(path=os.path.join(out,f'0{i+1}.png'))
                    await pg.evaluate("()=>{const e=document.getElementById('shotcap');if(e)e.remove();}")
                if k=='iphone69' and lang=='tr':
                    await pg.evaluate("()=>{state='menu';show('menu');openFull(11);}");await pg.wait_for_timeout(400)
                    await pg.screenshot(path=os.path.join(KOK,'store','iap-inceleme.png'))
                await pg.close()
        await b.close()
asyncio.run(main())
