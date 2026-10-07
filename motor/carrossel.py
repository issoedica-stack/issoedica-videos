# Render do carrossel diario @issoedica. Uso: python3 motor/carrossel.py copy.json pasta_saida
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os,json
import sys
W,H=1080,1350
COPY=sys.argv[1] if len(sys.argv)>1 else "/tmp/copy.json"
OUT=sys.argv[2] if len(sys.argv)>2 else "/tmp/cout"
os.makedirs(OUT,exist_ok=True)
d0=json.load(open(COPY)); slides=d0["slides"]
C_TOP=(9,12,28); C_BOT=(46,20,84); ACC=(124,92,255); ACC2=(0,224,198); WHITE=(247,248,252); MUT=(176,182,205)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def F(s,b=True): return ImageFont.truetype(FB if b else FR,s)
def bg():
 img=Image.new("RGB",(W,H),C_TOP); px=img.load()
 for y in range(H):
  t=(y/(H-1))**1.1; px_r=(int(C_TOP[0]+(C_BOT[0]-C_TOP[0])*t),int(C_TOP[1]+(C_BOT[1]-C_TOP[1])*t),int(C_TOP[2]+(C_BOT[2]-C_TOP[2])*t))
  for x in range(W): px[x,y]=px_r
 g=Image.new("L",(W,H),0); gd=ImageDraw.Draw(g); gd.ellipse([W-360,-360,W+360,360],fill=90); g=g.filter(ImageFilter.GaussianBlur(160))
 img=Image.composite(Image.blend(img,Image.new("RGB",(W,H),ACC),0.35),img,g)
 g2=Image.new("L",(W,H),0); gd2=ImageDraw.Draw(g2); gd2.ellipse([-380,H-380,380,H+380],fill=60); g2=g2.filter(ImageFilter.GaussianBlur(180))
 img=Image.composite(Image.blend(img,Image.new("RGB",(W,H),ACC2),0.25),img,g2)
 d=ImageDraw.Draw(img,"RGBA"); d.line([(0,H*0.72),(W,H*0.60)],fill=(124,92,255,60),width=3); return img
def wrap(d,t,f,mw):
 out=[]; cur=""
 for w in str(t).split():
  test=(cur+" "+w).strip()
  if d.textlength(test,font=f)<=mw: cur=test
  else:
   if cur: out.append(cur)
   cur=w
 if cur: out.append(cur)
 return out
def ml(d,t,f,x,y,mw,fill,lh=1.14):
 a,de=f.getmetrics(); lhh=int((a+de)*lh); L=wrap(d,t,f,mw)
 for i,ln in enumerate(L): d.text((x,y+i*lhh),ln,font=f,fill=fill)
 return y+len(L)*lhh
def chip(d):
 f=F(26); tw=d.textlength("ISSO É DICA",font=f); d.rounded_rectangle([80,88,80+tw+44,144],radius=28,fill=(255,255,255,18),outline=ACC,width=2); d.text((102,102),"ISSO É DICA",font=f,fill=WHITE)
def footer(d,i,n):
 y=H-72
 for k in range(n): d.ellipse([80+k*26,y,80+k*26+13,y+13],fill=ACC2 if k==i-1 else (95,101,128))
 d.text((W-80,y-4),"@issoedica",font=F(30),fill=MUT,anchor="ra")
def slide(i,n,s):
 img=bg(); d=ImageDraw.Draw(img,"RGBA"); chip(d); k=s["kind"]
 if k=="hook":
  y=286; y=ml(d,s["title"],F(82),80,y,W-160,WHITE,1.06); d.rounded_rectangle([80,y+38,200,y+48],radius=6,fill=ACC2)
  if s.get("body"): ml(d,s["body"],F(38,False),80,y+86,W-160,MUT,1.3)
  d.text((80,H-138),"Arrasta  ->",font=F(34),fill=ACC2)
 elif k=="point":
  d.text((78,232),f"{i-1:02d}",font=F(168),fill=(124,92,255,90)); y=452; y=ml(d,s["title"],F(62),80,y,W-160,WHITE,1.08)
  if s.get("body"): ml(d,s["body"],F(38,False),80,y+34,W-160,(214,218,234),1.34)
 else:
  y=300; y=ml(d,s["title"],F(72),80,y,W-160,WHITE,1.08)
  if s.get("body"): y=ml(d,s["body"],F(38,False),80,y+44,W-160,MUT,1.34)
  by=y+64; d.rounded_rectangle([80,by,W-80,by+100],radius=50,fill=ACC); d.text((W//2,by+32),'Comenta "IA"',font=F(38),fill=WHITE,anchor="ma")
 footer(d,i,n); img.convert("RGB").save(f"{OUT}/{i:02d}.jpg","JPEG",quality=84,optimize=True)
for i,s in enumerate(slides,1): slide(i,5,s)
open(f"{OUT}/legenda.txt","w").write(d0["legenda"])
print("RENDER_OK", os.listdir(OUT))
