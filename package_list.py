import flet as ft
from database import Database
from datetime import datetime
import qrcode
from io import BytesIO
import base64
import time

class PackageListPage(ft.UserControl):
    def __init__(self, page: ft.Page, go_to_main):
        super().__init__()
        self.page = page
        self.go_to_main = go_to_main
        self.packages = []
        self.selected_package = None
        self.details_dialog = None
        self.search_field = ft.TextField(
            hint_text="Rechercher...",
            prefix_icon=ft.icons.SEARCH,
            border_radius=20,
            content_padding=ft.padding.only(left=10, right=10, top=8, bottom=8),
            width=None,  # Permet l'expansion
            expand=True, # Le champ prendra tout l'espace disponible
            text_size=14,
            height=40,
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
            on_submit=self.do_search,  # Permet la recherche avec la touche Entrée
        )
        self.search_button = ft.IconButton(
            icon=ft.icons.SEARCH,
            icon_color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            icon_size=20,
            tooltip="Rechercher",
            on_click=self.do_search,
        )
        self.refresh_button = ft.IconButton(
            icon=ft.icons.REFRESH_ROUNDED,
            icon_color=ft.colors.BLUE,
            icon_size=24,
            tooltip="Rafraîchir la liste",
            on_click=self.refresh_list,
            rotate=ft.transform.Rotate(0, alignment=ft.alignment.center),
        )
        self.load_packages()
        self.current_device_list = None
        self.current_printer_name = None

    def load_packages(self):
        db = Database()
        try:
            self.packages = db.get_all_records()
        finally:
            db.close()

    def do_search(self, e):
        search_text = self.search_field.value
        if not search_text:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Veuillez entrer un terme de recherche", size=16))
            )
            return
            
        db = Database()
        try:
            results = db.search_records(search_text)
            if not results:
                self.page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Aucun résultat trouvé", size=16))
                )
                return
            self.show_search_results(results)
        finally:
            db.close()

    def show_search_results(self, results):
        def close_dialog(e):
            search_dialog.open = False
            self.page.update()

        # Create content for each result
        result_cards = []
        for package in results:
            result_cards.append(
                ft.Container(
                    content=ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.ListTile(
                                    leading=ft.Icon(
                                        name=ft.icons.INVENTORY_2_ROUNDED,
                                        color=ft.colors.BLUE,
                                        size=24,
                                    ),
                                    title=ft.Text(
                                        f"Colis #{package[0]}", 
                                        weight=ft.FontWeight.BOLD,
                                        size=16,
                                    ),
                                ),
                                ft.Divider(height=1),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Expéditeur:", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                                        ft.Text(f"Nom: {package[1]}", size=14),
                                        ft.Text(f"Ville: {package[2]}", size=14),
                                        ft.Text(f"Téléphone: {package[3]}", size=14),
                                    ], spacing=5),
                                    padding=10,
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Destinataire:", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                                        ft.Text(f"Nom: {package[4]}", size=14),
                                        ft.Text(f"Ville: {package[6]}", size=14),
                                        ft.Text(f"Téléphone: {package[5]}", size=14),
                                    ], spacing=5),
                                    padding=10,
                                ),
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text("Détails:", weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                                        ft.Text(f"Nombre de colis: {package[7]}", size=14),
                                        ft.Text(f"Type: {package[8]}", size=14),
                                        ft.Text(f"Valeur: {package[9]} €", size=14),
                                        ft.Text(f"Poids: {package[10]} Kg", size=14),
                                        ft.Text(f"Prix: {package[11]} €", size=14),
                                        ft.Text(f"Date: {package[12]}", size=14),
                                    ], spacing=5),
                                    padding=10,
                                ),
                            ]),
                            padding=10,
                        ),
                    ),
                    padding=ft.padding.only(bottom=10),
                )
            )

        # Create and show the dialog
        search_dialog = ft.AlertDialog(
            title=ft.Text(
                "Résultats de la recherche",
                size=20,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.BLUE,
            ),
            content=ft.Container(
                content=ft.Column(
                    controls=result_cards,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=10,
                ),
                height=500,
                width=600,
                padding=20,
                border_radius=10,
            ),
            actions=[
                ft.ElevatedButton(
                    "Fermer",
                    icon=ft.icons.CLOSE,
                    on_click=close_dialog,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE,
                        shape=ft.RoundedRectangleBorder(radius=10),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            shape=ft.RoundedRectangleBorder(radius=10),
        )

        self.page.dialog = search_dialog
        search_dialog.open = True
        self.page.update()

    def show_package_details(self, package):
        def close_dialog(e):
            self.details_dialog.open = False
            self.page.update()

        # Générer le QR code
        qr_code_data = self.generate_qr_code(package)
        
        # Créer l'image du QR code
        qr_code_image = ft.Image(
            src_base64=qr_code_data,
            width=200,
            height=200,
            fit=ft.ImageFit.CONTAIN,
        )

        # Create content for the dialog
        content = ft.Column(
            [
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.QR_CODE_2, size=24, color=ft.colors.BLUE),
                            ft.Text("QR Code", size=20, weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Container(
                            content=qr_code_image,
                            alignment=ft.alignment.center,
                            padding=10,
                        ),
                    ]),
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    padding=10,
                ),
                
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.icons.INVENTORY_2_ROUNDED, size=24, color=ft.colors.BLUE),
                            ft.Text(f"Colis #{package[0]}", size=20, weight=ft.FontWeight.BOLD),
                        ]),
                        ft.Divider(height=2, color=ft.colors.BLUE_200),
                        
                        # Expéditeur
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Expéditeur", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                                ft.Row([
                                    ft.Icon(ft.icons.PERSON, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Nom: {package[1]}", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.LOCATION_CITY, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Ville: {package[2]}", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.PHONE, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Téléphone: {package[3]}", size=14),
                                ]),
                            ], spacing=8),
                            padding=10,
                        ),
                        
                        # Destinataire
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Destinataire", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                                ft.Row([
                                    ft.Icon(ft.icons.PERSON, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Nom: {package[4]}", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.LOCATION_CITY, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Ville: {package[6]}", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.PHONE, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Téléphone: {package[5]}", size=14),
                                ]),
                            ], spacing=8),
                            padding=10,
                        ),
                        
                        # Informations du Colis
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Informations du Colis", size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE),
                                ft.Row([
                                    ft.Icon(ft.icons.INVENTORY_2_ROUNDED, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Nombre de colis: {package[7]}", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.CATEGORY, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Type: {package[8]}", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.PAYMENTS, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Valeur: {package[9]} €", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.SCALE, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Poids: {package[10]} Kg", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.PRICE_CHECK, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Prix: {package[11]} €", size=14),
                                ]),
                                ft.Row([
                                    ft.Icon(ft.icons.CALENDAR_TODAY, size=16, color=ft.colors.BLUE_GREY),
                                    ft.Text(f"Date: {package[12]}", size=14),
                                ]),
                            ], spacing=8),
                            padding=10,
                        ),
                    ]),
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    padding=10,
                ),
                
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Fermer",
                            icon=ft.icons.CLOSE,
                            on_click=close_dialog,
                            style=ft.ButtonStyle(
                                bgcolor=ft.colors.BLUE,
                                color=ft.colors.WHITE,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        )
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            height=500,
        )

        # Create and show the dialog
        self.details_dialog = ft.AlertDialog(
            content=ft.Container(
                content=content,
                padding=20,
                width=400,
            ),
            shape=ft.RoundedRectangleBorder(radius=10),
        )
        self.page.dialog = self.details_dialog
        self.details_dialog.open = True
        self.page.update()

    def generate_qr_code(self, package):
        # Créer le contenu du QR code
        data = f"""
        COLIS #{package[0]}
        
        EXPÉDITEUR:
        Nom: {package[1]}
        Ville: {package[2]}
        Tél: {package[3]}
        
        DESTINATAIRE:
        Nom: {package[4]}
        Ville: {package[6]}
        Tél: {package[5]}
        
        DÉTAILS COLIS:
        Nombre: {package[7]}
        Type: {package[8]}
        Valeur: {package[9]} €
        Poids: {package[10]} Kg
        Prix: {package[11]} €
        Date: {package[12]}
        """
        
        # Générer le QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir l'image en base64
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return img_str

    def build_list_item(self, package):
        # Get modification count
        db = Database()
        try:
            mods = db.get_record_modifications(package[0])
            mod_count = len(mods)
        finally:
            db.close()

        def delete_package(e):
            def confirm_delete(e):
                if e.control.text == "Oui":
                    db = Database()
                    try:
                        if db.delete_record(package[0]):
                            self.page.show_snack_bar(
                                ft.SnackBar(
                                    content=ft.Text("✅ Colis supprimé avec succès"),
                                    bgcolor=ft.colors.GREEN_400
                                )
                            )
                            self.load_packages()  # Recharger la liste
                        else:
                            self.page.show_snack_bar(
                                ft.SnackBar(
                                    content=ft.Text("❌ Erreur lors de la suppression"),
                                    bgcolor=ft.colors.RED_400
                                )
                            )
                    finally:
                        db.close()
                confirm_dialog.open = False
                self.page.update()

            confirm_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Confirmer la suppression"),
                content=ft.Text(f"Voulez-vous vraiment supprimer le colis #{package[0]} ?"),
                actions=[
                    ft.TextButton("Non", on_click=confirm_delete),
                    ft.TextButton(
                        "Oui",
                        on_click=confirm_delete,
                        style=ft.ButtonStyle(color=ft.colors.RED_400)
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.dialog = confirm_dialog
            confirm_dialog.open = True
            self.page.update()

        return ft.Card(
            content=ft.Container(
                content=ft.Column([
                    # Header with package ID and status
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.icons.INVENTORY_2_ROUNDED, color=ft.colors.BLUE, size=20),
                            ft.Text(f"Colis #{package[0]}", weight=ft.FontWeight.BOLD, size=16),
                            ft.Container(
                                content=ft.Text(
                                    f"{mod_count} modif.",
                                    color=ft.colors.WHITE,
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                bgcolor=ft.colors.BLUE if mod_count > 0 else ft.colors.GREY_400,
                                border_radius=8,
                                padding=ft.padding.only(left=6, right=6, top=3, bottom=3),
                            )
                        ], alignment=ft.MainAxisAlignment.START),
                        padding=8,
                        bgcolor=ft.colors.BLUE_50,
                        border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    ),
                    
                    # Main content with shipping details
                    ft.Container(
                        content=ft.Column([
                            # Sender info
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("EXPÉDITEUR", weight=ft.FontWeight.BOLD, 
                                        color=ft.colors.BLUE_GREY, size=12),
                                    ft.Text(package[1], weight=ft.FontWeight.W_500, size=14),
                                    ft.Row([
                                        ft.Icon(ft.icons.LOCATION_CITY, size=14, color=ft.colors.BLUE_GREY),
                                        ft.Text(f"{package[2]}", size=13),
                                    ], spacing=5),
                                    ft.Row([
                                        ft.Icon(ft.icons.PHONE, size=14, color=ft.colors.BLUE_GREY),
                                        ft.Text(f"{package[3]}", size=13),
                                    ], spacing=5),
                                ], spacing=4),
                                padding=ft.padding.only(bottom=8),
                            ),
                            
                            ft.Divider(height=1, color=ft.colors.BLUE_GREY_100),
                            
                            # Recipient info
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("DESTINATAIRE", weight=ft.FontWeight.BOLD, 
                                        color=ft.colors.BLUE_GREY, size=12),
                                    ft.Text(package[4], weight=ft.FontWeight.W_500, size=14),
                                    ft.Row([
                                        ft.Icon(ft.icons.LOCATION_CITY, size=14, color=ft.colors.BLUE_GREY),
                                        ft.Text(f"{package[6]}", size=13),
                                    ], spacing=5),
                                    ft.Row([
                                        ft.Icon(ft.icons.PHONE, size=14, color=ft.colors.BLUE_GREY),
                                        ft.Text(f"{package[5]}", size=13),
                                    ], spacing=5),
                                ], spacing=4),
                                padding=ft.padding.only(top=8, bottom=8),
                            ),
                            
                            ft.Divider(height=1, color=ft.colors.BLUE_GREY_100),
                            
                            # Package details
                            ft.Container(
                                content=ft.Column([
                                    ft.Text("DÉTAILS COLIS", weight=ft.FontWeight.BOLD, 
                                        color=ft.colors.BLUE_GREY, size=12),
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.INVENTORY_2_ROUNDED, size=14, color=ft.colors.BLUE_GREY),
                                                ft.Text(f"{package[7]} colis", size=13),
                                            ], spacing=4),
                                            expand=True,
                                        ),
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.CATEGORY, size=14, color=ft.colors.BLUE_GREY),
                                                ft.Text(f"{package[8]}", size=13),
                                            ], spacing=4),
                                            expand=True,
                                        ),
                                    ], spacing=10),
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.PAYMENTS, size=14, color=ft.colors.BLUE_GREY),
                                                ft.Text(f"{package[9]} €", size=13),
                                            ], spacing=4),
                                            expand=True,
                                        ),
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.SCALE, size=14, color=ft.colors.BLUE_GREY),
                                                ft.Text(f"{package[10]} Kg", size=13),
                                            ], spacing=4),
                                            expand=True,
                                        ),
                                    ], spacing=10),
                                    ft.Row([
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.PRICE_CHECK, size=14, color=ft.colors.BLUE_GREY),
                                                ft.Text(f"Prix: {package[11]} €", size=13),
                                            ], spacing=4),
                                            expand=True,
                                        ),
                                        ft.Container(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.CALENDAR_TODAY, size=14, color=ft.colors.BLUE_GREY),
                                                ft.Text(f"{package[12]}", size=13),
                                            ], spacing=4),
                                            expand=True,
                                        ),
                                    ], spacing=10),
                                ], spacing=8),
                                padding=ft.padding.only(top=8),
                            ),
                        ]),
                        padding=ft.padding.only(left=12, right=12, top=8, bottom=8),
                    ),
                    
                    # Action buttons
                    ft.Container(
                        content=ft.Row([
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_color=ft.colors.BLUE,
                                icon_size=20,
                                tooltip="Modifier",
                                on_click=lambda e, pkg=package: self.show_edit_dialog(pkg),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ft.colors.RED_400,
                                tooltip="Supprimer",
                                on_click=lambda e, pkg=package: delete_package(e),
                            ),
                            ft.IconButton(
                                icon=ft.icons.PRINT,
                                icon_color=ft.colors.BLUE,
                                icon_size=20,
                                tooltip="Imprimer",
                                on_click=lambda e, pkg=package: self.print_package(pkg),
                            ),
                        ], alignment=ft.MainAxisAlignment.END),
                        padding=ft.padding.only(right=8, bottom=4),
                    ),
                ]),
                border_radius=10,
            ),
            elevation=2,
        )

    def print_package(self, package):
        def show_print_dialog():
            def close_dialog(e):
                print_dialog.open = False
                self.page.update()

            def show_preview():
                try:
                    def start_print_process():
                        def show_connection_dialog():
                            # Dialogue de sélection de la méthode de connexion
                            connection_dialog = ft.AlertDialog(
                                modal=True,
                                title=ft.Text("Sélectionner le type de connexion"),
                                content=ft.Container(
                                    content=ft.Column([
                                        ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.BLUETOOTH, color=ft.colors.WHITE),
                                                ft.Text("Bluetooth"),
                                                ft.Container(
                                                    content=ft.Text("4 appareils", size=12),
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
                                            on_click=lambda e: self.search_devices('bluetooth'),
                                        ),
                                        ft.ElevatedButton(
                                            content=ft.Row([
                                                ft.Icon(ft.icons.WIFI_TETHERING, color=ft.colors.WHITE),
                                                ft.Text("WiFi Direct"),
                                                ft.Container(
                                                    content=ft.Text("3 appareils", size=12),
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
                                            on_click=lambda e: self.search_devices('wifi-direct'),
                                        ),
                                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                                    padding=30,
                                ),
                            )

                            def search_devices(connection_type):
                                # Animation de recherche
                                searching_dialog = ft.AlertDialog(
                                    modal=True,
                                    title=ft.Text(f"Recherche d'imprimantes {connection_type}"),
                                    content=ft.Column([
                                        ft.ProgressRing(width=40, height=40, stroke_width=3, color=ft.colors.BLUE),
                                        ft.Text(f"Recherche des périphériques {connection_type}..."),
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

                                # Liste des périphériques
                                devices = {
                                    'wifi-direct': [
                                        (
                                            "HP LaserJet Pro MFP M283dw", 
                                            "DIRECT-72-HP M283dw",
                                            "Excellent (100%)", 
                                            "Disponible",
                                            "Impression & Scan WiFi Direct, Recto-verso automatique"
                                        ),
                                        ("HP OfficeJet Pro 9020", "192.168.1.100", "Excellent (100%)", "Disponible", "Impression WiFi Direct"),
                                        ("Brother MFC-L3770CDW", "192.168.1.101", "Très bon (85%)", "Disponible", "Impression & Scan WiFi Direct"),
                                        ("Canon PIXMA TR8620", "192.168.1.102", "Bon (75%)", "Disponible", "Impression WiFi Direct"),
                                        ("Epson WorkForce Pro", "192.168.1.103", "Faible (45%)", "Hors ligne", "Non disponible"),
                                    ],
                                    'bluetooth': [
                                        ("HP LaserJet Pro", "20:FA:BB:02:00:01", "100%", "Disponible", ""),
                                        ("Canon PIXMA", "20:FA:BB:02:00:02", "85%", "Disponible", ""),
                                        ("Epson EcoTank", "20:FA:BB:02:00:03", "75%", "Occupée", ""),
                                    ]
                                }

                                # Créer et afficher le dialogue des périphériques
                                device_list = self.create_device_list_dialog(devices, connection_type)
                                self.current_device_list = device_list
                                self.page.dialog = device_list
                                device_list.open = True
                                self.page.update()

                            def connect_device(device_name, connection_type):
                                try:
                                    if self.current_device_list:
                                        self.current_device_list.open = False
                                        self.page.update()

                                    self.current_printer_name = device_name
                                    self.show_connection_dialog(device_name, connection_type)

                                except Exception as ex:
                                    self.show_error("Erreur de connexion", ex)

                            def show_connection_dialog(self, device_name, connection_type):
                                # Créer le dialogue de connexion
                                config_dialog = self.create_config_dialog(device_name, connection_type)
                                self.page.dialog = config_dialog
                                config_dialog.open = True
                                self.page.update()

                            def confirm_and_print(self, config_dialog, device_name):
                                try:
                                    # Mettre à jour le statut
                                    config_dialog.content.controls[1].value = "Statut: Connecté"
                                    config_dialog.content.controls[1].color = ft.colors.GREEN
                                    config_dialog.content.controls[-2].visible = False
                                    config_dialog.content.controls[-1].value = "Connexion établie"
                                    self.page.update()

                                    time.sleep(1)
                                    config_dialog.open = False
                                    self.page.update()

                                    # Démarrer l'impression
                                    self.start_printing(device_name)

                                except Exception as ex:
                                    self.show_error("Erreur d'impression", ex)

                            def show_error(self, message, ex):
                                self.page.show_snack_bar(
                                    ft.SnackBar(
                                        content=ft.Text(f"❌ {message}: {str(ex)}"),
                                        bgcolor=ft.colors.RED_400,
                                    )
                                )
                                self.page.update()

                            self.page.dialog = connection_dialog
                            connection_dialog.open = True
                            self.page.update()

                        show_connection_dialog()

                    # Générer le QR code pour l'aperçu
                    qr_code_data = self.generate_qr_code(package)
                    if not qr_code_data:
                        raise Exception("Erreur de génération du QR code")

                    # Créer l'image avec le QR code encodé en base64
                    qr_code_image = ft.Image(
                        src_base64=qr_code_data,
                        width=150,
                        height=150,
                        fit=ft.ImageFit.CONTAIN,
                    )

                    # Container pour le QR code
                    qr_container = ft.Container(
                        content=ft.Column([
                            ft.Text(
                                "QR Code de traçabilité",
                                weight=ft.FontWeight.BOLD,
                                color=ft.colors.BLUE,
                                size=16,
                                text_align=ft.TextAlign.CENTER
                            ),
                            qr_code_image,
                            ft.Text(
                                f"Code de suivi: TR{package[0]:06d}",
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                text_align=ft.TextAlign.CENTER
                            ),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        padding=10,
                        border=ft.border.all(1, ft.colors.BLUE_200),
                        border_radius=10,
                    )

                    # Créer la boîte de dialogue d'aperçu
                    preview_dialog = ft.AlertDialog(
                        modal=True,
                        title=ft.Text("Aperçu d'impression", weight=ft.FontWeight.BOLD),
                        content=ft.Container(
                            content=ft.Column([
                                # En-tête avec logo et titre
                                ft.Row([
                                    ft.Icon(ft.icons.LOCAL_SHIPPING, size=30, color=ft.colors.BLUE),
                                    ft.Text("BORDEREAU D'EXPEDITION", 
                                           size=20, 
                                           weight=ft.FontWeight.BOLD,
                                           color=ft.colors.BLUE),
                                ], alignment=ft.MainAxisAlignment.CENTER),
                                
                                # QR Code
                                qr_container,

                                # Informations détaillées
                                ft.Container(
                                    content=ft.Column([
                                        ft.Text(f"BORDEREAU D'EXPEDITION #{package[0]}", 
                                               size=16, 
                                               weight=ft.FontWeight.BOLD),
                                        ft.Divider(height=1, color=ft.colors.BLUE_200),
                                        
                                        # Expéditeur
                                        ft.Text("EXPEDITEUR", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Nom: {package[1]}"),
                                        ft.Text(f"Ville: {package[2]}"),
                                        ft.Text(f"Téléphone: {package[3]}"),
                                        ft.Divider(height=1),
                                        
                                        # Destinataire
                                        ft.Text("DESTINATAIRE", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Nom: {package[4]}"),
                                        ft.Text(f"Ville: {package[6]}"),
                                        ft.Text(f"Téléphone: {package[5]}"),
                                        ft.Divider(height=1),
                                        
                                        # Détails du colis
                                        ft.Text("DETAILS DU COLIS", weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Nombre de colis: {package[7]}"),
                                        ft.Text(f"Type: {package[8]}"),
                                        ft.Text(f"Valeur: {package[9]} €"),
                                        ft.Text(f"Poids: {package[10]} Kg"),
                                        ft.Text(f"Prix: {package[11]} €"),
                                        ft.Text(f"Date d'expédition: {package[12]}"),
                                    ]),
                                    padding=20,
                                    border=ft.border.all(1, ft.colors.GREY_400),
                                    border_radius=10,
                                ),
                            ], scroll=ft.ScrollMode.AUTO),
                            width=400,
                            height=600,
                            padding=20,
                            border=ft.border.all(1, ft.colors.GREY_400),
                            border_radius=10,
                        ),
                        actions=[
                            ft.TextButton("Fermer", on_click=lambda e: close_preview(preview_dialog)),
                            ft.ElevatedButton(
                                "Imprimer",
                                icon=ft.icons.PRINT,
                                on_click=lambda e: start_print_process(),
                                style=ft.ButtonStyle(
                                    color=ft.colors.WHITE,
                                    bgcolor=ft.colors.BLUE,
                                ),
                            ),
                        ],
                        actions_alignment=ft.MainAxisAlignment.END,
                    )

                    def close_preview(dialog):
                        dialog.open = False
                        self.page.update()

                    print_dialog.open = False
                    self.page.dialog = preview_dialog
                    preview_dialog.open = True
                    self.page.update()

                except Exception as ex:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"❌ Erreur d'aperçu: {str(ex)}"),
                            bgcolor=ft.colors.RED_400,
                        )
                    )

            # Dialogue principal d'impression
            print_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(f"Imprimer le colis #{package[0]}"),
                content=ft.Container(
                    content=ft.Column([
                        ft.Icon(ft.icons.PRINT, size=50, color=ft.colors.BLUE),
                        ft.Text(
                            "Aperçu avant impression",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.ElevatedButton(
                            content=ft.Row([
                                ft.Icon(ft.icons.PREVIEW),
                                ft.Text("Voir l'aperçu"),
                            ]),
                            on_click=lambda e: show_preview(),
                        ),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
                    padding=30,
                ),
                actions=[
                    ft.TextButton(
                        "Annuler",
                        icon=ft.icons.CANCEL,
                        on_click=close_dialog,
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            self.page.dialog = print_dialog
            print_dialog.open = True
            self.page.update()

        show_print_dialog()

    def do_print(self, content, dialog):
        # TODO: Implement actual printing
        self.page.show_snack_bar(
            ft.SnackBar(content=ft.Text("Impression en cours...", size=16))
        )
        dialog.open = False
        self.page.update()

    def delete_package(self, package):
        def confirm_delete(e):
            db = Database()
            try:
                if db.delete_record(package[0]):
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Colis supprimé avec succès!", size=16))
                    )
                    self.load_packages()
                else:
                    self.page.show_snack_bar(
                        ft.SnackBar(content=ft.Text("Erreur lors de la suppression", size=16))
                    )
            finally:
                db.close()
            confirm_dialog.open = False
            self.page.update()

        def cancel_delete(e):
            confirm_dialog.open = False
            self.page.update()

        confirm_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmer la suppression"),
            content=ft.Column([
                ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.RED_400, size=50),
                ft.Text(f"Voulez-vous vraiment supprimer le colis #{package[0]}?"),
                ft.Text("Cette action est irréversible.", color=ft.colors.RED_400, size=12),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=cancel_delete,
                ),
                ft.ElevatedButton(
                    "Supprimer",
                    color=ft.colors.WHITE,
                    bgcolor=ft.colors.RED_400,
                    icon=ft.icons.DELETE_FOREVER,
                    on_click=confirm_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = confirm_dialog
        confirm_dialog.open = True
        self.page.update()

    def show_edit_dialog(self, package):
        def close_dialog(e):
            edit_dialog.open = False
            self.page.update()

        def save_changes(e):
            # Collecter les données du formulaire
            data = {
                'name_exp': name_exp.value,
                'city_exp': city_exp.value,
                'phone_exp': phone_exp.value,
                'name_dest': name_dest.value,
                'city_dest': city_dest.value,
                'phone_dest': phone_dest.value,
                'nmbr_package': nmbr_package.value,
                'gender_package': gender_package.value,
                'value_package': value_package.value,
                'kilos': kilos.value,
                'price': price.value,
            }

            # Mettre à jour dans la base de données
            db = Database()
            try:
                success, message = db.modify_record(package[0], data)
                if success:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("✅ " + message),
                            bgcolor=ft.colors.GREEN_400
                        )
                    )
                    close_dialog(e)
                    self.load_packages()  # Recharger la liste
                else:
                    self.page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("❌ " + message),
                            bgcolor=ft.colors.RED_400
                        )
                    )
            except Exception as ex:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Erreur: {str(ex)}"),
                        bgcolor=ft.colors.RED_400
                    )
                )
            finally:
                db.close()

        # Créer les champs du formulaire avec les valeurs actuelles
        name_exp = ft.TextField(
            label="Nom Expéditeur",
            value=package[1],
            border_radius=10,
            width=350,
        )
        city_exp = ft.TextField(
            label="Ville Expéditeur",
            value=package[2],
            border_radius=10,
            width=350,
        )
        phone_exp = ft.TextField(
            label="Téléphone Expéditeur",
            value=package[3],
            border_radius=10,
            width=350,
        )
        name_dest = ft.TextField(
            label="Nom Destinataire",
            value=package[4],
            border_radius=10,
            width=350,
        )
        city_dest = ft.TextField(
            label="Ville Destinataire",
            value=package[6],
            border_radius=10,
            width=350,
        )
        phone_dest = ft.TextField(
            label="Téléphone Destinataire",
            value=package[5],
            border_radius=10,
            width=350,
        )
        nmbr_package = ft.TextField(
            label="Nombre de colis",
            value=str(package[7]),
            border_radius=10,
            width=350,
        )
        gender_package = ft.TextField(
            label="Type de colis",
            value=package[8],
            border_radius=10,
            width=350,
        )
        value_package = ft.TextField(
            label="Valeur",
            value=str(package[9]),
            border_radius=10,
            width=350,
        )
        kilos = ft.TextField(
            label="Poids (Kg)",
            value=str(package[10]),
            border_radius=10,
            width=350,
        )
        price = ft.TextField(
            label="Prix",
            value=str(package[11]),
            border_radius=10,
            width=350,
        )

        edit_dialog = ft.AlertDialog(
            title=ft.Text(f"Modifier Colis #{package[0]}", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column([
                    name_exp,
                    city_exp,
                    phone_exp,
                    name_dest,
                    city_dest,
                    phone_dest,
                    nmbr_package,
                    gender_package,
                    value_package,
                    kilos,
                    price,
                ], scroll=ft.ScrollMode.AUTO),
                height=400,
                width=400,
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                ft.ElevatedButton(
                    "Enregistrer",
                    on_click=save_changes,
                    bgcolor=ft.colors.BLUE,
                    color=ft.colors.WHITE,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self.page.dialog = edit_dialog
        edit_dialog.open = True
        self.page.update()

    def show_history(self, package):
        db = Database()
        try:
            mods = db.get_record_modifications(package[0])
            if mods:
                content = "\n".join([
                    f"• {action} le {date}" 
                    for action, date in mods
                ])
            else:
                content = "Aucune modification"

            history_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    f"Historique des modifications - Colis #{package[0]}", 
                    size=16, 
                    weight=ft.FontWeight.BOLD
                ),
                content=ft.Text(content),
                actions=[
                    ft.TextButton("Fermer", on_click=lambda e: close_history(history_dialog))
                ],
            )
            self.page.dialog = history_dialog
            history_dialog.open = True
            self.page.update()
        finally:
            db.close()

        def close_history(dialog):
            dialog.open = False
            self.page.update()

    def refresh_list(self, e):
        # Animer le bouton de rafraîchissement
        self.refresh_button.rotate.angle += 360
        self.refresh_button.update()
        
        try:
            # Recharger les données
            self.load_packages()
            
            # Mettre à jour l'interface
            self.update()
            
            # Afficher un message de succès
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("✅ Liste mise à jour"),
                    bgcolor=ft.colors.GREEN_400,
                    action="OK",
                )
            )
        except Exception as ex:
            # En cas d'erreur
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"❌ Erreur lors du rafraîchissement: {str(ex)}"),
                    bgcolor=ft.colors.RED_400,
                    action="OK",
                )
            )
        finally:
            # Réinitialiser la rotation du bouton
            self.refresh_button.rotate.angle = 0
            self.refresh_button.update()

    def build(self):
        return ft.Container(
            content=ft.Column([
                # Header with title and buttons
                ft.Container(
                    content=ft.Column([
                        ft.Row(
                            [
                                ft.Text("Liste des Colis", 
                                      size=24, 
                                      weight=ft.FontWeight.BOLD, 
                                      color=ft.colors.BLUE),
                                ft.Row(
                                    [
                                        self.refresh_button,  # Bouton de rafraîchissement
                                        ft.IconButton(
                                            icon=ft.icons.ARROW_BACK_ROUNDED,
                                            icon_color=ft.colors.BLUE,
                                            icon_size=24,
                                            tooltip="Retour",
                                            on_click=self.go_to_main
                                        ),
                                    ]
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        # Search row with input and button
                        ft.Row(
                            [
                                ft.Container(
                                    content=self.search_field,
                                    expand=True,
                                ),
                                self.search_button,
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=8,
                        ),
                    ], spacing=16),
                    padding=10,
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.BLUE_GREY_100,
                    ),
                ),

                # List container with scrolling
                ft.Container(
                    content=ft.Column(
                        [
                            ft.ListView(
                                controls=[self.build_list_item(package) for package in self.packages],
                                spacing=8,
                                padding=10,
                                expand=1,
                                auto_scroll=True,
                                height=500,
                            )
                        ],
                        scroll=ft.ScrollMode.ALWAYS,
                        expand=True,
                        spacing=8,
                    ),
                    bgcolor=ft.colors.WHITE,
                    border_radius=10,
                    padding=8,
                    expand=True,
                    shadow=ft.BoxShadow(
                        spread_radius=1,
                        blur_radius=15,
                        color=ft.colors.BLUE_GREY_100,
                    ),
                ),
            ],
            expand=True,
            spacing=16,
            ),
            padding=10,
            expand=True,
            bgcolor=ft.colors.BLUE_50,
        )

    def start_printing(self, device_name):
        try:
            # Animation de préparation de l'impression
            printing_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("Impression en cours"),
                content=ft.Column([
                    ft.Text(f"Imprimante: {device_name}"),
                    ft.ProgressBar(width=400, color=ft.colors.BLUE),
                    ft.Text("Préparation du document...", color=ft.colors.GREY_700),
                ], spacing=20),
            )

            self.page.dialog = printing_dialog
            printing_dialog.open = True
            self.page.update()

            # Étapes détaillées de l'impression
            steps = [
                ("Préparation...", "Configuration de l'imprimante"),
                ("Formatage...", "Mise en page du bordereau"),
                ("Envoi...", "Transmission vers l'imprimante"),
                ("Impression...", "Impression du bordereau"),
                ("QR Code...", "Impression du QR code"),
                ("Finalisation...", "Vérification de la qualité"),
            ]

            for i, (step, detail) in enumerate(steps):
                time.sleep(0.8)
                printing_dialog.content.controls[1].value = (i + 1) / len(steps)
                printing_dialog.content.controls[2].value = f"{step}\n{detail}"
                self.page.update()

            # Simuler l'impression terminée
            time.sleep(1)
            printing_dialog.open = False

            # Message de succès
            success_dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text("✅ Impression terminée"),
                content=ft.Column([
                    ft.Icon(ft.icons.CHECK_CIRCLE_OUTLINE, 
                           size=50, 
                           color=ft.colors.GREEN),
                    ft.Text(
                        "Le bordereau a été imprimé avec succès",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        f"Imprimante: {device_name}",
                        size=14,
                        color=ft.colors.GREY_700,
                    ),
                    ft.Divider(height=1, color=ft.colors.BLUE_200),
                    ft.Text(
                        "Vérifiez que le bordereau et le QR code sont bien lisibles",
                        size=12,
                        color=ft.colors.BLUE,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                actions=[
                    ft.TextButton(
                        "Fermer",
                        on_click=lambda e: close_success(),
                    ),
                    ft.ElevatedButton(
                        "Réimprimer",
                        icon=ft.icons.PRINT,
                        on_click=lambda e: self.start_printing(device_name),
                        style=ft.ButtonStyle(
                            color=ft.colors.WHITE,
                            bgcolor=ft.colors.BLUE,
                        ),
                    ),
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )

            def close_success():
                success_dialog.open = False
                self.page.update()

            self.page.dialog = success_dialog
            success_dialog.open = True
            self.page.update()

        except Exception as ex:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"❌ Erreur d'impression: {str(ex)}"),
                    bgcolor=ft.colors.RED_400,
                )
            )
            self.page.update()

    def create_device_list_dialog(self, devices, connection_type):
        return ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Imprimantes {connection_type} disponibles"),
            content=self.create_device_list_content(devices, connection_type),
            actions=[
                ft.TextButton(
                    "Actualiser",
                    icon=ft.icons.REFRESH,
                    on_click=lambda e: self.search_devices(connection_type),
                ),
                ft.TextButton(
                    "Annuler",
                    icon=ft.icons.CANCEL,
                    on_click=lambda e: self.close_device_list(),
                ),
            ],
        )

    def create_config_dialog(self, device_name, connection_type):
        # Configuration spécifique pour le M283dw
        if "M283dw" in device_name:
            config_value = self.get_m283dw_config()
            config_message = self.get_m283dw_instructions()
        else:
            config_value = f"SSID: {device_name}\nMot de passe: 12345678\nIP: 192.168.1.100"
            config_message = "Connectez-vous au réseau WiFi Direct de l'imprimante"

        return ft.AlertDialog(
            modal=True,
            title=ft.Text("Configuration WiFi Direct HP"),
            content=self.create_config_content(device_name, config_value, config_message),
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: self.close_config(),
                ),
                ft.ElevatedButton(
                    "Imprimer",
                    icon=ft.icons.PRINT,
                    on_click=lambda e: self.confirm_and_print(device_name),
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.GREEN,
                    ),
                ),
            ],
        )

    def search_devices(self, connection_type):
        # Animation de recherche
        searching_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Recherche d'imprimantes {connection_type}"),
            content=ft.Column([
                ft.ProgressRing(width=40, height=40, stroke_width=3, color=ft.colors.BLUE),
                ft.Text(f"Recherche des périphériques {connection_type}..."),
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

        # Liste des périphériques
        devices = {
            'wifi-direct': [
                (
                    "HP LaserJet Pro MFP M283dw", 
                    "DIRECT-72-HP M283dw",
                    "Excellent (100%)", 
                    "Disponible",
                    "Impression & Scan WiFi Direct, Recto-verso automatique"
                ),
                ("HP OfficeJet Pro 9020", "192.168.1.100", "Excellent (100%)", "Disponible", "Impression WiFi Direct"),
                ("Brother MFC-L3770CDW", "192.168.1.101", "Très bon (85%)", "Disponible", "Impression & Scan WiFi Direct"),
                ("Canon PIXMA TR8620", "192.168.1.102", "Bon (75%)", "Disponible", "Impression WiFi Direct"),
                ("Epson WorkForce Pro", "192.168.1.103", "Faible (45%)", "Hors ligne", "Non disponible"),
            ],
            'bluetooth': [
                ("HP LaserJet Pro", "20:FA:BB:02:00:01", "100%", "Disponible", ""),
                ("Canon PIXMA", "20:FA:BB:02:00:02", "85%", "Disponible", ""),
                ("Epson EcoTank", "20:FA:BB:02:00:03", "75%", "Occupée", ""),
            ]
        }

        # Créer et afficher le dialogue des périphériques
        device_list = self.create_device_list_dialog(devices, connection_type)
        self.current_device_list = device_list
        self.page.dialog = device_list
        device_list.open = True
        self.page.update()

    def create_device_list_content(self, devices, connection_type):
        return ft.Column([
            ft.ListTile(
                leading=ft.Icon(
                    ft.icons.WIFI_TETHERING if connection_type == 'wifi-direct'
                    else ft.icons.BLUETOOTH,
                    color=ft.colors.BLUE if status == "Disponible"
                          else ft.colors.GREY_400,
                    size=24,
                ),
                title=ft.Text(
                    name,
                    weight=ft.FontWeight.BOLD if status == "Disponible" else None
                ),
                subtitle=ft.Column([
                    ft.Text(address),
                    ft.Text(
                        f"Signal: {signal}",
                        color=ft.colors.GREY_700,
                        size=12,
                    ),
                    ft.Text(
                        extra[0] if connection_type == 'wifi-direct' and extra else "",
                        color=ft.colors.BLUE,
                        size=11,
                    ) if connection_type == 'wifi-direct' else ft.Container(),
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
                on_click=lambda e, name=name: self.connect_device(name, connection_type) 
                    if status == "Disponible" else None,
            ) for name, address, signal, status, *extra in devices[connection_type]
        ], scroll=ft.ScrollMode.AUTO)

    def get_m283dw_config(self):
        return (
            "1. Sur l'écran de l'imprimante, appuyez sur le bouton WiFi Direct\n"
            "2. SSID: DIRECT-72-HP M283dw\n"
            "3. Mot de passe WPA2: 12345678\n"
            "4. IP: 192.168.223.1\n"
            "5. Port: 9100"
        )

    def get_m283dw_instructions(self):
        return (
            "1. Connectez votre appareil au réseau WiFi Direct de l'imprimante\n"
            "2. Appuyez sur le bouton OK sur l'écran de l'imprimante pour accepter la connexion"
        )

    def close_device_list(self):
        if self.current_device_list:
            self.current_device_list.open = False
            self.page.dialog = None
            self.page.update()
