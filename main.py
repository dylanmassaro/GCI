import json
import hashlib
import os
import webbrowser

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle

# =========================
# Global Colors & Styles
# =========================
COLORS = {
    'ivory':     (1.0, 1.0, 0.94, 1),
    'teal':      (0.00, 0.42, 0.35, 1),
    'salmon':    (0.98, 0.50, 0.44, 1),
    'dark_blue': (0.18, 0.31, 0.38, 1),
}

FONTS = {
    'title': 40,
    'section': 26,
    'body': 20,
    'button': 22,
}

# Button & label style helpers (avoid background_color collisions by NOT baking it in)
BUTTON_STYLE = {
    'size_hint': (1, None),
    'height': 60,
    'font_size': FONTS['button'],
    'background_normal': '',
    'color': COLORS['ivory'],  # text color
}

LABEL_TITLE_STYLE = {
    'font_size': FONTS['title'],
    'color': COLORS['ivory'],
}

LABEL_SECTION_STYLE = {
    'font_size': FONTS['section'],
    'color': COLORS['ivory'],
}

LABEL_BODY_STYLE = {
    'font_size': FONTS['body'],
    'color': COLORS['ivory'],
}

TEXTINPUT_STYLE = {
    'multiline': False,
    'foreground_color': COLORS['ivory'],
    'background_color': (1, 1, 1, 0.12),  # subtle light on dark
    'cursor_color': COLORS['ivory'],
}

SPINNER_STYLE = {
    'size_hint_y': None,
    'height': 50,
    'background_normal': '',
    'background_color': COLORS['teal'],
    'color': COLORS['ivory'],
}

USER_FILE = 'users.json'
current_user = {'username': None}

# =========================
# Utilities
# =========================
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_credentials(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = {
        'password': hash_password(password),
        'reports': []
    }
    save_users(users)
    return True

def check_user_credentials(username, password):
    users = load_users()
    return username in users and users[username]['password'] == hash_password(password)

def set_screen_bg(widget, color_key='dark_blue'):
    with widget.canvas.before:
        Color(*COLORS[color_key])
        widget.bg_rect = Rectangle(size=widget.size, pos=widget.pos)
    widget.bind(size=lambda *a: _update_bg(widget), pos=lambda *a: _update_bg(widget))

def _update_bg(widget):
    widget.bg_rect.size = widget.size
    widget.bg_rect.pos = widget.pos

# =========================
# Screens
# =========================
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        layout.add_widget(Label(
            text='The Diabetes Destroying App',
            **LABEL_TITLE_STYLE
        ))

        # Username
        user_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=100, spacing=6)
        user_box.add_widget(Label(text='Enter your username', **LABEL_BODY_STYLE))
        self.username_input = TextInput(**TEXTINPUT_STYLE)
        user_box.add_widget(self.username_input)
        layout.add_widget(user_box)

        # Password
        pass_box = BoxLayout(orientation='vertical', size_hint=(1, None), height=100, spacing=6)
        pass_box.add_widget(Label(text='Enter your password', **LABEL_BODY_STYLE))
        self.password_input = TextInput(password=True, **TEXTINPUT_STYLE)
        self.password_input.bind(on_text_validate=lambda x: self.login_user(None))
        pass_box.add_widget(self.password_input)
        layout.add_widget(pass_box)

        # Login button
        login_btn = Button(text='Login', **BUTTON_STYLE, background_color=COLORS['teal'])
        login_btn.bind(on_press=self.login_user)
        layout.add_widget(login_btn)

        # Create account
        layout.add_widget(Button(
            text='New? Create an account here!',
            **BUTTON_STYLE,
            background_color=COLORS['salmon'],
            on_press=lambda x: setattr(self.manager, 'current', 'create_account')
        ))

        # Message label
        self.message_label = Label(text='', **LABEL_BODY_STYLE)
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def login_user(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if check_user_credentials(username, password):
            current_user['username'] = username
            self.username_input.text = ""
            self.password_input.text = ""
            self.manager.current = 'menu'
        else:
            self.message_label.text = 'Incorrect username or password.'


class CreateAccountPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)

        layout.add_widget(Label(text='Create an Account', **LABEL_TITLE_STYLE))

        self.name_input = TextInput(hint_text='Enter your username', **TEXTINPUT_STYLE)
        self.email_input = TextInput(hint_text='Enter your email', **TEXTINPUT_STYLE)
        self.password_input = TextInput(hint_text='Enter a password', password=True, **TEXTINPUT_STYLE)
        self.password_input.bind(on_text_validate=lambda x: self.create_account(None))

        self.message_label = Label(text='', **LABEL_BODY_STYLE)

        submit_btn = Button(text='Submit', **BUTTON_STYLE, background_color=COLORS['teal'])
        submit_btn.bind(on_press=self.create_account)

        layout.add_widget(self.name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(submit_btn)

        layout.add_widget(Button(
            text='Back to Login',
            **BUTTON_STYLE,
            background_color=COLORS['salmon'],
            on_press=lambda x: setattr(self.manager, 'current', 'login')
        ))

        layout.add_widget(self.message_label)
        self.add_widget(layout)

    def create_account(self, instance):
        username = self.name_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self.message_label.text = "Please enter username and password."
        elif save_user_credentials(username, password):
            self.message_label.text = 'Account created successfully!'
        else:
            self.message_label.text = 'Username already exists.'


class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)

        self.title_label = Label(text='', **LABEL_TITLE_STYLE)
        layout.add_widget(self.title_label)

        buttons = [
            ('Get a new risk factor', 'input', COLORS['teal']),
            ('Look at my previous reports', 'reports', COLORS['teal']),
            ('Helpful Sources & Links', 'sources', COLORS['salmon']),
            ('Settings', 'settings', COLORS['salmon'])
        ]
        for text, screen, bg in buttons:
            btn = Button(text=text, **BUTTON_STYLE, background_color=bg)
            btn.bind(on_press=lambda x, scr=screen: setattr(self.manager, 'current', scr))
            layout.add_widget(btn)

        layout.add_widget(Button(
            text='Log out',
            **BUTTON_STYLE,
            background_color=COLORS['dark_blue'],
            on_press=lambda x: setattr(self.manager, 'current', 'login')
        ))

        self.add_widget(layout)

    def on_pre_enter(self):
        self.title_label.text = f'Main Menu - {current_user["username"] or ""}'


class SourcesPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        layout.add_widget(Label(text='Helpful Sources & Links', **LABEL_TITLE_STYLE))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text="CDC Diabetes Prevention Program",
            background_color=COLORS['teal'],
            on_press=lambda x: webbrowser.open("https://www.cdc.gov/diabetes-prevention/index.html")
        ))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text="Open Mayo Clinic Diabetes Prevention",
            background_color=COLORS['salmon'],
            on_press=lambda x: webbrowser.open("https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/in-depth/diabetes-prevention/art-20047639?")
        ))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text='Back to Main Menu',
            background_color=COLORS['dark_blue'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))

        self.add_widget(layout)


class SettingsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=16)
        layout.add_widget(Label(text='Settings', **LABEL_TITLE_STYLE))

      
        layout.add_widget(Label(text='Change Your Password', **LABEL_SECTION_STYLE))
        self.new_password_input = TextInput(hint_text='Enter new password', password=True, **TEXTINPUT_STYLE)
        change_pass_btn = Button(text='Change Password', **BUTTON_STYLE, background_color=COLORS['teal'])
        change_pass_btn.bind(on_press=self.change_password)
        layout.add_widget(self.new_password_input)
        layout.add_widget(change_pass_btn)

   
        layout.add_widget(Label(text='Update Email', **LABEL_SECTION_STYLE))
        self.new_email_input = TextInput(hint_text='Enter new email', **TEXTINPUT_STYLE)
        update_email_btn = Button(text='Update Email', **BUTTON_STYLE, background_color=COLORS['teal'])
        update_email_btn.bind(on_press=self.update_email)
        layout.add_widget(self.new_email_input)
        layout.add_widget(update_email_btn)

       
        delete_account_btn = Button(text='Delete My Account', **BUTTON_STYLE, background_color=COLORS['salmon'])
        delete_account_btn.bind(on_press=self.delete_account)
        layout.add_widget(delete_account_btn)


        clear_btn = Button(text='Clear My Reports', **BUTTON_STYLE, background_color=COLORS['salmon'])
        clear_btn.bind(on_press=self.clear_reports)
        layout.add_widget(clear_btn)

        self.confirmation_label = Label(text='', **LABEL_BODY_STYLE)
        layout.add_widget(self.confirmation_label)

        layout.add_widget(Button(
            text='Back to Main Menu',
            **BUTTON_STYLE,
            background_color=COLORS['dark_blue'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))

        self.add_widget(layout)

    def delete_account(self, instance):
        users = load_users()
        username = current_user['username']
        if username in users:
            del users[username]
            save_users(users)
            current_user['username'] = None
            self.confirmation_label.text = 'Account deleted.'
            self.manager.current = 'login'

    def clear_reports(self, instance):
        users = load_users()
        username = current_user['username']
        if username and username in users:
            users[username]['reports'] = []
            save_users(users)
            self.confirmation_label.text = 'All reports cleared.'

    def change_password(self, instance):
        new_password = self.new_password_input.text.strip()
        if new_password:
            users = load_users()
            username = current_user['username']
            if username in users:
                users[username]['password'] = hash_password(new_password)
                save_users(users)
                self.new_password_input.text = ''
                self.confirmation_label.text = 'Password updated successfully.'

    def update_email(self, instance):
        new_email = self.new_email_input.text.strip()
        if new_email:
            users = load_users()
            username = current_user['username']
            if username in users:
                users[username]['email'] = new_email
                save_users(users)
                self.new_email_input.text = ''
                self.confirmation_label.text = 'Email updated successfully.'


class ResultsPage(Screen):
    def __init__(self, result_text='', **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        layout.add_widget(Label(text='Your Risk Result:', **LABEL_SECTION_STYLE))
        self.result_label = Label(text=result_text, **LABEL_BODY_STYLE)
        layout.add_widget(self.result_label)
        layout.add_widget(Button(
            text='Back to Main Menu',
            **BUTTON_STYLE,
            background_color=COLORS['salmon'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))
        self.add_widget(layout)

    def update_result(self, result_text):
        self.result_label.text = result_text
        users = load_users()
        username = current_user['username']
        if username in users:
            users[username].setdefault('reports', []).append(result_text)
            save_users(users)


class ReportsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        layout = BoxLayout(orientation='vertical', padding=20, spacing=12)
        layout.add_widget(Label(text='Previous Reports', **LABEL_TITLE_STYLE))

        self.reports_label = Label(text='', halign='left', valign='top', **LABEL_BODY_STYLE)
        self.reports_label.bind(size=self._wrap_text)

        scroll = ScrollView()
        scroll.add_widget(self.reports_label)

        layout.add_widget(scroll)
        layout.add_widget(Button(
            text='Back to Main Menu',
            **BUTTON_STYLE,
            background_color=COLORS['salmon'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))

        self.add_widget(layout)

    def _wrap_text(self, *args):
        self.reports_label.text_size = (self.reports_label.width, None)

    def on_pre_enter(self):
        users = load_users()
        username = current_user['username']
        if username and username in users:
            reports = users[username].get('reports', [])
            self.reports_label.text = '\n'.join(reports) if reports else 'No reports yet.'


class InputPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        root_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView()
        layout = GridLayout(cols=1, padding=20, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text='Get a new risk factor', **LABEL_SECTION_STYLE))

        self.categories = {
            'Age': ['0-30: 0 points', '31-40: 2 points', '41-50: 4 points', '51-60: 6 points', '61+ years: 8 points'],
            'Family History of Diabetes': ['No immediate family: 0 points', 'One grandparent, uncle/aunt: 3 points', 'One parent or sibling: 6 points', 'Both parents/multiple close relatives: 10 points'],
            'Blood Pressure Levels': ['Normal (<120/80): 0 points', 'Elevated (120-129/<80): 2 points', 'Stage 1 (130-139/80-89): 5 points', 'Stage 2 (140+/90+): 8 points', 'Crisis (180+/120+): 12 points'],
            'Blood Sugar Levels (Optional)': ['Normal (<100 mg/dL): 0 points', 'Borderline (100-109 mg/dL): 4 points', 'Prediabetes (110-125 mg/dL): 8 points', 'Diabetes (>125 mg/dL): 15 points'],
            'Physical Activity Levels': ['Active (5 days/week): 0 points', 'Moderately Active (3-4 days/week): 3 points', 'Low Activity (1-2 days/week): 6 points', 'Sedentary (No exercise): 10 points'],
            'Estimated Daily Calorie Intake': ['Healthy Intake: 0 points', 'Slightly Excessive: 3 points', 'Overeating: 7 points', 'Extreme Overeating: 12 points'],
            'Diet Quality/Habits': ['Healthy: 0 points', 'Average: 3 points', 'Poor: 7 points', 'Extremely Unhealthy: 12 points'],
            'Stress Levels': ['Low Stress: 0 points', 'Moderate Stress: 3 points', 'High Stress: 7 points', 'Chronic Stress: 10 points']
        }

        self.spinners = {}
        for category, values in self.categories.items():
            sub_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=6)
            sub_layout.add_widget(Label(text=f'{category}:', **LABEL_BODY_STYLE))
            spn = Spinner(text='Select Option', values=values, **SPINNER_STYLE)
            self.spinners[category] = spn
            sub_layout.add_widget(spn)
            layout.add_widget(sub_layout)

        layout.add_widget(Button(
            text='Submit',
            **BUTTON_STYLE,
            background_color=COLORS['teal'],
            on_press=self.submit_form
        ))
        layout.add_widget(Button(
            text='Back to Main Menu',
            **BUTTON_STYLE,
            background_color=COLORS['salmon'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))

        scroll_view.add_widget(layout)
        root_layout.add_widget(scroll_view)
        self.add_widget(root_layout)

    def submit_form(self, instance):
        selections = {key: spinner.text for key, spinner in self.spinners.items()}
        risk_score = self.calculate_fake_risk(selections)
        self.manager.get_screen('results').update_result(f'Estimated Risk Score: {risk_score}')
        self.manager.current = 'results'

    def calculate_fake_risk(self, selections):
        def score_from_text(value):
            if ':' in value:
                try:
                    return int(value.split(':')[1].strip().split()[0])
                except ValueError:
                    return 0
            return 0

        age_score = score_from_text(selections.get('Age', '0: 0'))
        family_history_score = score_from_text(selections.get('Family History of Diabetes', '0: 0'))
        bp_score = score_from_text(selections.get('Blood Pressure Levels', '0: 0'))
        blood_sugar_score = score_from_text(selections.get('Blood Sugar Levels (Optional)', '0: 0'))
        activity_score = score_from_text(selections.get('Physical Activity Levels', '0: 0'))
        calorie_score = score_from_text(selections.get('Estimated Daily Calorie Intake', '0: 0'))
        diet_score = score_from_text(selections.get('Diet Quality/Habits', '0: 0'))
        stress_score = score_from_text(selections.get('Stress Levels', '0: 0'))

        risk1 = age_score * family_history_score
        risk2 = bp_score * blood_sugar_score
        risk3 = stress_score * diet_score
        risk4 = calorie_score * (10 - activity_score)

        total = (
            age_score + family_history_score + bp_score + blood_sugar_score +
            activity_score + calorie_score + diet_score + stress_score +
            0.5 * risk1 + 0.6 * risk2 + 0.4 * risk3 + 0.7 * risk4
        )

        total = round(total, 2)

        if total <= 45:
            risk_level = "Low Risk"
        elif total <= 85:
            risk_level = "Moderate Risk"
        else:
            risk_level = "High Risk"

        return f"{total} ({risk_level})"

class RiskApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(CreateAccountPage(name='create_account'))
        sm.add_widget(MainMenu(name='menu'))
        sm.add_widget(InputPage(name='input'))
        sm.add_widget(SourcesPage(name='sources'))
        sm.add_widget(SettingsPage(name='settings'))
        sm.add_widget(ResultsPage(name='results'))
        sm.add_widget(ReportsPage(name='reports'))
        return sm

if __name__ == '__main__':
    RiskApp().run()
