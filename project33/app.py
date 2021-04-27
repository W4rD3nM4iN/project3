import sqlite3
from hashids import Hashids
from flask import Flask, render_template, request, flash, redirect, url_for

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=('GET', 'POST'))
def index():
    conn = connect_db()

    if request.method == 'POST':
        url = request.form['url']

        if not url:
            flash('Вы не ввели ссылку!')
            return redirect(url_for('index'))

        url_data = conn.execute('INSERT INTO urls (original_url) VALUES (?)',
                                (url,))
        conn.commit()
        conn.close()

        url_id = url_data.lastrowid
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid

        return render_template('index.html', short_url=short_url)

    return render_template('index.html')


@app.route('/<id>')
def url_redirect(id):
    conn = connect_db()

    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url_data = conn.execute('SELECT original_url, clicks FROM urls WHERE id = (?)', (original_id,)).fetchone()
        original_url = url_data['original_url']
        clicks = url_data['clicks']

        conn.execute('UPDATE urls SET clicks = ? WHERE id = ?',
                     (clicks + 1, original_id))

        conn.commit()
        conn.close()
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))


@app.route('/history')
def stats():
    conn = connect_db()
    db_urls = conn.execute('SELECT id, created, original_url, clicks FROM urls').fetchall()
    conn.close()

    urls = []
    for url in db_urls:
        url = dict(url)
        url['short_url'] = request.host_url + hashids.encode(url['id'])
        urls.append(url)

    return render_template('history.html', urls=urls)

@app.route('/billy')
def billy():
    return render_template('billy.html')

def connect_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


if __name__ == '__main__':
    app.run()
