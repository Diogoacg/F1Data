import fastf1
import fastf1.plotting
import customtkinter as ctk
import functions as f
import os
from PIL import Image
from tkinter import filedialog, messagebox

fastf1.plotting.setup_mpl()

class F1DataApp:
    def __init__(self):
        ctk.set_appearance_mode('dark')
        ctk.set_default_color_theme('blue')
        
        self.window = ctk.CTk()
        self.window.title("F1Data - Formula 1 Analysis Tool")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)
        
        self.create_main_interface()
        
    def create_main_interface(self):
        # Create header frame
        header_frame = ctk.CTkFrame(self.window)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        # Check if logo file exists and add it
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "f1data_logo.png")
        if os.path.exists(logo_path):
            logo_img = ctk.CTkImage(Image.open(logo_path), size=(120, 40))
            logo_label = ctk.CTkLabel(header_frame, image=logo_img, text="")
            logo_label.pack(side="left", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(header_frame, 
                                 text="Formula 1 Data Analysis Tool", 
                                 font=ctk.CTkFont(size=24, weight="bold"))
        title_label.pack(side="left", padx=20, pady=15)
        
        # Create a tabview for better organization
        self.tabview = ctk.CTkTabview(self.window)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create tabs
        self.lap_analysis_tab = self.tabview.add("Lap Analysis")
        self.race_analysis_tab = self.tabview.add("Race Analysis")
        self.team_analysis_tab = self.tabview.add("Team Analysis")
        self.testing_tab = self.tabview.add("Testing Analysis")
        self.settings_tab = self.tabview.add("Settings")
        
        # Populate the tabs
        self.create_lap_analysis_tab()
        self.create_race_analysis_tab()
        self.create_team_analysis_tab()
        self.create_testing_tab()
        self.create_settings_tab()
        
        # Create footer
        footer_frame = ctk.CTkFrame(self.window)
        footer_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        # Version info and credits
        credits_label = ctk.CTkLabel(footer_frame, text="F1Data v1.1 | By Diogo")
        credits_label.pack(side="left", padx=10, pady=5)
        
        # Exit button
        exit_button = ctk.CTkButton(footer_frame, text="Exit", command=self.window.destroy, 
                                  fg_color="transparent", border_width=1,
                                  text_color=("gray10", "#DCE4EE"), width=80)
        exit_button.pack(side="right", padx=10, pady=5)
        
    def create_lap_analysis_tab(self):
        # Common parameters frame
        params_frame = ctk.CTkFrame(self.lap_analysis_tab)
        params_frame.pack(fill='x', padx=10, pady=10)
        
        params_label = ctk.CTkLabel(params_frame, text="Session Parameters", 
                                  font=ctk.CTkFont(weight="bold"))
        params_label.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")
        
        # Year input
        year_label = ctk.CTkLabel(params_frame, text="Year:")
        year_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.year_entry = ctk.CTkEntry(params_frame, width=80)
        self.year_entry.insert(0, "2023")
        self.year_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Track input
        track_label = ctk.CTkLabel(params_frame, text="Track:")
        track_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.track_entry = ctk.CTkEntry(params_frame, width=120)
        self.track_entry.insert(0, "Austria")
        self.track_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Session input
        session_label = ctk.CTkLabel(params_frame, text="Session:")
        session_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.session_var = ctk.StringVar(value="R")
        session_dropdown = ctk.CTkOptionMenu(params_frame, 
                                          values=["FP1", "FP2", "FP3", "Q", "R", "S"],
                                          variable=self.session_var)
        session_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Drivers input
        drivers_label = ctk.CTkLabel(params_frame, text="Drivers:")
        drivers_label.grid(row=2, column=2, padx=10, pady=10, sticky="e")
        self.drivers_entry = ctk.CTkEntry(params_frame, width=220)
        self.drivers_entry.insert(0, "VER HAM LEC")
        self.drivers_entry.grid(row=2, column=3, padx=10, pady=10, sticky="w")
        
        # Lap analysis buttons frame
        buttons_frame = ctk.CTkFrame(self.lap_analysis_tab)
        buttons_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button1 = ctk.CTkButton(buttons_frame, 
                              text="Compare Speed Telemetry", 
                              command=lambda: self.execute_function(1))
        button1.pack(padx=20, pady=15, fill='x')
        
        button3 = ctk.CTkButton(buttons_frame, 
                              text="Compare Lap Times Evolution", 
                              command=lambda: self.execute_function(3))
        button3.pack(padx=20, pady=15, fill='x')
        
        # New button for tyre compound comparison
        button_tyre = ctk.CTkButton(buttons_frame, 
                                  text="Compare Tyre Compound Performance", 
                                  command=self.compare_tyre_compounds)
        button_tyre.pack(padx=20, pady=15, fill='x')
        
        # New button for sector times comparison
        button_sectors = ctk.CTkButton(buttons_frame, 
                                     text="Compare Sector Times", 
                                     command=self.compare_sector_times)
        button_sectors.pack(padx=20, pady=15, fill='x')
        
    def create_race_analysis_tab(self):
        # Race analysis frame
        params_frame = ctk.CTkFrame(self.race_analysis_tab)
        params_frame.pack(fill='x', padx=10, pady=10)
        
        params_label = ctk.CTkLabel(params_frame, text="Race Parameters", 
                                  font=ctk.CTkFont(weight="bold"))
        params_label.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")
        
        # Year input
        year_label = ctk.CTkLabel(params_frame, text="Year:")
        year_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.race_year_entry = ctk.CTkEntry(params_frame, width=80)
        self.race_year_entry.insert(0, "2023")
        self.race_year_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Track input
        track_label = ctk.CTkLabel(params_frame, text="Race:")
        track_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.race_track_entry = ctk.CTkEntry(params_frame, width=120)
        self.race_track_entry.insert(0, "Austria")
        self.race_track_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Race analysis buttons
        buttons_frame = ctk.CTkFrame(self.race_analysis_tab)
        buttons_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button2 = ctk.CTkButton(buttons_frame, 
                              text="Compare Mean Lap Times", 
                              command=lambda: self.execute_race_function(2))
        button2.pack(padx=20, pady=15, fill='x')
        
        button4 = ctk.CTkButton(buttons_frame, 
                              text="Race History Delta Chart", 
                              command=lambda: self.execute_race_function(4))
        button4.pack(padx=20, pady=15, fill='x')
        
        # New race analysis features
        button_pitstops = ctk.CTkButton(buttons_frame, 
                                      text="Pit Stop Analysis", 
                                      command=self.analyze_pitstops)
        button_pitstops.pack(padx=20, pady=15, fill='x')
        
        button_overtakes = ctk.CTkButton(buttons_frame, 
                                       text="Overtaking Positions", 
                                       command=self.analyze_overtakes)
        button_overtakes.pack(padx=20, pady=15, fill='x')
        
    def create_team_analysis_tab(self):
        params_frame = ctk.CTkFrame(self.team_analysis_tab)
        params_frame.pack(fill='x', padx=10, pady=10)
        
        params_label = ctk.CTkLabel(params_frame, text="Team Analysis Parameters", 
                                  font=ctk.CTkFont(weight="bold"))
        params_label.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")
        
        # Year input
        year_label = ctk.CTkLabel(params_frame, text="Year:")
        year_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.team_year_entry = ctk.CTkEntry(params_frame, width=80)
        self.team_year_entry.insert(0, "2023")
        self.team_year_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Track input
        track_label = ctk.CTkLabel(params_frame, text="Race/Track:")
        track_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.team_track_entry = ctk.CTkEntry(params_frame, width=120)
        self.team_track_entry.insert(0, "Monaco")
        self.team_track_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Session input
        session_label = ctk.CTkLabel(params_frame, text="Session:")
        session_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        
        self.team_session_var = ctk.StringVar(value="R")
        session_dropdown = ctk.CTkOptionMenu(params_frame, 
                                          values=["FP1", "FP2", "FP3", "Q", "R", "S"],
                                          variable=self.team_session_var)
        session_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Team analysis buttons
        buttons_frame = ctk.CTkFrame(self.team_analysis_tab)
        buttons_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button5 = ctk.CTkButton(buttons_frame, 
                              text="Team Pace Comparison", 
                              command=lambda: self.execute_team_function(5))
        button5.pack(padx=20, pady=15, fill='x')
        
        button_development = ctk.CTkButton(buttons_frame, 
                                        text="Team Development Throughout Season", 
                                        command=self.analyze_team_development)
        button_development.pack(padx=20, pady=15, fill='x')
        
        button_teammates = ctk.CTkButton(buttons_frame, 
                                      text="Teammates Comparison", 
                                      command=self.compare_teammates)
        button_teammates.pack(padx=20, pady=15, fill='x')
        
    def create_testing_tab(self):
        params_frame = ctk.CTkFrame(self.testing_tab)
        params_frame.pack(fill='x', padx=10, pady=10)
        
        params_label = ctk.CTkLabel(params_frame, text="Testing Session Parameters", 
                                  font=ctk.CTkFont(weight="bold"))
        params_label.grid(row=0, column=0, columnspan=4, padx=10, pady=(10, 5), sticky="w")
        
        # Year input
        year_label = ctk.CTkLabel(params_frame, text="Year:")
        year_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.testing_year_entry = ctk.CTkEntry(params_frame, width=80)
        self.testing_year_entry.insert(0, "2023")
        self.testing_year_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        
        # Test number
        test_label = ctk.CTkLabel(params_frame, text="Test Number:")
        test_label.grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.test_number_entry = ctk.CTkEntry(params_frame, width=80)
        self.test_number_entry.insert(0, "1")
        self.test_number_entry.grid(row=1, column=3, padx=10, pady=10, sticky="w")
        
        # Session number
        session_label = ctk.CTkLabel(params_frame, text="Session Day:")
        session_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.test_session_entry = ctk.CTkEntry(params_frame, width=80)
        self.test_session_entry.insert(0, "1")
        self.test_session_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
        
        # Testing analysis buttons
        buttons_frame = ctk.CTkFrame(self.testing_tab)
        buttons_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        button6 = ctk.CTkButton(buttons_frame, 
                              text="Compare Pace on Testing", 
                              command=lambda: self.execute_testing_function(6))
        button6.pack(padx=20, pady=15, fill='x')
        
        button_long_runs = ctk.CTkButton(buttons_frame, 
                                       text="Long Runs Analysis", 
                                       command=self.analyze_long_runs)
        button_long_runs.pack(padx=20, pady=15, fill='x')
        
    def create_settings_tab(self):
        settings_frame = ctk.CTkFrame(self.settings_tab)
        settings_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Appearance settings
        appearance_label = ctk.CTkLabel(settings_frame, text="Appearance", 
                                      font=ctk.CTkFont(weight="bold"))
        appearance_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        appearance_mode_label = ctk.CTkLabel(settings_frame, text="Appearance Mode:")
        appearance_mode_label.pack(anchor="w", padx=20, pady=(10, 0))
        
        appearance_mode = ctk.CTkOptionMenu(settings_frame, 
                                         values=["Dark", "Light", "System"],
                                         command=self.change_appearance_mode)
        appearance_mode.pack(anchor="w", padx=20, pady=(0, 10))
        
        # Theme settings
        theme_label = ctk.CTkLabel(settings_frame, text="Color Theme:")
        theme_label.pack(anchor="w", padx=20, pady=(10, 0))
        
        theme_option = ctk.CTkOptionMenu(settings_frame, 
                                       values=["blue", "dark-blue", "green"])
        theme_option.pack(anchor="w", padx=20, pady=(0, 20))
        
        # Data settings
        data_label = ctk.CTkLabel(settings_frame, text="Data Settings", 
                                font=ctk.CTkFont(weight="bold"))
        data_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Cache directory
        cache_label = ctk.CTkLabel(settings_frame, text="FastF1 Cache Directory:")
        cache_label.pack(anchor="w", padx=20, pady=(10, 0))
        
        cache_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        cache_frame.pack(anchor="w", fill="x", padx=20, pady=(0, 10))
        
        self.cache_entry = ctk.CTkEntry(cache_frame, width=300)
        self.cache_entry.insert(0, os.path.expanduser("~/.fastf1_cache"))
        self.cache_entry.pack(side="left", padx=(0, 10))
        
        browse_button = ctk.CTkButton(cache_frame, text="Browse", 
                                    command=self.browse_cache_directory, 
                                    width=80)
        browse_button.pack(side="left")
        
        # Save settings
        save_button = ctk.CTkButton(settings_frame, text="Save Settings", 
                                  command=self.save_settings)
        save_button.pack(anchor="center", padx=20, pady=20)
        
        # About section
        about_label = ctk.CTkLabel(settings_frame, text="About", 
                                 font=ctk.CTkFont(weight="bold"))
        about_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        about_text = ctk.CTkLabel(settings_frame, 
                               text="F1Data is a tool for statistical analysis of Formula 1 data.\n" + 
                               "It uses the FastF1 API to retrieve and analyze data from F1 sessions.")
        about_text.pack(anchor="w", padx=20, pady=0)
        
        version_label = ctk.CTkLabel(settings_frame, text="Version: 1.1")
        version_label.pack(anchor="w", padx=20, pady=(10, 0))
        
    def execute_function(self, func_num):
        try:
            year = int(self.year_entry.get())
            track = self.track_entry.get()
            session_type = self.session_var.get()
            drivers = self.drivers_entry.get().split()
            
            session = fastf1.get_session(year, track, session_type)
            session.load()
            
            if func_num == 1:
                f.plot_pace_comparison(drivers, session)
            elif func_num == 3:
                f.plot_lap_times(drivers, session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def execute_race_function(self, func_num):
        try:
            year = int(self.race_year_entry.get())
            track = self.race_track_entry.get()
            
            session = fastf1.get_session(year, track, 'R')
            session.load()
            
            if func_num == 2:
                f.plot_mean_lap_time(session)
            elif func_num == 4:
                f.plot_race_history(session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def execute_team_function(self, func_num):
        try:
            year = int(self.team_year_entry.get())
            track = self.team_track_entry.get()
            session_type = self.team_session_var.get()
            
            session = fastf1.get_session(year, track, session_type)
            session.load()
            
            if func_num == 5:
                f.plot_team_pace_comparison(session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def execute_testing_function(self, func_num):
        try:
            year = int(self.testing_year_entry.get())
            test_num = int(self.test_number_entry.get())
            session_num = int(self.test_session_entry.get())
            
            if func_num == 6:
                f.test_pace_comparison(year, test_num, session_num)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def compare_tyre_compounds(self):
        try:
            year = int(self.year_entry.get())
            track = self.track_entry.get()
            session_type = self.session_var.get()
            
            # Display dialog to select driver
            root = ctk.CTk()
            root.withdraw()
            
            from tkinter import simpledialog
            driver = simpledialog.askstring(
                "Driver Selection",
                "Enter driver code for tyre analysis (e.g. HAM, VER):",
                initialvalue=""
            )
            
            if driver:
                session = fastf1.get_session(year, track, session_type)
                session.load()
                f.compare_tyre_compounds(driver, session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def compare_sector_times(self):
        try:
            year = int(self.year_entry.get())
            track = self.track_entry.get()
            session_type = self.session_var.get()
            drivers = self.drivers_entry.get().split()
            
            session = fastf1.get_session(year, track, session_type)
            session.load()
            
            f.compare_sector_times(drivers, session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def analyze_pitstops(self):
        try:
            year = int(self.race_year_entry.get())
            track = self.race_track_entry.get()
            
            session = fastf1.get_session(year, track, 'R')
            session.load()
            
            f.analyze_pitstops(session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def analyze_overtakes(self):
        try:
            year = int(self.race_year_entry.get())
            track = self.race_track_entry.get()
            
            session = fastf1.get_session(year, track, 'R')
            session.load()
            
            f.analyze_overtakes(session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def analyze_team_development(self):
        try:
            year = int(self.team_year_entry.get())
            f.analyze_team_development(year)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def compare_teammates(self):
        try:
            year = int(self.team_year_entry.get())
            team = self.team_track_entry.get()
            
            f.compare_teammates(year, team)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            
    def analyze_long_runs(self):
        try:
            year = int(self.testing_year_entry.get())
            track = self.team_track_entry.get()
            session_type = self.team_session_var.get()
            
            session = fastf1.get_session(year, track, session_type)
            session.load()
            
            f.analyze_long_runs(session)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode.lower())
    
    def browse_cache_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.cache_entry.delete(0, 'end')
            self.cache_entry.insert(0, directory)
    
    def save_settings(self):
        # Save settings functionality would be implemented here
        cache_dir = self.cache_entry.get()
        if os.path.isdir(cache_dir):
            fastf1.Cache.enable_cache(cache_dir)
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully!")
        else:
            messagebox.showerror("Invalid Directory", "Please select a valid directory for the cache.")
    
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = F1DataApp()
    app.run()