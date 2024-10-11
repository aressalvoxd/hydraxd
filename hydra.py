from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import sounddevice as sd
import numpy as np
import wave
from twilio.rest import Client
import os

KV = '''
ScreenManager:
    LoginScreen:
    ChatScreen:

<LoginScreen>:
    name: 'login'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Giriş Yap'
        TextInput:
            id: phone_input
            hint_text: 'Telefon Numaranızı Girin'
        Button:
            text: 'Giriş Yap'
            on_press: app.login(phone_input.text)

<ChatScreen>:
    name: 'chat'
    BoxLayout:
        orientation: 'vertical'
        Label:
            text: 'Mesajlar'
        TextInput:
            id: message_input
            hint_text: 'Mesajınızı Yazın'
        Button:
            text: 'Gönder'
            on_press: app.send_message(message_input.text)
        Button:
            text: 'Ses Kaydı Başlat'
            on_press: app.start_recording()
        Button:
            text: 'Ses Kaydı Durdur'
            on_press: app.stop_recording()
        Button:
            text: 'Dosya Paylaş'
            on_press: app.open_filechooser()
        Button:
            text: 'Sesli Arama Yap'
            on_press: app.make_call('YOUR_PHONE_NUMBER')  # Hedef telefon numarasını burada belirtin.
'''

class LoginScreen(Screen):
    pass

class ChatScreen(Screen):
    pass

class MesajlasmaUygulamasi(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.recording = False
        self.audio_data = []

    def build(self):
        return Builder.load_string(KV)

    def login(self, phone):
        # Telefon numarası ile giriş işlemi
        self.root.current = 'chat'

    def send_message(self, message):
        # Mesaj gönderme işlemi
        print(f'Mesaj gönderildi: {message}')

    def start_recording(self):
        self.recording = True
        self.audio_data = []
        print("Ses kaydı başlatıldı.")
        sd.default.samplerate = 44100
        sd.default.channels = 1
        with sd.InputStream(callback=self.audio_callback):
            while self.recording:
                sd.sleep(100)

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.audio_data.append(indata.copy())

    def stop_recording(self):
        self.recording = False
        print("Ses kaydı durduruldu.")
        self.save_recording()

    def save_recording(self):
        filename = 'recording.wav'
        data = np.concatenate(self.audio_data, axis=0)
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16 bit
            wf.setframerate(44100)
            wf.writeframes(data.tobytes())
        print(f'Ses kaydı kaydedildi: {filename}')

    def open_filechooser(self):
        content = FileChooserIconView()
        content.bind(on_submit=self.file_selected)
        self.popup = Popup(title="Dosya Seç", content=content, size_hint=(0.9, 0.9))
        self.popup.open()

    def file_selected(self, instance, selection, touch):
        if selection:
            print(f'Seçilen dosya: {selection[0]}')
            self.popup.dismiss()

    def make_call(self, phone_number):
        # Twilio ile sesli arama yapma
        account_sid = 'YOUR_ACCOUNT_SID'
        auth_token = 'YOUR_AUTH_TOKEN'
        client = Client(account_sid, auth_token)

        call = client.calls.create(
            to=phone_number,
            from_='YOUR_TWILIO_NUMBER',  # Twilio'dan alınmış numara
            url='http://demo.twilio.com/docs/voice.xml'
        )
        print(f'Arama yapıldı: {call.sid}')

if __name__ == '__main__':
    MesajlasmaUygulamasi().run()
