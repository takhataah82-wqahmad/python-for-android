import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from jnius import autoclass
import speech_recognition as sr


PythonActivity = autoclass("org.kivy.android.PythonActivity")
Intent = autoclass("android.content.Intent")
Manifest = autoclass("android.Manifest")
PackageManager = autoclass("android.content.pm.PackageManager")


APPS = {
    "اینستاگرام": "com.instagram.android",
    "instagram": "com.instagram.android",
    "تلگرام": "org.telegram.messenger",
    "telegram": "org.telegram.messenger",
    "واتساپ": "com.whatsapp",
    "whatsapp": "com.whatsapp",
    "یوتیوب": "com.google.android.youtube",
    "youtube": "com.google.android.youtube",
    "کروم": "com.android.chrome",
    "chrome": "com.android.chrome",
}


def request_microphone_permission():
    """Request Android microphone permission at runtime on modern Android."""
    try:
        activity = PythonActivity.mActivity
        if activity.checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED:
            activity.requestPermissions([Manifest.permission.RECORD_AUDIO], 1001)
            return False
        return True
    except Exception as e:
        print("Permission error:", e)
        return False


def open_app(package_name):
    try:
        activity = PythonActivity.mActivity
        pm = activity.getPackageManager()
        intent = pm.getLaunchIntentForPackage(package_name)

        if intent:
            activity.startActivity(intent)
            return True
    except Exception as e:
        print(e)

    return False


def open_settings():
    try:
        activity = PythonActivity.mActivity
        intent = Intent("android.settings.SETTINGS")
        activity.startActivity(intent)
    except Exception as e:
        print(e)


def execute_command(command):
    command = command.lower().strip()

    if "تنظیمات" in command:
        open_settings()
        return "در حال باز کردن تنظیمات..."

    for name, package in APPS.items():
        if name in command:
            if open_app(package):
                return f"در حال باز کردن {name}"
            return f"{name} روی گوشی نصب نیست."

    return "این برنامه را پیدا نکردم."


class Jarvis(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(
            orientation="vertical",
            padding=30,
            spacing=25,
            **kwargs
        )

        self.title = Label(
            text="J A R V I S",
            font_size=38
        )
        self.add_widget(self.title)

        self.status = Label(
            text="سیستم آماده است",
            font_size=22
        )
        self.add_widget(self.status)

        self.button = Button(
            text="🎙 صحبت با JARVIS",
            font_size=24
        )
        self.button.bind(on_press=self.listen_start)
        self.add_widget(self.button)

    def listen_start(self, instance):
        if not request_microphone_permission():
            self.status.text = "لطفاً اجازه استفاده از میکروفون را بده."
            return

        self.status.text = "🎙 گوش می‌دهم..."

        threading.Thread(
            target=self.listen,
            daemon=True
        ).start()

    def listen(self):
        recognizer = sr.Recognizer()

        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=5
                )

            command = recognizer.recognize_google(
                audio,
                language="fa-IR"
            )

            result = execute_command(command)

            Clock.schedule_once(
                lambda dt: self.update_status(result)
            )

        except sr.WaitTimeoutError:
            Clock.schedule_once(
                lambda dt: self.update_status("زمان انتظار برای صحبت تمام شد.")
            )
        except sr.UnknownValueError:
            Clock.schedule_once(
                lambda dt: self.update_status("صدات رو متوجه نشدم.")
            )
        except sr.RequestError:
            Clock.schedule_once(
                lambda dt: self.update_status("اتصال سرویس تشخیص صدا برقرار نشد.")
            )
        except Exception as e:
            print(e)
            Clock.schedule_once(
                lambda dt: self.update_status("خطایی در تشخیص صدا رخ داد.")
            )

    def update_status(self, text):
        self.status.text = text


class JarvisApp(App):
    def build(self):
        return Jarvis()


if __name__ == "__main__":
    JarvisApp().run()
