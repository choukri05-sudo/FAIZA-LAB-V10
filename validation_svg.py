from pathlib import Path
import sys,csv,io,numpy as np
from PIL import Image
import cairosvg
sys.path.insert(0,str(Path(__file__).resolve().parent))
from faiza_lab_v10 import make_masters,PALETTES,S,labels_by_palette,grid_from_labels,metrics
R=Path(__file__).resolve().parent
masters=make_masters();rows=[]
for src in sorted((R/'svg').glob('*.svg')):
 key=src.stem;name=key.split('_')[0] if not key.startswith('floral_vert') else 'floral_vert'
 if key.startswith('floral_vert'):name='floral_vert'
 elif key.startswith('geometrique'):name='geometrique'
 else:name='coquelicot'
 gt=masters[name]; H,W=gt.shape
 try:
  b=cairosvg.svg2png(url=str(src),output_width=W*S,output_height=H*S)
  img=np.array(Image.open(io.BytesIO(b)).convert('RGB'))
  pred=grid_from_labels(labels_by_palette(img,PALETTES[name],mode='brut'),H,W)
  m=metrics(gt,pred,img)
  Image.fromarray(img).save(R/'exemples'/f'{key}_svg_rendu.png')
  rows.append({'source':key,'foreground':m['foreground'],'boundary_f1':m['boundary_f1'],'wrong_fg':m['wrong_fg'],'n_fg':m['n_fg']})
  print(key,round(m['foreground'],4),'erreurs',m['wrong_fg'],flush=True)
 except Exception as e:print('ERROR',key,e,flush=True)
with (R/'validation_svg.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
