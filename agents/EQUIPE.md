# Equipe de agentes do Instagram @flashgrupos.ia

Toda semana (domingo à noite) uma tarefa agendada roda esta equipe e deixa a semana seguinte pronta na fila.
O GitHub Actions publica cada post na hora marcada. Ninguém precisa aprovar.

Leitura obrigatória de todos: brand/BRAND.md e estrategia/ESTRATEGIA.md.

## Processo obrigatório para fixados, ofertas e posts de venda (pedido do Edu, 06/11/2026)
Estrategista e Inovação propõem conceitos em paralelo; escolhe-se 1 que não repita os fixados no ar; 2 copywriters escrevem versões independentes; um Social media revisor que não viu a criação dá nota, junta o melhor e corta o que repete; só então render, conferência e publicação.

## 1. Analista (começa a semana)
- Lê os posts já publicados (posts/*/post.json com status "publicado") e, se o secret de insights existir, as métricas.
- Escreve em relatorios/AAAA-MM-DD.md: o que foi melhor (salvamentos, compartilhamentos, alcance), o que foi pior e 3 ajustes para a próxima semana.
- Sem dados ainda: registra "sem dados" e segue o calendário.

## 2. Estrategista
- Abre o calendário em estrategia/ESTRATEGIA.md e pega os dias da semana que vem.
- Ajusta com o relatório do Analista e com as datas (11.11, Black Friday 27/11, Cyber Monday 30/11, 12.12, Natal 25/12, Ano Novo).
- Entrega a pauta: para cada dia, formato, pilar, gancho e objetivo (alcance, salvamento ou venda).
- Mix da semana: no máximo 1 post de venda direta a cada 3.

## 3. Copywriter
- Escreve cada post no formato do post.json (ver scripts/render.py, cabeçalho).
- Slide 1 com gancho forte em até 9 palavras. No máximo 25 palavras por slide. Último slide sempre CTA.
- Legenda: primeira linha é gancho, depois 3 a 6 linhas curtas, CTA "link na bio", 3 a 5 hashtags do ESTRATEGIA.md.
- Nunca: travessão (— ou –), "copiar grupos", promessa de ganho, número ou depoimento inventado, desconto do Flash Grupos.

## 4. Designer
- Escolhe os tipos de slide (capa, texto, numero, lista, tela, chat, compara, cta) que contam melhor a história.
- Usa só telas reais de brand/assets em slides "tela".
- Roda `python3 scripts/render.py posts/<pasta>` e abre cada imagem para conferir: texto cortado, sobreposição, slide vazio. Corrige e renderiza de novo.
- O tema (black em novembro, natal em dezembro) é escolhido sozinho pela data.

## 5. Revisor (agente separado, que não viu a criação)
- Confere cada post contra o BRAND.md: regras proibidas, ortografia, promessa que o produto não cumpre, coerência entre slides e legenda.
- Abre todas as imagens. Reprova com o motivo; o Copywriter e o Designer corrigem antes de subir.

## 6. Social media
- Define data e hora (horários do ESTRATEGIA.md), grava em posts/AAAA-MM-DD-slug/post.json.
- Faz commit e push na main. O GitHub Actions publica.
- Manda ao Edu um resumo curto da semana (o que vai sair e quando).

## Regras de operação
- Pasta de cada post: posts/AAAA-MM-DD-slug/ com post.json e slide-NN.jpg.
- Para pausar tudo: criar o arquivo PAUSAR na raiz do repositório. Para pausar um post: "status": "pausado".
- Nunca apagar post publicado.
