import os
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Adw, WebKit, GLib

APP_ID = "com.github.tuusuario.ytmusic_nativo"
COOKIES_FILE = os.path.expanduser("~/.local/share/ytmusic-cookies.txt")


class MusicaNativa(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="YouTube Music")
        self.set_default_size(1200, 800)
        self.app = app

        # 1. El Motor Web
        self.webview = WebKit.WebView()
        self.webview.set_hexpand(True)
        self.webview.set_vexpand(True)

        # Manejo de sesión y cookies (WebKit 6.0)
        self.network_session = WebKit.NetworkSession.get_default()
        cookie_manager = self.network_session.get_cookie_manager()
        cookie_manager.set_persistent_storage(
            COOKIES_FILE, WebKit.CookiePersistentStorage.TEXT
        )
        self.webview.load_uri("https://music.youtube.com")

        # 2. Contenedor principal con barra de título nativa
        self.toolbar_view = Adw.ToolbarView()
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)

        # Botón para cerrar la app de verdad (matar el proceso)
        quit_btn = Gtk.Button(label="Salir")
        quit_btn.add_css_class("destructive-action")
        quit_btn.connect("clicked", self.on_quit_clicked)
        self.header_bar.pack_end(quit_btn)

        self.toolbar_view.set_content(self.webview)
        self.set_content(self.toolbar_view)

        # 3. Interceptar el cierre de la ventana (la 'X')
        self.connect("close-request", self.on_close_request)

    def on_close_request(self, window):
        """Oculta la ventana en segundo plano para que la música siga."""
        self.set_visible(False)
        return True

    def on_quit_clicked(self, button):
        """Cierra la aplicación por completo."""
        self.app.release()
        self.app.quit()


class MiApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID)
        self.window = None

    def do_startup(self):
        Adw.Application.do_startup(self)
        # Mantiene la app viva en memoria aunque la ventana esté oculta
        self.hold()

    def do_activate(self):
        if not self.window:
            self.window = MusicaNativa(self)
        # Asegura que vuelva a ser visible si estaba oculta y la trae al frente
        self.window.set_visible(True)
        self.window.present()


if __name__ == '__main__':
    os.makedirs(os.path.dirname(COOKIES_FILE), exist_ok=True)
    if not os.path.exists(COOKIES_FILE):
        open(COOKIES_FILE, 'a').close()

    GLib.set_prgname(APP_ID)
    GLib.set_application_name("YouTube Music")

    app = MiApp()
    app.run(None)
