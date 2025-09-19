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
 
USER_FILE = 'users.json'

current_user = {'username': None}

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

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.5, 0.5, 0.5, 1) 
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.layout.add_widget(Label(text='The Diabetes Destroying App', font_size=36, bold=True))
        self.username_input = TextInput(hint_text='Enter your username')
        self.password_input = TextInput(hint_text='Enter your password', password=True)
        self.message_label = Label(text='')
        login_btn = Button(
            text='Login',
            font_size=30,
            size_hint=(1, 0.2),
            height=50,
            background_normal='',
            background_color=(0.2, 0.6, 0.86, 1),
            border=(16, 16, 16, 16)
        )
        login_btn.bind(on_press=self.login_user)
        self.layout.add_widget(self.username_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(login_btn)
        self.layout.add_widget(Button(text='New? Create an account here!', size_hint=(1, 0.1), on_press=lambda x: setattr(self.manager, 'current', 'create_account')))
        self.layout.add_widget(self.message_label)
        self.add_widget(self.layout)

    def login_user(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if check_user_credentials(username, password):
            current_user['username'] = username
            self.manager.current = 'menu'
        else:
            self.message_label.text = 'Incorrect username or password.'
    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

class CreateAccountPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(0.5, 0.5, 0.5, 1) 
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self._update_bg, pos=self._update_bg)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.layout.add_widget(Label(text='Create an Account', font_size=30, bold=True))
        self.name_input = TextInput(hint_text='Enter your name')
        self.email_input = TextInput(hint_text='Enter your email')
        self.password_input = TextInput(hint_text='Enter a password', password=True)
        self.message_label = Label(text='')
        submit_btn = Button(text='Submit')
        submit_btn.bind(on_press=self.create_account)
        self.layout.add_widget(self.name_input)
        self.layout.add_widget(self.email_input)
        self.layout.add_widget(self.password_input)
        self.layout.add_widget(submit_btn)
        self.layout.add_widget(Button(text='Back to Login', on_press=lambda x: setattr(self.manager, 'current', 'login')))
        self.layout.add_widget(self.message_label)
        self.add_widget(self.layout)

    def create_account(self, instance):
        username = self.name_input.text.strip()
        password = self.password_input.text.strip()
        if save_user_credentials(username, password):
            self.message_label.text = 'Account created successfully!'
        else:
            self.message_label.text = 'Username already exists.'
    
    def _update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

class MainMenu(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        # Store the title label so we can update it later
        self.title_label = Label(text='', font_size=30, bold=True)
        self.layout.add_widget(self.title_label)

        buttons = [
            ('Get a new risk factor', 'input'),
            ('Look at my previous reports', 'reports'),
            ('Helpful Sources & Links', 'sources'),
            ('Settings', 'settings')
        ]
        for text, screen in buttons:
            self.layout.add_widget(Button(text=text, on_press=lambda x, scr=screen: setattr(self.manager, 'current', scr)))

        self.layout.add_widget(Button(
            text='Log out',
            font_size=25,
            size_hint_y=None,
            height=50,
            background_normal='',
            background_color=(0.9, 0.2, 0.2, 1),
            border=(16, 16, 16, 16),
            on_press=lambda x: setattr(self.manager, 'current', 'login')
        ))

        self.add_widget(self.layout)

    def on_pre_enter(self):
        # Set title when the screen is shown
        self.title_label.text = f'Main Menu - {current_user["username"]}'

class SourcesPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Helpful Sources & Links', font_size=30, bold=True))
        layout.add_widget(Label(text='[List of helpful resources will go here]'))
        layout.add_widget(Button(text="CDC Diabetes Prevention Program",on_press=lambda x: webbrowser.open("https://www.cdc.gov/diabetes-prevention/index.html")))
        layout.add_widget(Button(text='Back to Main Menu', on_press=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

class SettingsPage(Screen):
    def delete_account(self, instance):
        users = load_users()
        username = current_user['username']
        if username in users:
            del users[username]
            save_users(users)
            current_user['username'] = None
            self.confirmation_label.text = 'Account deleted.'
            self.manager.current = 'login'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Settings', font_size=30, bold=True))

        clear_btn = Button(text='Clear My Reports')
        clear_btn.bind(on_press=self.clear_reports)
        layout.add_widget(clear_btn)

        layout.add_widget(Label(text='Change Your Password'))
        self.new_password_input = TextInput(hint_text='Enter new password', password=True)
        change_pass_btn = Button(text='Change Password')
        change_pass_btn.bind(on_press=self.change_password)
        layout.add_widget(self.new_password_input)
        layout.add_widget(change_pass_btn)

        layout.add_widget(Label(text='Update Email'))
        self.new_email_input = TextInput(hint_text='Enter new email')
        update_email_btn = Button(text='Update Email')
        update_email_btn.bind(on_press=self.update_email)
        layout.add_widget(self.new_email_input)
        layout.add_widget(update_email_btn)

        delete_account_btn = Button(text='Delete My Account')
        delete_account_btn.bind(on_press=self.delete_account)
        layout.add_widget(delete_account_btn)

        self.confirmation_label = Label(text='')
        layout.add_widget(self.confirmation_label)

        layout.add_widget(Button(text='Back to Main Menu', on_press=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

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

    def clear_reports(self, instance):
        users = load_users()
        username = current_user['username']
        if username and username in users:
            users[username]['reports'] = []
            save_users(users)

class ResultsPage(Screen):
    def __init__(self, result_text='', **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.label = Label(text='Your Risk Result:', font_size=25)
        self.result_label = Label(text=result_text, font_size=20)
        self.layout.add_widget(self.label)
        self.layout.add_widget(self.result_label)
        self.layout.add_widget(Button(text='Back to Main Menu', on_press=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(self.layout)

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
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        layout.add_widget(Label(text='Previous Reports', font_size=30, bold=True))

        self.reports_label = Label(text='', halign='left', valign='top')
        self.reports_label.bind(size=self.reports_label.setter('text_size'))

        scroll = ScrollView()
        scroll.add_widget(self.reports_label)

        layout.add_widget(scroll)
        layout.add_widget(Button(text='Back to Main Menu', on_press=lambda x: setattr(self.manager, 'current', 'menu')))
        self.add_widget(layout)

    def on_pre_enter(self):
        users = load_users()
        username = current_user['username']
        if username and username in users:
            reports = users[username].get('reports', [])
            self.reports_label.text = '\n'.join(reports) if reports else 'No reports yet.'


class InputPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        root_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView()
        layout = GridLayout(cols=1, padding=20, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))
        layout.add_widget(Label(text='Get a new risk factor', font_size=25, size_hint_y=None, height=50))

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
            sub_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=80)
            sub_layout.add_widget(Label(text=category + ':', size_hint_y=None, height=30))
            self.spinners[category] = Spinner(text='Select Option', values=values, size_hint_y=None, height=50)
            sub_layout.add_widget(self.spinners[category])
            layout.add_widget(sub_layout)

        layout.add_widget(Button(text='Submit', size_hint_y=None, height=50, on_press=self.submit_form))
        layout.add_widget(Button(text='Back to Main Menu', size_hint_y=None, height=50, on_press=lambda x: setattr(self.manager, 'current', 'menu')))

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
                return int(value.split(':')[1].strip().split()[0])
            return 0

        age_score = score_from_text(selections['Age'])
        family_history_score = score_from_text(selections['Family History of Diabetes'])
        bp_score = score_from_text(selections['Blood Pressure Levels'])
        blood_sugar_score = score_from_text(selections['Blood Sugar Levels (Optional)'])
        activity_score = score_from_text(selections['Physical Activity Levels'])
        calorie_score = score_from_text(selections['Estimated Daily Calorie Intake'])
        diet_score = score_from_text(selections['Diet Quality/Habits'])
        stress_score = score_from_text(selections['Stress Levels'])

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
