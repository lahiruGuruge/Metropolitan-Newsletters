import fitz, re, json, pathlib, subprocess, concurrent.futures, statistics, sys
from PIL import Image
ROOT=pathlib.Path(__file__).resolve().parent; DIST=ROOT/'dist'; DIST.mkdir(exist_ok=True)
SOURCE=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'input'
if not SOURCE.is_dir(): raise SystemExit('Usage: python ingest.py /path/to/newsletter-pdfs')
for n in ['pages','thumbs','pdfs']: (DIST/n).mkdir(exist_ok=True)
categories={
 'Business & Partnerships':r'partner|dealer|business|sales|customer|client|agreement|contract|distribution',
 'Products & Technology':r'canon|acer|pramac|york|mitsubishi|product|technology|camera|printer|laptop|generator|elevator|digital|software|\bAI\b',
 'Learning & Development':r'training|workshop|learning|development|seminar|qualification|graduate|leadership program|leadership programme|PIM|webinar',
 'Awards & Achievements':r'award|achievement|recognition|winner|champion|trophy|excellence|congratulat',
 'People & Leadership':r'appoint|promotion|chairman|director|new recruit|welcome|retire|service appreciation|long service|birthday',
 'Sports & Wellbeing':r'cricket|badminton|sport|golf|football|wellness|health|fitness|rugby|swimming|netball|basketball',
 'Community & Sustainability':r'CSR|donat|community|charity|sustainab|environment|school|blood|tree planting|children|social responsibility',
 'Events & Culture':r'celebrat|event|festival|poson|vesak|christmas|new year|avurudu|bakthi|gathering|party|trip|outing|exhibition|infotel',
 'HR & Digital Systems':r'\bHRIS\b|peoples\s*hr|appraisal|human resource|\bSAP\b|system migration|insurance polic|mobile app system',
 'Knowledge & Employee Resources':r'knowledge corner|kaizen|mindset|personal brand|emotional intelligence|nomophobia|quiz|hidden words|birthdays|spot the|find 6',
 'Branches & Facilities':r'branch|opening|inaugurat|re.launch|centre|center|showroom|office|facility|facilities'
}
def clean(t):
 t=re.sub(r'(?im)^.*VOLUME\s*\d+.*(?:ISSUE|20\d{2}).*$', '',t)
 t=re.sub(r'(?im)^\s*(?:ETRO NEWS|METRO NEWS|PAGE\s*\d+|\d{1,2})\s*$', '',t)
 t=re.sub(r'(?<=\w)-\n(?=\w)','',t)
 return re.sub(r'[ \t]+',' ',t).strip()
def process(arg):
 f,year,month,mi,i=arg
 d=fitz.open(f); p=d[i]; id=f'{year}-{mi:02d}-{i+1:02d}'
 raw=p.get_text(sort=True); ocr=len(raw.strip())<80
 if ocr:
  png=f'/tmp/ocr-{id}.png'; p.get_pixmap(matrix=fitz.Matrix(2,2)).save(png)
  raw=subprocess.run(['tesseract',png,'stdout','--psm','11'],capture_output=True,text=True).stdout
  pathlib.Path(png).unlink()
 text=clean(raw)
 lines=[]
 if not ocr:
  for b in p.get_text('dict')['blocks']:
   for l in b.get('lines',[]):
    s=' '.join(x['text'] for x in l['spans']).strip(); size=max((x['size'] for x in l['spans']),default=0)
    if len(s)>8 and not re.search(r'volume|issue|metro\s+news|ETRO\s+NEWS|^page',s,re.I) and len(s)<160:
     lines.append((size,s))
 title=''
 if lines:
  maxsize=max(s for s,t in lines)
  heads=[t for s,t in lines if s>=maxsize*.87]
  title=' '.join(heads[:3])[:180]
 if not title:
  title=' '.join(text.splitlines()[:2])[:150]
 if len(title)<8: title=f'{month} {year} • Page {i+1}'
 tags=[k for k,v in categories.items() if re.search(v,text,re.I)] or ['Other News']
 brands=[x for x in ['Canon','Acer','PRAMAC','York','Mitsubishi','Mcentre','Mservice','PIM','Metrocorp','hSenid'] if re.search(re.escape(x),text,re.I)]
 # Page images preserve the original source layout; text is a separate searchable transcript.
 pix=p.get_pixmap(matrix=fitz.Matrix(1200/p.rect.width,1200/p.rect.width),alpha=False)
 img=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
 img.save(DIST/'pages'/f'{id}.webp','WEBP',quality=80)
 img.thumbnail((420,600)); img.save(DIST/'thumbs'/f'{id}.webp','WEBP',quality=75)
 return {'id':id,'issue':f'{year}-{mi:02d}','year':year,'month':month,'monthNumber':mi,'page':i+1,'title':title,'text':text,'categories':tags,'brands':brands,'ocr':ocr,'pdf':f'pdfs/{year}-{mi:02d}.pdf'}
jobs=[]; issues=[]
for f in sorted(SOURCE.glob('*.pdf')):
 m=re.match(r'(\d+)\. News\s*letter (\w+) (\d+)',f.stem,re.I)
 if not m: raise ValueError('Unrecognised newsletter filename: '+f.name)
 mi,month,year=int(m[1]),m[2],int(m[3]); d=fitz.open(f)
 issues.append({'id':f'{year}-{mi:02d}','year':year,'month':month,'monthNumber':mi,'pages':len(d),'pdf':f'pdfs/{year}-{mi:02d}.pdf','cover':f'thumbs/{year}-{mi:02d}-01.webp'})
 jobs.extend((str(f),year,month,mi,i) for i in range(len(d)))
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 pages=list(ex.map(process,jobs))
old=json.load(open(DIST/'data.json')) if (DIST/'data.json').exists() else {'issues':[],'pages':[],'categories':[]}
replaced={i['id'] for i in issues}
added_pages=len(pages); added_issues=len(issues)
pages=[p for p in old['pages'] if p['issue'] not in replaced]+pages
issues=[i for i in old['issues'] if i['id'] not in replaced]+issues
pages.sort(key=lambda p:(p['year'],p['monthNumber'],p['page']))
overrides=json.load(open(ROOT/'title-overrides.json')) if (ROOT/'title-overrides.json').exists() else {}
for p in pages:
 if p['issue'] in replaced and p['id'] in overrides: p['title']=overrides[p['id']]
json.dump({'issues':sorted(issues,key=lambda x:x['id']),'pages':pages,'categories':list(dict.fromkeys(old['categories']+list(categories)+['Other News'])),'notes':'Issue dates are derived from supplied filenames. Categories are automatically suggested at page level. OCR may contain transcription errors; verify important details in the source PDF.'},open(DIST/'data.json','w'),ensure_ascii=False)
print('Indexed',len(pages),'pages from',len(issues),'issues; OCR:',sum(p['ocr'] for p in pages),flush=True)

print('Merged',added_pages,'pages from',added_issues,'issues; existing issues retained.',flush=True)
