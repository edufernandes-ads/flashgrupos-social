# Instagram @flashgrupos no automático

- `brand/` manual da marca, paleta, fontes, logos e prints do painel
- `estrategia/` posicionamento e calendário até 31/12/2026
- `agents/EQUIPE.md` papéis da equipe de agentes (analista, estrategista, copywriter, designer, revisor, social media)
- `posts/` um post por pasta (post.json + imagens)
- `scripts/render.py` gera as imagens
- `scripts/publish.py` publica no Instagram (roda no GitHub Actions a cada 30 min)

Pausar tudo: crie um arquivo chamado `PAUSAR` na raiz. Pausar um post: `"status": "pausado"` no post.json.

Secrets necessários (Settings > Secrets and variables > Actions): `IG_USER_ID` e `IG_TOKEN`.
