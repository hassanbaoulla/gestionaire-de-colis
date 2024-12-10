import flet as ft
from login import LoginPage
from signup import SignUpPage
from main import MainPage
from package_list import PackageListPage

class MyApp:  # No need to inherit from UserControl
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "Application de Gestion avec QR Codes"
        self.page.window.height = 740  # Corrected for deprecation
        self.page.window.width = 390  # Corrected for deprecation
         # Configuration de la page
        
        
        
        self.page.window.left = 900
        self.page.window.resizable=False
        #self.page.window.title_bar_hidden=True
        # self.page.scroll = "auto"
        # self.page.vertical_alignment = 'center'
        # self.page.horizontal_alignment = 'center'

        # Initially, show the LoginPage
        self.show_login_page()

    def show_login_page(self, e=None):  # Accept the event parameter
        self.page.views.clear()
        self.page.views.append(LoginPage(self.page, self.show_main_page, self.show_signup_page))
        self.page.update()

    def show_signup_page(self, e=None):  # Accept the event parameter
        self.page.views.clear()
        self.page.views.append(SignUpPage(self.page, self.show_login_page))
        self.page.update()

    def show_main_page(self, e=None):  # Accept the event parameter
        self.page.views.clear()
        self.page.views.append(MainPage(self.page, self.show_login_page, self.show_package_list))
        self.page.update()

    def show_package_list(self, e=None):  # Accept the event parameter
        self.page.views.clear()
        self.page.views.append(PackageListPage(self.page, self.show_main_page))
        self.page.update()


def main(page: ft.Page):
    MyApp(page)  # Initialize the app

if __name__ == "__main__":
    ft.app(target=main)
