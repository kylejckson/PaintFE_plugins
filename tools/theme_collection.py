from pathlib import Path
import json,re,zipfile,io,math,argparse
from PIL import Image,ImageDraw

REPO=Path(__file__).resolve().parents[1]
PAINTFE=Path(__file__).resolve().parents[3]
DEST=REPO/'plugins/kylejckson'
THEMES=[
 ('charcoal-frosted-aero','Charcoal Frosted Aero','dark','#202020','#2c2c2c','#eeeeee','#e8590c',10,.45,.35,.14,.35,False,'Charcoal, Signal orange and frosted panels that let your desktop show through.',['Dark','Glass','Frosted','Orange']),
 ('charcoal-sharp-glass','Charcoal Sharp Glass','dark','#242424','#303030','#eeeeee','#e8590c',0,.55,.40,.16,.16,False,'Straight edges, compact spacing and charcoal glass with a little Signal orange.',['Dark','Glass','Sharp','Orange']),
 ('retro-98','Retro 98','light','#c0c0c0','#d4d0c8','#101010','#000080',0,1.,1.,1.,0.,True,'System grey, navy highlights and square raised controls. Try Retro 98 Icons alongside it.',['Light','Retro','Opaque']),
 ('retro-xp','Retro XP','light','#ece9d8','#f5f3e9','#172333','#245edb',6,1.,1.,1.,0.,False,'A familiar mix of warm grey, bright blue and green, with softer corners.',['Light','Retro','Opaque','Blue']),
 ('paper-studio','Paper Studio','light','#f4f0e7','#fffaf2','#2b2925','#b84d25',6,1.,1.,1.,0.,False,'Warm paper, clear graphite text and quiet orange highlights. A calm place to work.',['Light','Opaque','Warm']),
 ('graphite-studio','Graphite Studio','dark','#242424','#333333','#e9e9e9','#9dbba9',4,1.,1.,1.,0.,False,'Neutral graphite surfaces and muted mint highlights. No coloured cast around your image.',['Dark','Opaque','Minimal']),
 ('northern-mist','Northern Mist','dark','#2e3440','#3b4252','#eceff4','#88c0d0',8,.72,.68,.28,.12,False,'Cool slate glass, soft teal highlights and enough surface to keep things clear.',['Dark','Glass','Cool']),
 ('moss-terminal','Moss Terminal','dark','#252c25','#343e31','#e1e4d2','#a9be8a',2,1.,1.,1.,0.,False,'Olive charcoal, parchment text and sage highlights in a compact, quiet layout.',['Dark','Opaque','Green','Compact']),
 ('amber-console','Amber Console','dark','#171717','#25221c','#f0e5cc','#e4b15e',1,1.,1.,1.,0.,False,'Almost black, warm amber and crisp outlines. A console feel without the blinking lights.',['Dark','Opaque','Amber','Sharp']),
 ('pearl-aero','Pearl Aero','light','#eef0f2','#ffffff','#20252a','#d45316',12,.72,.65,.22,.15,False,'Pearl-white glass, silver edges and a touch of Signal orange. Bright without feeling bare.',['Light','Glass','Frosted']),
]

def rgb(v):return tuple(bytes.fromhex(v.lstrip('#')))
def mix(a,b,t):return tuple(round(x*(1-t)+y*t) for x,y in zip(a,b))
def rgba(c,a=255):return ','.join(map(str,(*c,a)))
def manifest(path,name,id,description,tags,kind='theme',appearance='theme.txt'):
 path.mkdir(parents=True,exist_ok=True);(path/'art').mkdir(exist_ok=True)
 value=dict(schema=1,api=1,kind=kind,appearance=appearance,id='kylejckson.'+id,version='1.0.0',name=name,author='kylejckson',description=description,license='MIT',tags=tags,effects=[],icon='art/icon.png',screenshot='art/preview.png')
 (path/'manifest.json').write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8')
 licence=(REPO/'plugins/paintfe/two-tone/LICENSE').read_text().replace('PaintFE contributors','kylejckson');(path/'LICENSE').write_text(licence)
 return path

def theme_art(path,base,raised,accent,rounding):
 image=Image.new('RGBA',(64,64),base+(255,));d=ImageDraw.Draw(image)
 d.rounded_rectangle((5,9,59,55),radius=min(rounding,9),fill=raised,outline=accent,width=2)
 d.rectangle((7,12,57,20),fill=accent);d.rectangle((11,27,22,44),fill=accent);d.rectangle((28,28,51,33),fill=mix(raised,accent,.3));d.rectangle((28,38,46,43),fill=mix(raised,accent,.2))
 image.save(path/'art/icon.png')
 if not (path/'art/preview.png').exists():
  card=Image.new('RGBA',(640,400),base+(255,));draw=ImageDraw.Draw(card)
  draw.rounded_rectangle((35,35,605,365),radius=rounding,fill=raised,outline=accent,width=3)
  for i,c in enumerate([base,raised,mix(base,accent,.2),accent]):draw.rectangle((70+i*130,130,175+i*130,270),fill=c)
  card.save(path/'art/preview.png')

def themes():
 for slug,name,mode,bg,raised,fg,accent,radius,panel,toolbar,workspace,grain,bevel,description,tags in THEMES:
  path=manifest(DEST/slug,name,slug,description,tags);b=rgb(bg);r=rgb(raised);f=rgb(fg);a=rgb(accent);dark=mode=='dark'
  tint=b if dark else mix(b,(255,255,255),.6)
  glass=dict(enabled=panel<1,desktop=True,desktop_blur=panel<1,workspace_opacity=workspace,grain=grain)
  for part,opacity in [('panels',panel),('headers',.70 if dark else .85),('menus',max(panel,.84)),('toolbars',toolbar),('buttons',.84 if dark else .92)]:glass[part]=dict(enabled=True,opacity=opacity,tint=list(tint) if part in ['panels','menus','toolbars'] else None,border=.75)
  data=dict(theme_mode=mode,theme_preset='custom',advanced_customization='true',ui_density='compact' if slug in ['retro-98','charcoal-sharp-glass','moss-terminal','amber-console'] else 'normal',neon_mode='false',glow_intensity='0',shadow_strength='.2' if radius<3 else '.5',canvas_grid_visible='true',canvas_grid_opacity='.10' if panel<1 else '.20',glass=json.dumps(glass,separators=(',',':')),ui_polish=json.dumps(dict(mode='Off' if bevel else 'Subtle',retro_bevel=bevel,solid_headers=slug in ['retro-98','retro-xp'],spacing_scale=.95 if radius<3 else 1.,text_scale=1.,border_width=1.,focus_width=1.,icon_gap=3. if radius<3 else 4.),separators=(',',':')))
  for field in ['window','menu','widget','tool_shelf','tool_button','badge','tab','dialog','history']:data[field+'_rounding']=str(radius if field not in ['widget','tool_button','badge'] else min(radius,5))
  for mode_name in ['light','dark']:
   data['accent_'+mode_name+'_normal']=rgba(a);data['accent_'+mode_name+'_faint']=rgba(a,36);data['accent_'+mode_name+'_strong']=rgba(mix(a,(255,255,255),.20) if mode_name=='dark' else mix(a,(0,0,0),.2))
  border=mix(b,f,.24);muted=mix(b,f,.77);faint=mix(b,f,.66)
  colours={'bg_color':b,'panel_bg':b,'window_bg':b,'bg2':r,'bg3':mix(r,f,.07),'text_color':f,'text_muted':muted,'text_faint':faint,'border_color':border,'border_lit':mix(border,f,.25),'separator_color':border,'button_bg':r,'button_hover':mix(r,a,.18),'button_active':mix(r,a,.30),'floating_window_bg':b,'tool_shelf_bg':b,'tool_shelf_border':border,'toolbar_bg':b,'menu_bg':b,'icon_button_bg':r,'icon_button_active':mix(r,a,.30),'icon_button_disabled':mix(b,r,.6),'text_input_bg':mix(b,(0,0,0),.22) if dark else (255,255,255),'stepper_button_bg':r,'canvas_bg_top':mix(b,(0,0,0),.10) if dark else mix(b,(255,255,255),.2),'canvas_bg_bottom':mix(b,(0,0,0),.20) if dark else b,'glow_accent':a,'accent3':rgb('#4fa444') if slug=='retro-xp' else mix(a,rgb('#65a99a'),.5),'accent4':mix(a,rgb('#bd92c8'),.5)}
  for field,c in colours.items():data['ov_'+field]=rgba(c,0 if field=='glow_accent' else 255)
  (path/'theme.txt').write_text('# PaintFE '+name+'\n'+'\n'.join(k+'='+v for k,v in data.items())+'\n',encoding='utf-8');theme_art(path,b,r,a,radius)


def canonical_ids():
 source=(PAINTFE/'src/config/icons.rs').read_text();block=source.split('pub enum Icon {',1)[1].split('\n}',1)[0];variants=re.findall(r'^    (\w+),',block,re.M)
 group_source=source.split('pub fn pack_group',1)[1].split('/// Canonical',1)[0];group_source=re.sub(r'//[^\n]*','',group_source);groups={}
 for variants_text,group in re.findall(r'((?:Self::\w+\s*\|?\s*)+)=>\s*"(\w+)"',group_source):
  for v in re.findall(r'Self::(\w+)',variants_text):groups[v]=group
 overrides=dict(re.findall(r'\(Icon::(\w+), "([^"]+)"\)',source.split('const PACK_ID_OVERRIDES:',1)[1].split('];',1)[0]))
 excluded_source=(PAINTFE/'src/config/icon_packs.rs').read_text().split('const EXCLUDED_IDS:',1)[1].split('];',1)[0];excluded=set(re.findall(r'"([^"]+)"',excluded_source))
 def snake(v):return re.sub(r'(?<!^)([A-Z])',r'_\1',v).lower()
 ids=set()
 for v in variants:
  group=groups.get(v,'menu');base=snake(v).removeprefix('ui_').removeprefix(group+'_');id=overrides.get(v,group+'_'+base)
  if id not in excluded:ids.add(id)
 shapes=(PAINTFE/'src/ops/shapes.rs').read_text().split('pub enum ShapeKind {',1)[1].split('\n}',1)[0]
 ids.update('shape_'+snake(v) for v in re.findall(r'^    (\w+),',shapes,re.M))
 return sorted(ids)


def icon(id,dark=False):
 wide=id=='tool_shapes';image=Image.new('RGBA',(44 if wide else 24,24),(0,0,0,0));d=ImageDraw.Draw(image);ink=(220,220,213) if dark else (24,24,24);blue=(30,75,165);cyan=(58,163,190);red=(183,47,52);green=(40,137,67);gold=(222,174,53);paper=(249,248,235);gray=(160,165,167)
 def box(rect,fill,outline=ink,width=1):d.rectangle(rect,fill=fill,outline=outline,width=width)
 def poly(points,fill):d.polygon(points,fill=fill,outline=ink)
 def line(points,c=ink,w=1):d.line(points,fill=c,width=w)
 def plus(x,y,c=green):line([(x-3,y),(x+3,y)],ink,3);line([(x,y-3),(x,y+3)],ink,3);line([(x-2,y),(x+2,y)],c);line([(x,y-2),(x,y+2)],c)
 def cross(x=12,y=12):line([(x-4,y-4),(x+4,y+4)],red,3);line([(x-4,y+4),(x+4,y-4)],red,3)
 def document():poly([(5,2),(15,2),(20,7),(20,21),(5,21)],paper);line([(15,2),(15,7),(20,7)],gray)
 def eye():poly([(2,12),(7,7),(16,7),(22,12),(16,17),(7,17)],paper);d.ellipse((8,8,16,16),fill=blue,outline=ink);box((11,10,13,14),ink)
 def selection(ellipse=False):
  if ellipse:
   for angle in range(0,360,35):d.arc((3,3,21,20),angle,angle+18,fill=blue,width=1)
  else:
   for x in range(3,21,4):line([(x,3),(x+1,3)],blue);line([(x,20),(x+1,20)],blue)
   for y in range(3,20,4):line([(3,y),(3,y+1)],blue);line([(21,y),(21,y+1)],blue)
 def arrow(up=False):
  if up:poly([(12,3),(5,11),(9,11),(9,20),(15,20),(15,11),(19,11)],cyan)
  else:poly([(12,21),(5,13),(9,13),(9,4),(15,4),(15,13),(19,13)],cyan)
 if id.startswith('shape_'):
  kind=id[6:];pts=None
  if kind in ['ellipse','filled','outline','both']:d.ellipse((3,4,21,20),fill=cyan if kind!='outline' else None,outline=ink,width=2)
  elif kind=='heart':poly([(12,7),(8,3),(4,4),(2,8),(3,12),(12,21),(21,12),(22,8),(20,4),(16,3)],red)
  elif kind in ['triangle','right_triangle']:pts=[(3,20),(21,20),(3 if kind=='right_triangle' else 12,3)]
  elif kind=='diamond':pts=[(12,2),(22,12),(12,22),(2,12)]
  elif kind in ['pentagon','hexagon','octagon','star5','star6']:
   n={'pentagon':5,'hexagon':6,'octagon':8,'star5':10,'star6':12}[kind];pts=[(round(12+math.cos(-math.pi/2+i*2*math.pi/n)*(10 if not kind.startswith('star') or i%2==0 else 4)),round(12+math.sin(-math.pi/2+i*2*math.pi/n)*(10 if not kind.startswith('star') or i%2==0 else 4))) for i in range(n)]
  elif kind in ['cross','check']:
   if kind=='cross':cross()
   else:line([(3,12),(9,18),(21,4)],green,4)
  elif kind=='parallelogram':pts=[(7,4),(22,4),(17,20),(2,20)]
  elif kind=='trapezoid':pts=[(8,4),(16,4),(22,20),(2,20)]
  elif kind=='arrow':pts=[(2,8),(14,8),(14,3),(23,12),(14,21),(14,16),(2,16)]
  elif kind=='rounded_rect':d.rounded_rectangle((3,4,21,20),radius=4,fill=cyan,outline=ink)
  else:box((3,4,21,20),cyan)
  if pts:poly(pts,cyan)
 elif 'shapes' in id:
  box((2,8,13,20),blue);d.ellipse((10,9,23,21),fill=green,outline=ink);poly([(17 if wide else 15,4),(26 if wide else 22,17),(9 if wide else 7,17)],gold)
  if wide:d.ellipse((29,7,42,20),fill=red,outline=ink)
 elif id=='settings_interface':
  d.ellipse((2,3,22,21),fill=gold,outline=ink)
  for x,y,c in [(7,8,red),(14,6,blue),(18,13,green),(10,17,paper)]:d.rectangle((x-1,y-1,x+1,y+1),fill=c)
 elif id=='settings_hardware':
  box((2,3,22,17),gray);box((4,5,20,14),blue);box((10,18,14,20),gray);line([(6,21),(18,21)],ink,2)
 elif id=='settings_keybinds':
  box((1,6,23,20),gray)
  for y in [9,13]:
   for x in range(4,22,4):box((x,y,x+1,y+1),paper)
  box((6,17,18,18),paper)
 elif id=='settings_a_i':
  box((6,6,18,18),green);box((9,9,15,15),paper)
  for x in [8,12,16]:line([(x,2),(x,5)],gray,2);line([(x,19),(x,22)],gray,2)
  for y in [8,12,16]:line([(2,y),(5,y)],gray,2);line([(19,y),(22,y)],gray,2)
 elif id=='settings_plugins':
  poly([(4,4),(11,4),(11,1),(14,1),(14,4),(20,4),(20,11),(23,11),(23,14),(20,14),(20,20),(13,20),(13,17),(10,17),(10,20),(4,20)],gold)
 elif id=='settings_optional_features':
  poly([(3,7),(11,3),(21,7),(13,11)],gold);poly([(3,7),(13,11),(13,22),(3,18)],(173,124,58));poly([(13,11),(21,7),(21,18),(13,22)],gold);plus(17,16)
 elif id=='tool_smudge':
  poly([(7,21),(6,12),(11,3),(14,2),(16,4),(15,7),(12,12),(16,12),(20,10),(22,12),(18,17),(15,22)],(232,193,142));line([(3,18),(6,18)],blue,2)
 elif id=='tool_color_remover':
  poly([(8,2),(2,12),(3,17),(8,20),(13,17),(14,12)],cyan);cross(18,17)
 elif id=='tool_perspective_crop':
  poly([(4,3),(21,6),(18,20),(3,18)],None)
  for x,y in [(4,3),(21,6),(18,20),(3,18)]:box((x-1,y-1,x+1,y+1),paper)
 elif 'guides' in id:
  c=cyan if 'on' in id else gray;box((2,2,21,6),c);box((2,2,6,22),c)
  for x in range(8,22,4):line([(x,3),(x,5)],ink)
  for y in range(8,23,4):line([(3,y),(5,y)],ink)
  line([(8,14),(23,14)],red);line([(15,8),(15,23)],red)
 elif 'wrap_preview' in id:
  box((7,7,17,17),cyan if 'on' in id else gray)
  for x,y in [(1,1),(18,1),(1,18),(18,18)]:box((x,y,x+4,y+4),gold if 'on' in id else gray)
 elif 'mirror' in id:
  box((2,3,21,21),None);c=blue if not id.endswith('_off') else gray
  if id.endswith('_v'):
   line([(1,12),(23,12)],red);poly([(5,4),(18,4),(14,9),(9,9)],c);poly([(5,20),(18,20),(14,15),(9,15)],c)
  else:
   line([(12,1),(12,23)],red);poly([(4,8),(9,5),(9,18),(4,15)],c);poly([(20,8),(15,5),(15,18),(20,15)],c)
   if id.endswith('_q'):line([(1,12),(23,12)],red)
 elif 'grid_' in id:
  box((2,3,21,21),None);c=cyan if id.endswith('_on') else gray
  for x in [8,15]:line([(x,3),(x,21)],c)
  for y in [9,15]:line([(2,y),(21,y)],c)
  if id.endswith('_off'):line([(3,20),(20,4)],ink)
 elif any(v in id for v in ['pencil','brush','smudge']):
  poly([(4,18),(7,12),(17,2),(21,6),(11,16)],gold if 'pencil' in id else (150,95,43));poly([(4,18),(3,22),(9,20),(11,16)],blue if 'brush' in id else ink)
  line([(8,12),(12,16)],gray,3)
  if 'content' in id:plus(18,18)
  if 'dynamics' in id:
   for x,y in [(5,7),(12,14),(19,8)]:line([(x,2),(x,22)],ink);box((x-2,y-2,x+2,y+2),cyan)
 elif 'eraser' in id:poly([(3,15),(12,4),(21,12),(12,22)],(237,153,157));poly([(3,15),(7,10),(16,17),(12,22)],paper)
 elif 'clone_stamp' in id:box((4,16,20,21),gray);box((7,13,17,16),gray);poly([(10,13),(9,6),(10,3),(14,3),(15,6),(14,13)],(139,86,39))
 elif 'color_picker' in id:poly([(4,18),(3,22),(7,21),(17,11),(13,7)],gray);poly([(12,6),(16,2),(22,8),(18,12)],blue)
 elif any(v in id for v in ['rect_select','ellipse_select','lasso','deselect','select_all','selection_invert']):
  selection('ellipse' in id or 'lasso' in id)
  if 'deselect' in id:cross()
  if 'invert' in id:poly([(5,5),(19,5),(5,18)],blue)
 elif any(v in id for v in ['move_pixels','move_selection']):
  if 'selection' in id:selection()
  line([(12,3),(12,21)],blue,3);line([(3,12),(21,12)],blue,3)
  for points in [[(12,1),(8,6),(16,6)],[(12,23),(8,18),(16,18)],[(1,12),(6,8),(6,16)],[(23,12),(18,8),(18,16)]]:poly(points,blue)
 elif 'magic_wand' in id:line([(4,21),(16,8)],ink,3);line([(12,4),(22,4)],gold);line([(17,0),(17,9)],gold);line([(13,0),(21,8)],gold)
 elif 'pan' in id and not 'expand' in id:poly([(7,22),(4,16),(2,11),(4,9),(8,13),(7,5),(9,3),(11,10),(11,2),(13,2),(15,10),(15,4),(17,4),(18,12),(20,9),(22,10),(20,18),(17,22)],(232,193,142))
 elif 'text' in id and 'texture' not in id:box((3,3,21,7),blue);box((10,5,14,21),blue);line([(7,21),(17,21)],ink)
 elif any(v in id for v in ['zoom','reset_zoom','search']):
  d.ellipse((2,2,16,16),fill=(201,235,242),outline=ink,width=2);line([(15,15),(22,22)],(128,91,51),4)
  if 'out' in id:line([(5,9),(13,9)],ink,2)
  elif 'reset' in id:box((6,6,12,12),None)
  else:line([(5,9),(13,9)],ink,2);line([(9,5),(9,13)],ink,2)
 elif any(v in id for v in ['undo','redo','rotate','straighten']):
  flip='redo' in id;pts=[(3,8),(7,3),(7,6),(17,6),(21,10),(21,18),(18,18),(18,11),(16,9),(7,9),(7,12)];poly([(24-x,y) if flip else (x,y) for x,y in pts],gold)
 elif any(v in id for v in ['open','import']):
  poly([(2,5),(9,5),(11,8),(21,8),(21,21),(2,21)],gold);poly([(2,11),(23,11),(19,21),(2,21)],(244,210,90))
  if 'import' in id:plus(16,15)
 elif 'save' in id:box((3,2,21,22),blue);box((6,3,16,10),gray);box((7,14,18,21),paper);box((13,4,15,8),ink)
 elif 'new' in id or 'add_layer' in id or id=='layer_add':document();plus(17,17)
 elif 'duplicate' in id or 'copy' in id:box((2,3,15,16),paper);box((8,9,21,22),paper);line([(11,13),(18,13)],blue)
 elif 'delete' in id or 'remove' in id or 'close' in id or 'cancel' in id or 'cross' in id:
  if 'delete' in id:box((7,7,18,21),gray);box((5,4,20,7),gray);line([(10,10),(10,18)],ink);line([(15,10),(15,18)],ink)
  elif 'close' in id or 'cross' in id:
   for a,b in [((4,4),(20,20)),((4,20),(20,4))]:line([a,b],(255,255,255),5);line([a,b],ink,2)
  else:cross()
 elif any(v in id for v in ['visible','hidden','show_all','hide_all','solo']):
  eye()
  if 'hidden' in id or 'hide' in id:line([(3,21),(22,3)],red,2)
 elif 'layer' in id or 'flatten' in id:
  for offset in [8,4,0]:poly([(3,6+offset),(11,2+offset),(22,7+offset),(13,12+offset)],cyan if offset==0 else gray)
  if 'down' in id:arrow()
  if 'up' in id or 'top' in id:arrow(True)
 elif 'mask' in id:
  box((3,3,21,21),paper);box((4,4,12,20),ink)
  if 'new' in id:plus(17,17)
 elif 'gradient' in id:
  for x in range(3,21):line([(x,4),(x,21)],tuple(int(255*(x-3)/17) for _ in range(3)))
  box((2,3,22,22),None)
 elif 'fill' in id:poly([(5,6),(13,2),(21,11),(13,18),(4,10)],gray);line([(4,11),(12,18)],blue,3);poly([(3,13),(1,20),(6,20)],blue)
 elif 'mesh' in id or 'warp' in id or 'perspective' in id or 'crop' in id:
  for y in [4,11,19]:line([(3,y),(21,y+1)],blue)
  for x in [3,12,21]:line([(x,4),(x,20)],blue)
  for x,y in [(3,4),(21,5),(3,19),(21,20)]:box((x-1,y-1,x+1,y+1),paper)
 elif 'grid' in id or 'guides' in id or 'mirror' in id or 'wrap_preview' in id:
  box((2,3,21,21),None)
  if 'mirror' in id:line([(12,2),(12,22)],red,2);poly([(4,8),(9,6),(9,17),(4,15)],blue);poly([(20,8),(15,6),(15,17),(20,15)],blue)
  else:
   for x in [8,15]:line([(x,3),(x,21)],cyan)
   for y in [9,15]:line([(2,y),(21,y)],cyan)
 elif any(v in id for v in ['settings','properties','hardware','plugin']):
  for angle in range(0,360,45):
   x=round(12+math.cos(math.radians(angle))*8);y=round(12+math.sin(math.radians(angle))*8);box((x-2,y-2,x+2,y+2),gray)
  d.ellipse((5,5,19,19),fill=gray,outline=ink);d.ellipse((9,9,15,15),fill=blue,outline=ink)
 elif 'line' in id:line([(3,21),(21,3)],ink,3);line([(3,20),(20,3)],red)
 elif 'liquify' in id or any(v in id for v in ['distort','wave','ripple','twist']):
  for offset in [0,7]:line([(3,5+offset),(7,2+offset),(14,8+offset),(20,5+offset)],cyan,2)
 elif any(v in id for v in ['brightness','contrast','color','hue','saturation','levels','curves','adjust']):
  d.ellipse((3,3,21,21),fill=gold,outline=ink);d.pieslice((4,4,20,20),90,270,fill=blue);d.ellipse((9,9,15,15),fill=paper,outline=ink)
 elif 'help' in id or 'about' in id or 'info' in id:
  d.ellipse((3,3,21,21),fill=blue,outline=ink);box((11,9,13,18),paper,None);box((11,5,13,7),paper,None)
 elif any(v in id for v in ['noise','dither','pixel']):
  for y in range(4,21,4):
   for x in range(3,21,4):box((x,y,x+2,y+2),blue if (x+y)%3 else gray)
 elif 'blur' in id or 'glow' in id:
  for inset,c in [(2,(205,209,213)),(5,(161,178,192)),(8,(78,117,158))]:d.ellipse((inset,inset,24-inset,24-inset),fill=c)
 elif 'export' in id or 'print' in id:document();arrow(True)
 else:
  # Effect/menu family glyph: a framed document with its own small raster motif.
  box((3,3,21,21),paper);seed=sum((i+1)*ord(c) for i,c in enumerate(id))
  for col in range(4):
   h=3+(seed>>(col*2))%10;box((5+col*4,19-h,7+col*4,19),[blue,cyan,green,gold][col])
 return image.resize((image.width*2,48),Image.Resampling.NEAREST)


def icons():
 path=manifest(DEST/'retro-98-icons','Retro 98 Icons','retro-98-icons','Small, colourful pixel icons with crisp outlines. Made to go with Retro 98, and available separately.',['Retro','Pixel','Classic'],'icons','icons.zip');ids=canonical_ids();entries={}
 for id in ids:
  for dark in [False,True]:
   im=icon(id,dark);data=io.BytesIO();im.save(data,format='PNG');entries[id+('_dark' if dark else '_light')+'.png']=data.getvalue()
 entries['pack.ini']=b'name=Retro 98 Icons\nauthor=kylejckson\n';entries['icons.txt']=('\n'.join(ids)+'\n').encode()
 with zipfile.ZipFile(path/'icons.zip','w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
  for name,data in sorted(entries.items()):
   item=zipfile.ZipInfo(name,date_time=(1980,1,1,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED;z.writestr(item,data)
 icon('toolbar_save').resize((64,64),Image.Resampling.NEAREST).save(path/'art/icon.png')
 preview=Image.new('RGBA',(640,400),(192,192,192,255))
 for i,id in enumerate([x for x in ids if x.startswith(('tool_','toolbar_','layer_','settings_'))][:70]):preview.alpha_composite(icon(id),((i%10)*61+13,(i//10)*55+9))
 preview.save(path/'art/preview.png');print('Built',len(ids),'canonical icons,',len(entries),'ZIP entries.')

if __name__=='__main__':
 THEMES_DIR=DEST;DEST.mkdir(parents=True,exist_ok=True);themes();icons();print('Built ten theme definitions and one original icon pack.')
