from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"

DATABASE = os.path.join(os.path.dirname(__file__), "cafe_management.db")

def get_db_connection():
    print("接続しているDBファイル：", DATABASE)
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('add_item'))

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        initial_stock = request.form['initial_stock']

        if not name or not initial_stock.isdigit():
            flash("正しい材料名と初期在庫を入力してください", "error")
            return redirect(url_for('add_item'))

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO items (name, initial_stock) VALUES (?, ?)',
            (name, int(initial_stock))
        )
        conn.commit()
        conn.close()
        flash(f"材料「{name}」を登録しました", "success")
        return redirect(url_for('add_item'))

    return render_template('add_item.html')

@app.route('/items')
def list_items():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()
    conn.close()
    return render_template('list_items.html', items=items)

@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    conn = get_db_connection()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        initial_stock = request.form['initial_stock']

        if not name or not initial_stock.isdigit():
            flash("正しい材料名と初期在庫を入力してください", "error")
            return redirect(url_for('edit_item', item_id=item_id))

        conn.execute('UPDATE items SET name = ?, initial_stock = ? WHERE id = ?',
                     (name, int(initial_stock), item_id))
        conn.commit()
        conn.close()
        flash("材料を更新しました", "success")
        return redirect(url_for('list_items'))

    conn.close()
    return render_template('edit_item.html', item=item)

@app.route('/items/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM items WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash("材料を削除しました", "success")
    return redirect(url_for('list_items'))

@app.route('/logs/add', methods=['GET', 'POST'])
def add_log():
    conn = get_db_connection()
    items = conn.execute('SELECT * FROM items').fetchall()

    if request.method == 'POST':
        item_id = request.form['item_id']
        change = request.form['change']
        note = request.form['note']

        if not item_id or not change or not change.lstrip('-').isdigit():
            flash("正しい数量を入力してください", "error")
            return redirect(url_for('add_log'))

        conn.execute(
            'INSERT INTO logs (item_id, change, timestamp, note) VALUES (?, ?, ?, ?)',
            (int(item_id), int(change), datetime.now().isoformat(), note)
        )
        conn.commit()
        conn.close()
        flash("入出庫履歴を登録しました", "success")
        return redirect(url_for('list_logs'))

    conn.close()
    return render_template('add_log.html', items=items)

@app.route('/logs')
def list_logs():
    conn = get_db_connection()
    logs = conn.execute('''
        SELECT logs.id, items.name AS item_name, logs.change, logs.timestamp, logs.note
        FROM logs
        JOIN items ON logs.item_id = items.id
        ORDER BY logs.timestamp DESC
    ''').fetchall()
    conn.close()
    return render_template('list_logs.html', logs=logs)
if __name__ == '__main__':
    app.run(debug=True)
