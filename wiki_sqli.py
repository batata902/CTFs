from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
from contextlib import contextmanager
import string
import random

app = Flask(__name__)

chars = string.ascii_letters + string.digits
flag: str = f'$FLAG!{{{"".join(random.sample(chars, 15))}}}'

schema = f'''
CREATE TABLE IF NOT EXISTS paginas(
        id INTEGER PRIMARY KEY,
        titulo TEXT NOT NULL UNIQUE,
        descricao TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS flag(
	id INTEGER PRIMARY KEY,
	content TEXT
);

INSERT OR IGNORE INTO paginas(titulo, descricao)
VALUES
('Bolo', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'),
('MovimentosHistoricos', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'),
('A influencia do 67', 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.');

INSERT OR IGNORE INTO flag(content) VALUES ('{flag}');
'''

@contextmanager
def db():
        conn = sqlite3.connect('wikidb.db')
        cur = conn.cursor()
        try:
                yield conn, cur
        finally:
                conn.close()


@app.route('/')
def home():
        with db() as (_, cur):
                pages = cur.execute('SELECT titulo FROM paginas;').fetchall()

                return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MiniWiki</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        body {
            margin: 0;
            background: #f8f9fa;
            color: #212529;
            padding: 0 16px;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,.05);
        }

        h1 {
            margin-top: 0;
            color: #1a2530;
            font-size: 2rem;
        }

        h3 {
            margin-top: 35px;
            color: #495057;
        }

        p {
            line-height: 1.6;
            color: #4a5568;
            font-size: 16px;
        }

        form {
            display: flex;
            gap: 12px;
            margin: 30px 0;
        }

        input {
            flex: 1;
            padding: 14px 16px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.2s;
            -webkit-appearance: none;
        }

        input:focus {
            border-color: #2d7ef7;
        }

        button {
            padding: 14px 24px;
            border: none;
            background: #2d7ef7;
            color: white;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #1b68d8;
        }

        ul {
            padding-left: 0;
            list-style: none;
        }

        li {
            margin: 12px 0;
            padding: 16px;
            background: #fdfdfd;
            border: 1px solid #eef2f5;
            border-radius: 8px;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        li:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0,0,0,.03);
        }

        a {
            color: #2d7ef7;
            text-decoration: none;
            font-weight: 500;
            display: block;
        }

        a:hover {
            color: #1b68d8;
        }

        @media (max-width: 600px) {
            .container {
                margin: 20px 0;
                padding: 20px;
            }

            h1 {
                font-size: 1.75rem;
            }

            form {
                flex-direction: column;
                gap: 8px;
            }

            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>

<div class="container">
    <h1>MiniWiki</h1>
    <p>Bem-vindo à MiniWiki, uma enciclopédia criada pela comunidade.</p>

    <form action="{{ url_for('search') }}" method="GET">
        <input type="text" name="q" placeholder="Pesquisar artigo..." required>
        <button type="submit">Pesquisar</button>
    </form>

    <h3>Artigos populares</h3>
    <ul>
        {% for p in pages %}
        <li><a href="{{ url_for('page', titulo=p[0]) }}">{{ p[0] | capitalize }}</a></li>
        {% endfor %}
    </ul>
</div>

</body>
</html>''', pages=pages)

@app.route('/page/<titulo>')
def page(titulo: str):
        with db() as (_, cur):
                query = cur.execute(f"SELECT titulo, descricao FROM paginas WHERE titulo='{titulo}';")
                pagina = query.fetchone()
                if not pagina:
                        return redirect(url_for('search', q=titulo))

                return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ titulo }} - MiniWiki</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        body {
            margin: 0;
            background: #f8f9fa;
            color: #212529;
            padding: 0 16px;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,.05);
        }

        .back-link {
            color: #6c757d;
            text-decoration: none;
            font-size: 15px;
            display: inline-block;
            margin-bottom: 20px;
            transition: color 0.2s;
        }

        .back-link:hover {
            color: #212529;
        }

        h1 {
            margin-top: 0;
            color: #1a2530;
            font-size: 2.2rem;
            text-transform: capitalize;
        }

        p {
            line-height: 1.7;
            color: #333c48;
            font-size: 16px;
        }

        hr {
            margin: 40px 0;
            border: none;
            border-top: 1px solid #eee;
        }

        .footer-note {
            font-size: 14px;
            color: #868e96;
        }

        @media (max-width: 600px) {
            .container {
                margin: 20px 0;
                padding: 20px;
            }
            
            h1 {
                font-size: 1.8rem;
            }
        }
    </style>
</head>
<body>

<div class="container">
    <a href="/" class="back-link">← Página inicial</a>
    <h1>{{ titulo }}</h1>
    <p>{{ conteudo }}</p>
    <hr>
    <p class="footer-note">Artigo colaborativo da MiniWiki.</p>
</div>

</body>
</html>''', titulo=pagina[0], conteudo=pagina[1])

@app.route('/search')
def search():
        pesquisa = request.args.get('q', 'NULL').lower()
        with db() as (_, cur):
                query = cur.execute('SELECT id FROM paginas WHERE titulo = ?', (pesquisa,)).fetchone()
                if query:
                        return redirect(url_for('page', titulo=pesquisa))

        return render_template_string('''<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artigo não encontrado</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }

        body {
            margin: 0;
            background: #f8f9fa;
            color: #212529;
            padding: 0 16px;
        }

        .container {
            max-width: 800px;
            margin: 40px auto;
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,.05);
        }

        .back-link {
            color: #6c757d;
            text-decoration: none;
            font-size: 15px;
            display: inline-block;
            margin-bottom: 20px;
            transition: color 0.2s;
        }

        .back-link:hover {
            color: #212529;
        }

        h1 {
            margin-top: 0;
            color: #dc3545;
            font-size: 2rem;
        }

        p {
            line-height: 1.6;
            color: #4a5568;
            font-size: 16px;
        }

        form {
            display: flex;
            gap: 12px;
            margin: 30px 0;
        }

        input {
            flex: 1;
            padding: 14px 16px;
            border: 1px solid #ced4da;
            border-radius: 8px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.2s;
            -webkit-appearance: none;
        }

        input:focus {
            border-color: #dc3545;
        }

        button {
            padding: 14px 24px;
            border: none;
            background: #6c757d;
            color: white;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            transition: background 0.2s;
        }

        button:hover {
            background: #5a6268;
        }

        @media (max-width: 600px) {
            .container {
                margin: 20px 0;
                padding: 20px;
            }

            h1 {
                font-size: 1.75rem;
            }

            form {
                flex-direction: column;
                gap: 8px;
            }

            button {
                width: 100%;
            }
        }
    </style>
</head>
<body>

<div class="container">
    <a href="/" class="back-link">← Página inicial</a>
    <h1>404 - Artigo inexistente</h1>
    <p>O artigo "<b>{{ pesquisa }}</b>" não foi encontrado.</p>
    <p>Verifique a ortografia ou tente pesquisar outro termo.</p>

    <form action="/search" method="GET">
        <input type="text" name="q" placeholder="Pesquisar novamente..." required>
        <button type="submit">Pesquisar</button>
    </form>
</div>

</body>
</html>''', pesquisa=pesquisa)


if __name__ == '__main__':
        conn = sqlite3.connect('wikidb.db')
        conn.executescript(schema)
        conn.close()

        app.run()
