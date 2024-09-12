import sqlite3
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Funzione per creare il database e la tabella prenotazioni se non esistono
def create_db():
    conn = sqlite3.connect('prenotazioni.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS prenotazioni (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            data TEXT NOT NULL,
            tavolo TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Route per gestire la prenotazione del tavolo
@app.route('/prenota_tavolo', methods=['POST'])
def prenota_tavolo():
    try:
        # Recupera i dati dal form
        nome = request.form.get('name')
        data = request.form.get('date')
        tavolo = request.form.get('table')

        # Controllo se i dati sono presenti
        if not nome or not data or not tavolo:
            return jsonify({"success": False, "message": "Dati incompleti"}), 400

        # Controlla se il tavolo è già prenotato per quella data
        conn = sqlite3.connect('prenotazioni.db')
        c = conn.cursor()
        c.execute('SELECT * FROM prenotazioni WHERE data = ? AND tavolo = ?', (data, tavolo))
        result = c.fetchone()

        if result:
            conn.close()
            return jsonify({"success": False, "message": f"Tavolo {tavolo} già prenotato per la data {data}"}), 409

        # Inserisci la prenotazione nel database
        c.execute('INSERT INTO prenotazioni (nome, data, tavolo) VALUES (?, ?, ?)', (nome, data, tavolo))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Prenotazione effettuata con successo"}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


if __name__ == '__main__':
    create_db()  # Crea il database se non esiste
    app.run(port=5001)  # Avvia il server sulla porta 5001