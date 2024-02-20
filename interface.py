
    
from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import numpy as np
import datetime
import tkinter as tk
from fastf1.ergast import Ergast
import customtkinter as ctk
from tkinter import simpledialog
fastf1.plotting.setup_mpl()
import customtkinter as ctk
import functions as f


def get_details(func):
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')
    window = ctk.CTk()
    window.title("F1 stats tool")
    window.geometry("400x400")
    
    year_label = ctk.CTkLabel(window, text="Enter the year:")
    year_label.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
    year_entry = ctk.CTkEntry(window)
    year_entry.insert(0, "2023")  # Valor padrão
    year_entry.grid(row=0, column=1, padx=20, pady=20, sticky="ew")

    # track label
    track_label = ctk.CTkLabel(window, text="Enter the track:")
    track_label.grid(row=1, column=0, padx=20, pady=20, sticky="ew")
    track_entry = ctk.CTkEntry(window)
    track_entry.insert(0, "Austria")  # Valor padrão
    track_entry.grid(row=1, column=1, padx=20, pady=20, sticky="ew")

    # session label
    session_label = ctk.CTkLabel(window, text="Enter the session:")
    session_label.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
    session_entry = ctk.CTkEntry(window)
    session_entry.insert(0, "R")  # Valor padrão
    session_entry.grid(row=2, column=1, padx=20, pady=20, sticky="ew")

    # drivers label
    drivers_label = ctk.CTkLabel(window, text="Enter the drivers:")
    drivers_label.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
    drivers_entry = ctk.CTkEntry(window)
    drivers_entry.insert(0, "VER BOT HAM")  # Valor padrão
    drivers_entry.grid(row=3, column=1, padx=20, pady=20, sticky="ew")
    
    testing_session = ctk.CTkLabel(window, text="Testing session")
    testing_session.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
    testing_entry = ctk.CTkEntry(window)
    testing_entry.insert(0, "1 1")  # Valor padrão
    testing_entry.grid(row=4, column=1, padx=20, pady=20, sticky="ew")

    # button retorna os valores inseridos pela funcao  
    def on_enter():
        year = int(year_entry.get())
        track = track_entry.get()
        session = session_entry.get()
        drivers = drivers_entry.get().split()
        testing = testing_entry.get().split()
        session = fastf1.get_session(year, track, session)
        
        session.load()
        if func == 1:
            f.plot_pace_comparison(drivers, session)
        elif func == 2:
            f.plot_mean_lap_time(session)
        elif func == 3:
            f.plot_lap_times(drivers, session)
        elif func == 4:
            drivers = ['VER', 'PER', 'LEC', 'SAI', 'HAM', 'RUS', 'GAS', 'NOR', 'PIA', 'ZHO', 'BOT', 'ALO', 'STR', 'MAG', 'HUL']
            f.plot_race_history(session)
        elif func == 5:
            f.plot_team_pace_comparison(session)
        elif func == 6:
            f.test_pace_comparison(year, int(testing[0]), int(testing[1]))

    # button
    button = ctk.CTkButton(window, text="Enter", command=on_enter)
    button.grid(row=5, column=1, padx=20, pady=20, sticky="ew")

    # Envie entradas para o programa principal
    window.mainloop()

def main():
    ctk.set_appearance_mode('dark')
    ctk.set_default_color_theme('dark-blue')
    window = ctk.CTk()
    window.title("F1 stats tool")
    window.geometry("800x800")

    label = ctk.CTkLabel(window, text="Welcome to the F1 stats tool! \n By Diogo")
    label.pack(padx=10, pady=10)

    button1 = ctk.CTkButton(window, text="Compare the fastest laps of selected drivers in a session", command=lambda: get_details(1))
    button1.pack(padx=10, pady=10)

    button2 = ctk.CTkButton(window, text="Compare the mean lap times of all drivers", command=lambda: get_details(2))
    button2.pack(padx=10, pady=10)

    button3 = ctk.CTkButton(window, text="Compare the lap times of selected drivers in a session", command=lambda: get_details(3))
    button3.pack(padx=10, pady=10)

    button4 = ctk.CTkButton(window, text="Compare race history of selected drivers in a session by delta time", command=lambda: get_details(4)) 
    button4.pack(padx=10, pady=10)
    
    button5 = ctk.CTkButton(window, text="Compare teams pace on a certain track", command=lambda: get_details(5)) 
    button5.pack(padx=10, pady=10)
    
    button6 = ctk.CTkButton(window, text="Compare Pace on Testing", command=lambda: get_details(6))
    button6.pack(padx=10, pady=10)
    
    button7 = ctk.CTkButton(window, text="Exit", command=window.destroy)
    button7.pack(padx=10, pady=10)

    window.mainloop()

if __name__ == "__main__":
    main()