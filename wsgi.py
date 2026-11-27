"""Ponto de entrada de produção: a API Flask e o front-end Vue compilado na mesma origem.

O gunicorn carrega `wsgi:app`. As rotas `/api/*` continuam sendo da API; qualquer
outro caminho devolve um arquivo de `frontend/dist` ou o `index.html` da SPA
(o Vue Router usa history mode, então `/triagem` precisa cair no index).
"""

from pathlib import Path

from flask import abort, send_from_directory

from ticuida import create_app

app = create_app()

DIST = Path(__file__).resolve().parent / "frontend" / "dist"


@app.get("/", defaults={"caminho": ""})
@app.get("/<path:caminho>")
def spa(caminho: str):
    if caminho.startswith("api/"):
        abort(404)
    if caminho and (DIST / caminho).is_file():
        return send_from_directory(DIST, caminho)
    return send_from_directory(DIST, "index.html")
