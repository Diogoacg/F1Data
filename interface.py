import matplotlib.pyplot as plt
import fastf1
import fastf1.plotting
import numpy as np
import datetime
import customtkinter as ctk
from fastf1.ergast import Ergast
import seaborn as sns
import pandas as pd
import os
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import List, Optional, Tuple, Dict, Any, Union

# Set up the FastF1 plotting
fastf1.plotting.setup_mpl()

# Constants
DEFAULT_YEAR = "2025"
DEFAULT_TRACK = "Australia"
DEFAULT_SESSION = "R"
DEFAULT_DRIVERS = "VER HAM LEC"
DEFAULT_TESTING = "1 1"

# Configure the appearance
ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('dark-blue')

class F1StatsApp:
    def __init__(self, root):
        """Initialize the main application window."""
        self.root = root
        self.root.title("F1 Stats Tool")
        self.root.geometry("900x800")
        self.root.minsize(800, 700)
        
        # Create a frame for embedding plots
        self.plot_frame = None
        
        # Set up the UI
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI elements."""
        # App title
        title_frame = ctk.CTkFrame(self.root)
        title_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="F1 Statistics and Analysis Tool", 
            font=("Helvetica", 24, "bold")
        )
        title_label.pack(pady=10)
        
        subtitle_label = ctk.CTkLabel(
            title_frame, 
            text="Analyze F1 race data with advanced visualization tools",
            font=("Helvetica", 14)
        )
        subtitle_label.pack(pady=(0, 10))
        
        # Main content - button frame and plot frame
        content_frame = ctk.CTkFrame(self.root)
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Button frame
        button_frame = ctk.CTkFrame(content_frame)
        button_frame.pack(side="left", fill="y", padx=(0, 10), pady=10)
        
        # Analysis options
        options_label = ctk.CTkLabel(
            button_frame, 
            text="Analysis Options",
            font=("Helvetica", 16, "bold")
        )
        options_label.pack(pady=(10, 5), padx=10)
        
        # Create buttons for different analyses
        analysis_buttons = [
            ("Compare Fastest Laps", lambda: self.open_analysis_window(self.plot_pace_comparison)),
            ("Mean Lap Times", lambda: self.open_analysis_window(self.plot_mean_lap_time)),
            ("Compare Lap Times", lambda: self.open_analysis_window(self.plot_lap_times)),
            ("Race History Delta", lambda: self.open_analysis_window(self.plot_race_history)),
            ("Team Pace Comparison", lambda: self.open_analysis_window(self.plot_team_pace_comparison)),
            ("Testing Pace Analysis", lambda: self.open_analysis_window(self.plot_testing_pace)),
            ("Driver Championship", lambda: self.open_analysis_window(self.plot_driver_championship)),
            ("Constructor Championship", lambda: self.open_analysis_window(self.plot_constructor_championship)),
            ("Export Data to CSV", lambda: self.open_analysis_window(self.export_data_to_csv)),
            ("Exit", self.root.destroy)
        ]
        
        for text, command in analysis_buttons:
            btn = ctk.CTkButton(
                button_frame, 
                text=text, 
                command=command,
                width=250,
                height=40,
                corner_radius=10,
                font=("Helvetica", 14)
            )
            btn.pack(padx=10, pady=8, fill="x")
        
        # Plot frame - this will be initialized when a plot is created
        self.plot_container = ctk.CTkFrame(content_frame)
        self.plot_container.pack(side="right", fill="both", expand=True, pady=10)
        
        placeholder_label = ctk.CTkLabel(
            self.plot_container, 
            text="Select an analysis option\nto display visualization here",
            font=("Helvetica", 16)
        )
        placeholder_label.pack(expand=True)
        
        # Status bar at the bottom
        status_frame = ctk.CTkFrame(self.root, height=30)
        status_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Ready",
            font=("Helvetica", 12)
        )
        self.status_label.pack(side="left", padx=10)
        
        version_label = ctk.CTkLabel(
            status_frame, 
            text="v2.0",
            font=("Helvetica", 12)
        )
        version_label.pack(side="right", padx=10)

    def update_status(self, message: str):
        """Update the status bar with a message."""
        self.status_label.configure(text=message)
        self.root.update_idletasks()

    def clear_plot_container(self):
        """Clear the plot container to prepare for a new plot."""
        for widget in self.plot_container.winfo_children():
            widget.destroy()
        
        # Create a new frame for the plot
        self.plot_frame = ctk.CTkFrame(self.plot_container)
        self.plot_frame.pack(fill="both", expand=True, padx=10, pady=10)

    def embed_plot(self, figure):
        """Embed a matplotlib figure in the plot container."""
        self.clear_plot_container()
        
        canvas = FigureCanvasTkAgg(figure, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def open_analysis_window(self, analysis_function):
        """Open a window to gather parameters for the selected analysis."""
        details_window = ctk.CTkToplevel(self.root)
        details_window.title("Analysis Parameters")
        details_window.geometry("800x600")
        details_window.update()  # Force update to ensure window is rendered
        details_window.grab_set()  # Now set it as modal
        details_window.grab_set()  # Make window modal
        
        # Create a frame for the form
        form_frame = ctk.CTkFrame(details_window)
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Form title
        title_label = ctk.CTkLabel(
            form_frame, 
            text="Enter Analysis Parameters",
            font=("Helvetica", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="ew")
        
        # Year input
        year_label = ctk.CTkLabel(form_frame, text="Year:", font=("Helvetica", 14))
        year_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        year_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14))
        year_entry.insert(0, DEFAULT_YEAR)
        year_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        
        # Track input
        track_label = ctk.CTkLabel(form_frame, text="Track:", font=("Helvetica", 14))
        track_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        track_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14))
        track_entry.insert(0, DEFAULT_TRACK)
        track_entry.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        
        # Session input
        session_label = ctk.CTkLabel(form_frame, text="Session:", font=("Helvetica", 14))
        session_label.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        session_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14))
        session_entry.insert(0, DEFAULT_SESSION)
        session_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        
        # Help text for session
        session_help = ctk.CTkLabel(
            form_frame, 
            text="R=Race, Q=Qualifying, FP1/FP2/FP3=Practice",
            font=("Helvetica", 12),
            text_color="gray"
        )
        session_help.grid(row=4, column=1, padx=20, pady=(0, 10), sticky="w")
        
        # Drivers input
        drivers_label = ctk.CTkLabel(form_frame, text="Drivers:", font=("Helvetica", 14))
        drivers_label.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        drivers_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14))
        drivers_entry.insert(0, DEFAULT_DRIVERS)
        drivers_entry.grid(row=5, column=1, padx=20, pady=10, sticky="ew")
        
        # Help text for drivers
        drivers_help = ctk.CTkLabel(
            form_frame, 
            text="Enter space-separated driver codes (e.g., VER HAM LEC)",
            font=("Helvetica", 12),
            text_color="gray"
        )
        drivers_help.grid(row=6, column=1, padx=20, pady=(0, 10), sticky="w")
        
        # Testing input (only shown for testing analysis)
        testing_label = ctk.CTkLabel(form_frame, text="Testing Session:", font=("Helvetica", 14))
        testing_entry = ctk.CTkEntry(form_frame, font=("Helvetica", 14))
        testing_entry.insert(0, DEFAULT_TESTING)
        
        if analysis_function == self.plot_testing_pace:
            testing_label.grid(row=7, column=0, padx=20, pady=10, sticky="w")
            testing_entry.grid(row=7, column=1, padx=20, pady=10, sticky="ew")
            
            # Help text for testing
            testing_help = ctk.CTkLabel(
                form_frame, 
                text="Format: 'Test# Day#' (e.g., '1 1' for Test 1, Day 1)",
                font=("Helvetica", 12),
                text_color="gray"
            )
            testing_help.grid(row=8, column=1, padx=20, pady=(0, 10), sticky="w")
        
        # Create a progress indicator
        progress_var = ctk.DoubleVar()
        progress_bar = ctk.CTkProgressBar(form_frame)
        progress_bar.grid(row=9, column=0, columnspan=2, padx=20, pady=(20, 0), sticky="ew")
        progress_bar.set(0)
        
        # Status label
        status_label = ctk.CTkLabel(
            form_frame, 
            text="",
            font=("Helvetica", 12)
        )
        status_label.grid(row=10, column=0, columnspan=2, padx=20, pady=(5, 20), sticky="ew")
        
        # Button frame
        button_frame = ctk.CTkFrame(form_frame)
        button_frame.grid(row=11, column=0, columnspan=2, padx=20, pady=(10, 0), sticky="ew")
        
        # Create grid for buttons
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        def on_cancel():
            """Cancel and close the window."""
            details_window.destroy()
        
        def on_analyze():
            """Execute the analysis with the provided parameters."""
            progress_bar.set(0.1)
            status_label.configure(text="Loading data...")
            details_window.update_idletasks()
            
            try:
                year = int(year_entry.get())
                track = track_entry.get()
                session_type = session_entry.get()
                drivers = drivers_entry.get().split()
                
                # Update status bar in main window
                self.update_status(f"Analyzing {track} {session_type} {year}...")
                
                # Load session data
                if analysis_function == self.plot_testing_pace:
                    testing_params = testing_entry.get().split()
                    test_number = int(testing_params[0])
                    day_number = int(testing_params[1])
                    session = fastf1.get_testing_session(year, test_number, day_number)
                else:
                    session = fastf1.get_session(year, track, session_type)
                
                progress_bar.set(0.3)
                status_label.configure(text="Processing session data...")
                details_window.update_idletasks()
                
                session.load()
                progress_bar.set(0.7)
                status_label.configure(text="Generating visualization...")
                details_window.update_idletasks()
                
                # Call the appropriate analysis function
                analysis_function(session, drivers)
                
                progress_bar.set(1.0)
                status_label.configure(text="Analysis completed successfully!")
                self.update_status("Analysis completed")
                details_window.update_idletasks()
                
                # Close the window after a short delay
                details_window.after(1000, details_window.destroy)
                
            except Exception as e:
                progress_bar.set(0)
                status_label.configure(text=f"Error: {str(e)}")
                self.update_status(f"Error in analysis: {str(e)}")
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            button_frame, 
            text="Cancel", 
            command=on_cancel,
            width=100,
            fg_color="gray"
        )
        cancel_btn.grid(row=0, column=0, padx=(0, 5), pady=10, sticky="e")
        
        # Analyze button
        analyze_btn = ctk.CTkButton(
            button_frame, 
            text="Analyze", 
            command=on_analyze,
            width=100
        )
        analyze_btn.grid(row=0, column=1, padx=(5, 0), pady=10, sticky="w")

    def plot_pace_comparison(self, session, drivers: List[str]):
        """Plot the speed comparison of fastest laps for selected drivers."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        legend_elements = []
        for driver in drivers:
            try:
                fast_driver = session.laps.pick_driver(driver).pick_fastest()
                if fast_driver.empty:
                    self.update_status(f"No fastest lap data for {driver}")
                    continue
                
                driver_car_data = fast_driver.get_car_data()
                t = driver_car_data['Time']
                vCar = driver_car_data['Speed']
                
                # Get driver team color
                team = fast_driver['Team']
                team_color = fastf1.plotting.team_color(team)
                
                # Plot with team color
                line, = ax.plot(t, vCar, color=team_color, linewidth=2)
                legend_elements.append((line, f"{driver} ({team})"))
            except Exception as e:
                self.update_status(f"Error plotting {driver}: {str(e)}")
        
        # Add legend with driver names and teams
        ax.legend([elem[0] for elem in legend_elements], 
                 [elem[1] for elem in legend_elements])
        
        # Add grid and improve styling
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Speed [Km/h]', fontsize=12)
        ax.set_title(f'Fastest Lap Speed Comparison - {session.event.name} {session.name} {session.event.year}', 
                     fontsize=14, fontweight='bold')
        
        # Add track layout in an inset if available
        try:
            track_layout = session.get_track_status_data()
            if not track_layout.empty and 'Status' in track_layout.columns:
                # Add track info
                circuit_info = ctk.CTkLabel(
                    self.plot_frame,
                    text=f"Circuit: {session.event['CircuitName']}",
                    font=("Helvetica", 12, "bold")
                )
                circuit_info.pack(side="bottom", pady=(5, 0))
        except:
            pass
        
        # Add session details
        fig.text(0.02, 0.02, f"Session: {session.name}, Date: {session.date.strftime('%Y-%m-%d')}", 
                 fontsize=10)
        
        # Make tight layout and display
        fig.tight_layout()
        self.embed_plot(fig)

    def plot_mean_lap_time(self, session, drivers=None):
        """Plot mean lap times for all drivers, color-coded by team."""
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Get quick laps, filtered to exclude outliers
        laps = session.laps.pick_quicklaps()
        
        # Dictionary to store mean lap times
        mean_lap_times = {}
        all_drivers = session.results['Abbreviation'].values if 'results' in session.__dict__ else laps['Driver'].unique()
        
        # Calculate mean lap times for each driver
        for driver in all_drivers:
            try:
                driver_laps = laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Convert lap times to seconds
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                
                # Remove outliers (more than 2 std from mean)
                if len(lap_times) > 3:  # Need enough laps to calculate std
                    mean = lap_times.mean()
                    std = lap_times.std()
                    lap_times = lap_times[abs(lap_times - mean) <= 2 * std]
                
                if not lap_times.empty:
                    mean_lap_times[driver] = lap_times.mean()
            except Exception as e:
                self.update_status(f"Error processing {driver}: {str(e)}")
        
        # Sort drivers by mean lap time
        sorted_drivers = sorted(mean_lap_times, key=mean_lap_times.get)
        
        # Get team colors
        team_colors = {}
        for driver in sorted_drivers:
            try:
                driver_team = laps.pick_driver(driver)['Team'].iloc[0]
                team_colors[driver] = fastf1.plotting.team_color(driver_team)
            except:
                team_colors[driver] = '#999999'  # Default gray if team color not found
        
        # Plot bars with team colors
        bars = []
        for driver in sorted_drivers:
            bar = ax.bar(driver, mean_lap_times[driver], color=team_colors[driver])
            bars.append(bar)
        
        # Add value labels on top of bars
        for bar in ax.patches:
            height = bar.get_height()
            # Format time as mm:ss.ms
            mins = int(height // 60)
            secs = height % 60
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.1,
                f"{mins}:{secs:.3f}",
                ha='center', 
                va='bottom',
                rotation=45,
                fontsize=8
            )
        
        # Configure plot styling
        ax.set_xlabel('Driver', fontsize=12)
        ax.set_ylabel('Mean Lap Time (seconds)', fontsize=12)
        ax.set_title(f'Mean Lap Time per Driver - {session.event.name} {session.name} {session.event.year}', 
                     fontsize=14, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)
        
        # Add horizontal line for the fastest lap time
        if mean_lap_times:
            fastest_time = min(mean_lap_times.values())
            ax.axhline(y=fastest_time, color='r', linestyle='--', 
                       label=f'Fastest: {int(fastest_time // 60)}:{fastest_time % 60:.3f}')
            
        # Make the plot more compact to fit all drivers
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.25)
        fig.tight_layout()
        
        self.embed_plot(fig)

    def plot_lap_times(self, session, drivers: List[str]):
        """Plot lap times progression throughout the session for selected drivers."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Store driver's team for legend grouping
        driver_teams = {}
        
        for driver in drivers:
            try:
                driver_laps = session.laps.pick_driver(driver)
                if driver_laps.empty:
                    self.update_status(f"No lap data for {driver}")
                    continue
                
                # Get driver's team for color
                team = driver_laps['Team'].iloc[0]
                team_color = fastf1.plotting.team_color(team)
                driver_teams[driver] = team
                
                lap_number = driver_laps['LapNumber']
                time = driver_laps['LapTime'].dt.total_seconds()
                
                # Plot with markers to identify pit stops if available
                if 'PitOutTime' in driver_laps.columns:
                    pit_laps = driver_laps[~driver_laps['PitOutTime'].isna()]['LapNumber']
                    # Mark pit stops with a different marker
                    for pit_lap in pit_laps:
                        if pit_lap in lap_number.values:
                            idx = lap_number[lap_number == pit_lap].index[0]
                            ax.scatter(pit_lap, time[idx], 
                                      marker='o', s=100, edgecolor='black', 
                                      facecolor=team_color, zorder=10)
                
                # Plot the lap times
                ax.plot(lap_number, time, label=driver, color=team_color, 
                       marker='o', markersize=4, linewidth=2)
                
                # Add trendline to see progression
                if len(lap_number) > 3:
                    z = np.polyfit(lap_number, time, 1)
                    p = np.poly1d(z)
                    ax.plot(lap_number, p(lap_number), 
                           linestyle='--', color=team_color, alpha=0.5)
            except Exception as e:
                self.update_status(f"Error plotting {driver}: {str(e)}")
        
        # Group drivers by team in the legend
        handles, labels = ax.get_legend_handles_labels()
        by_team = {}
        for handle, label in zip(handles, labels):
            if label in driver_teams:
                team = driver_teams[label]
                if team not in by_team:
                    by_team[team] = []
                by_team[team].append((handle, label))
        
        # Create a new list with team headers
        new_handles = []
        new_labels = []
        for team, driver_list in by_team.items():
            # Add team name as a header
            new_handles.append(plt.Line2D([0], [0], color='white'))
            new_labels.append(f"{team}")
            # Add drivers under team
            for handle, label in driver_list:
                new_handles.append(handle)
                new_labels.append(f"  {label}")
        
        # Add the modified legend
        ax.legend(new_handles, new_labels, loc='upper right')
        
        # Add grid and styling
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Lap Number', fontsize=12)
        ax.set_ylabel('Lap Time (seconds)', fontsize=12)
        ax.set_title(f'Lap Time Progression - {session.event.name} {session.name} {session.event.year}', 
                     fontsize=14, fontweight='bold')
        
        # Add median lap time line
        all_times = []
        for driver in drivers:
            try:
                driver_times = session.laps.pick_driver(driver)['LapTime'].dt.total_seconds()
                all_times.extend(driver_times)
            except:
                pass
        
        if all_times:
            median_time = np.median(all_times)
            ax.axhline(y=median_time, color='gray', linestyle='--', 
                      label=f'Median: {int(median_time // 60)}:{median_time % 60:.3f}')
        
        # Format y-axis as minutes:seconds
        import matplotlib.ticker as ticker
        def time_formatter(x, pos):
            minutes = int(x // 60)
            seconds = x % 60
            return f"{minutes}:{seconds:.1f}"
        
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
        
        fig.tight_layout()
        self.embed_plot(fig)

    def plot_race_history(self, session, drivers=None):
        """Plot race history showing delta to leader's reference time."""
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Get all drivers or use provided list
        all_drivers = session.results['Abbreviation'].values if drivers is None else drivers
        
        # Find the winner (first in results)
        winner = session.results['Abbreviation'].iloc[0]
        
        # Calculate reference lap time (winner's average)
        winner_time = session.results['Time'].iloc[0]
        if pd.isna(winner_time):
            self.update_status("Cannot calculate reference time, winner's time is not available")
            return
            
        # Convert to seconds and calculate average
        reference_lap_time = winner_time.total_seconds() / session.total_laps
        
        # Plot delta time for each driver
        for driver in all_drivers:
            try:
                driver_laps = session.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Get driver's team for color
                team = driver_laps['Team'].iloc[0]
                team_color = fastf1.plotting.team_color(team)
                
                # Convert lap times to seconds
                lap_times = driver_laps['LapTime'].dt.total_seconds()
                
                # Replace invalid lap times with interpolated values
                for i in range(1, len(lap_times)-1):
                    if lap_times.iloc[i] <= 0 or pd.isna(lap_times.iloc[i]):
                        lap_times.iloc[i] = (lap_times.iloc[i-1] + lap_times.iloc[i+1]) / 2
                
                # Calculate cumulative time
                cumulative_times = lap_times.cumsum()
                
                # Calculate reference cumulative time
                lap_numbers = driver_laps['LapNumber']
                reference_times = np.array([reference_lap_time * lap for lap in lap_numbers])
                
                # Calculate and plot delta
                delta = reference_times - cumulative_times
                
                # Plot with thicker line for winner
                linewidth = 3 if driver == winner else 1.5
                linestyle = '-' if driver == winner else '--'
                
                ax.plot(lap_numbers, delta, 
                       label=f"{driver} ({team})",
                       color=team_color,
                       linewidth=linewidth,
                       linestyle=linestyle)
                
                # Mark pit stops if available
                if 'PitInLap' in driver_laps.columns:
                    pit_laps = driver_laps[driver_laps['PitInLap'] == True]['LapNumber']
                    for pit_lap in pit_laps:
                        idx = lap_numbers[lap_numbers == pit_lap].index
                        if not idx.empty:
                            ax.scatter(pit_lap, delta.iloc[idx[0]], 
                                    marker='s', s=50, color=team_color, 
                                    edgecolor='black', zorder=10)
            except Exception as e:
                self.update_status(f"Error plotting {driver}: {str(e)}")
        
        # Add horizontal line at y=0 (reference time)
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.5)
        
        # Add vertical lines for race quarters
        for quarter in range(1, 4):
            lap = int(session.total_laps * quarter / 4)
            ax.axvline(x=lap, color='gray', linestyle=':', alpha=0.3)
            ax.text(lap, ax.get_ylim()[0], f"Lap {lap}", 
                   ha='center', va='bottom', fontsize=8, alpha=0.7)
        
        # Grid and styling
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Lap Number', fontsize=12)
        ax.set_ylabel('Delta to Reference (seconds)', fontsize=12)
        ax.set_title(f'Race History - {session.event.name} {session.name} {session.event.year}', 
                     fontsize=14, fontweight='bold')
        
        # Add legend with sorted order (winner first)
        handles, labels = ax.get_legend_handles_labels()
        # Find winner index
        winner_idx = next((i for i, label in enumerate(labels) if label.startswith(winner)), None)
        if winner_idx is not None:
            # Move winner to the beginning
            handles.insert(0, handles.pop(winner_idx))
            labels.insert(0, labels.pop(winner_idx))
        
        ax.legend(handles, labels, loc='upper right')
        
        fig.tight_layout()
        self.embed_plot(fig)


    def plot_team_pace_comparison(self, session, drivers=None):
        """Plot team pace comparison as a boxplot."""
        # Set up seaborn styling
        sns.set_style("darkgrid")
        fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
        
        # Get quick laps
        laps = session.laps.pick_quicklaps()
        
        # Convert lap times to seconds
        transformed_laps = laps.copy()
        transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()
        
        # Order teams from fastest to slowest
        team_order = (
            transformed_laps[["Team", "LapTime (s)"]]
            .groupby("Team")
            .median()["LapTime (s)"]
            .sort_values()
            .index
        )
        
        # Create color palette using team colors
        team_palette = {team: fastf1.plotting.team_color(team) for team in team_order}
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create boxplot
        sns.boxplot(
            data=transformed_laps,
            x="Team",
            y="LapTime (s)",
            hue="Team",
            order=team_order,
            palette=team_palette,
            ax=ax,
            whiskerprops=dict(color="white"),
            boxprops=dict(edgecolor="white"),
            medianprops=dict(color="grey"),
            capprops=dict(color="white"),
        )
        
        # Add swarm plot of individual lap times
        sns.swarmplot(
            data=transformed_laps,
            x="Team",
            y="LapTime (s)",
            order=team_order,
            size=4,
            color="white",
            edgecolor="black",
            linewidth=0.5,
            alpha=0.7,
            ax=ax
        )
        
        # Add a text label for each team showing their median lap time
        for i, team in enumerate(team_order):
            team_data = transformed_laps[transformed_laps["Team"] == team]["LapTime (s)"]
            if not team_data.empty:
                median_time = team_data.median()
                mins = int(median_time // 60)
                secs = median_time % 60
                ax.text(
                    i, 
                    team_data.min() - 0.5, 
                    f"{mins}:{secs:.3f}",
                    ha='center',
                    va='top',
                    fontsize=9,
                    fontweight='bold'
                )
        
        # Calculate and display the gap to the fastest team
        fastest_median = transformed_laps.groupby("Team")["LapTime (s)"].median().min()
        for i, team in enumerate(team_order):
            if i > 0:  # Skip the fastest team
                team_median = transformed_laps[transformed_laps["Team"] == team]["LapTime (s)"].median()
                gap = team_median - fastest_median
                ax.text(
                    i,
                    transformed_laps[transformed_laps["Team"] == team]["LapTime (s)"].max() + 0.3,
                    f"+{gap:.3f}s",
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    color='red'
                )
        
        # Styling
        ax.set_title(f"Team Pace Comparison - {session.event.name} {session.name} {session.event.year}", 
                    fontsize=14, fontweight='bold')
        ax.set_xlabel("")  # Remove x-label as it's redundant
        ax.set_ylabel("Lap Time (seconds)", fontsize=12)
        
        # Format y-axis as minutes:seconds
        import matplotlib.ticker as ticker
        def time_formatter(x, pos):
            minutes = int(x // 60)
            seconds = x % 60
            return f"{minutes}:{seconds:.1f}"
        
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
        
        # Remove legend as it's redundant
        ax.get_legend().remove()
        
        # Make x-axis labels horizontal to save space
        plt.xticks(rotation=0)
        
        fig.tight_layout()
        self.embed_plot(fig)

    def plot_testing_pace(self, session, drivers):
        """Plot pace comparison for testing sessions."""
        # Create tabs for different visualizations
        self.clear_plot_container()
        
        tab_view = ctk.CTkTabview(self.plot_frame)
        tab_view.pack(fill="both", expand=True)
        
        # Create tabs
        tab_view.add("Fastest Laps")
        tab_view.add("Lap Count")
        tab_view.add("Stint Analysis")
        
        # Tab 1: Fastest Laps Comparison
        fastest_tab = tab_view.tab("Fastest Laps")
        
        # Create a figure for fastest laps
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        
        # Get fastest lap for each driver
        fastest_laps = {}
        team_colors = {}
        
        for driver in session.laps['Driver'].unique():
            try:
                driver_laps = session.laps.pick_driver(driver)
                if not driver_laps.empty:
                    fastest_lap = driver_laps.pick_fastest()
                    if not fastest_lap.empty:
                        lap_time = fastest_lap['LapTime'].total_seconds()
                        fastest_laps[driver] = lap_time
                        
                        # Get team color
                        team = driver_laps['Team'].iloc[0]
                        team_colors[driver] = fastf1.plotting.team_color(team)
            except Exception as e:
                self.update_status(f"Error processing {driver}: {str(e)}")
        
        # Sort by fastest lap time
        sorted_drivers = sorted(fastest_laps, key=fastest_laps.get)
        
        # Ensure we have drivers to plot
        if sorted_drivers:
            # Calculate gap to fastest
            fastest_time = fastest_laps[sorted_drivers[0]]
            
            # Plot bars
            for i, driver in enumerate(sorted_drivers):
                gap = fastest_laps[driver] - fastest_time if i > 0 else 0
                ax1.barh(driver, fastest_laps[driver], color=team_colors.get(driver, '#999999'))
                
                # Add time labels
                mins = int(fastest_laps[driver] // 60)
                secs = fastest_laps[driver] % 60
                ax1.text(
                    fastest_laps[driver] + 0.1, 
                    i,
                    f"{mins}:{secs:.3f}" + (f" (+{gap:.3f}s)" if i > 0 else ""),
                    va='center',
                    fontsize=9
                )
            
            # Styling
            ax1.set_title(f"Fastest Lap Comparison - {session.event.name} Testing")
            ax1.set_xlabel("Lap Time (seconds)")
            ax1.grid(True, axis='x', alpha=0.3)
            
            # Format x-axis as minutes:seconds
            import matplotlib.ticker as ticker
            def time_formatter(x, pos):
                minutes = int(x // 60)
                seconds = x % 60
                return f"{minutes}:{seconds:.1f}"
            
            ax1.xaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
            
            # Embed in tab
            canvas1 = FigureCanvasTkAgg(fig1, master=fastest_tab)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(fastest_tab, text="No lap data available").pack(expand=True)
        
        # Tab 2: Lap Count
        lap_count_tab = tab_view.tab("Lap Count")
        
        # Create a figure for lap count
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        
        # Count laps per driver
        lap_counts = {}
        for driver in session.laps['Driver'].unique():
            lap_count = len(session.laps.pick_driver(driver))
            lap_counts[driver] = lap_count
        
        # Sort by lap count (descending)
        sorted_by_laps = sorted(lap_counts.items(), key=lambda x: x[1], reverse=True)
        
        if sorted_by_laps:
            # Plot bars
            drivers, counts = zip(*sorted_by_laps)
            bars = ax2.barh(drivers, counts, color=[team_colors.get(d, '#999999') for d in drivers])
            
            # Add count labels
            for bar in ax2.patches:
                ax2.text(
                    bar.get_width() + 0.5, 
                    bar.get_y() + bar.get_height()/2,
                    f"{int(bar.get_width())} laps",
                    va='center',
                    fontsize=9
                )
            
            # Styling
            ax2.set_title(f"Laps Completed - {session.event.name} Testing")
            ax2.set_xlabel("Number of Laps")
            ax2.grid(True, axis='x', alpha=0.3)
            
            # Embed in tab
            canvas2 = FigureCanvasTkAgg(fig2, master=lap_count_tab)
            canvas2.draw()
            canvas2.get_tk_widget().pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(lap_count_tab, text="No lap data available").pack(expand=True)
        
        # Tab 3: Stint Analysis
        stint_tab = tab_view.tab("Stint Analysis")
        
        # Create figure for stint analysis
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        
        # Identify stints (consecutive laps without pit stops)
        stints = {}
        for driver in drivers:
            try:
                driver_laps = session.laps.pick_driver(driver)
                if driver_laps.empty:
                    continue
                
                # Sort by lap number
                driver_laps = driver_laps.sort_values('LapNumber')
                
                # Group into stints (identify gaps > 1 in lap numbers)
                current_stint = []
                last_lap = None
                driver_stints = []
                
                for _, lap in driver_laps.iterrows():
                    lap_num = lap['LapNumber']
                    
                    if last_lap is not None and lap_num > last_lap + 1:
                        # Gap detected, end current stint
                        if len(current_stint) >= 3:  # Only consider stints with 3+ laps
                            driver_stints.append(current_stint)
                        current_stint = [lap]
                    else:
                        current_stint.append(lap)
                    
                    last_lap = lap_num
                
                # Add the last stint if valid
                if len(current_stint) >= 3:
                    driver_stints.append(current_stint)
                
                stints[driver] = driver_stints
            except Exception as e:
                self.update_status(f"Error processing stints for {driver}: {str(e)}")
        
        # Plot stint analysis
        has_data = False
        for driver, driver_stints in stints.items():
            if not driver_stints:
                continue
                
            has_data = True
            color = team_colors.get(driver, '#999999')
            
            for i, stint in enumerate(driver_stints):
                # Extract lap times
                lap_numbers = [lap['LapNumber'] for lap in stint]
                lap_times = [lap['LapTime'].total_seconds() for lap in stint]
                
                # Plot the stint
                ax3.plot(lap_numbers, lap_times, 
                        marker='o', linestyle='-', 
                        color=color, alpha=0.7,
                        label=f"{driver} - Stint {i+1}")
        
        if has_data:
            # Styling
            ax3.set_title(f"Stint Analysis - {session.event.name} Testing")
            ax3.set_xlabel("Lap Number")
            ax3.set_ylabel("Lap Time (seconds)")
            ax3.grid(True, alpha=0.3)
            ax3.legend()
            
            # Format y-axis as minutes:seconds
            import matplotlib.ticker as ticker
            ax3.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
            
            # Embed in tab
            canvas3 = FigureCanvasTkAgg(fig3, master=stint_tab)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(stint_tab, text="No stint data available").pack(expand=True)

    def plot_driver_championship(self, session, drivers=None):
        """Plot driver championship standings."""
        # Create Ergast API client
        ergast = Ergast()
        
        # Get year from session
        year = session.event.year
        
        # Get driver standings
        driver_standings = ergast.get_driver_standings(season=year, round='last')
        
        if driver_standings.empty:
            ctk.CTkLabel(self.plot_frame, text=f"No championship data available for {year}").pack(expand=True)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Extract top drivers (limit to top 20)
        top_drivers = driver_standings.head(20)
        
        # Create horizontal bar chart
        bars = ax.barh(
            top_drivers['Driver'],
            top_drivers['Points'],
            height=0.6,
            color=[fastf1.plotting.team_color(team) for team in top_drivers['Team']]
        )
        
        # Add point values
        for bar in ax.patches:
            ax.text(
                bar.get_width() + 1, 
                bar.get_y() + bar.get_height()/2,
                f"{int(bar.get_width())}",
                va='center',
                fontweight='bold'
            )
        
        # Add driver position numbers
        for i, (_, row) in enumerate(top_drivers.iterrows()):
            ax.text(
                -5, 
                i,
                f"{int(row['Position'])}",
                va='center',
                ha='center',
                fontweight='bold',
                color='white',
                bbox=dict(facecolor='black', alpha=0.7, boxstyle='circle')
            )
        
        # Style the plot
        ax.set_title(f"Driver Championship Standings - {year}", fontsize=16, fontweight='bold')
        ax.set_xlabel("Points", fontsize=12)
        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Remove y-axis label and shift x-axis to make room for position numbers
        ax.set_ylabel("")
        ax.spines['left'].set_position(('outward', 10))
        
        # Add a legend for teams
        teams = top_drivers['Team'].unique()
        team_handles = [plt.Rectangle((0,0), 1, 1, color=fastf1.plotting.team_color(team)) for team in teams]
        ax.legend(team_handles, teams, loc='lower right', ncol=2)
        
        # Display the plot
        fig.tight_layout()
        self.embed_plot(fig)

    def plot_constructor_championship(self, session, drivers=None):
        """Plot constructor championship standings."""
        # Create Ergast API client
        ergast = Ergast()
        
        # Get year from session
        year = session.event.year
        
        # Get constructor standings
        constructor_standings = ergast.get_constructor_standings(season=year, round='last')
        
        if constructor_standings.empty:
            ctk.CTkLabel(self.plot_frame, text=f"No constructor championship data available for {year}").pack(expand=True)
            return
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Create horizontal bar chart with team colors
        bars = ax.barh(
            constructor_standings['Constructor'],
            constructor_standings['Points'],
            height=0.6,
            color=[fastf1.plotting.team_color(team) for team in constructor_standings['Constructor']]
        )
        
        # Add point values
        for bar in ax.patches:
            ax.text(
                bar.get_width() + 1, 
                bar.get_y() + bar.get_height()/2,
                f"{int(bar.get_width())}",
                va='center',
                fontweight='bold'
            )
        
        # Add team position numbers
        for i, (_, row) in enumerate(constructor_standings.iterrows()):
            ax.text(
                -5, 
                i,
                f"{int(row['Position'])}",
                va='center',
                ha='center',
                fontweight='bold',
                color='white',
                bbox=dict(facecolor='black', alpha=0.7, boxstyle='circle')
            )
        
        # Style the plot
        ax.set_title(f"Constructor Championship Standings - {year}", fontsize=16, fontweight='bold')
        ax.set_xlabel("Points", fontsize=12)
        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Remove y-axis label and shift x-axis to make room for position numbers
        ax.set_ylabel("")
        ax.spines['left'].set_position(('outward', 10))
        
        # Display the plot
        fig.tight_layout()
        self.embed_plot(fig)

    def export_data_to_csv(self, session, drivers):
        """Export session data to CSV files."""
        self.clear_plot_container()
        
        # Create a frame for export options
        export_frame = ctk.CTkFrame(self.plot_frame)
        export_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            export_frame, 
            text="Export Session Data to CSV",
            font=("Helvetica", 18, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Session info
        session_info = ctk.CTkLabel(
            export_frame, 
            text=f"Session: {session.event.name} {session.name} {session.event.year}",
            font=("Helvetica", 14)
        )
        session_info.pack(pady=(0, 20))
        
        # Create exportable data options
        export_options = [
            ("All Lap Times", "laps", session.laps),
            ("Fastest Laps", "fastest_laps", session.laps.pick_fastest_per_driver()),
            ("Race Results", "results", session.results if hasattr(session, 'results') else None),
            ("Car Data (Speed, RPM, etc.)", "car_data", None),  # Will be processed separately
            ("Weather Data", "weather", session.weather_data if hasattr(session, 'weather_data') else None)
        ]
        
        # Create a dictionary to store checkbutton variables
        self.export_vars = {}
        
        # Create checkbuttons for each option
        for text, key, _ in export_options:
            var = ctk.BooleanVar(value=True)
            self.export_vars[key] = var
            
            cb = ctk.CTkCheckBox(
                export_frame, 
                text=text,
                variable=var,
                font=("Helvetica", 14)
            )
            cb.pack(anchor="w", padx=30, pady=5)
        
        # Output directory selection
        dir_frame = ctk.CTkFrame(export_frame)
        dir_frame.pack(fill="x", padx=20, pady=20)
        
        dir_label = ctk.CTkLabel(
            dir_frame, 
            text="Output Directory:",
            font=("Helvetica", 14)
        )
        dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        self.output_dir = ctk.StringVar(value=os.path.expanduser("~"))
        dir_entry = ctk.CTkEntry(
            dir_frame, 
            textvariable=self.output_dir,
            width=300,
            font=("Helvetica", 14)
        )
        dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        def browse_directory():
            import tkinter.filedialog as filedialog
            directory = filedialog.askdirectory(initialdir=self.output_dir.get())
            if directory:
                self.output_dir.set(directory)
        
        browse_btn = ctk.CTkButton(
            dir_frame, 
            text="Browse...",
            command=browse_directory,
            width=100
        )
        browse_btn.grid(row=0, column=2, padx=10, pady=10)
        
        dir_frame.grid_columnconfigure(1, weight=1)
        
        # Progress bar and status
        progress_var = ctk.DoubleVar(value=0)
        progress_bar = ctk.CTkProgressBar(export_frame, variable=progress_var)
        progress_bar.pack(fill="x", padx=30, pady=(20, 5))
        
        status_label = ctk.CTkLabel(
            export_frame, 
            text="Ready to export data",
            font=("Helvetica", 12)
        )
        status_label.pack(pady=(0, 20))
        
        def perform_export():
            try:
                # Create output directory if it doesn't exist
                output_dir = self.output_dir.get()
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                # Prefix for all files
                prefix = f"{session.event.year}_{session.event.name.replace(' ', '_')}_{session.name}"
                
                # Get selected export options
                export_items = []
                for text, key, data in export_options:
                    if self.export_vars[key].get() and data is not None:
                        export_items.append((key, data))
                
                # Special case for car data
                if self.export_vars["car_data"].get():
                    # Only export car data for selected drivers
                    for driver in drivers:
                        try:
                            # Get fastest lap car data
                            lap = session.laps.pick_driver(driver).pick_fastest()
                            if not lap.empty:
                                car_data = lap.get_car_data()
                                if car_data is not None:
                                    export_items.append((f"car_data_{driver}", car_data))
                        except Exception as e:
                            status_label.configure(text=f"Error getting car data for {driver}: {str(e)}")
                
                # Total number of items to export
                total_items = len(export_items)
                
                # Export each item
                for i, (key, data) in enumerate(export_items):
                    if data is not None and not data.empty:
                        filename = f"{prefix}_{key}.csv"
                        filepath = os.path.join(output_dir, filename)
                        
                        # Update status
                        status_label.configure(text=f"Exporting {filename}...")
                        self.root.update_idletasks()
                        
                        # Export to CSV
                        data.to_csv(filepath)
                        
                        # Update progress
                        progress_var.set((i + 1) / total_items)
                        self.root.update_idletasks()
                
                # Update status on completion
                status_label.configure(text=f"Export complete! Files saved to {output_dir}")
                progress_var.set(1.0)
                
            except Exception as e:
                status_label.configure(text=f"Error during export: {str(e)}")
        
        # Export button
        export_btn = ctk.CTkButton(
            export_frame, 
            text="Export Selected Data",
            command=perform_export,
            font=("Helvetica", 14, "bold")
        )
        export_btn.pack(pady=20)

if __name__ == "__main__":
    root = ctk.CTk()
    app = F1StatsApp(root)
    root.mainloop()