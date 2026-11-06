#!/usr/bin/env python3
"""Social media do Flash Grupos: publica no Instagram o post que chegou na hora.

Roda no GitHub Actions (a cada 30 min). Precisa do secret:
  IG_TOKEN    token do Instagram (API com login do Instagram, graph.instagram.com).
              Opcional: IG_USER_ID (se vazio, descobre sozinho) e IG_API=facebook para usar graph.facebook.com.
O token dura 60 dias e é renovado sozinho a cada execução (refresh_access_token).
Opcional:
  IMAGE_BASE_URL  endereço público das imagens (padrão: raw do GitHub deste repositório)

Regras:
- Publica no máximo 1 post por execução, o mais antigo que já venceu (data + hora de Brasília).
- Pula posts com "status": "publicado" ou "pausado".
- Se existir o arquivo PAUSAR na raiz, não publica nada.
- Depois de publicar grava status, id e link no post.json (o workflow faz o commit).
"""
import json, os, sys, time, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://graph.facebook.com/v21.0" if os.environ.get("IG_API") == "facebook" else "https://graph.instagram.com/v21.0"
BRT = timezone(timedelta(hours=-3))


def call(method, path, **params):
    params["access_token"] = os.environ["IG_TOKEN"]
    data = urllib.parse.urlencode(params).encode()
    url = f"{API}/{path}"
    if method == "GET":
        req = urllib.request.Request(url + "?" + data.decode())
    else:
        req = urllib.request.Request(url, data=data, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise SystemExit(f"Erro da API do Instagram ({e.code}) em {path}: {body}")


def wait_ready(cid, tries=30):
    for _ in range(tries):
        st = call("GET", cid, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise SystemExit(f"Container {cid} falhou: {st}")
        time.sleep(5)
    raise SystemExit(f"Container {cid} não ficou pronto a tempo")


def caption(post):
    tags = " ".join("#" + h.lstrip("#") for h in post.get("hashtags", []))
    txt = post.get("legenda", "").strip()
    for bad in ("—", "–"):
        txt = txt.replace(bad, ",")
    return (txt + ("\n\n" + tags if tags else ""))[:2200]


def ig_id():
    if os.environ.get("IG_USER_ID"):
        return os.environ["IG_USER_ID"]
    return str(call("GET", "me", fields="user_id").get("user_id") or call("GET", "me", fields="id")["id"])


def refresh_token():
    if "graph.instagram.com" not in API:
        return
    try:
        r = call("GET", "refresh_access_token", grant_type="ig_refresh_token")
        same = r.get("access_token") == os.environ["IG_TOKEN"]
        print(f"Token renovado por mais {int(r.get('expires_in', 0)) // 86400} dias" + ("" if same else " (token novo gerado: atualize o secret IG_TOKEN)"))
    except SystemExit as e:
        print(f"Aviso: não renovou o token: {e}")


def publish(post_dir: Path, post: dict):
    ig = ig_id()
    repo = os.environ.get("GITHUB_REPOSITORY", "")
    base = os.environ.get("IMAGE_BASE_URL") or f"https://raw.githubusercontent.com/{repo}/main"
    urls = [f"{base}/posts/{post_dir.name}/{img}" for img in post["imagens"]]
    fmt = post.get("formato", "carrossel")
    if fmt == "story":
        cid = call("POST", f"{ig}/media", image_url=urls[0], media_type="STORIES")["id"]
    elif len(urls) == 1:
        cid = call("POST", f"{ig}/media", image_url=urls[0], caption=caption(post))["id"]
    else:
        kids = []
        for u in urls[:10]:
            k = call("POST", f"{ig}/media", image_url=u, is_carousel_item="true")["id"]
            kids.append(k)
        for k in kids:
            wait_ready(k)
        cid = call("POST", f"{ig}/media", media_type="CAROUSEL", children=",".join(kids), caption=caption(post))["id"]
    wait_ready(cid)
    mid = call("POST", f"{ig}/media_publish", creation_id=cid)["id"]
    link = call("GET", mid, fields="permalink").get("permalink", "")
    return mid, link


def due_posts():
    now = datetime.now(BRT)
    out = []
    for d in sorted((ROOT / "posts").iterdir()):
        f = d / "post.json"
        if not f.exists():
            continue
        p = json.loads(f.read_text(encoding="utf8"))
        if p.get("status") in ("publicado", "pausado", "arquivado", "substituido") or not p.get("imagens"):
            continue
        if p.get("aprovado") is not True:  # regra do Edu: só publica roteiro aprovado por ele
            continue
        when = datetime.fromisoformat(f'{p["data"]}T{p.get("hora", "12:00")}').replace(tzinfo=BRT)
        if when <= now and now - when < timedelta(days=2):
            out.append((when, d, p))
    return sorted(out, key=lambda x: x[0])


def main():
    if (ROOT / "PAUSAR").exists():
        print("Arquivo PAUSAR encontrado: nada publicado.")
        return
    if not os.environ.get("IG_TOKEN"):
        print("Secret IG_TOKEN ainda não configurado: nada publicado.")
        return
    if datetime.now(BRT).hour == 9:
        refresh_token()
    due = due_posts()
    if not due:
        print("Nenhum post na hora.")
        return
    when, d, p = due[0]
    mid, link = publish(d, p)
    p.update(status="publicado", media_id=mid, permalink=link,
             publicado_em=datetime.now(BRT).isoformat(timespec="minutes"))
    (d / "post.json").write_text(json.dumps(p, ensure_ascii=False, indent=2), encoding="utf8")
    print(f"Publicado {d.name}: {link}")


if __name__ == "__main__":
    main()
