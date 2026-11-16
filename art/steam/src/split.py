import numpy as np
from PIL import Image
src=np.asarray(Image.open('art/steam/src/capsule_source.png').convert('RGB')).astype(float)
H,W,_=src.shape
# title block region
X0,X1,Y0,Y1=712,1640,250,580
plate=src.copy()
top=src[Y0-12:Y0].mean(0); bot=src[Y1:Y1+12].mean(0)
for y in range(Y0,Y1):
    t=(y-Y0)/(Y1-Y0); plate[y,X0:X1]=(top*(1-t)+bot*t)[X0:X1]
# smooth the patched columns horizontally a little
from PIL import ImageFilter
pi=Image.fromarray(plate.astype('uint8')); bl=np.asarray(pi.filter(ImageFilter.GaussianBlur(6))).astype(float)
plate[Y0:Y1,X0:X1]=bl[Y0:Y1,X0:X1]
# color-to-alpha against plate
d=np.clip((src-plate)/np.maximum(255-plate,1),0,1); a=d.max(2)
a[:Y0-0]=0; a[Y1:]=0; a[:, :X0]=0; a[:, X1:]=0
a[a<0.03]=0
fg=np.where(a[...,None]>0, plate+(src-plate)/np.maximum(a[...,None],1e-3),0).clip(0,255)
L=np.dstack([fg,a*255]).astype('uint8')
Image.fromarray(L).crop((X0,Y0,X1,Y1)).save('art/steam/src/title_layer.png')
Image.fromarray(plate.astype('uint8')).save('art/steam/src/plate.png')
