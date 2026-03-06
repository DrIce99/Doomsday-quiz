class KeyboardInputManager:
    def __init__(self, root, callback_check, callback_next=None, confirm_required=False):
        """
        :param root: La finestra principale (CTk)
        :param callback_check: La funzione check_answer(valore) del quiz
        :param confirm_required: Se True, serve INVIO per confermare
        """
        self.root = root
        self.callback_check = callback_check
        self.callback_next = callback_next
        self.confirm_required = confirm_required
        self.current_selection = None
        self.btn_map = {}

    def setup_map(self, buttons_dict):
        """Associa i valori (0-6) ai widget CTkButton per l'effetto hover"""
        self.btn_map = buttons_dict

    def bind_keys(self):
        # Bind per numeri (0-6) sia tastiera che tastierino
        for i in range(7):
            self.root.bind(f"{i}", lambda e, v=i: self._handle_input(v))
            self.root.bind(f"<KP_{i}>", lambda e, v=i: self._handle_input(v))
        
        # Bind per Invio (Confirm)
        self.root.bind("<Return>", self._confirm_selection)
        self.root.bind("<KP_Enter>", self._confirm_selection)
        
        self.root.bind("<space>", self._handle_space)

    def _handle_input(self, value):
        if not self.confirm_required:
            self.callback_check(value)
        else:
            # Reset immediato delle selezioni precedenti
            self._reset_button_effects()
            
            if value in self.btn_map:
                self.current_selection = value
                self.btn_map[value].configure(
                    border_width=5, 
                    border_color="#f1c40f" # Giallo acceso
                )

    def _confirm_selection(self, event=None):
        if self.confirm_required and self.current_selection is not None:
            val = self.current_selection
            self.current_selection = None
            self._reset_button_effects()
            self.callback_check(val)

    def _reset_button_effects(self):
        for btn in self.btn_map.values():
            if btn.winfo_exists(): # Sicurezza anti-crash
                btn.configure(border_width=0)
            
    def _handle_space(self, event=None):
        if self.callback_next:
            self._reset_button_effects() # Pulizia bordi rimasti
            self.current_selection = None # Pulizia selezione logica
            self.callback_next()
