import customtkinter as ctk


class UsersView:
    def __init__(self, parent):
        self.parent = parent
        self._setup_ui()
    
    def _setup_ui(self):
        content = ctk.CTkFrame(self.parent)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        title = ctk.CTkLabel(
            content,
            text="👥 Gestión de Perfiles",
            font=("Arial", 24, "bold")
        )
        title.pack(pady=20)
        
        desc = ctk.CTkLabel(
            content,
            text="Esta función estará disponible próximamente\n"
                 "Podrás guardar configuraciones por perfil de usuario",
            font=("Arial", 14),
            text_color="gray",
            justify="center"
        )
        desc.pack(pady=10)