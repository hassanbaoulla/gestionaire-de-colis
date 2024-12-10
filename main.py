import flet as ft
from database import Database
import qrcode
from io import BytesIO
from PIL import Image
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import base64
import time

class MainPage(ft.UserControl):
    def __init__(self, page: ft.Page, go_to_login, go_to_package_list):
        super().__init__()
        self.page = page
        self.go_to_login = go_to_login
        self.go_to_package_list = go_to_package_list

        # Champs de la base de données avec style français
        self.name_exp_field = ft.TextField(
            label="Nom Expéditeur",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.PERSON,
            hint_text="Entrez le nom de l'expéditeur",
            helper_text="Champ obligatoire",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.city_exp_field = ft.Dropdown(
            label="Ville Expéditeur",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.LOCATION_CITY,
            helper_text="Sélectionnez une ville",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
            options=[
                ft.dropdown.Option("Paris"),
                ft.dropdown.Option("Les Mureaux"),
            ],
            value="Paris",  # Valeur par défaut
        )
        
        self.phone_exp_field = ft.TextField(
            label="Téléphone Expéditeur",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.PHONE,
            hint_text="Entrez le numéro de téléphone",
            helper_text="Format: 0XXXXXXXXX",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.name_dest_field = ft.TextField(
            label="Nom Destinataire",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.PERSON_OUTLINE,
            hint_text="Entrez le nom du destinataire",
            helper_text="Champ obligatoire",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.city_dest_field = ft.Dropdown(
            label="Ville Destinataire",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.LOCATION_CITY_OUTLINED,
            helper_text="Sélectionnez une ville",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
            options=[
                ft.dropdown.Option("Kenitra"),
                ft.dropdown.Option("Rabat"),
                ft.dropdown.Option("Casablanca"),
                ft.dropdown.Option("Marrakech"),
                ft.dropdown.Option("Agadir"),
                ft.dropdown.Option("Tiznit"),
                ft.dropdown.Option("Bouzakarn"),
                ft.dropdown.Option("Guelmim"),
            ],
            value="Casablanca",  # Valeur par défaut
        )
        
        self.phone_dest_field = ft.TextField(
            label="Téléphone Destinataire",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.PHONE_OUTLINED,
            hint_text="Entrez le numéro de téléphone",
            helper_text="Format: 0XXXXXXXXX",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.nmbr_package_field = ft.TextField(
            label="Nombre de Colis",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.INVENTORY_2,
            hint_text="Entrez le nombre de colis",
            helper_text="Nombre entier positif",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.gender_package_field = ft.TextField(
            label="Type de Colis",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.CATEGORY,
            hint_text="Entrez le type de colis",
            helper_text="Ex: Documents, Colis, etc.",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.value_package_field = ft.TextField(
            label="Valeur (€)",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.ATTACH_MONEY,
            hint_text="Entrez la valeur en euros",
            helper_text="Nombre décimal positif",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.kilos_field = ft.TextField(
            label="Poids (KG)",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.SCALE,
            hint_text="Entrez le poids en kilogrammes",
            helper_text="Nombre décimal positif",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.price_field = ft.TextField(
            label="Prix (€)",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.PAYMENTS,
            hint_text="Entrez le prix en euros",
            helper_text="Nombre décimal positif",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )

        # QR Code
        self.qr_code_image = None

        # Bouton de scan QR code
        self.read_qr_button = ft.IconButton(
            icon=ft.icons.QR_CODE_SCANNER,
            icon_color=ft.colors.BLUE,
            icon_size=24,
            tooltip="Scanner un QR Code",
            on_click=self.read_qr_code,
        )

    def build(self):
        # Créer une liste de contrôles de base
        controls = [
            self.name_exp_field,
            self.city_exp_field,
            self.phone_exp_field,
            self.name_dest_field,
            self.phone_dest_field,
            self.city_dest_field,
            self.nmbr_package_field,
            self.gender_package_field,
            self.value_package_field,
            self.kilos_field,
            self.price_field,
            ft.Row([
                ft.ElevatedButton(
                    "Enregistrer",
                    icon=ft.icons.SAVE,
                    on_click=self.add_record,
                    bgcolor=ft.colors.GREEN,
                    color=ft.colors.WHITE
                ),
                ft.ElevatedButton(
                    "Effacer",
                    icon=ft.icons.CLEAR_ALL,
                    on_click=self.clear_fields,
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        ]

        # Ajouter l'image QR code seulement si elle existe
        if self.qr_code_image:
            controls.append(self.qr_code_image)

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Accueil", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        self.read_qr_button,
                        ft.IconButton(
                            icon=ft.icons.LIST_ALT,
                            tooltip="Liste des colis",
                            on_click=self.go_to_package_list
                        ),
                        ft.IconButton(
                            icon=ft.icons.LOGOUT,
                            tooltip="Déconnexion",
                            on_click=self.return_to_login
                        )
                    ])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.ListView(
                    controls=controls,
                    spacing=10,
                    padding=20,
                    height=500,
                    expand=1,
                )
            ], spacing=20),
            padding=ft.padding.only(top=20, left=20, right=20),
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0),
            ),
            expand=True
        )

    def return_to_login(self, e):
        self.go_to_login()

    def add_record(self, e):
        try:
            # Validate inputs
            if not all([
                self.name_exp_field.value,
                self.city_exp_field.value,
                self.phone_exp_field.value,
                self.name_dest_field.value,
                self.phone_dest_field.value,
                self.city_dest_field.value,
                self.nmbr_package_field.value,
                self.gender_package_field.value,
                self.value_package_field.value,
                self.kilos_field.value,
                self.price_field.value
            ]):
                self.page.show_snack_bar(ft.SnackBar(content=ft.Text("Please fill in all fields")))
                return

            db = Database()
            try:
                # Insert record and get the ID
                record_id = db.insert_record(
                    self.name_exp_field.value,
                    self.city_exp_field.value,
                    self.phone_exp_field.value,
                    self.name_dest_field.value,
                    self.phone_dest_field.value,
                    self.city_dest_field.value,
                    int(self.nmbr_package_field.value),
                    self.gender_package_field.value,
                    float(self.value_package_field.value),
                    float(self.kilos_field.value),
                    float(self.price_field.value)
                )

                # Générer le QR code
                data = f"""
                ID: {record_id}
                EXPEDITEUR:
                Nom: {self.name_exp_field.value}
                Ville: {self.city_exp_field.value}
                Tel: {self.phone_exp_field.value}
                
                DESTINATAIRE:
                Nom: {self.name_dest_field.value}
                Ville: {self.city_dest_field.value}
                Tel: {self.phone_dest_field.value}
                
                COLIS:
                Nombre: {self.nmbr_package_field.value}
                Type: {self.gender_package_field.value}
                Valeur: {self.value_package_field.value} €
                Poids: {self.kilos_field.value} Kg
                Prix: {self.price_field.value} €
                Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                """
                
                # Créer le QR code
                qr = qrcode.QRCode(
                    version=None,
                    error_correction=qrcode.constants.ERROR_CORRECT_H,
                    box_size=10,
                    border=4,
                )
                qr.add_data(data)
                qr.make(fit=True)
                qr_image = qr.make_image(fill_color="black", back_color="white")
                
                # Convertir en base64
                buffer = BytesIO()
                qr_image.save(buffer, format="PNG")
                qr_code_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
                
                # Créer et afficher l'image
                if self.qr_code_image is None:
                    self.qr_code_image = ft.Image(
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                    )
                
                self.qr_code_image.src_base64 = qr_code_data
                
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"✅ Colis ajouté avec succès! ID: {record_id}"))
                )
                
                # Clear fields
                self.clear_fields(None)
                
            finally:
                db.close()
                
        except ValueError as ve:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Veuillez entrer des nombres valides"))
            )
        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text(f"❌ Erreur: {str(ex)}"))
            )

    def clear_fields(self, e):
        for field in [
            self.name_exp_field,
            self.phone_exp_field,
            self.name_dest_field,
            self.phone_dest_field,
            self.nmbr_package_field,
            self.gender_package_field,
            self.value_package_field,
            self.kilos_field,
            self.price_field
        ]:
            field.value = ""
        
        # Réinitialiser les dropdowns à leurs valeurs par défaut
        self.city_exp_field.value = "Paris"
        self.city_dest_field.value = "Casablanca"
        
        if self.qr_code_image:
            self.qr_code_image.src_base64 = None
            
        self.update()

    def read_qr_code(self, e):
        def scan_qr():
            try:
                # Initialiser la caméra
                cap = cv2.VideoCapture(0)
                
                while True:
                    # Lire l'image de la caméra
                    ret, frame = cap.read()
                    
                    # Détecter les QR codes dans l'image
                    decoded_objects = decode(frame)
                    
                    # Dessiner un rectangle autour des QR codes détectés
                    for obj in decoded_objects:
                        points = obj.polygon
                        if len(points) > 4:
                            hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                            points = hull
                        
                        # Dessiner les points du polygone
                        n = len(points)
                        for j in range(n):
                            cv2.line(frame, points[j], points[(j+1) % n], (0, 255, 0), 3)

                        # Extraire et décoder les données
                        qr_data = obj.data.decode('utf-8')
                        
                        # Fermer la caméra
                        cap.release()
                        cv2.destroyAllWindows()
                        
                        # Traiter les données du QR code
                        self.process_qr_data(qr_data)
                        return
                    
                    # Afficher le flux vidéo
                    cv2.imshow('QR Code Scanner', frame)
                    
                    # Quitter si 'q' est pressé
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Nettoyer
                cap.release()
                cv2.destroyAllWindows()
                
            except Exception as ex:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Erreur de scan: {str(ex)}"))
                )

        # Lancer le scan dans un thread séparé
        import threading
        threading.Thread(target=scan_qr).start()

    def process_qr_data(self, qr_data):
        try:
            # Essayer de traiter comme un QR code de colis
            lines = qr_data.split('\n')
            data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip()
            
            if 'ID' in data:
                # C'est un QR code de colis
                self.show_scanned_details(data)
            else:
                # C'est un QR code universel
                self.show_universal_qr(qr_data)
                
        except Exception as ex:
            # Afficher le contenu brut si le format n'est pas reconnu
            self.show_universal_qr(qr_data)

    def show_universal_qr(self, qr_data):
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        content = ft.Column([
            ft.Text("QR Code Scanné", 
                   size=20, 
                   weight=ft.FontWeight.BOLD,
                   color=ft.colors.BLUE),
            ft.Divider(height=2, color=ft.colors.BLUE_200),
            
            ft.Container(
                content=ft.Column([
                    ft.Text("Contenu:", weight=ft.FontWeight.BOLD),
                    ft.Text(
                        qr_data,
                        selectable=True,  # Rendre le texte sélectionnable
                        size=14,
                    ),
                ]),
                padding=20,
                border=ft.border.all(1, ft.colors.BLUE_200),
                border_radius=10,
            ),
            
            # Boutons d'action pour le contenu
            ft.Row([
                ft.IconButton(
                    icon=ft.icons.COPY,
                    tooltip="Copier le contenu",
                    on_click=lambda _: self.page.set_clipboard(qr_data)
                ),
                ft.IconButton(
                    icon=ft.icons.OPEN_IN_BROWSER,
                    tooltip="Ouvrir le lien",
                    on_click=lambda _: self.page.launch_url(qr_data) if qr_data.startswith(('http://', 'https://')) else None,
                    visible=qr_data.startswith(('http://', 'https://'))
                ),
            ], alignment=ft.MainAxisAlignment.CENTER),
        ])

        dialog = ft.AlertDialog(
            content=content,
            actions=[
                ft.TextButton("Fermer", on_click=close_dialog),
            ],
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def show_scanned_details(self, data):
        def close_dialog(e):
            dialog.open = False
            self.page.update()

        content = ft.Column([
            # En-tête
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.INVENTORY_2_ROUNDED, size=30, color=ft.colors.BLUE),
                    ft.Text("Détails du Colis Scanné", 
                           size=20, 
                           weight=ft.FontWeight.BOLD,
                           color=ft.colors.BLUE),
                ], alignment=ft.MainAxisAlignment.CENTER),
                padding=10,
            ),
            
            ft.Divider(height=2, color=ft.colors.BLUE_200),
            
            # Informations principales
            ft.Container(
                content=ft.Column([
                    # ID et Code de suivi
                    ft.Container(
                        content=ft.Column([
                            ft.Text("IDENTIFICATION", 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.colors.BLUE,
                                   size=16),
                            ft.Text(f"ID Colis: #{data.get('ID', 'N/A')}", size=14),
                            ft.Text(f"Code de suivi: TR{data.get('ID', '000000'):06d}", size=14),
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLUE_200),
                        border_radius=10,
                    ),
                    
                    # Expéditeur
                    ft.Container(
                        content=ft.Column([
                            ft.Text("EXPÉDITEUR", 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.colors.BLUE,
                                   size=16),
                            ft.Row([
                                ft.Icon(ft.icons.PERSON, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Nom: {data.get('Nom', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.LOCATION_CITY, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Ville: {data.get('Ville', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.PHONE, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Tél: {data.get('Tel', 'N/A')}", size=14),
                            ]),
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLUE_200),
                        border_radius=10,
                    ),
                    
                    # Destinataire
                    ft.Container(
                        content=ft.Column([
                            ft.Text("DESTINATAIRE", 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.colors.BLUE,
                                   size=16),
                            ft.Row([
                                ft.Icon(ft.icons.PERSON, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Nom: {data.get('Nom', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.LOCATION_CITY, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Ville: {data.get('Ville', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.PHONE, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Tél: {data.get('Tel', 'N/A')}", size=14),
                            ]),
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLUE_200),
                        border_radius=10,
                    ),
                    
                    # Détails du colis
                    ft.Container(
                        content=ft.Column([
                            ft.Text("DÉTAILS DU COLIS", 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.colors.BLUE,
                                   size=16),
                            ft.Row([
                                ft.Icon(ft.icons.INVENTORY_2, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Nombre: {data.get('Nombre', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.CATEGORY, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Type: {data.get('Type', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.ATTACH_MONEY, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Valeur: {data.get('Valeur', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.SCALE, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Poids: {data.get('Poids', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.PAYMENTS, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Prix: {data.get('Prix', 'N/A')}", size=14),
                            ]),
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLUE_200),
                        border_radius=10,
                    ),
                    
                    # Date et statut
                    ft.Container(
                        content=ft.Column([
                            ft.Text("SUIVI", 
                                   weight=ft.FontWeight.BOLD,
                                   color=ft.colors.BLUE,
                                   size=16),
                            ft.Row([
                                ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text(f"Date: {data.get('Date', 'N/A')}", size=14),
                            ]),
                            ft.Row([
                                ft.Icon(ft.icons.LOCAL_SHIPPING, size=16, color=ft.colors.BLUE_GREY),
                                ft.Text("Statut: En cours de traitement", 
                                      size=14,
                                      color=ft.colors.ORANGE),
                            ]),
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLUE_200),
                        border_radius=10,
                    ),
                ], spacing=10),
                padding=20,
            ),
        ], scroll=ft.ScrollMode.AUTO)

        dialog = ft.AlertDialog(
            modal=True,
            content=content,
            actions=[
                ft.TextButton(
                    "Fermer",
                    icon=ft.icons.CLOSE,
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=ft.colors.RED_400,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def do_print(self, content, dialog):
        def close_printer_dialog(e):
            printer_dialog.open = False
            self.page.update()

        def search_printers(printer_type):
            # Animation de recherche
            searching_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Recherche d'imprimantes"),
                content=ft.Column([
                    ft.ProgressRing(width=40, height=40, stroke_width=3, color=ft.colors.BLUE),
                    ft.Text(f"Recherche d'imprimantes {printer_type}..."),
                    ft.Text("Veuillez patienter...", color=ft.colors.GREY_500, size=12),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
            )
            self.page.dialog = searching_dialog
            searching_dialog.open = True
            self.page.update()

            # Simuler la recherche
            time.sleep(2)
            searching_dialog.open = False
            self.page.update()

            # Liste des imprimantes avec leur statut
            return {
                'bluetooth': [
                    ("HP Printer BT-001", "20:FA:BB:02:00:01", "Disponible", "100%"),
                    ("Canon PIXMA BT", "20:FA:BB:02:00:02", "Disponible", "85%"),
                    ("Epson BT Printer", "20:FA:BB:02:00:03", "Occupée", "-"),
                    ("Brother BT", "20:FA:BB:02:00:04", "Hors ligne", "-"),
                ],
                'wifi': [
                    ("HP LaserJet Pro", "192.168.1.100", "Disponible", "192.168.1.100"),
                    ("Canon PIXMA WiFi", "192.168.1.101", "Disponible", "192.168.1.101"),
                    ("Epson WorkForce", "192.168.1.102", "Hors ligne", "-"),
                    ("Brother WiFi", "192.168.1.103", "Occupée", "192.168.1.103"),
                ]
            }.get(printer_type, [])

        def connect_printer(printer_type, e):
            try:
                printers = search_printers(printer_type)
                if not printers:
                    raise Exception("Aucune imprimante trouvée")

                # Liste des imprimantes avec statut et détails
                printer_list = ft.AlertDialog(
                    modal=True,
                    title=ft.Text(f"Imprimantes {printer_type} disponibles"),
                    content=ft.Column([
                        ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(
                                        ft.icons.PRINT if printer_type == 'wifi' else ft.icons.BLUETOOTH,
                                        color=ft.colors.BLUE if status == "Disponible" 
                                              else ft.colors.GREY_400,
                                        size=24,
                                    ),
                                    title=ft.Text(name),
                                    subtitle=ft.Column([
                                        ft.Text(address),
                                        ft.Text(
                                            f"Signal: {details}" if status == "Disponible" else "",
                                            color=ft.colors.GREY_700,
                                            size=12,
                                        ),
                                    ]),
                                    trailing=ft.Container(
                                        content=ft.Text(
                                            status,
                                            color=ft.colors.GREEN if status == "Disponible"
                                                  else ft.colors.RED if status == "Hors ligne"
                                                  else ft.colors.ORANGE,
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        padding=5,
                                    ),
                                    disabled=status != "Disponible",
                                    on_click=lambda _, name=name, status=status: 
                                        select_printer(name) if status == "Disponible" else None,
                                )
                            ] + [ft.Divider(height=1)] if i < len(printers)-1 else [])
                        ) for i, (name, address, status, details) in enumerate(printers)
                    ], scroll=ft.ScrollMode.AUTO, height=300),
                    actions=[
                        ft.TextButton(
                            "Actualiser",
                            icon=ft.icons.REFRESH,
                            on_click=lambda e: refresh_printers()
                        ),
                        ft.TextButton(
                            "Annuler",
                            icon=ft.icons.CANCEL,
                            on_click=lambda e: close_printer_list(printer_list)
                        ),
                    ],
                )

                def refresh_printers():
                    printer_list.open = False
                    self.page.update()
                    connect_printer(printer_type, None)

                def select_printer(printer_name):
                    try:
                        printer_list.open = False
                        self.page.update()

                        # Animation de connexion
                        connecting_dialog = ft.AlertDialog(
                            modal=True,
                            title=ft.Text("Connexion à l'imprimante"),
                            content=ft.Column([
                                ft.ProgressRing(width=40, height=40, stroke_width=3),
                                ft.Text(f"Connexion à {printer_name}..."),
                                ft.Text("Établissement de la connexion...", 
                                      color=ft.colors.GREY_500, 
                                      size=12),
                            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                        )
                        self.page.dialog = connecting_dialog
                        connecting_dialog.open = True
                        self.page.update()

                        time.sleep(1.5)
                        connecting_dialog.open = False

                        # Dialogue d'impression avec barre de progression
                        progress = ft.ProgressBar(width=400, color=ft.colors.BLUE)
                        printing_dialog = ft.AlertDialog(
                            modal=True,
                            title=ft.Text("Impression en cours"),
                            content=ft.Column([
                                ft.Text(f"Imprimante: {printer_name}"),
                                progress,
                                ft.Text("Préparation...", 
                                      color=ft.colors.GREY_700,
                                      size=14),
                            ], spacing=20),
                        )

                        self.page.dialog = printing_dialog
                        printing_dialog.open = True
                        self.page.update()

                        # Étapes détaillées de l'impression
                        steps = [
                            ("Initialisation...", "Configuration de l'imprimante"),
                            ("Envoi des données...", "Transmission du document"),
                            ("Impression en cours...", "Impression des pages"),
                            ("Finalisation...", "Finalisation du travail d'impression")
                        ]

                        for i, (step, detail) in enumerate(steps):
                            time.sleep(0.8)
                            progress.value = (i + 1) / len(steps)
                            printing_dialog.content.controls[-1].value = f"{step}\n{detail}"
                            self.page.update()

                        printing_dialog.open = False
                        self.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text("✅ Impression terminée avec succès!"),
                                action="OK",
                                action_color=ft.colors.GREEN,
                            )
                        )

                    except Exception as ex:
                        self.page.show_snack_bar(
                            ft.SnackBar(
                                content=ft.Text(f"❌ Erreur d'impression: {str(ex)}"),
                                bgcolor=ft.colors.RED_400,
                            )
                        )
                    finally:
                        self.page.update()

                def close_printer_list(dialog):
                    dialog.open = False
                    self.page.update()

                self.page.dialog = printer_list
                printer_list.open = True
                self.page.update()

            except Exception as ex:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"❌ Erreur: {str(ex)}"),
                        bgcolor=ft.colors.RED_400,
                    )
                )

        # Dialogue de sélection de la méthode de connexion
        printer_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Sélectionner une méthode de connexion"),
            content=ft.Container(
                content=ft.Column([
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.BLUETOOTH, color=ft.colors.WHITE),
                            ft.Text("Connexion Bluetooth"),
                            ft.Container(
                                content=ft.Text("4 imprimantes", size=12),
                                bgcolor=ft.colors.BLUE_900,
                                padding=5,
                                border_radius=10,
                            ),
                        ]),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE,
                            color=ft.colors.WHITE,
                            padding=20,
                        ),
                        width=300,
                        on_click=lambda e: connect_printer('bluetooth', e),
                    ),
                    ft.ElevatedButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.WIFI, color=ft.colors.WHITE),
                            ft.Text("Connexion WiFi"),
                            ft.Container(
                                content=ft.Text("4 imprimantes", size=12),
                                bgcolor=ft.colors.GREEN_900,
                                padding=5,
                                border_radius=10,
                            ),
                        ]),
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.GREEN,
                            color=ft.colors.WHITE,
                            padding=20,
                        ),
                        width=300,
                        on_click=lambda e: connect_printer('wifi', e),
                    ),
                ], spacing=20, alignment=ft.MainAxisAlignment.CENTER),
                padding=30,
            ),
            actions=[
                ft.TextButton(
                    "Annuler",
                    icon=ft.icons.CANCEL,
                    on_click=close_printer_dialog,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        if dialog:
            dialog.open = False
        self.page.dialog = printer_dialog
        printer_dialog.open = True
        self.page.update()
