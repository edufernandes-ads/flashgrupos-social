#!/usr/bin/env python3
"""Designer do Flash Grupos: transforma posts/<id>/post.json em imagens 1080x1350 (ou 1080x1920).

Uso: python3 scripts/render.py posts/2026-11-09-tempo        (um post)
     python3 scripts/render.py --all                          (todos sem imagens)

post.json:
{
  "data": "2026-11-09", "hora": "12:00", "formato": "carrossel" | "imagem" | "story",
  "tema": "auto" | "black" | "natal" | "padrao",
  "legenda": "...", "hashtags": ["..."],
  "slides": [ {"tipo": "capa", ...}, ... ]
}
Tipos de slide e campos:
  capa:    selo, titulo (use *palavra* para destacar), sub, mascote (true/false)
  texto:   numero, titulo, corpo
  lista:   titulo, itens [..], (icone "check" | "x")
  tela:    titulo, imagem (arquivo em brand/assets), legenda,
           recorte [x0, y0, x1, y1] opcional (frações 0..1 da imagem: mostra só esse pedaço, ampliado)
  chat:    titulo, grupo, info (linha abaixo do nome do grupo), mensagens [{"de": "Flash Grupos", "texto": "..."}]
  compara: titulo, esquerda {rotulo, itens}, direita {rotulo, itens}
  numero:  grande, titulo, corpo
  cta:     titulo, sub, botao
"""
import base64, html, json, re, sys, mimetypes
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = ROOT / "brand"
HANDLE = "@flashgrupos.ia"

TEMAS = {
    "padrao": dict(acc="#8b5cf6", acc2="#c4b5fd", deep="#7c3aed", deep3="#4c1d95", apoio="#f472b6",
                   selo="", logo="rosto-padrao.png", glow="139,92,246"),
    "black": dict(acc="#8b5cf6", acc2="#c4b5fd", deep="#7c3aed", deep3="#4c1d95", apoio="#f472b6",
                  selo="BLACK NOVEMBER", logo="rosto-padrao.png", glow="139,92,246"),
    "natal": dict(acc="#e23b4e", acc2="#ff8a96", deep="#c8283c", deep3="#7a1220", apoio="#f3c766",
                  selo="BLACK NATALINA", logo="logo-preguica-natal-512.png", glow="226,59,78"),
}


def tema_da_data(d: str) -> str:
    dt = date.fromisoformat(d)
    if date(2026, 12, 1) <= dt <= date(2026, 12, 31):
        return "natal"
    if date(2026, 11, 6) <= dt <= date(2026, 11, 30):
        return "black"
    return "padrao"


def data_uri(p: Path) -> str:
    mt = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
    if p.suffix == ".woff2":
        mt = "font/woff2"
    return f"data:{mt};base64," + base64.b64encode(p.read_bytes()).decode()


def rich(t: str) -> str:
    """Escapa e transforma *texto* em destaque e quebras de linha em <br>."""
    t = html.escape(t or "")
    t = re.sub(r"\*(.+?)\*", r'<em class="hl">\1</em>', t)
    return t.replace("\n", "<br>")


def fonts_css() -> str:
    out = []
    for w in (300, 400, 500, 600, 700, 800):
        f = BRAND / "fonts" / f"poppins-{w}.woff2"
        if f.exists():
            out.append(f"@font-face{{font-family:P;font-weight:{w};src:url({data_uri(f)}) format('woff2')}}")
    return "\n".join(out)


CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)spx;height:%(H)spx}
body{font-family:P,Poppins,sans-serif;color:#fafafa;background:#09090b;overflow:hidden;position:relative;-webkit-font-smoothing:antialiased}
.bg{position:absolute;inset:0;background:
 radial-gradient(900px 700px at 85%% -10%%,rgba(%(glow)s,.30),transparent 60%%),
 radial-gradient(700px 600px at -10%% 110%%,rgba(%(glow)s,.16),transparent 60%%),#09090b}
.grid{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.035) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.035) 1px,transparent 1px);background-size:60px 60px;mask-image:radial-gradient(ellipse at center,#000 30%%,transparent 80%%)}
.wrap{position:absolute;inset:0;padding:96px 90px 150px;display:flex;flex-direction:column}
.top{display:flex;align-items:center;justify-content:space-between;margin-bottom:50px}
.selo{display:inline-flex;align-items:center;gap:10px;padding:12px 22px;border-radius:999px;font-weight:700;font-size:22px;letter-spacing:.14em;color:%(acc2)s;background:rgba(%(glow)s,.14);border:1.5px solid rgba(%(glow)s,.45)}
.selo i{width:10px;height:10px;border-radius:50%%;background:%(acc)s;box-shadow:0 0 14px %(acc)s}
.hl{font-style:normal;color:%(acc2)s;background:linear-gradient(90deg,%(acc2)s,%(acc)s);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent}
h1{font-weight:800;font-size:96px;line-height:1.02;letter-spacing:-.035em}
h2{font-weight:700;font-size:68px;line-height:1.08;letter-spacing:-.03em}
.sub{margin-top:34px;font-size:36px;line-height:1.4;color:#d4d4d8;font-weight:400;max-width:860px}
.corpo{margin-top:32px;font-size:40px;line-height:1.42;color:#d4d4d8}
.num{width:96px;height:96px;border-radius:28px;display:grid;place-items:center;font-weight:800;font-size:46px;color:#fff;background:linear-gradient(135deg,%(acc)s,%(deep3)s);box-shadow:0 20px 50px rgba(%(glow)s,.35);margin-bottom:44px}
.lista{margin-top:46px;display:flex;flex-direction:column;gap:22px}
.item{display:flex;gap:24px;align-items:flex-start;padding:28px 30px;border-radius:26px;background:#111113;border:1px solid rgba(255,255,255,.08);font-size:34px;line-height:1.35;color:#fafafa}
.ic{flex:none;width:46px;height:46px;border-radius:14px;display:grid;place-items:center;background:rgba(%(glow)s,.18);color:%(acc2)s;font-weight:800;font-size:28px}
.ic.x{background:rgba(239,68,68,.15);color:#f87171}
.shot{margin-top:46px;border-radius:28px;overflow:hidden;border:1px solid rgba(255,255,255,.12);background:#111113;box-shadow:0 40px 90px rgba(0,0,0,.6),0 0 0 8px rgba(%(glow)s,.08)}
.bar{height:50px;display:flex;align-items:center;gap:10px;padding:0 22px;background:#18181b;border-bottom:1px solid rgba(255,255,255,.08)}
.bar i{width:14px;height:14px;border-radius:50%%;background:#3f3f46}.bar span{margin-left:16px;font-size:19px;color:#a1a1aa}
.shot img{display:block;width:100%%;max-height:%(shotmax)spx;object-fit:cover;object-position:top}
.leg{margin-top:30px;font-size:30px;color:#a1a1aa;line-height:1.4}
.phone{margin:60px auto 0;width:880px;border-radius:44px;background:#0b141a;border:10px solid #1f1f23;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.6)}
.ph-h{display:flex;align-items:center;gap:18px;padding:22px 26px;background:#1f2c34}
.ph-a{width:58px;height:58px;border-radius:50%%;background:linear-gradient(135deg,%(acc)s,%(deep3)s)}
.ph-h b{font-size:27px;font-weight:600}.ph-h small{display:block;font-size:20px;color:#8696a0;font-weight:400}
.ph-b{padding:26px;display:flex;flex-direction:column;gap:18px;background:#0b141a}
.msg{align-self:flex-start;max-width:92%%;background:#202c33;border-radius:0 22px 22px 22px;padding:24px 28px;font-size:32px;line-height:1.42;color:#e9edef}
.msg .who{display:block;font-size:21px;font-weight:600;color:%(acc2)s;margin-bottom:6px}
.msg .lk{color:#53bdeb}
.cols{margin-top:60px;display:grid;grid-template-columns:1fr 1fr;gap:24px;align-items:start}
.col{border-radius:30px;padding:36px 32px;background:#111113;border:1px solid rgba(255,255,255,.08)}
.col.on{background:linear-gradient(180deg,rgba(%(glow)s,.20),rgba(%(glow)s,.04));border-color:rgba(%(glow)s,.55)}
.col h3{font-size:34px;font-weight:700;margin-bottom:26px;letter-spacing:.02em}
.col p{font-size:31px;line-height:1.35;color:#d4d4d8;padding:22px 0;border-top:1px solid rgba(255,255,255,.07)}
.big{font-weight:800;font-size:230px;line-height:.95;letter-spacing:-.05em}
.mascote{position:absolute;right:70px;bottom:150px;width:330px;height:330px;border-radius:50%%;overflow:hidden;border:6px solid %(acc)s;box-shadow:0 0 0 14px rgba(%(glow)s,.15),0 40px 80px rgba(0,0,0,.55)}
.mascote img{width:100%%;height:100%%;object-fit:cover}
.cta-m{width:300px;height:300px;margin-bottom:56px}
.cta-m img{width:100%%;height:100%%;border-radius:50%%;border:6px solid %(acc)s;box-shadow:0 0 0 12px rgba(%(glow)s,.18),0 40px 90px rgba(%(glow)s,.35)}
.btn{margin-top:56px;align-self:flex-start;padding:30px 50px;border-radius:999px;font-weight:700;font-size:36px;color:#fff;background:linear-gradient(135deg,%(acc)s,%(deep)s);box-shadow:0 22px 50px rgba(%(glow)s,.45)}
.foot{position:absolute;left:90px;right:90px;bottom:56px;display:flex;align-items:center;justify-content:space-between;font-size:24px;color:#a1a1aa}
.brand{display:flex;align-items:center;gap:16px;font-weight:600;color:#fafafa}
.brand img{width:52px;height:52px;border-radius:14px}
.dots{display:flex;gap:10px}.dots i{width:12px;height:12px;border-radius:50%%;background:#3f3f46}.dots i.on{width:34px;border-radius:8px;background:%(acc)s}
.next{color:%(acc2)s;font-weight:600}
"""


def slide_html(s: dict, i: int, n: int, T: dict, assets: dict) -> str:
    t = s.get("tipo", "texto")
    body = ""
    top = ""
    selo = s.get("selo", T["selo"] if i == 0 else "")
    if selo:
        top = f'<div class="top"><span class="selo"><i></i>{html.escape(selo)}</span></div>'
    if t == "capa":
        body = f'<h1>{rich(s.get("titulo"))}</h1>'
        if s.get("sub"):
            body += f'<p class="sub">{rich(s["sub"])}</p>'
        if s.get("mascote", True):
            body += f'<div class="mascote"><img src="{assets["logo"]}"></div>'
        pb = 300 if s.get("mascote", True) else 60
        body = f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:{pb}px">' + body + "</div>"
    elif t == "texto":
        if s.get("numero"):
            body += f'<div class="num">{html.escape(str(s["numero"]))}</div>'
        body += f'<h2>{rich(s.get("titulo"))}</h2>'
        if s.get("corpo"):
            body += f'<p class="corpo">{rich(s["corpo"])}</p>'
        body = '<div style="flex:1;display:flex;flex-direction:column;justify-content:center">' + body + "</div>"
    elif t == "numero":
        body = f'<div class="big hl">{rich(s.get("grande"))}</div><h2 style="margin-top:30px">{rich(s.get("titulo"))}</h2>'
        if s.get("corpo"):
            body += f'<p class="corpo">{rich(s["corpo"])}</p>'
        body = '<div style="flex:1;display:flex;flex-direction:column;justify-content:center">' + body + "</div>"
    elif t == "lista":
        x = s.get("icone") == "x"
        items = "".join(
            f'<div class="item"><span class="ic{" x" if x else ""}">{"✕" if x else "✓"}</span><span>{rich(it)}</span></div>'
            for it in s.get("itens", []))
        body = f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center"><h2>{rich(s.get("titulo"))}</h2><div class="lista">{items}</div></div>'
    elif t == "tela":
        img = assets["shot"](s["imagem"])
        if s.get("recorte"):
            from PIL import Image
            x0, y0, x1, y1 = s["recorte"]
            iw, ih = Image.open(BRAND / "assets" / s["imagem"]).size
            cw = 900  # largura útil do slide
            sc = cw / ((x1 - x0) * iw)
            boxh = round((y1 - y0) * ih * sc)
            tag = (f'<div style="height:{boxh}px;overflow:hidden"><img src="{img}" style="max-height:none;object-fit:fill;'
                   f'width:{round(iw * sc)}px;height:{round(ih * sc)}px;max-width:none;margin-left:{-round(x0 * iw * sc)}px;margin-top:{-round(y0 * ih * sc)}px"></div>')
        else:
            tag = f'<img src="{img}">'
        body = (f'<h2 style="font-size:58px">{rich(s.get("titulo"))}</h2>'
                f'<div class="shot"><div class="bar"><i></i><i></i><i></i><span>painel.flashgrupos.com</span></div>'
                f'{tag}</div>')
        if s.get("legenda"):
            body += f'<p class="leg">{rich(s["legenda"])}</p>'
        body = '<div style="flex:1;display:flex;flex-direction:column;justify-content:center">' + body + "</div>"
    elif t == "chat":
        msgs = ""
        for m in s.get("mensagens", []):
            txt = html.escape(m.get("texto") or "")
            txt = re.sub(r"\*(.+?)\*", r"<b>\1</b>", txt).replace("\n", "<br>")
            txt = re.sub(r"((?:s\.shopee|meli\.la|amzn\.to|flashgrupos)[^\s<]*)", r'<span class="lk">\1</span>', txt)
            msgs += f'<div class="msg"><span class="who">{html.escape(m.get("de", "Flash Grupos"))}</span>{txt}</div>'
        body = (f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center"><h2 style="font-size:58px">{rich(s.get("titulo"))}</h2><div class="phone"><div class="ph-h"><div class="ph-a"></div>'
                f'<div><b>{html.escape(s.get("grupo", "VIP Achadinhos"))}</b><small>{html.escape(s.get("info", "1.024 participantes"))}</small></div></div>'
                f'<div class="ph-b">{msgs}</div></div></div>')
    elif t == "compara":
        def col(c, on):
            ps = "".join(f"<p>{rich(x)}</p>" for x in c.get("itens", []))
            return f'<div class="col{" on" if on else ""}"><h3>{rich(c.get("rotulo"))}</h3>{ps}</div>'
        body = f'<div style="flex:1;display:flex;flex-direction:column;justify-content:center"><h2>{rich(s.get("titulo"))}</h2><div class="cols">{col(s.get("esquerda", {}), False)}{col(s.get("direita", {}), True)}</div></div>'
    elif t == "cta":
        body = (f'<div class="cta-m"><img src="{assets["logo"]}"></div><h2>{rich(s.get("titulo"))}</h2>')
        if s.get("sub"):
            body += f'<p class="corpo">{rich(s["sub"])}</p>'
        body += f'<div class="btn">{html.escape(s.get("botao", "Teste 7 dias: link na bio"))}</div>'
        body = '<div style="flex:1;display:flex;flex-direction:column;justify-content:center">' + body + "</div>"
    dots = "".join(f'<i class="{"on" if k == i else ""}"></i>' for k in range(n)) if n > 1 else ""
    nxt = '<span class="next">arrasta →</span>' if (n > 1 and i == 0) else dots
    foot = (f'<div class="foot"><div class="brand"><img src="{assets["logo"]}">{HANDLE}</div>'
            f'<div class="dots">{nxt}</div></div>')
    return f'<div class="bg"></div><div class="grid"></div><div class="wrap">{top}{body}</div>{foot}'


def render(post_dir: Path):
    from playwright.sync_api import sync_playwright
    post = json.loads((post_dir / "post.json").read_text(encoding="utf8"))
    tema = post.get("tema", "auto")
    if tema == "auto":
        tema = tema_da_data(post["data"])
    T = TEMAS[tema]
    story = post.get("formato") == "story"
    W, H = 1080, (1920 if story else 1350)
    cache = {}

    def shot(name):
        if name not in cache:
            cache[name] = data_uri(BRAND / "assets" / name)
        return cache[name]

    assets = {"logo": data_uri(BRAND / "assets" / T["logo"]), "shot": shot}
    css = fonts_css() + CSS % dict(W=W, H=H, shotmax=760 if not story else 1100, **T)
    slides = post["slides"]
    out = []
    for old in post_dir.glob("slide-*.jpg"):
        old.unlink()
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": W, "height": H})
        for i, s in enumerate(slides):
            doc = f'<!doctype html><html><head><meta charset="utf-8"><style>{css}</style></head><body>{slide_html(s, i, len(slides), T, assets)}</body></html>'
            pg.set_content(doc, wait_until="load")
            pg.evaluate("document.fonts.ready")
            f = post_dir / f"slide-{i + 1:02d}.jpg"
            pg.screenshot(path=str(f), type="jpeg", quality=92)
            out.append(f.name)
        b.close()
    post["imagens"] = out
    post["tema_usado"] = tema
    (post_dir / "post.json").write_text(json.dumps(post, ensure_ascii=False, indent=2), encoding="utf8")
    print(post_dir.name, tema, len(out), "imagens")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--all"]:
        for d in sorted((ROOT / "posts").iterdir()):
            if (d / "post.json").exists() and not list(d.glob("slide-*.jpg")):
                render(d)
    else:
        for a in args:
            render(Path(a).resolve())
