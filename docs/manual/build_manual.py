#!/usr/bin/env python3
"""Builds a CD-booklet style PDF manual from a content file.

  build_manual.py CONTENT.py BANNER.png OUT.pdf

Two passes through Chromium (Playwright): the first finds the page every section starts on
(invisible markers, read back with pdftotext), the second prints the contents page with
those numbers. The markers are absolutely positioned, so removing them changes no layout.
"""
import html, json, os, re, runpy, subprocess, sys, tempfile

# Ndot 77 JP Extended is Nothing's font and is not stored in this repository: point NDOT_FONT at
# your own copy (for example pulled from the phone's /system/fonts).
FONT = os.environ.get('NDOT_FONT', 'Ndot77JPExtended.ttf')
HERE = os.path.dirname(os.path.abspath(__file__))

CSS = r"""
@font-face { font-family: 'Ndot'; src: url('file://%(font)s'); }
@page {
  size: 148mm 148mm; margin: 13mm 12mm 15mm 12mm;
  background-color: #0a0a0a;
  @bottom-left { content: "%(running)s"; font-family: 'Ndot'; font-size: 6.5pt; color: #5a5a5a; letter-spacing: .06em; }
  @bottom-right { content: counter(page); font-family: 'Ndot'; font-size: 8pt; color: #4cff7a; }
}
@page cover { margin: 0; @bottom-left { content: none } @bottom-right { content: none } }
@page opener { @bottom-left { content: none } }
html, body { margin: 0; background: transparent; }
/* the faint dot matrix behind every page (a fixed layer repeats on each printed page) */
.grid { position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: -1;
        background-image: radial-gradient(circle, #222 0.3mm, transparent 0.36mm);
        background-size: 3.2mm 3.2mm; }
body { font-family: 'Ndot'; color: #e6e6e6; font-size: 8.4pt; line-height: 1.55; letter-spacing: .015em;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
/* the faint dot matrix behind every page */
.grid { position: fixed; top: -13mm; left: -12mm; width: 148mm; height: 148mm; z-index: -1;
        background-image: radial-gradient(circle, #1c1c1c 0.35mm, transparent 0.4mm);
        background-size: 3.2mm 3.2mm; }
.cover { page: cover; height: 148mm; width: 148mm; position: relative; overflow: hidden;
         background: #000; break-after: page; }
.cover img { position: absolute; left: 0; width: 148mm; top: 18mm; }
.cover .kind { position: absolute; left: 0; right: 0; bottom: 27mm; text-align: center;
               color: #fff; font-size: 15pt; letter-spacing: .18em; }
.cover .ver { position: absolute; left: 0; right: 0; bottom: 20mm; text-align: center;
              color: #d71921; font-size: 7.5pt; letter-spacing: .2em; }
.cover .subt { position: absolute; left: 24mm; right: 24mm; bottom: 9mm; text-align: center;
               color: #8a8a8a; font-size: 6.8pt; letter-spacing: .12em; line-height: 1.5; }
.cover .disc { position: absolute; width: 9mm; height: 9mm; border-radius: 50%%; background: #d71921;
               right: 9mm; bottom: 9mm; box-shadow: 0 0 4mm #d71921aa; }
.back .kind { color: #4cff7a; text-shadow: 0 0 2.2mm #2be86a; font-size: 8pt; letter-spacing: .08em; bottom: 66mm; }
.back .ver { bottom: 58mm; }
h1.contents { font-size: 15pt; color: #fff; letter-spacing: .14em; margin: 0 0 4mm; }
.toc { break-after: page; }
.toc .ch { display: flex; color: #fff; font-size: 9pt; margin: 3.2mm 0 1mm; letter-spacing: .06em; }
.toc .sec { display: flex; color: #b9b9b9; font-size: 7.4pt; margin: .45mm 0 .45mm 6mm; }
.toc .t { white-space: nowrap; overflow: hidden; }
.toc .dots { flex: 1; border-bottom: 0.35mm dotted #3c3c3c; margin: 0 1.6mm 1.2mm; }
.toc .n { color: #4cff7a; min-width: 7mm; text-align: right; }
.toc .ch .n { color: #d71921; }
.opener { page: opener; break-before: page; break-after: page; height: 118mm; display: flex; position: relative;
          flex-direction: column; justify-content: center; }
.opener .num { font-size: 64pt; line-height: 1; color: #d71921; text-shadow: 0 0 3mm #d7192188; }
.opener h1 { font-size: 17pt; color: #fff; letter-spacing: .08em; margin: 4mm 0 4mm; font-weight: normal;
             text-shadow: 0 0 2mm #ffffff55; }
.opener .intro { color: #a9a9a9; font-size: 8.2pt; }
h2 { font-size: 10.5pt; color: #fff; font-weight: normal; letter-spacing: .05em; margin: 7mm 0 2mm;
     padding-bottom: 1.2mm; border-bottom: 0.3mm solid #2a2a2a; break-after: avoid; position: relative; }
h2 .no { color: #d71921; margin-right: 2mm; }
.sec:first-of-type h2 { margin-top: 0; }
p { margin: 0 0 2.2mm; }
strong { color: #fff; font-weight: normal; text-shadow: 0 0 .9mm #ffffff66; }
em { color: #d8d8d8; font-style: normal; text-decoration: underline; text-decoration-color: #555; }
code { color: #4cff7a; font-family: 'Ndot'; font-size: .95em; overflow-wrap: anywhere; }
pre { overflow-wrap: anywhere; font-family: 'Ndot'; color: #4cff7a; background: #050505; border: 0.3mm solid #1f3b27;
      padding: 2mm 2.6mm; font-size: 7pt; line-height: 1.45; white-space: pre-wrap; break-inside: avoid;
      margin: 0 0 2.4mm; }
ul, ol { margin: 0 0 2.4mm; padding-left: 5mm; }
li { margin: 0 0 .9mm; }
ul { list-style: none; }
ul li { position: relative; }
ul li::before { content: ""; position: absolute; left: -3.6mm; top: 1.5mm; width: 1.1mm; height: 1.1mm; border-radius: 50%%; background: #d71921; box-shadow: 0 0 .8mm #d71921; }
ol li::marker { color: #d71921; }
table { width: 100%%; border-collapse: collapse; margin: 0 0 3mm; font-size: 7.2pt; break-inside: auto; }
th { text-align: left; color: #fff; font-weight: normal; border-bottom: 0.4mm solid #d71921; padding: 1mm 1.4mm; }
td { border-bottom: 0.25mm solid #222; padding: 1mm 1.4mm; vertical-align: top; overflow-wrap: anywhere; }
tr { break-inside: avoid; }
.note, .warn, .tech { padding: 2.2mm 2.8mm; margin: 0 0 2.6mm; break-inside: avoid; border-left: 1mm solid; }
.note { border-color: #4cff7a; background: #0b1a10; }
.warn { border-color: #d71921; background: #1e0a0b; }
.tech { border-color: #5a5a5a; background: #141414; color: #c9c9c9; font-size: 7.6pt; }
.note::before, .warn::before, .tech::before { display: block; font-size: 6.6pt; letter-spacing: .16em; margin-bottom: 1mm; }
.note::before { content: "TIP"; color: #4cff7a; }
.warn::before { content: "WARNING"; color: #ff4a52; }
.tech::before { content: "TECHNICAL"; color: #8a8a8a; }
.note p:last-child, .warn p:last-child, .tech p:last-child { margin-bottom: 0; }
figure.shot { margin: 0 0 3mm; break-inside: avoid; text-align: center; }
figure.shot img { max-width: 62%%; max-height: 98mm; border: 0.3mm solid #2a2a2a; }
figure.shot figcaption { color: #8a8a8a; font-size: 6.6pt; margin-top: 1mm; }
figure.shot.missing { border: 0.35mm dashed #444; padding: 3mm; color: #777; font-size: 6.8pt; }
.mk { position: absolute; left: 0; top: 0; font-size: 6px; color: #0a0a0a; font-family: sans-serif; white-space: nowrap; }
"""


def esc(s):
    return html.escape(s, quote=True)


def render(d, banner, pages, shots_dir):
    running = esc(d['TITLE'].upper() + '  ·  INSTRUCTION MANUAL').replace('"', '\\"')
    css = CSS % {'font': FONT, 'running': running}
    out = ['<!doctype html><html><head><meta charset="utf-8"><style>', css, '</style></head><body>',
           '<div class="grid"></div>']
    # cover
    out.append(f'<div class="cover"><img src="file://{esc(banner)}">'
               f'<div class="kind">INSTRUCTION MANUAL</div>'
               f'<div class="ver">{esc(d["VERSION"].upper())}  ·  MANUAL IN EARLY BETA</div>'
               f'<div class="subt">{esc(d.get("SUBTITLE", "").upper())}</div>'
               f'<div class="disc"></div></div>')
    # contents
    out.append('<div class="toc"><h1 class="contents">CONTENTS</h1>')
    for ci, ch in enumerate(d['CHAPTERS'], 1):
        n = pages.get(f'C{ci}', '000')
        out.append(f'<div class="ch"><span class="t">{ci:02d}  {esc(ch["title"].upper())}</span>'
                   f'<span class="dots"></span><span class="n">{n}</span></div>')
        for si, s in enumerate(ch['sections'], 1):
            n = pages.get(f'S{ci}.{si}', '000')
            out.append(f'<div class="sec"><span class="t">{ci}.{si}  {esc(s["title"])}</span>'
                       f'<span class="dots"></span><span class="n">{n}</span></div>')
    out.append('</div>')
    # chapters
    for ci, ch in enumerate(d['CHAPTERS'], 1):
        out.append(f'<div class="opener"><span class="mk">@@C{ci}@@</span><div class="num">{ci:02d}</div>'
                   f'<h1>{esc(ch["title"].upper())}</h1><div class="intro">{ch.get("intro", "")}</div></div>')
        out.append('<div class="chapter">')
        for si, s in enumerate(ch['sections'], 1):
            body = s['html']
            body = re.sub(r'<figure class="shot" data-need="([^"]*)"></figure>',
                          lambda m: shot(m.group(1), shots_dir), body)
            out.append(f'<div class="sec"><h2><span class="mk">@@S{ci}.{si}@@</span>'
                       f'<span class="no">{ci}.{si}</span>{esc(s["title"])}</h2>{body}</div>')
        out.append('</div>')
    # back cover
    out.append('<div class="cover back" style="break-before:page;break-after:auto">'
               '<div class="kind">©DR.ESSENCE  ·  NDOT FONTS ARE OWNED BY ©NOTHING</div>'
               f'<div class="ver">{esc(d["TITLE"].upper())}  ·  {esc(d["VERSION"].upper())}  ·  FREE AND OPEN SOURCE</div></div>')
    out.append('</body></html>')
    return '\n'.join(out)


SHOTS = {}


def shot(need, shots_dir):
    """A screenshot if one is mapped for this description, else a dashed placeholder."""
    f = SHOTS.get(need); cap = need
    if isinstance(f, dict): f, cap = f['file'], f['caption']
    if f and shots_dir and os.path.exists(os.path.join(shots_dir, f)):
        return (f'<figure class="shot"><img src="file://{esc(os.path.join(shots_dir, f))}">'
                f'<figcaption>{esc(cap)}</figcaption></figure>')
    return f'<figure class="shot missing">SCREENSHOT: {esc(need)}</figure>'


def chromium_pdf(html_path, pdf_path):
    js = f"""
const {{ chromium }} = require('playwright');
(async () => {{
  const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://{html_path}'); await p.evaluate(() => document.fonts.ready);
  await p.pdf({{ path: '{pdf_path}', preferCSSPageSize: true, printBackground: true }});
  await b.close();
}})();"""
    subprocess.run(['node', '-e', js], check=True)


def find_pages(pdf):
    n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True, text=True).stdout).group(1))
    pages = {}
    for i in range(1, n + 1):
        t = subprocess.run(['pdftotext', '-raw', '-f', str(i), '-l', str(i), pdf, '-'], capture_output=True, text=True).stdout
        for m in re.findall(r'@@([CS][\d.]+)@@', t):
            pages.setdefault(m, str(i))
    return pages, n


def main():
    content, banner, out_pdf = sys.argv[1:4]
    shots_dir = os.path.abspath(sys.argv[4]) if len(sys.argv) > 4 else None
    if shots_dir and os.path.exists(os.path.join(shots_dir, 'map.json')):
        SHOTS.update(json.load(open(os.path.join(shots_dir, 'map.json'))))
    d = runpy.run_path(content)
    tmp = tempfile.mkdtemp()
    h = os.path.join(tmp, 'm.html'); p1 = os.path.join(tmp, 'pass1.pdf')
    open(h, 'w').write(render(d, os.path.abspath(banner), {}, shots_dir)); chromium_pdf(h, p1)
    pages, n1 = find_pages(p1)
    html2 = render(d, os.path.abspath(banner), pages, shots_dir).replace('class="mk"', 'class="mk" hidden')
    # markers removed for the final print: same layout (they are absolutely positioned)
    html2 = re.sub(r'<span class="mk" hidden>@@[CS][\d.]+@@</span>', '', html2)
    open(h, 'w').write(html2); chromium_pdf(h, os.path.abspath(out_pdf))
    _, n2 = find_pages(os.path.abspath(out_pdf))
    missing = [k for k in [f'C{i}' for i in range(1, len(d['CHAPTERS']) + 1)] if k not in pages]
    print(f'{out_pdf}: {n2} pages (pass 1: {n1}); sections located: {len(pages)}; missing chapters: {missing}')


if __name__ == '__main__':
    main()
