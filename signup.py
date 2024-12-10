import flet as ft
from database import Database

class SignUpPage(ft.UserControl):
    def __init__(self, page: ft.Page, go_to_login):
        super().__init__()
        self.page = page
        self.go_to_login = go_to_login
        
        # Champs d'inscription
        self.username_field = ft.TextField(
            label="Nom d'utilisateur",
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.PERSON,
            hint_text="Entrez votre nom d'utilisateur",
            helper_text="Champ obligatoire",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )
        
        self.password_field = ft.TextField(
            label="Mot de passe",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.LOCK,
            hint_text="Entrez votre mot de passe",
            helper_text="Minimum 6 caractères",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )

        self.verify_password_field = ft.TextField(
            label="Confirmer le mot de passe",
            password=True,
            can_reveal_password=True,
            border_radius=10,
            width=350,
            prefix_icon=ft.icons.LOCK_CLOCK,
            hint_text="Confirmez votre mot de passe",
            helper_text="Doit être identique au mot de passe",
            border_color=ft.colors.BLUE,
            focused_border_color=ft.colors.BLUE,
            focused_bgcolor=ft.colors.BLUE_50,
        )

    def signup(self, e):
        username = self.username_field.value
        password = self.password_field.value
        verify_password = self.verify_password_field.value
        
        # Validation des champs
        if not all([username, password, verify_password]):
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Veuillez remplir tous les champs"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
            
        # Vérification de la longueur du mot de passe
        if len(password) < 6:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Le mot de passe doit contenir au moins 6 caractères"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
            
        # Vérification de la correspondance des mots de passe
        if password != verify_password:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Les mots de passe ne correspondent pas"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
            
        try:
            db = Database()
            db.insert_user(username, password, "")  # Phone field vide
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Compte créé avec succès"),
                    bgcolor=ft.colors.GREEN_400
                )
            )
            self.go_to_login()
        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(str(e)),
                    bgcolor=ft.colors.RED_400
                )
            )
        finally:
            db.close()

    def build(self):
        return ft.Container(
            content=ft.Column([
                ft.Text(
                    "Inscription",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                ),
                self.username_field,
                self.password_field,
                self.verify_password_field,
                ft.ElevatedButton(
                    "S'inscrire",
                    width=200,
                    on_click=self.signup,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_700,
                    )
                ),
                ft.TextButton(
                    "Déjà un compte? Se connecter",
                    on_click=lambda _: self.go_to_login()
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            alignment=ft.alignment.center
        )
