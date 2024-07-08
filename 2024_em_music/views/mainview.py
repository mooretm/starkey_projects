""" Main view for Speaker Balancer. """

###########
# Imports #
###########
# Import GUI packages
import tkinter as tk
from tkinter import ttk


#########
# BEGIN #
#########
class MainFrame(ttk.Frame):
    def __init__(self, parent, settings, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Assign variables
        self.parent = parent
        self.settings = settings

        # Populate frame with widgets
        self.draw_widgets()


    def draw_widgets(self):
        """ Populate the main view with all widgets. """
        ##########
        # Styles #
        ##########
        # Fonts
        self.style = ttk.Style(self)
        self.style.configure('Heading.TLabel', font=('TkDefaultFont', 16))
        self.style.configure('Big.TLabel', font=('TkDefaultFont', 15))
        self.style.configure('Medium.TLabel', font=('TkDefaultFont', 12))
        self.style.configure('TLabel', font=('TkDefaultFont', 10))
        self.style.configure('Big.TButton', font=('TKDefaultFont', 15))
        # Colors
        custom_color = 'DeepSkyBlue' # 'SystemWindow' 'DeepSkyBlue'


        ##########
        # Header #
        ##########
        # Heading
        tk.Label(self, text="New Project", bg=custom_color,
                 font=('TkDefaultFont', 20), 
                 #borderwidth=0.5, 
                 #relief='groove'
                 ).grid(row=5, column=5, sticky='nsew')
        # ttk.Separator(self, orient='horizontal').grid(row=10, column=5, 
        #     columnspan=30, sticky='we')


        #################
        # Create frames #
        #################
        options = {'padx':10, 'pady':10}
        options_small = {'padx':5, 'pady':5}
        
        # Main frame
        frm_main = ttk.Frame(self)
        frm_main.grid(column=5, row=5, **options)


        #########################
        # Presentation Controls #
        #########################
        # # Example:
        # ttk.Label(lfrm_playback, text="Duration (s):").grid(
        #     column=5, row=5, sticky='e', **options_small)
        # ent_dur = ttk.Entry(lfrm_playback, 
        #     textvariable=self.settings['duration'], width=6)
        # ent_dur.grid(column=10, row=5, sticky='w', **options_small)


    #############
    # Functions #
    #############
    def _on_submit(self):
        """ Send submit event to controller. """
        self.event_generate('<<MainSubmit>>')


    def _on_save(self):
        """ Send save event to controller. """
        self.event_generate('<<MainSave>>')


    def _on_play(self):
        """ Send start audio playback event to controller. """
        self.event_generate('<<MainPlay>>')


    def _on_stop(self):
        """ Send stop audio playback event to controller. """
        self.event_generate('<<MainStop>>')
