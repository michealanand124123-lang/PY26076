from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.label import MDLabel
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, Screen

import venom_backend  # Ensure this exists

# Optional window size for testing on PC
Window.size = (400, 600)
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        self.input = MDTextField(
            hint_text="Say something to Venom...",
            multiline=False,
            size_hint=(1, None),
            height="40dp"
        )

        self.button = MDRectangleFlatButton(
            text="Ask Venom",
            pos_hint={"center_x": 0.5},
            on_release=self.ask_venom
        )

        self.output = MDLabel(
            text="",
            halign="center",
            theme_text_color="Custom",
            text_color=(1, 1, 1, 1),
            font_style="H6"
        )

        layout.add_widget(self.input)
        layout.add_widget(self.button)
        layout.add_widget(self.output)

        self.add_widget(layout)

    def ask_venom(self, *args):
        user_input = self.input.text.strip()
        if user_input:
            reply = venom_backend.process_query(user_input)
            self.output.text = f"Venom: {reply}"
        else:
            self.output.text = "Venom: Dei... sollu da onna?"

class VenomApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Purple"
        self.theme_cls.theme_style = "Dark"
        sm = ScreenManager()
        sm.add_widget(MainScreen(name="main"))
        return sm

if __name__ == "__main__":
    VenomApp().run()