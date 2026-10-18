"""Create web-optimised copies without changing newsletter page order."""
import pathlib, re, subprocess, concurrent.futures, sys
root=pathlib.Path(__file__).resolve().parent
src=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else root/'input'
dest=root/'dist/pdfs';dest.mkdir(parents=True,exist_ok=True)
def run(f):
 m=re.match(r'(\d+)\. Newsletter (\w+) (\d+)',f.stem)
 if not m:return
 out=dest/f'{m[3]}-{int(m[1]):02d}.pdf'
 subprocess.run(['gs','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.5','-dPDFSETTINGS=/ebook','-dNOPAUSE','-dBATCH','-dQUIET',f'-sOutputFile={out}',str(f)],check=True,capture_output=True)
 print(out.name,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:list(ex.map(run,src.glob('*.pdf')))
