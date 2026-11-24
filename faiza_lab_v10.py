#!/usr/bin/env python3
# FAIZA V10 - experimental reverse calibration from known final bead grids.
# NO ML / no generative AI. Python, OpenCV, NumPy and Pillow only.
# NOT VTracer or ImageTracerJS: those two upstream engines are not installed here.
from __future__ import annotations
import csv, json, math, os, io, statistics, collections
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from skimage.color import rgb2lab
ROOT=Path(__file__).resolve().parent
S=10; SEED=20261123
np.random.seed(SEED)
PALETTES={
 'coquelicot': ['#F5F2ED','#15151A','#6D1725','#CD2434','#EE5148','#8D5B2B','#D9A547','#F5D78D','#462C29','#FBEAC7'],
 'floral_vert': ['#F5F2ED','#075946','#0F846B','#67B993','#F1E9D6','#EEA9BE','#B4215A','#E8BB4C','#263D3B'],
 'geometrique': ['#F5F2ED','#141D36','#CB3042','#E3AA4F','#EEE5CE','#1A8A82','#6F3768','#7D93A8']
}
def to_rgb(hex):return tuple(int(hex[i:i+2],16) for i in (1,3,5))
def make_masters():
 # Coquelicot comes from actual V08 hand-built bead chart. Not a proven craft chart.
 p=ROOT/'masters'/'source_v08_grille_corps.csv'
 if not p.exists():raise FileNotFoundError('Missing included masters/source_v08_grille_corps.csv')
 cmap={'':0, 'C0':1,'C1':2,'C2':3,'C3':4,'C4':5,'C5':6,'C6':7,'C7':8,'C8':9}
 with p.open(encoding='utf-8-sig',newline='') as f:
  rows=list(csv.reader(f))[1:]
 pop=np.array([[cmap.get(v.strip(),0) for v in row[1:63]] for row in rows],np.uint8)
 # floral bracelet: repeat tiny flowers and coherent 1-cell contrasting borders.
 H,W=38,100
 f=np.full((H,W),2,np.uint8)
 f[0:2,:]=1;f[-2:,:]=1;f[:,0:2]=1;f[:,-2:]=1
 f[3:35,3:97]=3
 for cx in [15,38,61,84]:
  for cy in [12,26]:
   for y in range(cy-7,cy+8):
    for x in range(cx-7,cx+8):
     if 0<=y<H and 0<=x<W:
      dx=x-cx;dy=y-cy
      # four petal ovals, dark outline and pale inner
      for ox,oy in [(-4,0),(4,0),(0,-4),(0,4)]:
       r=((dx-ox)/3.0)**2+((dy-oy)/3.0)**2
       if r<=1.6:f[y,x]=8
       if r<=1.05:f[y,x]=4
      if dx*dx+dy*dy<=3.5:f[y,x]=7
   for y in [6,19,33]:
    for x in range(cx-2,cx+3):
     if 0<=x<W and 0<=y<H: f[y,x]=5 if (x+y)%2 else 6
 f[4,4:-4]=1;f[-5,4:-4]=1
 # geometric bracelet, includes isolated diagonal and narrow step-lines
 H,W=48,96;g=np.full((H,W),1,np.uint8)
 g[0:2,:]=3;g[-2:,:]=3;g[:,0:2]=3;g[:,-2:]=3
 for cx in [15,47,79]:
  for y in range(4,44):
   for x in range(max(2,cx-15),min(W-2,cx+16)):
    dx=abs(x-cx);dy=abs(y-24)
    d=dx/14+dy/18
    if d<1:g[y,x]=2
    if 0.83<d<1.08:g[y,x]=3
    if d<0.68:g[y,x]=4
    if 0.50<d<0.63:g[y,x]=5
    if d<0.37:g[y,x]=6
    if d<0.20:g[y,x]=3
  for x in range(cx-14,cx+15,2):
   if x>=0 and x<W:
    for y in [7,41]:g[y,x]=7
 for y in range(5,44,5):
  for x in range(1,W-1):
   if (x+y)%13==0:g[y,x]=3
 return {'coquelicot':pop,'floral_vert':f,'geometrique':g}

def render_beads(gt,palette,seed=SEED):
 H,W=gt.shape;bg=np.array([236,232,224],np.uint8)
 img=np.tile(bg,(H*S,W*S,1))
 rng=np.random.default_rng(seed)
 colors=[np.array(to_rgb(x),np.float32) for x in palette]
 for j in range(H):
  for i in range(W):
   c=int(gt[j,i]);
   if not c:continue
   x=int(i*S+S/2); y=int(j*S+S/2)
   # deep round bead rim and inner color with very slight texture.
   color=colors[c]; illum=0.93+0.06*(i/W)+0.06*(1-j/H)+float(rng.normal(0,0.02))
   col=tuple(int(x) for x in np.clip(color*illum,0,255))
   edge=tuple(int(x) for x in np.clip(color*0.59,0,255))
   cv2.circle(img,(x,y),int(S*.46),edge,-1,cv2.LINE_AA)
   cv2.circle(img,(x,y),int(S*.39),col,-1,cv2.LINE_AA)
   hi=tuple(int(x) for x in np.clip(color*.80+np.array([255,255,255])*.20,0,255))
   cv2.circle(img,(x-2,y-2),max(1,int(S*.10)),hi,-1,cv2.LINE_AA)
 return img

def distort(src,typ,val):
 # vals are experimental perturbations, not acceptance cutoffs.
 im=src.copy()
 if typ=='propre':return im
 if typ=='flou':
  return cv2.GaussianBlur(im,(0,0),val) if val else im
 if typ=='reduction':
  h,w=im.shape[:2]
  tiny=cv2.resize(im,(max(4,round(w*val)),max(4,round(h*val))),interpolation=cv2.INTER_AREA)
  return cv2.resize(tiny,(w,h),interpolation=cv2.INTER_LINEAR)
 if typ=='jpeg':
  ok,by=cv2.imencode('.jpg',cv2.cvtColor(im,cv2.COLOR_RGB2BGR),[cv2.IMWRITE_JPEG_QUALITY,int(val)])
  return cv2.cvtColor(cv2.imdecode(by,cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
 if typ=='bruit':
  rng=np.random.default_rng(SEED+int(val))
  return np.clip(im.astype(np.float32)+rng.normal(0,val,im.shape),0,255).astype(np.uint8)
 if typ=='lumiere':
  return np.clip((im.astype(np.float32)/255)**(1/val)*255,0,255).astype(np.uint8)
 raise ValueError(typ)

def lab_palette(colors):
 return rgb2lab(np.asarray([[to_rgb(c) for c in colors]],np.float32)/255)[0]

def labels_by_palette(image_rgb,colors,mode='brut'):
 # pixel-wise nearest LAB; label 0=blank/background; known calibration palette.
 inp=image_rgb
 if mode=='lisse':inp=cv2.bilateralFilter(inp,7,32,32)
 ref=lab_palette(colors).astype('float32')
 h,w=inp.shape[:2]
 # binned conversion for memory/time, 1/2 or 1/3px is adequate for a 10px bead.
 step=2
 sm=inp[::step,::step,:]
 lab=rgb2lab(sm.astype(np.float32)/255).astype('float32')
 flat=lab.reshape(-1,3)
 pred=np.empty(flat.shape[0],np.uint8)
 for start in range(0,len(flat),24000):
  pts=flat[start:start+24000]
  diff=((pts[:,None,:]-ref[None,:,:])**2).sum(axis=2)
  pred[start:start+len(pts)]=np.argmin(diff,axis=1)
 ids=pred.reshape(sm.shape[:2])
 if mode=='lisse': ids=cv2.medianBlur(ids,3)
 return cv2.resize(ids,(w,h),interpolation=cv2.INTER_NEAREST)

def grid_from_labels(lbl,H,W):
 # sample pixels at each expected cell center; five-point vote is stable for real bead textures.
 y=(np.arange(H)*S+S//2).astype(int);x=(np.arange(W)*S+S//2).astype(int)
 points=[]
 for ox,oy in [(0,0),(-2,0),(2,0),(0,-2),(0,2)]:
  yy=np.clip(y+oy,0,lbl.shape[0]-1);xx=np.clip(x+ox,0,lbl.shape[1]-1)
  points.append(lbl[np.ix_(yy,xx)])
 arr=np.stack(points,axis=0)
 # majority; ties resolve to center.
 vals=np.empty((H,W),np.uint8)
 for j in range(H):
  # vectorized row count
  group=arr[:,j,:]
  for k in range(W):
   cnt=np.bincount(group[:,k],minlength=10)
   top=np.where(cnt==cnt.max())[0]
   vals[j,k]=int(group[0,k]) if group[0,k] in top else int(top[0])
 return vals

def metrics(gt,pred, image):
 fg=gt>0
 hit=pred==gt
 # foreground color accuracy; exact full-grid accuracy includes background.
 accuracy=float(hit[fg].mean()) if fg.any() else np.nan
 exact=float(hit.mean())
 pfg=pred>0
 iou=float((fg&pfg).sum()/max(1,(fg|pfg).sum()))
 # motif accent classes excluding dominant color and background
 u,cts=np.unique(gt[fg],return_counts=True)
 top=u[int(np.argmax(cts))] if len(u) else -1
 accent=fg&(gt!=top)
 ac=float(hit[accent].mean()) if accent.any() else np.nan
 # boundary truth/pred disagree over 4-neighbors, normalize over gt boundary locations
 ey0=gt[:-1,:]!=gt[1:,:];ex0=gt[:,:-1]!=gt[:,1:]
 ey1=pred[:-1,:]!=pred[1:,:];ex1=pred[:,:-1]!=pred[:,1:]
 tp=int((ey0&ey1).sum()+(ex0&ex1).sum());fn=int((ey0&(~ey1)).sum()+(ex0&(~ex1)).sum());fp=int(((~ey0)&ey1).sum()+((~ex0)&ex1).sum())
 bf1=2*tp/max(1,2*tp+fp+fn)
 # rank-normalized image metrics over same output pixel dimensions
 gray=cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
 lap=float(cv2.Laplacian(gray,cv2.CV_32F).var())
 gx=cv2.Sobel(gray,cv2.CV_32F,1,0,ksize=3);gy=cv2.Sobel(gray,cv2.CV_32F,0,1,ksize=3)
 ten=float(np.mean(gx*gx+gy*gy))
 # local contrast ratio (image-wide)
 contrast=float(np.percentile(gray,95)-np.percentile(gray,5))
 return dict(exact=exact,foreground=accuracy,accent=ac,mask_iou=iou,boundary_f1=bf1,laplacian=lap,tenengrad=ten,contrast=contrast,wrong_fg=int((~hit&fg).sum()),n_fg=int(fg.sum()))

def make_svg_from_pixel_labels(lbl,colors,out,scale=1, simplification=1.0):
 # Actual contour-based SVG, no vtracer / imagetracer. Paths traced from quantized mask.
 h,w=lbl.shape
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">',f'<rect width="{w}" height="{h}" fill="{colors[0]}"/>']
 paths=0
 for idx in range(1,len(colors)):
  mask=((lbl==idx).astype('uint8')*255)
  contours,hier=cv2.findContours(mask,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_SIMPLE)
  childmap={}
  if hier is not None:
   for j,meta in enumerate(hier[0]):
    par=int(meta[3])
    if par>=0:childmap.setdefault(par,[]).append(j)
  for q,c in enumerate(contours):
   if hier is not None and hier[0][q][3]>=0:continue  # holes attached through fill-rule
   if cv2.contourArea(c)<5:continue
   d=[]
   for j in [q]+childmap.get(q,[]):
    c2=contours[j]
    if cv2.contourArea(c2)<5:continue
    pp=cv2.approxPolyDP(c2,max(.5,simplification),True).reshape(-1,2)
    if len(pp)>=3:d.append('M '+' L '.join(f'{int(x)} {int(y)}' for x,y in pp)+' Z')
   if d:parts.append(f'<path fill="{colors[idx]}" fill-rule="evenodd" d="{" ".join(d)}"/>');paths+=1
 parts.append('</svg>')
 Path(out).write_text('\n'.join(parts),encoding='utf-8')
 return paths

def thumbnail(source,dest,maxsize=(550,650)):
 i=Image.open(source).convert('RGB');i.thumbnail(maxsize);i.save(dest)

def real_crop(path):
 name=Path(path).stem
 rgb=np.array(Image.open(path).convert('RGB'))
 # Fixed reproducible editorial crops, NOT automatic segmentation.
 if name=='1000025722':
  # Flower top is 500x520 px centered in original photo
  rgb=rgb[260:945,120:750]
 elif name=='1000025726': rgb=rgb[60:1230,70:435]
 elif name=='1000025716':rgb=rgb[35:1460,80:580]
 elif name=='1000025721':rgb=rgb[80:1040,150:1390]
 elif name=='1000025729':rgb=rgb[70:1350,50:560]
 h,w=rgb.shape[:2];scale=min(1,550/max(h,w))
 return cv2.resize(rgb,(round(w*scale),round(h*scale)),interpolation=cv2.INTER_AREA)

def real_vector(img,outsvg,colors=8):
 # KMeans photo -> contour based SVG, baseline only; source image lacks a truthful grid target.
 x=cv2.GaussianBlur(img,(3,3),0.6)
 lab=cv2.cvtColor(x,cv2.COLOR_RGB2LAB)
 rng=np.random.default_rng(SEED)
 h,w=lab.shape[:2]
 # use kmeans using OpenCV
 data=lab.reshape(-1,3).astype('float32')
 cv2.setRNGSeed(42)
 _,ids,pal=cv2.kmeans(data,colors,None,(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,14,0.15),2,cv2.KMEANS_PP_CENTERS)
 cent=np.uint8(np.clip(pal.reshape(1,colors,3),0,255))
 palette=cv2.cvtColor(cent,cv2.COLOR_LAB2RGB).reshape(colors,3)
 cols=['#%02X%02X%02X'%tuple(int(a) for a in p) for p in palette]
 labels=ids.reshape(h,w).astype(np.uint8)
 # use first palette shade as background only if most frequent border; reorder indices
 border=np.concatenate([labels[:8,:].ravel(),labels[-8:,:].ravel(),labels[:,:8].ravel(),labels[:,-8:].ravel()]);bg=int(np.bincount(border,minlength=colors).argmax());
 if bg!=0:labels=np.where(labels==0,255,np.where(labels==bg,0,labels)).astype('uint8');labels[labels==255]=bg;cols[0],cols[bg]=cols[bg],cols[0]
 pcount=make_svg_from_pixel_labels(labels,cols,outsvg,simplification=1.5)
 view=np.zeros_like(img)
 for ii,col in enumerate(cols):view[labels==ii]=to_rgb(col)
 return view,pcount,labels

def main():
 for d in ['masters','svg','exemples','cas_reels']: (ROOT/d).mkdir(parents=True,exist_ok=True)
 masters=make_masters(); rows=[]; choices=[]
 experiments=[('propre',0)]+[('flou',x) for x in [.6,1.2,1.8,2.5,3.5,5]]+[('reduction',x) for x in [.8,.6,.45,.30,.20]]+[('jpeg',x) for x in [80,55,35,18]]+[('bruit',x) for x in [5,10,20,35]]+[('lumiere',x) for x in [.80,.60,.42]]
 for name,gt in masters.items():
  colors=PALETTES[name]
  np.save(ROOT/'masters'/f'{name}_GT.npy',gt)
  orig=render_beads(gt,colors)
  Image.fromarray(orig).save(ROOT/'masters'/f'{name}_rendu_synthetique.png')
  # canonical master design as actual colored cell PNG and CSV
  rgb=np.array([to_rgb(x) for x in colors],np.uint8)[gt]
  Image.fromarray(cv2.resize(rgb,(gt.shape[1]*S,gt.shape[0]*S),interpolation=cv2.INTER_NEAREST)).save(ROOT/'masters'/f'{name}_grille_reference.png')
  with (ROOT/'masters'/f'{name}_grille_reference.csv').open('w',newline='') as f:csv.writer(f).writerows(gt.tolist())
  for typ,val in experiments:
   im=distort(orig,typ,val)
   for mode in ['brut','lisse']:
    quant=labels_by_palette(im,colors,mode)
    pred=grid_from_labels(quant,*gt.shape)
    met=metrics(gt,pred,im)
    row={'motif':name,'degradation':typ,'niveau':val,'traitement':mode,**met}
    rows.append(row)
    if typ in ['propre','flou','reduction'] and (val==0 or val in [1.8,3.5,5,.45,.20]):
     choices.append((name,typ,val,mode,im,quant,pred))
   if typ=='flou' and val in [1.8,3.5,5] and name=='coquelicot':
    Image.fromarray(im).save(ROOT/'exemples'/f'coquelicot_flou_{val}.png')
   if typ=='reduction' and val in [.45,.20] and name=='geometrique':
    Image.fromarray(im).save(ROOT/'exemples'/f'geometrique_resolution_{val}.png')
  print('OK',name,gt.shape,len(experiments),flush=True)
 with (ROOT/'mesures_completes.csv').open('w',encoding='utf-8-sig',newline='') as f:
  wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
 # reference test case SVG: SVG from quantized pixels not a bead-grid rects file.
 for name,typ,val,mode,im,quant,pred in choices:
  if mode=='lisse' and ((typ=='propre') or (typ=='flou' and val in [1.8,3.5]) or(typ=='reduction' and val==.20)):
   key=f'{name}_{typ}_{str(val).replace(".","p")}'
   count=make_svg_from_pixel_labels(quant[::2,::2],PALETTES[name],ROOT/'svg'/f'{key}.svg',simplification=.8)
   print('SVG',key,count,flush=True)
   rgb=np.array([to_rgb(x) for x in PALETTES[name]],np.uint8)[pred]
   Image.fromarray(cv2.resize(rgb,(pred.shape[1]*S,pred.shape[0]*S),interpolation=cv2.INTER_NEAREST)).save(ROOT/'exemples'/f'{key}_grille.png')
 # real photographs chosen for variety, only qualitative/no target answer.
 real_info=[]
 for id,domain in [('1000025722','coquelicot_ancien'),('1000025726','bracelet_vert'),('1000025721','geometrie_franche'),('1000025716','bracelet_geometrique'),('1000025729','pastel_geom')]:
  p=ROOT/'sources'/(id+'.jpg')
  if not p.exists():
   print('SKIP real-photo comparison (photo not bundled for copyright):', domain, flush=True)
   continue
  img=real_crop(p)
  Image.fromarray(img).save(ROOT/'cas_reels'/f'{domain}_photo_recadree.png')
  q,paths,labels=real_vector(img,ROOT/'svg'/f'{domain}_trace_opencv.svg')
  Image.fromarray(q).save(ROOT/'cas_reels'/f'{domain}_vectorisation_apercu.png')
  gray=cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
  m={'source':id+'.jpg','nom':domain,'largeur':img.shape[1],'hauteur':img.shape[0], 'laplacien':float(cv2.Laplacian(gray,cv2.CV_32F).var()),'formes_vectorielles':paths,'fond_manuel':True}
  real_info.append(m)
 if real_info:
  (ROOT/'cas_reels'/'mesures_photos_reelles.json').write_text(json.dumps(real_info,indent=2,ensure_ascii=False),encoding='utf-8')
 (ROOT/'protocole.json').write_text(json.dumps({'size_cell_px':S,'seed':SEED,'palettes':PALETTES,'experiments':experiments,'note':'Primary measurements use rendered controlled known-ground-truth bead charts; real photos cannot provide ground-truth manufacturing grids. VTracer and ImageTracerJS were NOT executed.'},indent=2,ensure_ascii=False),encoding='utf-8')
 print('COMPLETE',len(rows),'rows',flush=True)
if __name__=='__main__':main()
