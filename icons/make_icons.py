from PIL import Image, ImageDraw, ImageFont, features
import math, os
S=4096
BR=(10,77,65); BR2=(47,168,140)
def grad(size, c1, c2):
    im=Image.new('RGB',(size,size)); px=im.load()
    for y in range(size):
        for x in range(size):
            t=(x+y)/(2*size-2)
            px[x,y]=tuple(int(c1[i]+(c2[i]-c1[i])*t) for i in range(3))
    return im
def glyph(size, scale=1.0):
    # transparent layer: open book + check mark, centered, scale<1 shrinks (adaptive safe zone)
    L=Image.new('RGBA',(size,size),(0,0,0,0)); d=ImageDraw.Draw(L)
    u=size/1000*scale; cx=cy=size/2
    def P(x,y): return (cx+(x-500)*u, cy+(y-500)*u)
    W=(255,255,255,255)
    # book pages (two panels)
    left=[P(120,330),P(480,400),P(480,780),P(120,700)]
    right=[P(880,330),P(520,400),P(520,780),P(880,700)]
    d.polygon(left,fill=W); d.polygon(right,fill=(255,255,255,225))
    # cover edge
    d.polygon([P(90,700),P(480,790),P(480,830),P(90,740)],fill=(255,255,255,170))
    d.polygon([P(910,700),P(520,790),P(520,830),P(910,740)],fill=(255,255,255,170))
    # check mark on right page
    col=(10,77,65,255); w=int(46*u)
    pts=[P(620,560),P(700,640),P(810,500)]
    d.line(pts,fill=col,width=w,joint='curve')
    for p in (pts[0],pts[2]): d.ellipse([p[0]-w/2,p[1]-w/2,p[0]+w/2,p[1]+w/2],fill=col)
    # lines on left page
    for i,yy in enumerate((470,550,630)):
        d.line([P(190,yy-10+i*0),P(410,yy+22)],fill=(10,77,65,160),width=int(26*u))
    # star/cap dot above book
    r=60*u; c=P(500,230)
    d.ellipse([c[0]-r,c[1]-r,c[0]+r,c[1]+r],fill=(255,214,102,255))
    return L
# master (full-bleed, no alpha)
bg=grad(S,BR,BR2).convert('RGBA')
bg.alpha_composite(glyph(S,1.0))
master=bg.convert('RGB')
def save(img,path,size):
    img.resize((size,size),Image.LANCZOS).save(path,'PNG')
for s in (20,29,40,58,60,76,80,87,120,152,167,180,1024):
    save(master,f'icons/ios/icon-{s}.png',s)
save(master,'icons/play/play-store-icon-512.png',512)
for name,s in (('mdpi',48),('hdpi',72),('xhdpi',96),('xxhdpi',144),('xxxhdpi',192)):
    save(master,f'icons/android/ic_launcher-{name}-{s}.png',s)
# adaptive: 108dp canvas; glyph within 66% safe zone
fg=glyph(S,0.62)
bgonly=grad(S,BR,BR2)
for name,s in (('mdpi',108),('hdpi',162),('xhdpi',216),('xxhdpi',324),('xxxhdpi',432)):
    fg.resize((s,s),Image.LANCZOS).save(f'icons/android/ic_launcher_foreground-{name}-{s}.png','PNG')
    bgonly.resize((s,s),Image.LANCZOS).save(f'icons/android/ic_launcher_background-{name}-{s}.png','PNG')
# monochrome (themed icons, Android 13+)
mono=Image.new('RGBA',(S,S),(0,0,0,0)); a=fg.split()[3]
mono=Image.merge('RGBA',(Image.new('L',(S,S),0),Image.new('L',(S,S),0),Image.new('L',(S,S),0),a))
mono.resize((432,432),Image.LANCZOS).save('icons/android/ic_launcher_monochrome-432.png','PNG')
# source files for @capacitor/assets
master.resize((1024,1024),Image.LANCZOS).save('icons/icon-only.png')
fg.resize((1024,1024),Image.LANCZOS).save('icons/icon-foreground.png')
bgonly.resize((1024,1024),Image.LANCZOS).save('icons/icon-background.png')
for s in (192,512):
    save(master,f'icons/pwa/icon-{s}.png',s)
# round preview sheet
# feature graphic 1024x500
FW,FH=2048,1000
fgim=grad(FW,BR,BR2).crop((0,0,FW,FH)).convert('RGBA')
g=glyph(700,1.0); fgim.alpha_composite(g,(1180,150))
d=ImageDraw.Draw(fgim)
import subprocess
def font(sz,bold=True):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p,sz,layout_engine=ImageFont.Layout.RAQM)
f1=font(190); f2=font(80)
d.text((1100,400),'المدارس',font=f1,fill='white',anchor='rm',direction='rtl',language='ar')
d.text((1100,600),'مساعد المعلم',font=f2,fill=(255,255,255,235),anchor='rm',direction='rtl',language='ar')
fgim.convert('RGB').resize((1024,500),Image.LANCZOS).save('icons/play/feature-graphic-1024x500.png')
print('ok')
