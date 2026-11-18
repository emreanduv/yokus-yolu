import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1024,'height':500})
        await pg.goto('file:///home/claude/yokus-yolu-app/www/index.html');await pg.wait_for_timeout(600)
        await pg.click('#lang .btn[data-l=tr]')
        await pg.evaluate("""()=>{SAVE.tips={gas:1,air:1,fuel:1,coin:1};SAVE.muted=true;SAVE.sel.stage='kapadokya';SAVE.sel.car='devran';startRun();input.gas=1;for(let i=0;i<330;i++)update(1/60);input.gas=0;state='paused';show(null);window.NOHUD=1;
          ['brk','gas','hudBtns'].forEach(i=>document.getElementById(i).style.display='none');
          const e=document.createElement('div');e.innerHTML='<div class=title style="font-size:96px;text-align:right">YOKUŞ YOLU</div><div class=sig style="text-align:right;font-size:18px;margin-top:6px;color:#fff;text-shadow:0 2px 6px rgba(0,0,0,.9)">Bir Mr. Anduv! yapımıdır.</div>';e.style.cssText='position:fixed;right:40px;top:40px;z-index:30';document.body.appendChild(e);}""")
        await pg.wait_for_timeout(400)
        await pg.screenshot(path='/home/claude/yokus-yolu-app/store/play-feature-1024x500.png')
        await b.close()
asyncio.run(main())
