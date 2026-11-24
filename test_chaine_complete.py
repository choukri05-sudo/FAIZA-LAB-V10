from pathlib import Path
import sys, csv, io, numpy as np
from PIL import Image
import cairosvg
sys.path.insert(0,str(Path(__file__).resolve().parent))
from faiza_lab_v10 import make_masters, render_beads, distort, PALETTES, S,labels_by_palette,grid_from_labels,metrics,make_svg_from_pixel_labels
R=Path(__file__).resolve().parent
masters=make_masters();out=[]
cases=[('propre',0)]+[('flou',x) for x in [1.2,1.8,2.5,3.5]]+[('reduction',x) for x in [.3,.2]]
for motif,gt in masters.items():
 original=render_beads(gt,PALETTES[motif])
 for deg,val in cases:
  test=distort(original,deg,val)
  labels=labels_by_palette(test,PALETTES[motif],mode='brut')
  pixpred=grid_from_labels(labels,*gt.shape);pmetric=metrics(gt,pixpred,test)
  key=f'{motif}_{deg}_{str(val).replace(".","p")}_full'
  svg=R/'svg'/f'{key}.svg'
  n=make_svg_from_pixel_labels(labels[::2,::2],PALETTES[motif],svg,simplification=.8)
  rendered=np.array(Image.open(io.BytesIO(cairosvg.svg2png(url=str(svg),output_width=gt.shape[1]*S,output_height=gt.shape[0]*S))).convert('RGB'))
  postlabels=labels_by_palette(rendered,PALETTES[motif],mode='brut')
  final=grid_from_labels(postlabels,*gt.shape);fmetric=metrics(gt,final,rendered)
  out.append({'motif':motif,'degradation':deg,'niveau':val,'cellules_correctes_avant_vectorisation':round(pmetric['foreground'],6),'cellules_correctes_apres_svg':round(fmetric['foreground'],6),'erreurs_avant':pmetric['wrong_fg'],'erreurs_finales':fmetric['wrong_fg'],'formes_svg':n})
  if (deg=='flou' and val in [1.2,1.8,2.5]) or (deg=='reduction' and val==.2):
   Image.fromarray(rendered).save(R/'exemples'/f'{key}_svg.png')
  print(key,round(pmetric['foreground'],3),'->',round(fmetric['foreground'],3),flush=True)
with (R/'test_chaine_complete.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(out[0]));w.writeheader();w.writerows(out)
