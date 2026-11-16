import numpy as np
from PIL import Image, ImageFilter, ImageDraw
plate=Image.open('art/steam/src/plate.png').convert('RGB'); T=Image.open('art/steam/src/title_layer.png'); T=T.crop(T.getbbox())
PW,PH=plate.size; RADIO_R=775
arr=np.asarray(plate).astype(float); BGC=tuple(int(v) for v in np.median(arr[600:900,1250:1600].reshape(-1,3),0))
def bgcanvas(w,h):
    yy,xx=np.mgrid[0:h,0:w]; r=np.sqrt(((xx-w*.55)/(w*.75))**2+((yy-h*.45)/(h*.75))**2)
    f=np.clip(1.15-0.45*r,0.55,1.15); c=np.array(BGC)[None,None,:]*f[...,None]
    return Image.fromarray(c.clip(0,255).astype('uint8'))
def feather(img,right=None,bottom=None):
    m=Image.new('L',img.size,255); d=ImageDraw.Draw(m); w,h=img.size
    if right:
        for i in range(right): d.line([(w-right+i,0),(w-right+i,h)],fill=int(255*(1-i/right)))
    if bottom:
        mm=Image.new('L',img.size,255); dd=ImageDraw.Draw(mm)
        for i in range(bottom): dd.line([(0,h-bottom+i),(w,h-bottom+i)],fill=int(255*(1-i/bottom)))
        m=Image.fromarray(np.minimum(np.asarray(m),np.asarray(mm)))
    return m
def put_title(c,tw,cx,cy):
    s=tw/T.width; t=T.resize((round(T.width*s),round(T.height*s)),Image.LANCZOS)
    c=c.convert('RGBA'); c.alpha_composite(t,(round(cx-t.width/2),round(cy-t.height/2))); return c.convert('RGB')
def crop_plate(x0,y0,w,h):
    return plate.crop((x0,y0,x0+w,y0+h))
out='art/steam/'
def save(c,size,name): c.resize(size,Image.LANCZOS).save(out+name); print(name,size)
# main capsule 1232x706
w=round(PH*1232/706); c=crop_plate((PW-w)//2,0,w,PH); x0=(PW-w)//2
c=put_title(c,0.44*w,(RADIO_R-x0+w)/2+8,PH*0.47); save(c,(1232,706),'main_capsule_1232x706.png')
# header 920x430 (store + library header)
h=round(PW*430/920); y0=48; c=crop_plate(0,y0,PW,h); c=put_title(c,0.44*PW,(RADIO_R+PW)/2+8,h*0.47)
save(c,(920,430),'header_capsule_920x430.png')
# small 462x174: radio as a sliver, title nearly fills
x0=520; w=PW-x0; h=round(w*174/462); y0=round(400-h/2); c=crop_plate(x0,y0,w,h)
c=put_title(c,0.68*w,(RADIO_R-x0+w)/2-10,h*0.5); save(c,(462,174),'small_capsule_462x174.png')
# page background 1438x810 (no title, dim)
w=round(PH*1438/810); c=bgcanvas(w,PH); c.paste(plate.crop((0,0,min(w,PW),PH)),(0,0)); 
c=Image.blend(c,Image.new('RGB',c.size,(0,0,0)),0.35); save(c,(1438,810),'page_background_1438x810.png')
# vertical-ish: radio on top, title below
def portrait(W2,H2,name,size,ry,ty):
    c=bgcanvas(W2,H2); r=plate.crop((0,0,W2,PH)); c.paste(r,(0,ry),feather(r,right=160,bottom=170))
    if ry>0:
        top=plate.crop((0,0,W2,1)).resize((W2,ry)); c.paste(bgcanvas(W2,ry),(0,0))
    c=put_title(c,0.86*W2,W2/2,ty); save(c,size,name)
portrait(1000,round(1000*896/748),'vertical_capsule_748x896.png',(748,896),0,1060)
portrait(1000,1500,'library_capsule_600x900.png',(600,900),60,1220)
# library hero 3840x1240, no title
w=round(PH*3840/1240); c=bgcanvas(w,PH); c.paste(plate.crop((0,0,1300,PH)),(0,0),feather(plate.crop((0,0,1300,PH)),right=300))
save(c,(3840,1240),'library_hero_3840x1240.png')
# library logo 1280x720 transparent
L=Image.new('RGBA',(1280,720),(0,0,0,0)); s=1200/T.width; t=T.resize((1200,round(T.height*s)),Image.LANCZOS); L.alpha_composite(t,(40,(720-t.height)//2)); L.save(out+'library_logo_1280x720.png'); print('logo')
