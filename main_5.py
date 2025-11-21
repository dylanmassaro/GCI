import json
import hashlib
import os
import webbrowser

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget

# =========================
# Global Colors & Styles
# =========================
COLORS = {
    'ivory':     (1.0, 1.0, 0.94, 1),
    'teal_1':      (0.00, 0.42, 0.35, 1),
    'salmon':    (0.98, 0.50, 0.44, 1),
    'dark_blue': (0.1, 0.46, 0.61, 0.75),
    'teal_2': (0.00, 0.50, 0.40, 1),
    'teal_3': (0.00, 0.54, 0.44, 1),
    'teal_4': (0.00, 0.59, 0.48, 1)
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
    'write_tab': False,
}

SPINNER_STYLE = {
    'size_hint_y': None,
    'height': 50,
    'background_normal': '',
    'background_color': COLORS['teal_2'],
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
        login_btn = Button(text='Login', **BUTTON_STYLE, background_color=COLORS['teal_2'])
        login_btn.bind(on_press=self.login_user)
        layout.add_widget(login_btn)

        # Create account
        layout.add_widget(Button(
            text='New? Create an account here!',
            **BUTTON_STYLE,
            background_color=COLORS['teal_1'],
            on_press=lambda x: setattr(self.manager, 'current', 'create_account')
        ))

        # Message label
        self.message_label = Label(text='', **LABEL_BODY_STYLE)
        layout.add_widget(self.message_label)

        self.add_widget(layout)

    def login_user(self, instance):
        username = self.username_input.text.strip()
        password = self.password_input.text.strip()
        if not username or not password:
            self.message_label.text = "Please enter username and password."
        elif check_user_credentials(username, password):
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

        submit_btn = Button(text='Submit', **BUTTON_STYLE, background_color=COLORS['teal_1'])
        submit_btn.bind(on_press=self.create_account)

        layout.add_widget(self.name_input)
        layout.add_widget(self.email_input)
        layout.add_widget(self.password_input)
        layout.add_widget(submit_btn)

        layout.add_widget(Button(
            text='Back to Login',
            **BUTTON_STYLE,
            background_color=COLORS['teal_1'],
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
            ('Get a new risk factor', 'input', COLORS['teal_1']),
            ('Look at my previous reports', 'reports', COLORS['teal_2']),
            ('Helpful Sources & Links', 'sources', COLORS['teal_3']),
            ('Settings', 'settings', COLORS['teal_4'])
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
            background_color=COLORS['teal_1'],
            on_press=lambda x: webbrowser.open("https://www.cdc.gov/diabetes-prevention/index.html")
        ))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text="Mayo Clinic Diabetes Prevention",
            background_color=COLORS['teal_2'],
            on_press=lambda x: webbrowser.open("https://www.mayoclinic.org/diseases-conditions/type-2-diabetes/in-depth/diabetes-prevention/art-20047639?")
        ))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text="Prediabetes Clinical Guidelines",
            background_color=COLORS['teal_3'],
            on_press=lambda x: webbrowser.open("https://www.mainehealth.org/health-care-professionals/clinical-guidelines-protocols/prediabetes-clinical-guidelines")
        ))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text="Lifestyle and the Prevention of Type 2 Diabetes",
            background_color=COLORS['teal_4'],
            on_press=lambda x: webbrowser.open("https://pmc.ncbi.nlm.nih.gov/articles/PMC6125024/")
        ))

        layout.add_widget(Button(
            **BUTTON_STYLE,
            text="Type 2 Diabetes: Overview",
            background_color=COLORS['teal_3'],
            on_press=lambda x: webbrowser.open("https://my.clevelandclinic.org/health/diseases/21501-type-2-diabetes")
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
        self.new_password_input.bind(on_text_validate=lambda x: self.change_password(None))
        change_pass_btn = Button(text='Change Password', **BUTTON_STYLE, background_color=COLORS['teal_1'])
        change_pass_btn.bind(on_press=self.change_password)
        layout.add_widget(self.new_password_input)
        layout.add_widget(change_pass_btn)

        layout.add_widget(Label(text='Update Email', **LABEL_SECTION_STYLE))
        self.new_email_input = TextInput(hint_text='Enter new email', **TEXTINPUT_STYLE)
        self.new_email_input.bind(on_text_validate=lambda x: self.update_email(None))
        update_email_btn = Button(text='Update Email', **BUTTON_STYLE, background_color=COLORS['teal_2'])
        update_email_btn.bind(on_press=self.update_email)
        layout.add_widget(self.new_email_input)
        layout.add_widget(update_email_btn)

        delete_account_btn = Button(text='Delete My Account', **BUTTON_STYLE, background_color=COLORS['teal_3'])
        delete_account_btn.bind(on_press=self.delete_account)
        layout.add_widget(delete_account_btn)

        clear_btn = Button(text='Clear My Reports', **BUTTON_STYLE, background_color=COLORS['teal_4'])
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

    def show_confirmation(self, message, confirm_callback):
        box = BoxLayout(orientation='vertical', padding=20, spacing=10)
        box.add_widget(Label(text=message, **LABEL_BODY_STYLE))

        btn_box = BoxLayout(spacing=10, size_hint=(1, None), height=50)
        yes_btn = Button(text='Yes', background_color=COLORS['salmon'])
        no_btn = Button(text='No', background_color=COLORS['teal_1'])
        btn_box.add_widget(yes_btn)
        btn_box.add_widget(no_btn)

        box.add_widget(btn_box)

        popup = Popup(
            title="Confirm Action",
            content=box,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )

        yes_btn.bind(on_press=lambda x: (confirm_callback(), popup.dismiss()))
        no_btn.bind(on_press=lambda x: popup.dismiss())

        popup.open()

    def delete_account(self, instance):
        self.show_confirmation(
            "Are you sure you want to delete your account?\nThis cannot be undone.",
            self.confirm_delete_account
        )

    def confirm_delete_account(self):
        users = load_users()
        username = current_user['username']
        if username in users:
            del users[username]
            save_users(users)
            current_user['username'] = None
            self.confirmation_label.text = 'Account deleted.'
            self.manager.current = 'login'

    def clear_reports(self, instance):
        self.show_confirmation(
            "Are you sure you want to clear all your reports?",
            self.confirm_clear_reports
        )

    def confirm_clear_reports(self):
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

        self.result_label = Label(text=result_text, **LABEL_BODY_STYLE, halign='left', valign='top')
        self.result_label.bind(size=self._wrap_text)
        layout.add_widget(self.result_label)

        self.link_button = Button(
            text='Helpful Resource',
            **BUTTON_STYLE,
            background_color=COLORS['teal_2']
        )
        self.link_button.opacity = 0
        self.link_button.disabled = True
        layout.add_widget(self.link_button)

        layout.add_widget(Button(
            text='Back to Main Menu',
            **BUTTON_STYLE,
            background_color=COLORS['teal_1'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))
        self.add_widget(layout)

    def _wrap_text(self, *args):
        self.result_label.text_size = (self.result_label.width, None)

    def update_result(self, result_text, link=None):
        self.result_label.text = result_text
        users = load_users()
        username = current_user['username']
        if username in users:
            users[username].setdefault('reports', []).append(result_text)
            save_users(users)

        # Reset button bindings each time
        self.link_button.unbind(on_press=None)
        if link:
            self.link_button.opacity = 1
            self.link_button.disabled = False
            self.link_button.text = "Learn more"
            self.link_button.bind(on_press=lambda x: webbrowser.open(link))
        else:
            self.link_button.opacity = 0
            self.link_button.disabled = True


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
            background_color=COLORS['teal_1'],
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
            self.reports_label.text = '\n\n'.join(reports) if reports else 'No reports yet.'


class InputPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        set_screen_bg(self, 'dark_blue')

        root_layout = BoxLayout(orientation='vertical')
        scroll_view = ScrollView()
        layout = GridLayout(cols=1, padding=20, spacing=10, size_hint_y=None)
        layout.bind(minimum_height=layout.setter('height'))

        layout.add_widget(Label(text='Get a new risk factor', **LABEL_SECTION_STYLE))

        # INTERNAL SCORING (hidden from user)
        # Each option: (label_shown_to_user, points)
        self.category_options = {
            'Age': [
                ('0-30', 0),
                ('31-40', 2),
                ('41-50', 4),
                ('51-60', 6),
                ('61+ years', 8),
            ],
            'Family History of Diabetes': [
                ('No immediate family history', 0),
                ('One grandparent, uncle/aunt with diabetes', 3),
                ('One parent or sibling with diabetes', 6),
                ('Both parents / multiple close relatives with diabetes', 10),
            ],
            'Blood Pressure Levels': [
                ('Normal (<120/80)', 0),
                ('Elevated (120-129/<80)', 2),
                ('Stage 1 (130-139/80-89)', 5),
                ('Stage 2 (140+/90+)', 8),
                ('Hypertensive crisis (180+/120+)', 12),
            ],
            'Blood Sugar Levels (Optional)': [
                ('Normal (<100 mg/dL)', 0),
                ('Borderline (100-109 mg/dL)', 4),
                ('Prediabetes (110-125 mg/dL)', 8),
                ('Diabetes (>125 mg/dL)', 15),
            ],
            'Physical Activity Levels': [
                ('Active (5+ days/week)', 0),
                ('Moderately active (3-4 days/week)', 3),
                ('Low activity (1-2 days/week)', 6),
                ('Sedentary (no regular exercise)', 10),
            ],
            'Estimated Daily Calorie Intake': [
                ('Healthy for my body/height/weight', 0),
                ('Slightly higher than recommended', 3),
                ('Overeating most days', 7),
                ('Extreme overeating / frequent binges', 12),
            ],
            'Diet Quality/Habits': [
                ('Mostly whole foods, low sugar', 0),
                ('Average mix of healthy and unhealthy', 3),
                ('Frequent fast food / sugary drinks', 7),
                ('Very poor diet, almost all processed', 12),
            ],
            'Stress Levels': [
                ('Low stress', 0),
                ('Moderate stress', 3),
                ('High stress', 7),
                ('Chronic/overwhelming stress', 10),
            ],
        }

        self.spinners = {}
        for category, options in self.category_options.items():
            sub_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=100, spacing=6)
            sub_layout.add_widget(Label(text=f'{category}:', **LABEL_BODY_STYLE))
            labels = [opt[0] for opt in options]
            spn = Spinner(text='Select Option', values=labels, **SPINNER_STYLE)
            self.spinners[category] = spn
            sub_layout.add_widget(spn)
            layout.add_widget(sub_layout)

        layout.add_widget(Button(
            text='Submit',
            **BUTTON_STYLE,
            background_color=COLORS['teal_1'],
            on_press=self.submit_form
        ))
        layout.add_widget(Button(
            text='Back to Main Menu',
            **BUTTON_STYLE,
            background_color=COLORS['teal_1'],
            on_press=lambda x: setattr(self.manager, 'current', 'menu')
        ))

        scroll_view.add_widget(layout)
        root_layout.add_widget(scroll_view)
        self.add_widget(root_layout)

    def finish_submission(self, selections):
        result_text, link = self.calculate_risk(selections)
        results_page = self.manager.get_screen('results')
        results_page.update_result(result_text, link)
        self.manager.current = 'results'

    def submit_form(self, instance):
        selections = {key: spinner.text for key, spinner in self.spinners.items()}

        unanswered = [key for key, value in selections.items() if value == 'Select Option']

        if unanswered:
            missing_text = "You did not answer the following:\n\n" + "\n".join(f"• {q}" for q in unanswered)

            box = BoxLayout(orientation='vertical', padding=20, spacing=10)
            box.add_widget(Label(text=missing_text, **LABEL_BODY_STYLE))

            btn_box = BoxLayout(spacing=10, size_hint=(1, None), height=50)
            back_btn = Button(text='Go Back', background_color=COLORS['teal_1'])
            submit_anyway_btn = Button(text='Submit Anyway', background_color=COLORS['salmon'])

            btn_box.add_widget(back_btn)
            btn_box.add_widget(submit_anyway_btn)
            box.add_widget(btn_box)

            popup = Popup(
                title="Missing Answers",
                content=box,
                size_hint=(0.85, 0.55),
                auto_dismiss=False
            )

            back_btn.bind(on_press=lambda x: popup.dismiss())
            submit_anyway_btn.bind(on_press=lambda x: (popup.dismiss(), self.finish_submission(selections)))

            popup.open()
        else:
            self.finish_submission(selections)

    def calculate_risk(self, selections):
        # Map selections → scores
        scores = {}
        max_scores = {}
        ratios = {}

        for category, options in self.category_options.items():
            selected_label = selections.get(category, 'Select Option')
            # Find matching points
            points = 0
            for label, pts in options:
                if label == selected_label:
                    points = pts
                    break
            max_pt = max(pts for _, pts in options)
            scores[category] = points
            max_scores[category] = max_pt
            ratios[category] = points / max_pt if max_pt > 0 else 0

        # Pull named scores for composite
        age_score = scores['Age']
        family_history_score = scores['Family History of Diabetes']
        bp_score = scores['Blood Pressure Levels']
        blood_sugar_score = scores['Blood Sugar Levels (Optional)']
        activity_score = scores['Physical Activity Levels']
        calorie_score = scores['Estimated Daily Calorie Intake']
        diet_score = scores['Diet Quality/Habits']
        stress_score = scores['Stress Levels']

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
            link = "https://pmc.ncbi.nlm.nih.gov/articles/PMC6125024/"
        elif total <= 85:
            risk_level = "Moderate Risk"
            link = "https://www.mainehealth.org/health-care-professionals/clinical-guidelines-protocols/prediabetes-clinical-guidelines"
        else:
            risk_level = "High Risk"
            link = "https://my.clevelandclinic.org/health/diseases/21501-type-2-diabetes"

        # Per-category qualitative feedback
        area_messages = {}
        for category in self.category_options.keys():
            r = ratios[category]
            if r <= 0.25:
                msg = "Strong area / lower risk based on this factor."
            elif r <= 0.5:
                msg = "Okay, but there is some room for improvement."
            else:
                msg = "This area is contributing a lot to your risk and may need attention."

            area_messages[category] = msg

        # Identify best and worst areas
        sorted_by_ratio = sorted(ratios.items(), key=lambda x: x[1], reverse=True)
        worst_areas = [name for name, r in sorted_by_ratio if r >= 0.5]
        best_areas = [name for name, r in sorted_by_ratio if r <= 0.25]

        worst_str = ", ".join(worst_areas) if worst_areas else "None identified based on what you entered."
        best_str = ", ".join(best_areas) if best_areas else "None clearly stood out based on what you entered."

        breakdown_lines = [f"- {cat}: {msg}" for cat, msg in area_messages.items()]

        result_text = (
            f"Overall risk score: {total} ({risk_level}).\n\n"
            f"Areas that most increase your risk:\n{worst_str}\n\n"
            f"Areas you appear to be doing well in:\n{best_str}\n\n"
            "Category breakdown:\n" +
            "\n".join(breakdown_lines) +
            "\n\nNote: This tool is for educational purposes only and is not a medical diagnosis."
        )

        return result_text, link


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
