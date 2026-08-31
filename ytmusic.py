import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
gi.require_version('WebKit', '6.0')
from gi.repository import Gtk, Adw, WebKit, GLib
import os

# --- Configuración de persistencia (Cookies para login) ---
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
        cookie_manager.set_persistent_storage(COOKIES_FILE, WebKit.CookiePersistentStorage.TEXT)
        self.webview.load_uri("https://music.youtube.com")

        # 2. Contenedor principal con barra de título nativa
        self.toolbar_view = Adw.ToolbarView()
        self.header_bar = Adw.HeaderBar()
        self.toolbar_view.add_top_bar(self.header_bar)
        
        # Botón para cerrar la app de verdad (matar el proceso)
        quit_btn = Gtk.Button(label="Salir")
        quit_btn.add_css_class("destructive-action") # Le da un tono rojo de advertencia
        quit_btn.connect("clicked", self.on_quit_clicked)
        self.header_bar.pack_end(quit_btn)

        # El contenido principal ahora es directamente la web
        self.toolbar_view.set_content(self.webview)
        self.set_content(self.toolbar_view)

        # 3. Interceptar el cierre de la ventana (la 'X')
        self.connect("close-request", self.on_close_request)

    def on_close_request(self, window):
        """
        Se ejecuta cuando el usuario presiona la 'X'.
        En lugar de cerrar, ocultamos la ventana para que la música siga.
        """
        print("Ocultando ventana en segundo plano. La música sigue sonando...")
        self.set_visible(False)
        # Retornar True significa "Yo me encargo del cierre, no destruyas la ventana"
        return True 

    def on_quit_clicked(self, button):
        """Cierra la aplicación por completo"""
        print("Cerrando aplicación...")
        self.app.quit()

class MiApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.github.tuusuario.ytmusic_nativo")
        self.window = None

    def do_activate(self):
        # Si la ventana no existe, la creamos. 
        # Si ya existe (estaba oculta), simplemente la traemos al frente.
        if not self.window:
            self.window = MusicaNativa(self)
        self.window.present()

if __name__ == '__main__':
    # Asegurar que el archivo de cookies exista
    if not os.path.exists(COOKIES_FILE):
        open(COOKIES_FILE, 'a').close()
        
    app = MiApp()
    # Le decimos a la aplicación que se mantenga viva en memoria 
    # incluso si no hay ventanas visibles en pantalla.
    app.hold()
    app.run(None)
