from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooser
from kivymd.uix.filemanager import MDFileManager
from io import BytesIO
from PIL import Image
from PIL import ExifTags  # To access EXIF data
from kivy.uix.image import Image as KivyImage, CoreImage
from kivy.graphics.texture import Texture
import subprocess

from database import DataBase
from kivy.core.window import Window

Window.size = 	(360, 640)

class HomeWindow(Screen):
    pass

class CreateAccountWindow(Screen):
    mat_no = ObjectProperty(None)
    namee = ObjectProperty(None)    
    department = ObjectProperty(None)
    level = ObjectProperty(None)
    password = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.profile_image = None
        super().__init__(**kwargs)
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path,
        )
        
        self.image_path = ""        

    def file_manager_open(self):
        self.file_manager.show("/")

    def select_path(self, path):
        self.exit_manager()
        self.image_path = path
        # self.image.source = path

    def exit_manager(self, *args):
        self.file_manager.close()

    def signup_button(self):
        if self.namee.text != "" and self.mat_no.text != "" and self.department.text != "" and self.level.text != "":
            if self.password.text != "":
                with open(self.image_path, 'rb') as image_file:
                    self.profile_image = image_file.read()
                result = db.add_user(
                    self.mat_no.text,
                    self.namee.text,
                    self.department.text,
                    self.level.text,
                    self.password.text,
                    self.profile_image,  # Pass the profile image data
                    )
                if result == 1:
                    self.reset()
                    self.manager.current = "login"
                else:
                    self.invalidForm()
            else:
                self.invalidForm()
        else:
            self.invalidForm()

    def login(self):
        self.reset()
        self.manager.current = "login"

    def reset(self):
        self.mat_no.text = ""
        self.namee.text = ""        
        self.department.text = "" 
        self.level.text = ""

    def invalidForm(self):
        pop = MDDialog(title='Invalid Form',
                       text='Please fill in all inputs with valid information.')
        pop.open()

class LoginWindow(Screen):
    mat_no = ObjectProperty(None)
    password = ObjectProperty(None)

    def loginBtn(self):
        if db.validate(self.mat_no.text, self.password.text):
            # MyMainApp.user_matricno = self.mat_no.text  # Set the user's MatricNo
            ProfileWindow.current = self.mat_no.text  # Set the current attribute
            self.reset()
            self.manager.current = "profile"
        else:
            self.invalidLogin()

    def createBtn(self):
        self.reset()
        self.manager.current = "create"

    def reset(self):
        self.mat_no.text = ""
        self.password.text = ""

    def invalidLogin(self):
        pop = MDDialog(title='Invalid Login',
                       text='Invalid username or password.')
        pop.open()

class ProfileWindow(Screen):
    mat_no = ObjectProperty(None)
    n = ObjectProperty(None)
    department = ObjectProperty(None)
    level = ObjectProperty(None)
    profile_image = ObjectProperty(None)  # Add a profile_image property
    

    def on_enter(self, *args):
        user_data = db.get_user(self.current)
        if user_data:
            name, department, level, password, profile_image_data = user_data
            self.n.text = "Name: " + name
            self.mat_no.text = "Matric No: " + self.current
            self.department.text = "Department: " + department
            self.level.text = "Level: " + str(level)

            # Convert the binary blob data to an image
            if profile_image_data:
                image = Image.open(BytesIO(profile_image_data))

                # Check for the image's EXIF data to fix orientation
                try:
                    for orientation in ExifTags.TAGS.keys():
                        if ExifTags.TAGS[orientation] == 'Orientation':
                            break
                    exif = dict(image._getexif().items())

                    if exif[orientation] == 3:
                        image = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image = image.rotate(90, expand=True)
                except (AttributeError, KeyError, IndexError):
                    # No EXIF data or no 'Orientation' tag found
                    pass

                image = image.rotate(180)
            
                # Create a Kivy Texture from the PIL Image
                kivy_texture = Texture.create(size=(image.width, image.height))
                kivy_texture.blit_buffer(image.tobytes(), colorfmt='rgb', bufferfmt='ubyte')
                
                # Set the texture of your profile_image widget
                self.profile_image.texture = kivy_texture
    def capture_card(self):
        # Get the FloatLayout containing the card widget
        card_layout = self.ids.card_layout

        # Export the FloatLayout as an image
        screenshot_filename = "id_card.png"
        card_layout.export_to_png(screenshot_filename)

        # Open the captured image with the default image viewer
        try:
            import os
            os.system(f"start {screenshot_filename}")  # Open the image using the default system viewer
        except Exception as e:
            print(f"Error opening the captured image: {e}")

db = DataBase("id_card.db")

class WindowManager(ScreenManager):
    pass

class IdCard(MDApp):
  
    user_matricno = None 
    def build(self):
        kv = Builder.load_string('''
# Your KV code goes here

ScreenManager:
    HomeWindow:
    CreateAccountWindow:
    LoginWindow:
    ProfileWindow:

<HomeWindow>:
    name: 'home'
    FloatLayout:
        BoxLayout:                   
            orientation:"vertical"
            BoxLayout:
                canvas:
                    Color:
                        rgba:  0,76/255, 153/155,1 #Blue 
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius:[0,0,40,40]

            BoxLayout:
                orientation:"vertical"

                BoxLayout:
                    orientation:"vertical"
                    Widget:
                        canvas:
                            Color:
                                rgba: 1,1,1,1
                            Rectangle:
                                size: self.size
                                pos: self.pos
            BoxLayout:
                orientation:"vertical"

                BoxLayout:
                    orientation:"vertical"
                    Widget:
                        canvas:
                            Color:
                                rgba: 1,1,1,1
                            Rectangle:
                                size: self.size
                                pos: self.pos

        MDCard:
            oriantation:"vertical"
            size_hint:[.8,.6]
            pos_hint:{"center_x":0.5, "center_y":0.6}
            padding:[20,10,20,10]

            BoxLayout:
                orientation:"vertical"

                MDLabel:
                    pos: self.pos
                    text:"STUDENT ID CARD"
                    font_size: 50
                    halign:"center"
                    theme_text_color:"Primary"
                    bold: True

                MDFillRoundFlatButton:
                    text:"LOGIN"
                    size_hint_x:0.5
                    pos_hint:{"center_x":.5}
                    on_release:
                        app.root.current = "login"

                MDFlatButton:
                    text:"Create Account"
                    pos_hint:{"center_x":.5}
                    #pos: self.pos
                    size_hint_x: .5
                    on_release:
                        app.root.current = "create"

<CreateAccountWindow>:
    name: "create"

    namee: namee
    mat_no: mat_no
    department: dept
    level: level
    password: password
    

    FloatLayout:
        BoxLayout:                   
            orientation:"vertical"
            BoxLayout:
                canvas:
                    Color:
                        rgba:  0,76/255, 153/155,1 #Blue 
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius:[0,0,40,40]
                MDIconButton:
                    icon: "arrow-left"
                    md_bg_color: 0, 0, 0, .2
                    x: "12dp"
                    pos_hint: {"top": 1}
                    on_release: app.root.current = "home"                

            BoxLayout:
                orientation:"vertical"

                BoxLayout:
                    orientation:"vertical"
                    Widget:
                        canvas:
                            Color:
                                rgba: 1,1,1,1
                            Rectangle:
                                #size: self.size
                                #pos: self.pos
            BoxLayout:
                orientation:"vertical"

                BoxLayout:
                    orientation:"vertical"
                    Widget:
                        canvas:
                            Color:
                                rgba: 1,1,1,1
                            Rectangle:
                                #size: self.size
                                #pos: self.pos

        MDCard:
            oriantation:"vertical"
            size_hint:[.8,.7]
            pos_hint:{"center_x":0.5, "center_y":0.6}
            padding:[20,10,20,10]

            BoxLayout:
                orientation:"vertical"

                MDLabel:
                    pos: self.pos
                    text:"Create an Account"
                    font_size: 50
                    halign:"center"
                    theme_text_color:"Custom"
                    text_color: 0,1,0,1
                    bold: True

                BoxLayout:
                    orientation:"vertical"
                    #size: self.size
                    MDTextField:
                        id: namee
                        hint_text: "Full Name"
                        icon_right: "account"
                        required: True
                    MDTextField:
                        id: mat_no
                        hint_text: "Matriculation Number"
                        icon_right: "account-multiple-plus"
                        required: True
                    MDTextField:
                        id: dept
                        hint_text: "Department"
                        icon_right: "account-multiple-plus"
                        required: True
                    MDTextField:
                        id: level
                        hint_text: "Level"
                        icon_right: "account-multiple-plus"
                        required: True
                    MDTextField:
                        id: password
                        hint_text: "Create Password"
                        icon_right: "key-variant"
                        required: True
                        password:True
                    MDRaisedButton:
                        text: "Upload Image"
                        on_release: root.file_manager_open()                    
                    
                    MDFillRoundFlatButton:
                        text:"Create Account"
                        pos_hint:{"center_x":.5}
                        #pos: self.pos
                        size_hint_x: .5
                        on_release:
                            root.manager.transition.direction = "left"
                            root.signup_button()

                    MDFlatButton:
                        text:"Use existing account?"
                        size_hint_x:0.5
                        pos_hint:{"center_x":.5}
                        on_release:
                            root.manager.transition.direction = "left"
                            app.root.current = "login"
                            # root.login()  
<LoginWindow>:
    name: "login"

    mat_no: mat_no
    password: login_password

    FloatLayout:
    BoxLayout:                   
        orientation:"vertical"
        BoxLayout:
            canvas:
                Color:
                    rgba:  0,76/255, 153/155,1 #Blue 
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius:[0,0,40,40]
            MDIconButton:
                icon: "arrow-left"
                md_bg_color: 0, 0, 0, .2
                x: "12dp"
                pos_hint: {"top": 1}
                on_release: app.root.current = "home"              

        BoxLayout:
            orientation:"vertical"

            BoxLayout:
                orientation:"vertical"
                Widget:
                    canvas:
                        Color:
                            rgba: 1,1,1,1
                        Rectangle:
                            size: self.size
                            pos: self.pos
        BoxLayout:
            orientation:"vertical"

            BoxLayout:
                orientation:"vertical"
                Widget:
                    canvas:
                        Color:
                            rgba: 1,1,1,1
                        Rectangle:
                            size: self.size
                            pos: self.pos

    MDCard:
        oriantation:"vertical"
        size_hint:[.8,.6]
        pos_hint:{"center_x":0.5, "center_y":0.6}
        padding:[20,10,20,10]

        BoxLayout:
            orientation:"vertical"

            MDLabel:
                pos: self.pos
                text:"ID CARD"
                font_size: 60
                halign:"center"
                theme_text_color:"Primary"
                bold: True
                

            MDLabel:
                #pos: self.pos
                text:"LOGIN PAGE"
                font_size: 50
                halign:"center"
                theme_text_color:"Custom"
                text_color: 0,1,0,1
                bold: True

            MDTextField:
                id: mat_no
                hint_text:"Matric No"
                icon_right: "account"
            
            MDTextField:
                id: login_password
                hint_text:"Password"
                password:True
                icon_right: 'key-variant'


            MDFillRoundFlatButton:
                text:"LOGIN"
                size_hint_x:0.5
                pos_hint:{"center_x":.5}
                on_release:
                    root.loginBtn()

            MDFlatButton:
                text:"Create an account?"
                pos_hint:{"center_x":.5}
                #pos: self.pos
                size_hint_x: .5
                on_release:
                    app.root.current = "create"

<ProfileWindow>:
    name: 'profile'

    mat_no: mat_no
    n: n
    department: department
    level: level
    profile_image: profile_image

    FloatLayout:
        BoxLayout:
            canvas:
                Color:
                    rgba: 0, 128/255, 128/255, 1
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [20, 20, 0, 0]  # Adjust the radius to create rounded corners

            MDIconButton:
                icon: "arrow-left"
                md_bg_color: 0, 0, 0, .2
                x: "12dp"
                pos_hint: {"top": 1}
                on_release: app.root.current = "home"

        FloatLayout:
            id: card_layout
            Image:
                source: 'images (3).jpg'  # Adjust the image path
                size: self.size
                pos: self.pos
            MDCard:
                id: card_widget
                orientation: "vertical"
                size_hint: [0.8, 0.6]
                pos_hint: {"center_x": 0.5, "center_y": 0.5}
                border_radius: 20
                radius: [30]
                md_bg_color: "lightblue"

                MDIconButton:
                    icon: "account-school"
                    pos_hint: {"top": 1, "left": 1}                    
                Image:
                    id: profile_image
                    source: ""
                    size_hint: 1, None
                    height: "170dp"
                    width: "200dp"
                    allow_stretch: True  # Maintain aspect ratio while fitting within the space
                    keep_ratio: True

                MDLabel:
                    id: n
                    text: "Name: "
                    font_size: 25
                    halign: 'center'
                    theme_text_color: "Primary"

                MDLabel:
                    id: mat_no
                    text: "Matric No: "
                    halign: 'center'
                    theme_text_color: "Secondary"

                MDLabel:
                    id: department
                    text: "Department: "
                    font_size: 20
                    halign: 'center'
                    theme_text_color: "Primary"

                MDLabel:
                    id: level
                    text: "Level: "
                    halign: 'center'
                    theme_text_color: "Secondary"
        
        
        MDFillRoundFlatButton:
            text: "Save ID Card"
            size_hint: None, None
            size: "150dp", "40dp"
            pos_hint: {"center_x": 0.5, "y": 0.05}
            on_release: root.capture_card()

        MDFillRoundFlatButton:
            text: "Log Out"
            on_release:
                app.root.current = "login"
                root.manager.transition.direction = "down"


''')        
        sm = WindowManager()      
        screens = [HomeWindow(name='home'), LoginWindow(name="login"), CreateAccountWindow(name="create"), ProfileWindow(name="profile")]
        for screen in screens:
            sm.add_widget(screen)
        return sm
    



if __name__ == "__main__":
    IdCard().run()
