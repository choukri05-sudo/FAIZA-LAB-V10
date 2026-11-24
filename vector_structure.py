"""Structure-aware vector output: reconstruct bead-cell labels *before* SVG.
This is a specialized beadwork-photo branch, not a general artistic vectorizer.
"""
from pathlib import Path
import sys, csv, io, numpy as np
from PIL import Image
import cairosvg
sys.path.insert(0,str(Path(__file__).resolve().parent))
from faiza_lab_v10 import make_masters, render_beads, distort, PALETTES, S,labels_by_palette,grid_from_labels,metrics
R=Path(__file__).resolve().parent

def grid_to_svg(grid,cols,path):
 H,W=grid.shape
 lines=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W*S}" height="{H*S}">',f'<rect width="{W}" height="{H}" fill="{cols[0]}"/>']
 paths=0
 for y in range(H):
  x=0
  while x<W:
   col=int(grid[y,x]);z=x+1
   while z<W and grid[y,z]==col:z+=1
   if col:
    lines.append(f'<rect x="{x}" y="{y}" width="{z-x}" height="1" fill="{cols[col]}"/>');paths+=1
   x=z
 lines.append('</svg>')
 Path(path).write_text('\n'.join(lines),encoding='utf-8')
 return paths

if __name__=='__main__':
 masters=make_masters();rows=[]
 cases=[('propre',0)]+[('flou',x) for x in [1.2,1.8,2.5,3.5]]+[('reduction',x) for x in [.3,.2]]+[('bruit',x) for x in [10,20,35]]+[('jpeg',x) for x in [35,18]]+[('lumiere',x) for x in [.8,.6]]
 for motif,gt in masters.items():
  original=render_beads(gt,PALETTES[motif])
  for kind,val in cases:
   im=distort(original,kind,val)
   for mode in ['brut','lisse']:
    pred=grid_from_labels(labels_by_palette(im,PALETTES[motif],mode=mode),*gt.shape)
    met=metrics(gt,pred,im)
    if (kind=='propre') or (motif=='coquelicot' and kind=='flou' and val in [1.2,1.8,2.5]) or (motif=='geometrique' and kind=='reduction' and val==.2):
     key=f'{motif}_{kind}_{str(val).replace(".","p")}_{mode}_structure'
     file=R/'svg'/f'{key}.svg'
     nc=grid_to_svg(pred,PALETTES[motif],file)
     b=cairosvg.svg2png(url=str(file),output_width=gt.shape[1]*S,output_height=gt.shape[0]*S)
     img=np.array(Image.open(io.BytesIO(b)).convert('RGB'))
     # Structural SVG can roundtrip exactly: read exact cell-center RGB color.
     c=np.array([tuple(int(x[i:i+2],16) for i in (1,3,5)) for x in PALETTES[motif]])
     centers=img[S//2::S,S//2::S]
     out=np.argmin(((centers[:,:,None,:].astype(int)-c[None,None,:,:])**2).sum(-1),-1)
     if np.any(out!=pred):raise ValueError(f'RLE SVG roundtrip failed {key}: {np.sum(out!=pred)}')
     if mode=='brut':Image.fromarray(img).save(R/'exemples'/f'{key}.png')
    rows.append(dict(motif=motif,degradation=kind,niveau=val,mode=mode,precision_grid_finale=met['foreground'],cellules_erronees=met['wrong_fg'],n=met['n_fg']))
  print('STRUCT SVG OK',motif,flush=True)
 with (R/'test_vectorisation_structurelle.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
