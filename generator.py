from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import base64

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configurazione delle cartelle di upload
FINAL_FOLDER = 'Final-Web-Site'
UPLOAD_FOLDER_IMG = os.path.join(FINAL_FOLDER, 'img')
UPLOAD_FOLDER_MAP = os.path.join(FINAL_FOLDER, 'maps')

app.config['FINAL_FOLDER'] = FINAL_FOLDER
app.config['UPLOAD_FOLDER_IMG'] = UPLOAD_FOLDER_IMG
app.config['UPLOAD_FOLDER_MAP'] = UPLOAD_FOLDER_MAP

# Creazione delle cartelle se non esistono
if not os.path.exists(FINAL_FOLDER):
    os.makedirs(FINAL_FOLDER)

if not os.path.exists(UPLOAD_FOLDER_IMG):
    os.makedirs(UPLOAD_FOLDER_IMG)

if not os.path.exists(UPLOAD_FOLDER_MAP):
    os.makedirs(UPLOAD_FOLDER_MAP)

# Funzione ausiliaria per gestire le dimensioni in px
def parse_px(value):
    return float(value.replace('px', '')) if isinstance(value, str) and 'px' in value else float(value)

# Route per la homepage
@app.route('/')
def index():
    return render_template('index.html')

# Route per il salvataggio della homepage
@app.route('/save_homepage', methods=['POST'])
def save_homepage():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

        title = data.get('title')
        slides = data.get('slides', [])
        sections = data.get('sections', [])

        # Gestione delle immagini della slideshow
        for i, slide in enumerate(slides):
            image_data = base64.b64decode(slide['data'])
            image_filename = f'image_{i}.jpg'
            image_path = os.path.join(app.config['UPLOAD_FOLDER_IMG'], image_filename)

            with open(image_path, 'wb') as img_file:
                img_file.write(image_data)

            # Modifica del percorso per includere il punto prima di /img
            slide['image'] = f'./img/{image_filename}'

        # Creazione del file HTML per la homepage
        page_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link href="stylehome.css" rel="stylesheet">
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
        </head>
        <body>
            <header class="header">
                <div class="container">
                    <h1>{title}</h1>
                    <nav class="navbar navbar-expand-lg navbar-light">
                        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                        <div class="collapse navbar-collapse justify-content-center" id="navbarNav">
                            <ul class="navbar-nav">
                                <li class="nav-item">
                                    <a class="nav-link text-white" href="homepage.html">Home</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link text-white" href="./maps/mappa_statica.html">Prenotazione</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link text-white" href="menu.html">Menù</a>
                                </li>
                            </ul>
                        </div>
                    </nav>
                </div>
            </header>
            <main class="container">
                <section id="home" class="mb-5">
                    <div id="carouselExampleIndicators" class="carousel slide mb-4" data-ride="carousel">
                        <ol class="carousel-indicators">
        """

        for i in range(len(slides)):
            page_content += f'<li data-target="#carouselExampleIndicators" data-slide-to="{i}" class="{ "active" if i == 0 else ""}"></li>'

        page_content += '</ol><div class="carousel-inner">'

        for i, slide in enumerate(slides):
            page_content += f"""
            <div class="carousel-item {'active' if i == 0 else ''}">
                <img class="d-block w-100" src="{slide['image']}" alt="{slide['title']}">
                <div class="carousel-caption d-none d-md-block">
                    <div class="carousel-caption-bg">
                        <h5>{slide['title']}</h5>
                        <p>{slide['description']}</p>
                    </div>
                </div>
            </div>
            """

        page_content += """
                        </div>
                        <a class="carousel-control-prev" href="#carouselExampleIndicators" role="button" data-slide="prev">
                            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                            <span class="sr-only">Previous</span>
                        </a>
                        <a class="carousel-control-next" href="#carouselExampleIndicators" role="button" data-slide="next">
                            <span class="carousel-control-next-icon" aria-hidden="true"></span>
                            <span class="sr-only">Next</span>
                        </a>
                    </div>
                    <div class="row mb-5">
        """

        if len(sections) >= 2:
            page_content += f"""
            <div class="col-md-12">
                <div class="col-md-12">
                {sections[0]}
                </div>
                <div class="col-md-12">
                {sections[1]}
                </div>
            </div>
            """

        page_content += """
                    </div>
                    <div class="row mb-5">
        """

        if len(sections) > 2:
            page_content += f"""
            <div class="col-12">
                <div class="col-12">
                {sections[2]}
                </div>
            </div>
            """

        page_content += """
                    </div>
                </section>
            </main>
            <footer class="footer">
                <div class="container">
                    <p>&copy; 2024 """ + title + """. Tutti i diritti riservati.</p>
                </div>
            </footer>
            <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
        </html>
        """

        file_name = "homepage.html"
        file_path = os.path.join(app.config['FINAL_FOLDER'], file_name)

        with open(file_path, 'w') as file:
            file.write(page_content)

        return jsonify({"success": True, "file_path": file_name})

    except Exception as e:
        print(f"Errore durante il salvataggio della pagina: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# Route per il salvataggio del menu
@app.route('/save_menu', methods=['POST'])
def save_menu():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400

        menu_sections = data.get('menu_sections', [])
        if not menu_sections:
            return jsonify({"success": False, "message": "No menu sections received"}), 400

        menu_content = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Menù - La Tavola Perfetta</title>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
            <style>
                body, html {{
                    margin: 0;
                    padding: 0;
                    font-family: 'Roboto', sans-serif;
                    background-color: #f9f9f9;
                }}
                .header {{
                    background-color: #343a40;
                    padding: 20px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5rem;
                }}
                .menu-section {{
                    margin-bottom: 50px;
                }}
                .menu-item {{
                    margin-bottom: 30px;
                    border: 1px solid #ddd;
                    padding: 15px;
                    border-radius: 5px;
                    background-color: #fff;
                    text-align: center;
                }}
                .menu-item img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 5px;
                    margin-bottom: 10px;
                }}
                .menu-item h4 {{
                    margin: 10px 0 5px;
                    font-size: 1.5rem;
                }}
                .menu-item p {{
                    margin: 0;
                    color: #555;
                }}
                .section-title {{
                    margin-bottom: 30px;
                    color: #343a40;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <header class="header text-white mb-3">
                <div class="container text-center">
                    <h1 class="display-4">Il Nostro Menù</h1>
                    <nav class="navbar navbar-expand-lg navbar-light">
                        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                            <span class="navbar-toggler-icon"></span>
                        </button>
                        <div class="collapse navbar-collapse justify-content-center" id="navbarNav">
                            <ul class="navbar-nav">
                                <li class="nav-item">
                                    <a class="nav-link text-dark" href="homepage.html">Home</a>
                                </li>
                                <li class="nav-item">
                                    <a class="nav-link text-white" href="./maps/mappa_statica.html">Prenotazione</a>
                                </li>
                                <li class="nav-item active">
                                    <a class="nav-link text-dark" href="menu.html">Menù</a>
                                </li>
                            </ul>
                        </div>
                    </nav>
                </div>
            </header>
            <main class="container">
                <section id="menu">
        """

        for section in menu_sections:
            section_name = section['name']
            section_items = section.get('items', [])

            if not section_name:
                return jsonify({"success": False, "message": "Section name is missing"}), 400

            menu_content += f"""
            <div class="menu-section">
                <h2 class="section-title text-dark">{section_name}</h2>
                <div class="row">
            """

            for item in section_items:
                item_name = item.get('name')
                item_description = item.get('description')
                item_image = item.get('image')

                if not item_name or not item_description:
                    return jsonify({"success": False, "message": "Item name or description is missing"}), 400

                if item_image:
                    try:
                        image_data = base64.b64decode(item_image)
                    except (ValueError, IndexError):
                        return jsonify({"success": False, "message": "Image data is malformed"}), 400

                    image_filename = f'{section_name.lower().replace(" ", "_")}_{item_name.lower().replace(" ", "_")}.jpg'
                    image_path = os.path.join(app.config['UPLOAD_FOLDER_IMG'], image_filename)

                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)

                    # Modifica del percorso per includere il punto prima di /img
                    item_image_path = f'./img/{image_filename}'
                else:
                    item_image_path = ""

                menu_content += f"""
                <div class="col-md-4 menu-item">
                    {'<img src="' + item_image_path + '" class="img-fluid" alt="' + item_name + '">' if item_image_path else ''}
                    <h4 class="text-dark mt-2">{item_name}</h4>
                    <p class="text-dark">{item_description}</p>
                </div>
                """

            menu_content += """
                </div>
            </div>
            """

        menu_content += """
                </section>
            </main>
            <footer class="bg-dark text-white text-center p-3">
                <div class="container">
                    <p>&copy; 2024 La Tavola Perfetta. Tutti i diritti riservati.</p>
                </div>
            </footer>

            <script src="https://code.jquery.com/jquery-3.5.1.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.16.1/dist/umd/popper.min.js"></script>
            <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
        </html>
        """

        file_name = "menu.html"
        file_path = os.path.join(app.config['FINAL_FOLDER'], file_name)

        with open(file_path, 'w') as file:
            file.write(menu_content)

        return jsonify({"success": True, "file_path": file_name})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# Route per il salvataggio della mappa statica
@app.route('/save_map_static', methods=['POST'])
def save_map_static():
    try:
        data = request.get_json()
        if not data or 'mapElements' not in data:
            return jsonify({"success": False, "message": "Nessun elemento della mappa trovato"}), 400

        map_elements_html = ""

        for element in data['mapElements']:
            element_id = element.get('id')
            if 'restaurant-hall' in element_id:
                left = parse_px(element.get('left', '0px'))
                top = parse_px(element.get('top', '0px'))
                width = parse_px(element.get('width', '0px'))
                height = parse_px(element.get('height', '0px'))
                dataX = float(element.get('dataX', '0'))
                dataY = float(element.get('dataY', '0'))
                innerHTML = element.get('innerHTML', '')

                hall_inner_html = ""

                for child_element in data['mapElements']:
                    if child_element['id'].startswith('map-ele') and child_element.get('parent') == element_id:
                        child_left = parse_px(child_element.get('left', '0px'))
                        child_top = parse_px(child_element.get('top', '0px'))
                        child_width = parse_px(child_element.get('width', '0px'))
                        child_height = parse_px(child_element.get('height', '0px'))
                        child_dataX = float(child_element.get('dataX', '0'))
                        child_dataY = float(child_element.get('dataY', '0'))
                        child_innerHTML = child_element.get('innerHTML', '')

                        # Estrazione dei dati del tavolo
                        table_number = ''
                        table_seats = ''
                        if 'data-table-number' in child_innerHTML:
                            start_num = child_innerHTML.find('data-table-number="') + len('data-table-number="')
                            end_num = child_innerHTML.find('"', start_num)
                            table_number = child_innerHTML[start_num:end_num]

                        if 'data-table-seats' in child_innerHTML:
                            start_seats = child_innerHTML.find('data-table-seats="') + len('data-table-seats="')
                            end_seats = child_innerHTML.find('"', start_seats)
                            table_seats = child_innerHTML[start_seats:end_seats]

                        hall_inner_html += f"""
                        <div class="element map-ele" id="{child_element['id']}" 
                             style="left: {child_left}px; top: {child_top}px; 
                                    width: {child_width}px; height: {child_height}px; 
                                    transform: translate({child_dataX}px, {child_dataY}px); 
                                    display: flex; justify-content: center; align-items: center; font-weight: bold; text-align: center;">
                            Tavolo {table_number}<br>
                            {table_seats} posti
                        </div>
                        """

                map_elements_html += f"""
                <div class="element" id="{element_id}" 
                     style="left: {left}px; top: {top}px; width: {width}px; height: {height}px; 
                            transform: translate({dataX}px, {dataY}px);">
                    {innerHTML}
                    {hall_inner_html}
                </div>
                """

        final_html = f"""
        <!DOCTYPE html>
        <html lang="it">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Mappa Statica Ristorante</title>
            <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/sweetalert2@11/dist/sweetalert2.min.css">
            <style>
                body {{ font-family: 'Roboto', sans-serif; background-color: #f0f0f0; }}
                .map-container {{
                    position: relative;
                    width: 85vw;
                    height: 85vh;
                    background-color: #e0cda9;
                    border: 2px solid #000;
                    margin: 20px auto;
                }}
                .element {{
                    position: absolute;
                    border: 2px solid #343a40;
                    background-color: rgba(255, 255, 255, 0.8);
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.2);
                }}
                .selected {{
                    background-color: lightblue;
                    border-color: blue;
                }}
                .form-container {{
                    margin: 20px auto;
                    width: 85vw;
                    max-width: 600px;
                    padding: 20px;
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }}
            </style>
        </head>
        <body>
        <header class="header text-white mb-3" style="background-color: #343a40 !important;">
            <div class="container text-center">
                <h1 class="display-4" style="color: white;">Prenota un Tavolo</h1>
                <nav class="navbar navbar-expand-lg navbar-light">
                    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                        <span class="navbar-toggler-icon" style="background-color: white;"></span>
                    </button>
                    <div class="collapse navbar-collapse justify-content-center" id="navbarNav">
                        <ul class="navbar-nav">
                            <li class="nav-item">
                                <a class="nav-link" href="../homepage.html" style="color: white;">Home</a>
                            </li>
                            <li class="nav-item">
                                    <a class="nav-link text-white" href="./maps/mappa_statica.html">Prenotazione</a>
                            </li>
                            <li class="nav-item">
                                <a class="nav-link" href="../menu.html" style="color: white;">Menù</a>
                            </li>
                        </ul>
                    </div>
                </nav>
            </div>
        </header>

            <div class="map-container">
                {map_elements_html}
            </div>

            <div class="form-container">
    <h2>Prenotazione Tavolo</h2>
    <form id="reservation-form" action="http://localhost:5001/prenota_tavolo" method="POST">
        <div class="form-group">
            <label for="name">Nome:</label>
            <input type="text" id="name" name="name" class="form-control" required>
        </div>
        <div class="form-group">
            <label for="date">Data:</label>
            <input type="date" id="date" name="date" class="form-control" required>
        </div>
        <div class="form-group">
            <label for="table">Tavolo Selezionato:</label>
            <input type="text" id="table" name="table" class="form-control" readonly>
        </div>
        <button type="submit" class="btn btn-primary">Prenota</button>
    </form>
</div>

            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <script>
            
                document.addEventListener('DOMContentLoaded', (event) => {{
                    const mapContainer = document.querySelector('.map-container');
                    const tableInput = document.getElementById('table');
                    
                    let tooltip = null;

                    mapContainer.addEventListener('mouseover', function(event) {{
                        const target = event.target.closest('.map-ele');
                        if (target) {{
                            const dragHandle = target.querySelector('.drag-handle');
                            const tableNumber = dragHandle ? dragHandle.getAttribute('data-table-number') : '';
                            const tableSeats = dragHandle ? dragHandle.getAttribute('data-table-seats') : '';
                            
                            if (tableNumber && tableSeats) {{
                                tooltip = Swal.fire({{
                                    title: 'Tavolo Selezionato',
                                    html: 'Hai selezionato il tavolo con numero: ' + tableNumber + '<br>Posti a sedere: ' + tableSeats,
                                    icon: 'info',
                                    showConfirmButton: false,
                                    timer: 3000,
                                    toast: true,
                                    position: 'top-right'
                                }});
                            }}
                        }}
                    }});

                    mapContainer.addEventListener('mouseout', function(event) {{
                        if (tooltip) {{
                            tooltip.close();
                            tooltip = null;
                        }}
                    }});

                    mapContainer.addEventListener('dblclick', function(event) {{
                        const target = event.target.closest('.map-ele');
                        if (target) {{
                            const dragHandle = target.querySelector('.drag-handle');
                            const tableNumber = dragHandle ? dragHandle.getAttribute('data-table-number') : '';
                            const tableSeats = dragHandle ? dragHandle.getAttribute('data-table-seats') : '';
                            
                            if (tableNumber && tableSeats) {{
                                // Aggiorna il campo "Tavolo Selezionato" del modulo
                                tableInput.value = 'Hai selezionato il tavolo con numero: ' + tableNumber + ', Posti a sedere: ' + tableSeats;
                            }}
                        }}
                    }});

                    // Aggiunta: gestire il submit del form e mostrare il popup di successo
                   const form = document.getElementById('reservation-form');
form.addEventListener('submit', function(event) {{
    event.preventDefault();
    const formData = new FormData(form);

    fetch(form.action, {{
        method: 'POST',
        body: formData
    }})
    .then(response => {{
        // Prima gestiamo i codici di stato specifici
        if (response.status === 409) {{
            return response.json().then(data => {{
                console.log('409 Response data:', data); // Log per debug
                Swal.fire({{
                    title: 'Tavolo già prenotato',
                    text: data.message || 'Il tavolo è già prenotato per questa data.',
                    icon: 'warning',
                    confirmButtonText: 'OK'
                }});
            }});
        }} else if (!response.ok) {{
            // Gestisci gli altri errori generali
            return response.json().then(data => {{
                console.log('Error Response data:', data); // Log per debug
                Swal.fire({{
                    title: 'Errore',
                    text: data.message || 'Si è verificato un errore durante la prenotazione.',
                    icon: 'error',
                    confirmButtonText: 'OK'
                }});
            }});
        }} else {{
            // Gestisci la risposta positiva
            return response.json().then(data => {{
                if (data.success) {{
                    Swal.fire({{
                        title: 'Prenotazione effettuata con successo',
                        text: data.message,
                        icon: 'success',
                        confirmButtonText: 'OK'
                    }});
                }}
            }});
        }}
    }})
    .catch(error => {{
        console.error('Fetch error:', error); // Log per debug
        Swal.fire({{
            title: 'Errore',
            text: 'Errore durante la comunicazione con il server.',
            icon: 'error',
            confirmButtonText: 'OK'
        }});
    }});
}});
                }});
            </script>
        </body>
        </html>
        """

        file_name = "mappa_statica.html"
        file_path = os.path.join(app.config['UPLOAD_FOLDER_MAP'], file_name)

        with open(file_path, 'w') as f:
            f.write(final_html)

        return jsonify({"success": True, "file_path": file_name})

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500



# Route per servire file dalle cartelle di upload
@app.route('/img/<filename>')
def uploaded_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_IMG'], filename)

@app.route('/maps/<filename>')
def uploaded_map(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER_MAP'], filename)

if __name__ == '__main__':
    app.run(debug=True)
