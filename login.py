import flet as ft
from database import Database

class LoginPage(ft.UserControl):
    def __init__(self, page: ft.Page, go_to_main, go_to_signup):
        super().__init__()
        self.page = page
        self.go_to_main = go_to_main
        self.go_to_signup = go_to_signup
        
        # Champs de connexion
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

    def login(self, e):
        username = self.username_field.value
        password = self.password_field.value
        
        if not username or not password:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Veuillez remplir tous les champs"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
            
        try:
            db = Database()
            user = db.get_user(username, password)
            db.close()
            
            if user:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("✅ Connexion réussie"),
                        bgcolor=ft.colors.GREEN_400
                    )
                )
                self.go_to_main()
            else:
                self.page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text("❌ Nom d'utilisateur ou mot de passe incorrect"),
                        bgcolor=ft.colors.RED_400
                    )
                )
        except Exception as e:
            self.page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text(f"❌ Erreur de connexion: {str(e)}"),
                    bgcolor=ft.colors.RED_400
                )
            )

    def build(self):
        return ft.Container(
            content=ft.Column([
                # Logo ou Titre
                ft.Icon(
                    ft.icons.LOCAL_SHIPPING,
                    size=64,
                    color=ft.colors.BLUE_700,
                ),
                ft.Text(
                    "Connexion",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.colors.BLUE_700
                ),
                
                # Champs de saisie
                self.username_field,
                self.password_field,
                
                # Bouton de connexion
                ft.ElevatedButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.LOGIN),
                            ft.Text("Se connecter", size=16),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    width=200,
                    on_click=self.login,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.BLUE_700,
                        padding=15,
                    )
                ),
                
                # Lien d'inscription
                ft.TextButton(
                    content=ft.Row(
                        [
                            ft.Icon(ft.icons.PERSON_ADD, color=ft.colors.BLUE_700),
                            ft.Text("Pas de compte? S'inscrire", color=ft.colors.BLUE_700),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    on_click=lambda _: self.go_to_signup()
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20),
            alignment=ft.alignment.center,
            padding=50,
            bgcolor=ft.colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.colors.BLUE_GREY_100,
                offset=ft.Offset(0, 0),
            ),
        )
