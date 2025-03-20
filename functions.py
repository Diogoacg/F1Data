from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting
import numpy as np
import datetime
import seaborn as sns
from fastf1.ergast import Ergast
import tkinter as tk
from matplotlib.colors import ListedColormap
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib import cm
import matplotlib as mpl
from typing import List, Dict, Tuple, Optional
import statsmodels.api as sm

# Setup FastF1 plotting
fastf1.plotting.setup_mpl(mpl_timedelta_support=True, misc_mpl_mods=True)

def plot_pace_comparison(drivers: List[str], session: fastf1.core.Session):
    """
    Plot speed telemetry comparison between drivers
    
    Args:
        drivers: List of driver abbreviations
        session: FastF1 session object
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add title and session information
    title = f"Speed Telemetry Comparison - {session.event['EventName']} {session.event.year} ({session.name})"
    plt.suptitle(title, fontsize=16, y=0.98)
    
    driver_colors = {}
    for driver in drivers:
        try:
            fast_driver = session.laps.pick_driver(driver).pick_fastest()
            driver_car_data = fast_driver.get_car_data()
            
            # Get the team color for consistent visualization
            color = fastf1.plotting.driver_color(driver)
            driver_colors[driver] = color
            
            t = driver_car_data['Time']
            vCar = driver_car_data['Speed']
            
            # Plot with improved styling
            ax.plot(t, vCar, label=f"{driver} - {fast_driver['Team']}", color=color, linewidth=2)
            
        except Exception as e:
            print(f"Error processing driver {driver}: {e}")

    # Add distance markers for track reference
    try:
        # Get circuit length
        circuit_info = session.get_circuit_info()
        circuit_length = circuit_info['CircuitLength']
        
        # Mark sectors if available
        if 'Sectors' in circuit_info:
            sectors = circuit_info['Sectors']
            for i, sector in enumerate(sectors):
                plt.axvline(x=sector, color='gray', linestyle='--', alpha=0.5)
                plt.text(sector, ax.get_ylim()[1]*0.95, f"S{i+1}", backgroundcolor='white', 
                         fontsize=9, ha='center')
    except:
        # If circuit info not available, continue without markers
        pass

    # Enhance the plot appearance
    ax.set_xlabel('Time', fontsize=12)
    ax.set_ylabel('Speed [km/h]', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    plt.show()

def plot_mean_lap_time(race: fastf1.core.Session):
    """
    Plot mean lap times for each driver in the race
    
    Args:
        race: FastF1 race session object
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get all drivers who took part in the race
    drivers = race.results['Abbreviation'].values
    
    # Dictionary to store mean lap times and additional data
    mean_lap_times = {}
    team_colors = {}
    driver_info = {}
    
    for driver in drivers:
        try:
            # Filter for clean laps (no in/out laps or yellow flags)
            driver_laps = race.laps.pick_driver(driver).pick_quicklaps()
            
            # Store team for color reference
            team = driver_laps['Team'].iloc[0] if not driver_laps.empty else None
            team_colors[driver] = fastf1.plotting.team_color(team) if team else '#333333'
            driver_info[driver] = {'Team': team}
            
            # Calculate the mean lap time, excluding outliers using IQR method
            lap_times = driver_laps['LapTime'].dt.total_seconds().values
            
            if len(lap_times) > 3:  # Only apply outlier removal if we have enough data
                q1 = np.percentile(lap_times, 25)
                q3 = np.percentile(lap_times, 75)
                iqr = q3 - q1
                
                # Filter out the outliers
                filtered_times = lap_times[(lap_times >= q1 - 1.5 * iqr) & (lap_times <= q3 + 1.5 * iqr)]
                mean_lap_time = np.mean(filtered_times) if len(filtered_times) > 0 else np.mean(lap_times)
            else:
                mean_lap_time = np.mean(lap_times) if len(lap_times) > 0 else 0
            
            # Store mean time and lap count for reference
            mean_lap_times[driver] = mean_lap_time
            driver_info[driver]['LapCount'] = len(driver_laps)
            
        except Exception as e:
            print(f"Error processing driver {driver}: {e}")
            mean_lap_times[driver] = 0
    
    # Sort drivers by their mean lap time (fastest first)
    sorted_drivers = sorted([d for d in mean_lap_times if mean_lap_times[d] > 0], 
                           key=lambda x: mean_lap_times[x])
    
    # Plot the bars
    bars = []
    for i, driver in enumerate(sorted_drivers):
        if mean_lap_times[driver] > 0:
            # Convert to time format for display
            td = datetime.timedelta(seconds=mean_lap_times[driver])
            bar = ax.bar(i, mean_lap_times[driver], color=team_colors[driver], 
                        edgecolor='black', linewidth=1, alpha=0.8)
            bars.append(bar)
            
            # Add lap count as annotation
            lap_count = driver_info[driver]['LapCount']
            ax.text(i, mean_lap_times[driver] + 0.05, f"{lap_count} laps", 
                    ha='center', va='bottom', fontsize=8)
            
            # Add time as text
            time_str = f"{int(td.total_seconds() // 60):01d}:{td.seconds % 60:02d}.{td.microseconds // 1000:03d}"
            ax.text(i, mean_lap_times[driver] / 2, time_str, 
                    ha='center', va='center', fontsize=10, color='white', fontweight='bold')
    
    # Set the tick labels to driver codes
    ax.set_xticks(range(len(sorted_drivers)))
    ax.set_xticklabels(sorted_drivers)
    
    # Style improvements
    title = f"Mean Lap Times - {race.event['EventName']} {race.event.year}"
    ax.set_title(title, fontsize=14)
    ax.set_ylabel('Lap Time (seconds)', fontsize=12)
    ax.grid(axis='y', alpha=0.3)
    
    # Convert y-axis to time format
    def format_time(x, pos):
        minutes = int(x // 60)
        seconds = int(x % 60)
        return f"{minutes}:{seconds:02d}"
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    
    # Add gap to fastest as secondary axis
    if mean_lap_times and sorted_drivers:
        fastest_time = mean_lap_times[sorted_drivers[0]]
        ax2 = ax.twinx()
        ax2.set_ylim(ax.get_ylim())
        
        def format_gap(x, pos):
            gap = x - fastest_time
            if gap == 0:
                return "Leader"
            return f"+{gap:.3f}s"
        
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_gap))
        ax2.set_ylabel('Gap to Fastest', fontsize=12)
    
    plt.tight_layout()
    plt.show()

def plot_lap_times(drivers: List[str], session: fastf1.core.Session):
    """
    Plot lap time evolution for selected drivers
    
    Args:
        drivers: List of driver abbreviations
        session: FastF1 session object
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add title with session info
    title = f"Lap Time Evolution - {session.event['EventName']} {session.event.year} ({session.name})"
    plt.suptitle(title, fontsize=16, y=0.98)
    
    # Keep track of maximum and minimum lap times for axis scaling
    all_lap_times = []
    
    for driver in drivers:
        try:
            driver_laps = session.laps.pick_driver(driver)
            
            # Skip if no lap data
            if driver_laps.empty:
                print(f"No lap data found for driver {driver}")
                continue
                
            lap_number = driver_laps['LapNumber']
            lap_time = driver_laps['LapTime'].dt.total_seconds()
            
            # Skip NaN values
            mask = ~np.isnan(lap_time)
            lap_number = lap_number[mask]
            lap_time = lap_time[mask]
            
            if len(lap_time) == 0:
                continue
                
            # Filter outliers using IQR method
            if len(lap_time) > 3:
                q1 = np.percentile(lap_time, 25)
                q3 = np.percentile(lap_time, 75)
                iqr = q3 - q1
                
                # Filter out extreme outliers (1.5 * IQR is standard for outlier detection)
                outlier_mask = (lap_time >= q1 - 1.5 * iqr) & (lap_time <= q3 + 1.5 * iqr)
                lap_number = lap_number[outlier_mask]
                lap_time = lap_time[outlier_mask]
                
                if len(lap_time) == 0:
                    continue
            
            # Get driver color
            color = fastf1.plotting.driver_color(driver)
            
            # Store valid lap times for axis scaling
            all_lap_times.extend(lap_time)
            
            # Plot the lap times
            ax.plot(lap_number, lap_time, 'o-', label=driver, color=color, markersize=5, linewidth=2)
            
            # Annotate fastest lap
            if len(lap_time) > 0:
                fastest_idx = np.argmin(lap_time)
                fastest_lap = lap_time.iloc[fastest_idx]
                fastest_lap_num = lap_number.iloc[fastest_idx]
                
                # Only mark if it's actually the fastest in the selection
                if fastest_lap == min(all_lap_times):
                    ax.plot(fastest_lap_num, fastest_lap, 'r*', markersize=12)
                    ax.annotate(f"Fastest: {datetime.timedelta(seconds=fastest_lap)}", 
                              (fastest_lap_num, fastest_lap),
                              textcoords="offset points", xytext=(0, -15),
                              ha='center', fontsize=10, fontweight='bold')
            
        except Exception as e:
            print(f"Error processing driver {driver}: {e}")
    
    # Format y-axis as time
    def format_time(x, pos):
        minutes = int(x // 60)
        seconds = x % 60
        return f"{minutes}:{seconds:.3f}" if seconds >= 10 else f"{minutes}:0{seconds:.3f}"
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    
    # Enhance plot appearance
    ax.set_xlabel('Lap Number', fontsize=12)
    ax.set_ylabel('Lap Time', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # Set y-axis limits to make the differences more visible
    if all_lap_times:
        median_time = np.median(all_lap_times)
        min_time = max(min(all_lap_times) - 1, median_time * 0.95)
        max_time = min(max(all_lap_times) + 1, median_time * 1.05)
        ax.set_ylim(min_time, max_time)
    
    plt.tight_layout()
    plt.show()
    """
    Plot lap time evolution for selected drivers
    
    Args:
        drivers: List of driver abbreviations
        session: FastF1 session object
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Add title with session info
    title = f"Lap Time Evolution - {session.event['EventName']} {session.event.year} ({session.name})"
    plt.suptitle(title, fontsize=16, y=0.98)
    
    # Keep track of maximum and minimum lap times for axis scaling
    all_lap_times = []
    
    for driver in drivers:
        try:
            driver_laps = session.laps.pick_driver(driver)
            
            # Skip if no lap data
            if driver_laps.empty:
                print(f"No lap data found for driver {driver}")
                continue
                
            lap_number = driver_laps['LapNumber']
            lap_time = driver_laps['LapTime'].dt.total_seconds()
            
            # Skip NaN values
            mask = ~np.isnan(lap_time)
            lap_number = lap_number[mask]
            lap_time = lap_time[mask]
            
            if len(lap_time) == 0:
                continue
                
            # Get driver color
            color = fastf1.plotting.driver_color(driver)
            
            # Store valid lap times for axis scaling
            all_lap_times.extend(lap_time)
            
            # Plot the lap times
            ax.plot(lap_number, lap_time, 'o-', label=driver, color=color, markersize=5, linewidth=2)
            
            # Annotate fastest lap
            if len(lap_time) > 0:
                fastest_idx = np.argmin(lap_time)
                fastest_lap = lap_time.iloc[fastest_idx]
                fastest_lap_num = lap_number.iloc[fastest_idx]
                
                # Only mark if it's actually the fastest in the selection
                if fastest_lap == min(all_lap_times):
                    ax.plot(fastest_lap_num, fastest_lap, 'r*', markersize=12)
                    ax.annotate(f"Fastest: {datetime.timedelta(seconds=fastest_lap)}", 
                              (fastest_lap_num, fastest_lap),
                              textcoords="offset points", xytext=(0, -15),
                              ha='center', fontsize=10, fontweight='bold')
            
        except Exception as e:
            print(f"Error processing driver {driver}: {e}")
    
    # Format y-axis as time
    def format_time(x, pos):
        minutes = int(x // 60)
        seconds = x % 60
        return f"{minutes}:{seconds:.3f}" if seconds >= 10 else f"{minutes}:0{seconds:.3f}"
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    
    # Enhance plot appearance
    ax.set_xlabel('Lap Number', fontsize=12)
    ax.set_ylabel('Lap Time', fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    # Set y-axis limits to make the differences more visible
    if all_lap_times:
        median_time = np.median(all_lap_times)
        min_time = max(min(all_lap_times) - 1, median_time * 0.95)
        max_time = min(max(all_lap_times) + 1, median_time * 1.05)
        ax.set_ylim(min_time, max_time)
    
    plt.tight_layout()
    plt.show()

def plot_race_history(session: fastf1.core.Session):
    """
    Plot race history delta chart showing gaps between cars over time
    
    Args:
        session: FastF1 race session object
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Get drivers that started the race
    drivers = session.results['Abbreviation'].values
    
    # Get race winner
    winner = session.results['Abbreviation'].iloc[0]
    
    # Get reference lap time (average lap time of the winner)
    winner_laps = session.laps.pick_driver(winner)
    winner_lap_times = winner_laps['LapTime'].dt.total_seconds().values
    
    # Filter out potential negative or NaN values from lap times
    winner_lap_times = winner_lap_times[winner_lap_times > 0]
    
    if len(winner_lap_times) > 0:
        reference_lap_time = np.mean(winner_lap_times)
    else:
        # Fallback if winner_lap_times is empty
        race_time = session.results['Time'].iloc[0]
        reference_lap_time = race_time.total_seconds() / session.total_laps
    
    # Plot the delta times for each driver
    for driver in drivers:
        try:
            driver_laps = session.laps.pick_driver(driver)
            
            # Skip if no lap data
            if driver_laps.empty:
                continue
                
            # Get lap times and clean up negative or invalid values
            lap_times = driver_laps['LapTime'].dt.total_seconds().values
            lap_numbers = driver_laps['LapNumber'].values
            
            # Interpolate negative lap times (e.g., pit stops) with the average of adjacent laps
            for i in range(1, len(lap_times) - 1):
                if lap_times[i] <= 0:
                    lap_times[i] = (lap_times[i-1] + lap_times[i+1]) / 2
            
            # Remove any remaining invalid times at the start or end
            valid_indices = lap_times > 0
            lap_times = lap_times[valid_indices]
            lap_numbers = lap_numbers[valid_indices]
            
            # Calculate cumulative time
            cumulative_times = np.cumsum(lap_times)
            
            # Calculate theoretical time if they had winner's pace
            theoretical_times = np.array([reference_lap_time * i for i in range(1, len(cumulative_times) + 1)])
            
            # Calculate delta
            delta_times = theoretical_times - cumulative_times
            
            # Get driver color for consistent visualization
            color = fastf1.plotting.driver_color(driver)
            
            # Plot with driver name at the end of the line
            ax.plot(lap_numbers, delta_times, '-', color=color, linewidth=2)
            
            # Add driver code label at the end of each line
            if len(lap_numbers) > 0:
                last_lap = lap_numbers[-1]
                last_delta = delta_times[-1]
                ax.text(last_lap + 0.1, last_delta, driver, color=color, 
                       fontweight='bold', ha='left', va='center')
            
        except Exception as e:
            print(f"Error processing driver {driver}: {e}")
    
    # Add zero reference line
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    # Enhance plot appearance
    title = f"Race History Chart - {session.event['EventName']} {session.event.year}"
    ax.set_title(title, fontsize=16)
    ax.set_xlabel('Lap Number', fontsize=12)
    ax.set_ylabel('Gap to Theoretical Pace (seconds)', fontsize=12)
    ax.grid(True, alpha=0.3)
    
    # Add lap markers for pit stops if available
    for driver in drivers[:5]:  # Limit to top 5 to avoid cluttering
        try:
            pit_stops = session.laps.pick_driver(driver).pick_flag('PitOut')
            if not pit_stops.empty:
                for _, stop in pit_stops.iterrows():
                    lap = stop['LapNumber']
                    ax.axvline(x=lap, color=fastf1.plotting.driver_color(driver), 
                             linestyle='--', alpha=0.5)
                    ax.text(lap, ax.get_ylim()[1]*0.95, f"{driver} pit", 
                          rotation=90, va='top', ha='right', fontsize=8)
        except:
            pass
    
    plt.tight_layout()
    plt.show()

def plot_team_pace_comparison(session: fastf1.core.Session):
    """
    Plot boxplot showing team pace comparison
    
    Args:
        session: FastF1 session object
    """
    # Setup plotting for team colors
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
    
    # Get clean laps for analysis
    laps = session.laps.pick_quicklaps()
    
    # Create a copy for transformations
    transformed_laps = laps.copy()
    
    # Convert lap times to seconds for easier plotting
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()
    
    # Order teams from fastest to slowest based on median lap time
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )
    
    # Create a color palette using team colors
    team_palette = {team: fastf1.plotting.team_color(team) for team in team_order}
    
    # Create the figure and plot
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Create the boxplot
    sns.boxplot(
        data=transformed_laps,
        x="Team",
        y="LapTime (s)",
        hue="Team",
        order=team_order,
        palette=team_palette,
        whiskerprops=dict(color="white"),
        boxprops=dict(edgecolor="white"),
        medianprops=dict(color="grey"),
        capprops=dict(color="white"),
    )
    
    # Add title with session info
    title = f"Team Pace Comparison - {session.event['EventName']} {session.event.year} ({session.name})"
    plt.title(title, fontsize=16)
    
    # Format the y-axis as time
    def format_time(x, pos):
        minutes = int(x // 60)
        seconds = x % 60
        return f"{minutes}:{seconds:.3f}" if seconds >= 10 else f"{minutes}:0{seconds:.3f}"
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    
    # Add horizontal grid lines for better readability
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Remove the x-axis label since it's redundant
    ax.set_xlabel(None)
    ax.set_ylabel("Lap Time", fontsize=12)
    
    # Calculate and display the gap to fastest team
    fastest_team_time = transformed_laps.groupby("Team")["LapTime (s)"].median().min()
    
    for i, team in enumerate(team_order):
        team_median = transformed_laps[transformed_laps["Team"] == team]["LapTime (s)"].median()
        gap = team_median - fastest_team_time
        
        # Only show gap if it's not the fastest team
        if gap > 0:
            ax.text(i, team_median, f"+{gap:.3f}s", 
                   ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.grid(visible=False)
    plt.show()

def test_pace_comparison(year: int, n_test: int, session_day: int):
    """
    Compare pace during testing sessions
    
    Args:
        year: Season year
        n_test: Test event number
        session_day: Test session day
    """
    try:
        # Get testing session data
        session = fastf1.get_testing_session(year, n_test, session_day)
        session.load()
        
        # Show driver list for reference
        drivers = session.laps['Driver'].unique()
        
        # Create a dialog to select drivers
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Use a simple dialog to get drivers for comparison
        from tkinter import simpledialog
        selected_drivers = simpledialog.askstring(
            "Driver Selection",
            f"Enter driver codes separated by spaces (available: {' '.join(drivers)})",
            initialvalue=' '.join(drivers[:3])
        )
        
        if selected_drivers:
            driver_list = selected_drivers.split()
            plot_pace_comparison(driver_list, session)
        
    except Exception as e:
        print(f"Error in test_pace_comparison: {e}")

def compare_tyre_compounds(driver: str, session: fastf1.core.Session):
    """
    Compare performance across different tyre compounds for a driver
    
    Args:
        driver: Driver abbreviation
        session: FastF1 session object
    """
    # Get laps for the specified driver
    driver_laps = session.laps.pick_driver(driver)
    
    # Skip if no data
    if driver_laps.empty:
        print(f"No lap data available for {driver}")
        return
    
    # Group laps by compound
    compounds = driver_laps['Compound'].unique()
    
    if len(compounds) <= 1:
        print(f"Not enough tyre compounds for comparison. Found: {compounds}")
        return
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot 1: Lap time by compound
    compound_colors = {
        'SOFT': 'red',
        'MEDIUM': 'yellow',
        'HARD': 'white',
        'INTERMEDIATE': 'green',
        'WET': 'blue'
    }
    
    # Group data by compound
    for compound in compounds:
        compound_laps = driver_laps[driver_laps['Compound'] == compound]
        
        if compound_laps.empty:
            continue
            
        lap_times = compound_laps['LapTime'].dt.total_seconds()
        lap_numbers = compound_laps['LapNumber']
        
        # Skip laps with missing times
        mask = ~np.isnan(lap_times)
        lap_numbers = lap_numbers[mask]
        lap_times = lap_times[mask]
        
        color = compound_colors.get(compound, 'gray')
        ax1.plot(lap_numbers, lap_times, 'o-', label=compound, 
                color=color, markersize=6, markeredgecolor='black')
    
    # Format y-axis as time
    def format_time(x, pos):
        minutes = int(x // 60)
        seconds = x % 60
        return f"{minutes}:{seconds:.3f}" if seconds >= 10 else f"{minutes}:0{seconds:.3f}"
    
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    
    # Plot 2: Tyre age effects
    for compound in compounds:
        compound_laps = driver_laps[driver_laps['Compound'] == compound]
        
        if compound_laps.empty or len(compound_laps) < 3:
            continue
            
        # Group by stint
        stints = compound_laps.groupby('Stint')
        
        for stint_number, stint in stints:
            if len(stint) < 3:  # Skip very short stints
                continue
                
            lap_times = stint['LapTime'].dt.total_seconds()
            tyre_life = stint['TyreLife'].values
            
            # Skip laps with missing times
            mask = ~np.isnan(lap_times)
            tyre_life = tyre_life[mask]
            lap_times = lap_times[mask]
            
            # Plot tyre degradation
            color = compound_colors.get(compound, 'gray')
            label = f"{compound} (Stint {stint_number})"
            ax2.plot(tyre_life, lap_times, 'o-', label=label, 
                    color=color, markersize=4, alpha=0.7)
    
    ax2.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
    
    # Add horizontal lines for different compounds' average lap times in plot 1
    for compound in compounds:
        compound_laps = driver_laps[driver_laps['Compound'] == compound]
        if not compound_laps.empty:
            lap_times = compound_laps['LapTime'].dt.total_seconds()
            avg_time = np.nanmean(lap_times)
            if not np.isnan(avg_time):
                color = compound_colors.get(compound, 'gray')
                ax1.axhline(y=avg_time, color=color, linestyle='--', alpha=0.5)
                ax1.text(ax1.get_xlim()[1] * 0.98, avg_time, f"{compound} avg", 
                      color=color, ha='right', va='bottom', fontweight='bold')
    
    # Enhance plot appearance
    title = f"Tyre Compound Comparison - {driver} - {session.event['EventName']} {session.event.year}"
    fig.suptitle(title, fontsize=16, y=0.98)
    
    ax1.set_title("Lap Time by Compound", fontsize=14)
    ax1.set_xlabel("Lap Number", fontsize=12)
    ax1.set_ylabel("Lap Time", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    
    ax2.set_title("Tyre Degradation Effects", fontsize=14)
    ax2.set_xlabel("Tyre Life (laps)", fontsize=12)
    ax2.set_ylabel("Lap Time", fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='upper left')
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.show()

def compare_sector_times(drivers: List[str], session: fastf1.core.Session):
    """
    Compare sector times between drivers
    
    Args:
        drivers: List of driver abbreviations
        session: FastF1 session object
    """
    # Set up the plot
    fig, axes = plt.subplots(3, 1, figsize=(12, 15))
    
    # Add title
    title = f"Sector Time Comparison - {session.event['EventName']} {session.event.year} ({session.name})"
    fig.suptitle(title, fontsize=16, y=0.98)
    
    # Analyze each driver
    for driver in drivers:
        try:
            driver_laps = session.laps.pick_driver(driver)
            
            # Skip if no data
            if driver_laps.empty:
                print(f"No lap data available for {driver}")
                continue
            
            # Get the driver color for consistent visualization
            color = fastf1.plotting.driver_color(driver)
            
            # Plot each sector
            for sector in range(1, 4):
                sector_col = f'Sector{sector}Time'
                
                if sector_col not in driver_laps.columns:
                    print(f"Sector time data not available for {driver}")
                    continue
                
                sector_times = driver_laps[sector_col].dt.total_seconds()
                lap_numbers = driver_laps['LapNumber']
                
                # Skip laps with missing times
                mask = ~np.isnan(sector_times)
                lap_numbers = lap_numbers[mask]
                sector_times = sector_times[mask]
                
                # Plot sector times
                axes[sector-1].plot(lap_numbers, sector_times, 'o-', 
                                 label=driver, color=color, markersize=4)
                
                # Highlight the fastest sector time
                if not sector_times.empty:
                    fastest_idx = sector_times.idxmin()
                    fastest_time = sector_times[fastest_idx]
                    fastest_lap = lap_numbers[fastest_idx]
                    axes[sector-1].plot(fastest_lap, fastest_time, '*', color=color, markersize=10)
        
        except Exception as e:
            print(f"Error processing driver {driver}: {e}")
    
    # Format the plots
    for i, ax in enumerate(axes):
        # Format y-axis as time
        def format_time(x, pos):
            return f"{x:.3f}s"
        
        ax.yaxis.set_major_formatter(plt.FuncFormatter(format_time))
        ax.set_title(f"Sector {i+1} Times", fontsize=14)
        ax.set_xlabel("Lap Number" if i == 2 else "", fontsize=12)
        ax.set_ylabel("Sector Time", fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='upper right')
        
        # Adjust y-axis to better show differences
        if not ax.lines:
            continue
            
        all_times = np.concatenate([line.get_ydata() for line in ax.lines if line.get_marker() != '*'])
        if len(all_times) > 0:
            median = np.median(all_times)
            ax.set_ylim(median * 0.95, median * 1.05)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.92)
    plt.show()

def analyze_pitstops(race: fastf1.core.Session):
    """
    Analyze pit stops from a race session
    
    Args:
        race: FastF1 race session object
    """
    # Get pit stop data
    try:
        pit_stops = race.pit_stops
        
        if pit_stops is None or pit_stops.empty:
            print("No pit stop data available for this race.")
            return
            
    except Exception as e:
        print(f"Error accessing pit stop data: {e}")
        return
    
    # Set up the plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), gridspec_kw={'width_ratios': [1.5, 1]})
    
    # Plot 1: Pit stop durations by driver
    drivers = pit_stops['Driver'].unique()
    driver_colors = {}
    
    for driver in drivers:
        driver_stops = pit_stops[pit_stops['Driver'] == driver]
        durations = driver_stops['Duration'].dt.total_seconds()
        stops = range(1, len(durations) + 1)
        
        # Get color for the driver
        try:
            color = fastf1.plotting.driver_color(driver)
            driver_colors[driver] = color
        except:
            color = "gray"
            driver_colors[driver] = color
        
        # Plot the durations
        ax1.scatter(stops, durations, color=color, s=80, label=driver)
        ax1.plot(stops, durations, color=color, alpha=0.5)
    
    # Plot 2: Average pit stop time by team
    team_stop_times = {}
    
    # Get pit stop data by team
    for _, stop in pit_stops.iterrows():
        driver = stop['Driver']
        duration = stop['Duration'].total_seconds()
        
        # Get the team for this driver
        try:
            team = race.get_driver(driver)['TeamName']
            
            if team not in team_stop_times:
                team_stop_times[team] = []
            
            team_stop_times[team].append(duration)
        except:
            pass
    
    # Calculate average pit stop time by team
    teams = []
    avg_times = []
    std_times = []
    team_colors_list = []
    
    for team, times in team_stop_times.items():
        if len(times) > 0:
            teams.append(team)
            avg_times.append(np.mean(times))
            std_times.append(np.std(times) if len(times) > 1 else 0)
            
            # Get team color
            try:
                team_colors_list.append(fastf1.plotting.team_color(team))
            except:
                team_colors_list.append("gray")
    
    # Sort by average pit stop time
    sorted_indices = np.argsort(avg_times)
    teams = [teams[i] for i in sorted_indices]
    avg_times = [avg_times[i] for i in sorted_indices]
    std_times = [std_times[i] for i in sorted_indices]
    team_colors_list = [team_colors_list[i] for i in sorted_indices]
    
    # Plot the bars
    y_pos = np.arange(len(teams))
    bars = ax2.barh(y_pos, avg_times, align='center', color=team_colors_list, height=0.6)
    
    # Add error bars
    ax2.errorbar(avg_times, y_pos, xerr=std_times, fmt='none', ecolor='black', capsize=3)
    
    # Format the plot
    ax1.set_title("Pit Stop Durations by Driver", fontsize=14)
    ax1.set_xlabel("Stop Number", fontsize=12)
    ax1.set_ylabel("Duration (seconds)", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper right')
    
    ax2.set_title("Average Pit Stop Time by Team", fontsize=14)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(teams)
    ax2.set_xlabel("Duration (seconds)", fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    # Add pit stop time annotations
    for i, v in enumerate(avg_times):
        ax2.text(v + 0.1, i, f"{v:.2f}s", va='center')
    
    # Add title with race info
    title = f"Pit Stop Analysis - {race.event['EventName']} {race.event.year}"
    fig.suptitle(title, fontsize=16, y=0.98)
    
    plt.tight_layout()
    plt.subplots_adjust(top=0.93)
    plt.show()

def analyze_overtakes(race: fastf1.core.Session):
    """
    Analyze overtaking positions in a race
    
    Args:
        race: FastF1 race session object
    """
    # Get lap data
    laps = race.laps
    
    # Create a dictionary to store position changes
    position_changes = {}
    
    # Initialize a grid for the heatmap
    lap_count = race.laps['LapNumber'].max()
    drivers = race.results['Abbreviation'].values
    overtakes_grid = np.zeros((len(drivers), lap_count))
    
    # Fill in driver starting and final positions
    for i, driver in enumerate(drivers):
        # Get laps for this driver
        driver_laps = laps.pick_driver(driver)
        
        if driver_laps.empty:
            continue
        
        # Get position at each lap
        for _, lap in driver_laps.iterrows():
            lap_num = lap['LapNumber']
            if 1 <= lap_num <= lap_count:
                position = lap['Position']
                if not np.isnan(position):
                    # Store position in the grid (0-indexed)
                    overtakes_grid[i, int(lap_num)-1] = position
    
    # Fill in gaps in the grid using linear interpolation
    for i in range(len(drivers)):
        for j in range(lap_count):
            if overtakes_grid[i, j] == 0 and j > 0:
                # Simple carry-forward from previous lap
                overtakes_grid[i, j] = overtakes_grid[i, j-1]
    
    # Create a figure for the position chart
    fig, ax = plt.subplots(figsize=(15, 10))
    
    # Plot the position line for each driver
    for i, driver in enumerate(drivers):
        try:
            # Calculate valid positions
            positions = overtakes_grid[i, :]
            laps = np.arange(1, lap_count + 1)
            
            # Get driver color
            try:
                color = fastf1.plotting.driver_color(driver)
            except:
                color = None
            
            # Plot the positions with a line
            ax.plot(laps, positions, '-', color=color, label=driver, linewidth=2)
            
            # Add driver code at the beginning and end
            if len(positions) > 0:
                ax.text(1, positions[0], driver, ha='right', va='center', fontsize=9, color=color)
                ax.text(lap_count, positions[-1], driver, ha='left', va='center', fontsize=9, color=color)
        except Exception as e:
            print(f"Error plotting driver {driver}: {e}")
    
    # Enhance plot appearance
    title = f"Position Changes - {race.event['EventName']} {race.event.year}"
    ax.set_title(title, fontsize=16)
    ax.set_xlabel("Lap Number", fontsize=12)
    ax.set_ylabel("Position", fontsize=12)
    
    # Invert y-axis so that position 1 is at the top
    ax.set_ylim(len(drivers) + 0.5, 0.5)
    ax.set_yticks(range(1, len(drivers) + 1))
    
    # Add grid for better readability
    ax.grid(True, alpha=0.3)
    
    # Identify and mark significant overtakes
    for lap in range(1, lap_count):
        for i, driver in enumerate(drivers):
            # Check for position gain/loss
            if lap < lap_count and overtakes_grid[i, lap] != overtakes_grid[i, lap-1]:
                pos_change = int(overtakes_grid[i, lap-1] - overtakes_grid[i, lap])
                
                # Only mark significant changes (more than 1 position)
                if abs(pos_change) > 1:
                    marker = '^' if pos_change > 0 else 'v'
                    color = 'green' if pos_change > 0 else 'red'
                    ax.scatter(lap + 1, overtakes_grid[i, lap], marker=marker, color=color, s=100, alpha=0.7)
                    
                    # Add annotation for big position changes
                    if abs(pos_change) > 2:
                        ax.text(lap + 1, overtakes_grid[i, lap], 
                              f"{pos_change:+d}" if pos_change > 0 else f"{pos_change}", 
                              ha='center', va='bottom', fontsize=8, color=color)
    
    # Add markers for pit stops if available
    try:
        pit_stops = race.pit_stops
        if pit_stops is not None and not pit_stops.empty:
            for _, stop in pit_stops.iterrows():
                driver = stop['Driver']
                lap = stop['Lap']
                
                # Find the driver index
                driver_idx = np.where(drivers == driver)[0]
                
                if len(driver_idx) > 0 and lap <= lap_count:
                    driver_idx = driver_idx[0]
                    position = overtakes_grid[driver_idx, int(lap)-1]
                    
                    # Mark the pit stop
                    ax.scatter(lap, position, marker='s', color='blue', s=80, alpha=0.7)
                    
        # Add lap markers for safety car periods if available
        try:
            for lap_number in range(1, lap_count + 1):
                lap_data = race.laps.pick_lap(lap_number).iloc[0]
                
                if 'IsVCDeployedLap' in lap_data and lap_data['IsVCDeployedLap']:
                    ax.axvspan(lap_number - 0.5, lap_number + 0.5, alpha=0.2, color='yellow')
                elif 'IsSCDeployedLap' in lap_data and lap_data['IsSCDeployedLap']:
                    ax.axvspan(lap_number - 0.5, lap_number + 0.5, alpha=0.2, color='orange')
        except:
            # Safety car data might not be available
            pass
            
    except:
        # Pit stop data might not be available
        pass
    
    plt.tight_layout()
    plt.show()

def analyze_team_development(year: int):
    """
    Analyze team development throughout the season
    
    Args:
        year: Season year
    """
    # Use Ergast API to get race schedule
    ergast = Ergast()
    
    try:
        # Get all races for the season
        races = ergast.get_race_schedule(year)
        
        if races.empty:
            print(f"No race data found for {year}")
            return
        
        # Select representative races from the season (approximately one per month)
        race_count = len(races)
        
        if race_count < 3:
            selected_races = races
        else:
            # Select races distributed throughout the season
            indices = np.linspace(0, race_count - 1, 6, dtype=int)
            selected_races = races.iloc[indices]
        
        # Dictionary to store team performance data
        team_data = {}
        
        # Dictionary to store track names for x-axis labels
        track_names = []
        
        # Analyze each selected race
        for i, (_, race) in enumerate(selected_races.iterrows()):
            round_num = race['round']
            race_name = race['raceName']
            track_names.append(f"{race_name}")
            
            try:
                # Get qualifying session
                session = fastf1.get_session(year, round_num, 'Q')
                session.load()
                
                # Get the fastest lap for each driver
                fastest_laps = {}
                for driver in session.drivers:
                    try:
                        driver_laps = session.laps.pick_driver(driver).pick_fastest()
                        if not driver_laps.empty:
                            fastest_laps[driver] = driver_laps['LapTime'].dt.total_seconds().values[0]
                    except:
                        pass
                
                # Group by team
                for driver, lap_time in fastest_laps.items():
                    try:
                        team = session.get_driver(driver)['TeamName']
                        
                        if team not in team_data:
                            team_data[team] = {'times': [None] * len(selected_races), 'color': None}
                            
                            # Get team color
                            try:
                                team_data[team]['color'] = fastf1.plotting.team_color(team)
                            except:
                                team_data[team]['color'] = "gray"
                        
                        # Store the better of the two drivers' times or update if faster
                        if team_data[team]['times'][i] is None or lap_time < team_data[team]['times'][i]:
                            team_data[team]['times'][i] = lap_time
                    except:
                        pass
            
            except Exception as e:
                print(f"Error processing {race_name}: {e}")
                # Fill with None if data couldn't be loaded
                for team in team_data:
                    if team_data[team]['times'][i] is None:
                        team_data[team]['times'][i] = None
        
        # Now plot the data
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Convert lap times to percentage from fastest
        normalized_data = {}
        
        # Find fastest time for each race
        fastest_times = [min([team_data[team]['times'][i] for team in team_data if team_data[team]['times'][i] is not None], 
                            default=None) 
                        for i in range(len(selected_races))]
        
        # Normalize the lap times as percentage from fastest
        for team in team_data:
            normalized_data[team] = []
            
            for i, time in enumerate(team_data[team]['times']):
                if time is not None and fastest_times[i] is not None:
                    # Calculate percentage difference from fastest
                    percentage = 100 * (time - fastest_times[i]) / fastest_times[i]
                    normalized_data[team].append(percentage)
                else:
                    normalized_data[team].append(None)
        
        # Plot the normalized data
        for team, data in normalized_data.items():
            # Replace None with NaN for plotting
            plot_data = [x if x is not None else np.nan for x in data]
            
            # Only plot if we have some valid data
            if not all(np.isnan(x) for x in plot_data):
                ax.plot(range(len(selected_races)), plot_data, 'o-', 
                       label=team, color=team_data[team]['color'], 
                       linewidth=2, markersize=8)
        
        # Add horizontal line at 0% (fastest)
        ax.axhline(y=0, color='black', linestyle='--', alpha=0.5)
        
        # Add team labels at the end of each line
        for team, data in normalized_data.items():
            # Find last valid data point
            valid_indices = [i for i, x in enumerate(data) if x is not None]
            
            if valid_indices:
                last_idx = valid_indices[-1]
                last_val = data[last_idx]
                
                # Add team name at the end of the line
                ax.text(last_idx + 0.1, last_val, team, 
                       color=team_data[team]['color'], 
                       fontweight='bold', ha='left', va='center')
        
        # Enhance plot appearance
        title = f"Team Development Throughout {year} Season"
        ax.set_title(title, fontsize=16)
        ax.set_xlabel("Race", fontsize=12)
        ax.set_ylabel("Gap to Fastest (percentage)", fontsize=12)
        ax.set_xticks(range(len(selected_races)))
        ax.set_xticklabels(track_names, rotation=45, ha='right')
        ax.grid(True, alpha=0.3)
        
        # Set y-limit for better visualization
        y_values = [x for team in normalized_data for x in normalized_data[team] if x is not None]
        if y_values:
            y_max = min(max(y_values) * 1.1, 5)  # Limit to 5% if larger
            ax.set_ylim(-0.1, y_max)
        
        plt.tight_layout()
        plt.show()
        
    except Exception as e:
        print(f"Error analyzing team development: {e}")

def compare_teammates(year: int, team: str):
    """
    Compare teammates' performance against each other
    
    Args:
        year: Season year
        team: Team name (full name or abbreviated)
    """
    # Use Ergast API to get team data
    ergast = Ergast()
    
    try:
        # Get team drivers
        constructor_standings = ergast.get_constructor_standings(year)
        
        # Find the exact team name
        team_exact = None
        
        for _, constructor in constructor_standings.iterrows():
            constructor_name = constructor['constructorName']
            
            # Check if the team name matches (case insensitive)
            if team.lower() in constructor_name.lower():
                team_exact = constructor_name
                break
        
        if team_exact is None:
            print(f"Team '{team}' not found in {year} constructor standings")
            return
        
        # Get driver standings to find the teammates
        driver_standings = ergast.get_driver_standings(year)
        
        # Find the drivers of this team
        teammates = []
        
        for _, driver in driver_standings.iterrows():
            if driver['constructorName'] == team_exact:
                teammates.append({
                    'driver': f"{driver['givenName']} {driver['familyName']}",
                    'code': driver['driverCode'],
                    'driverId': driver['driverId']
                })
        
        if len(teammates) < 2:
            print(f"Could not find at least two drivers for team {team_exact} in {year}")
            return
        
        # Get race schedule for the season
        races = ergast.get_race_schedule(year)
        
        # Prepare data structures to collect performance data
        qualifying_data = {teammate['code']: [] for teammate in teammates}
        race_data = {teammate['code']: [] for teammate in teammates}
        race_names = []
        
        # Analyze each race
        for _, race in races.iterrows():
            round_num = race['round']
            race_name = race['raceName']
            
            try:
                # Get qualifying session
                quali = fastf1.get_session(year, round_num, 'Q')
                quali.load()
                
                # Get race session
                race_session = fastf1.get_session(year, round_num, 'R')
                race_session.load()
                
                # Extract data if both teammates participated
                quali_results = []
                race_results = []
                
                for teammate in teammates:
                    code = teammate['code']
                    
                    # Get qualifying position
                    driver_quali = quali.results[quali.results['Abbreviation'] == code]
                    quali_pos = driver_quali['Position'].iloc[0] if not driver_quali.empty else None
                    
                    # Get race position
                    driver_race = race_session.results[race_session.results['Abbreviation'] == code]
                    race_pos = driver_race['Position'].iloc[0] if not driver_race.empty else None
                    
                    if quali_pos is not None and race_pos is not None:
                        quali_results.append((code, quali_pos))
                        race_results.append((code, race_pos))
                
                # Only store data if we have results for all teammates
                if len(quali_results) == len(teammates) and len(race_results) == len(teammates):
                    race_names.append(race_name)
                    
                    for code, pos in quali_results:
                        qualifying_data[code].append(pos)
                    
                    for code, pos in race_results:
                        race_data[code].append(pos)
            
            except Exception as e:
                print(f"Error processing {race_name}: {e}")
        
        # Now create the visualization
        if not race_names:
            print("No valid race data found for comparison")
            return
        
        # Set up the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [1, 1]})
        
        # Plot qualifying comparison
        x = np.arange(len(race_names))
        width = 0.35
        
        bars = []
        for i, teammate in enumerate(teammates):
            code = teammate['code']
            
            # Get color from fastf1 if available
            try:
                color = fastf1.plotting.driver_color(code)
            except:
                # Use default colors if fastf1 color is not available
                colors = ['#3366CC', '#DC3912', '#FF9900', '#109618']
                color = colors[i % len(colors)]
            
            bars.append(ax1.bar(x - width/2 + (i * width/len(teammates)), qualifying_data[code], 
                              width/len(teammates), label=code, color=color, alpha=0.8))
        
        # Add qualifying data annotations
        for i, teammate in enumerate(teammates):
            code = teammate['code']
            for j, pos in enumerate(qualifying_data[code]):
                ax1.text(x[j] - width/2 + (i * width/len(teammates)), pos, 
                       str(int(pos)), ha='center', va='bottom', fontsize=8)
        
        # Configure qualifying plot
        ax1.set_title("Qualifying Position Comparison", fontsize=14)
        ax1.set_ylabel("Position", fontsize=12)
        ax1.set_xticks(x)
        ax1.set_xticklabels(race_names, rotation=45, ha='right', fontsize=10)
        ax1.set_ylim(20.5, 0.5)  # Invert y-axis so position 1 is at the top
        ax1.grid(axis='y', alpha=0.3)
        ax1.legend()
        
        # Plot race comparison
        bars = []
        for i, teammate in enumerate(teammates):
            code = teammate['code']
            
            # Get color from fastf1 if available
            try:
                color = fastf1.plotting.driver_color(code)
            except:
                # Use default colors if fastf1 color is not available
                colors = ['#3366CC', '#DC3912', '#FF9900', '#109618']
                color = colors[i % len(colors)]
            
            bars.append(ax2.bar(x - width/2 + (i * width/len(teammates)), race_data[code], 
                              width/len(teammates), label=code, color=color, alpha=0.8))
        
        # Add race data annotations
        for i, teammate in enumerate(teammates):
            code = teammate['code']
            for j, pos in enumerate(race_data[code]):
                ax2.text(x[j] - width/2 + (i * width/len(teammates)), pos, 
                       str(int(pos)), ha='center', va='bottom', fontsize=8)
        
        # Configure race plot
        ax2.set_title("Race Position Comparison", fontsize=14)
        ax2.set_xlabel("Race", fontsize=12)
        ax2.set_ylabel("Position", fontsize=12)
        ax2.set_xticks(x)
        ax2.set_xticklabels(race_names, rotation=45, ha='right', fontsize=10)
        ax2.set_ylim(20.5, 0.5)  # Invert y-axis so position 1 is at the top
        ax2.grid(axis='y', alpha=0.3)
        ax2.legend()
        
        # Calculate head-to-head statistics
        h2h_quali = {code: 0 for code in qualifying_data}
        h2h_race = {code: 0 for code in race_data}
        
        for i in range(len(race_names)):
            # Find the best qualifier
            best_quali = min([(code, qualifying_data[code][i]) for code in qualifying_data], key=lambda x: x[1])
            h2h_quali[best_quali[0]] += 1
            
            # Find the best race finisher
            best_race = min([(code, race_data[code][i]) for code in race_data], key=lambda x: x[1])
            h2h_race[best_race[0]] += 1
        
        # Add head-to-head statistics as a text box
        h2h_text = "Head-to-Head Statistics:\n"
        h2h_text += "Qualifying:\n"
        for code, wins in h2h_quali.items():
            h2h_text += f"  {code}: {wins} ({wins/len(race_names)*100:.1f}%)\n"
        
        h2h_text += "Race:\n"
        for code, wins in h2h_race.items():
            h2h_text += f"  {code}: {wins} ({wins/len(race_names)*100:.1f}%)"
        
        # Place the text box in the upper right corner of the figure
        fig.text(0.98, 0.98, h2h_text, ha='right', va='top', 
                bbox=dict(boxstyle="round,pad=0.5", facecolor='white', alpha=0.8),
                fontsize=10)
        
        # Add title with team info
        title = f"Teammate Comparison - {team_exact} ({year})"
        fig.suptitle(title, fontsize=16)
        
        plt.tight_layout()
        plt.subplots_adjust(top=0.94, hspace=0.2)
        plt.show()
        
    except Exception as e:
        print(f"Error comparing teammates: {e}")

def analyze_long_runs(session: fastf1.core.Session):
    """
    Analyze long runs from a testing or practice session
    
    Args:
        session: FastF1 session object
    """
    # Get clean laps for analysis
    laps = session.laps
    
    # Get all drivers in the session
    drivers = laps['Driver'].unique()
    
    # Create a dialog to select a driver
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    # Use a simple dialog to get the driver for analysis
    from tkinter import simpledialog
    selected_driver = simpledialog.askstring(
        "Driver Selection",
        f"Enter driver code for long run analysis (available: {' '.join(drivers)})",
        initialvalue=drivers[0] if len(drivers) > 0 else ""
    )
    
    if not selected_driver:
        return
    
    # Get laps for the selected driver
    driver_laps = laps.pick_driver(selected_driver)
    
    # Skip if no data
    if driver_laps.empty:
        print(f"No lap data available for {selected_driver}")
        return
    
    # Group laps by stint
    stints = driver_laps.groupby('Stint')
    
    # Filter stints to include only those with a minimum number of laps
    min_stint_length = 5  # Minimum laps for a "long run"
    long_stints = []
    
    for stint_number, stint in stints:
        if len(stint) >= min_stint_length:
            long_stints.append((stint_number, stint))
    
    if not long_stints:
        print(f"No long runs (>= {min_stint_length} laps) found for {selected_driver}")
        return
    
    # Create the plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), gridspec_kw={'height_ratios': [2, 1]})
    
    # Plot 1: Lap times for each stint
    compound_colors = {
        'SOFT': 'red',
        'MEDIUM': 'yellow',
        'HARD': 'white',
        'INTERMEDIATE': 'green',
        'WET': 'blue'
    }
    
    # Track the minimum and maximum lap times for y-axis scaling
    all_lap_times = []
    
    for stint_number, stint in long_stints:
        # Get compound information
        compound = stint['Compound'].iloc[0] if 'Compound' in stint.columns else 'Unknown'
        
        # Get lap times and convert to seconds
        lap_times = stint['LapTime'].dt.total_seconds()
        tyre_life = stint['TyreLife'].values
        
        # Skip NaN values
        mask = ~np.isnan(lap_times)
        tyre_life = tyre_life[mask]
        lap_times = lap_times[mask]
        
        if len(lap_times) == 0:
            continue
            
        # Filter outliers using IQR method if we have enough laps
        if len(lap_times) > 5:
            q1 = np.percentile(lap_times, 25)
            q3 = np.percentile(lap_times, 75)
            iqr = q3 - q1
            
            # Filter out extreme outliers
            outlier_mask = (lap_times >= q1 - 1.5 * iqr) & (lap_times <= q3 + 1.5 * iqr)
            tyre_life = tyre_life[outlier_mask]
            lap_times = lap_times[outlier_mask]
            
            if len(lap_times) == 0:
                continue
            
        # Store for y-axis scaling
        all_lap_times.extend(lap_times)
        
        # Get color for the compound
        color = compound_colors.get(compound, 'gray')
        
        # Plot the lap times
        label = f"Stint {stint_number} ({compound})"
        ax1.plot(tyre_life, lap_times, 'o-', label=label, color=color, linewidth=2, markersize=6)
        
        # Add stint information (average, best, degradation)
        avg_time = np.mean(lap_times)
        best_time = np.min(lap_times)
        
        # Calculate lap time degradation (simple linear regression)
        if len(lap_times) >= 3:
            x = sm.add_constant(tyre_life)  # Add a constant for the intercept
            model = sm.OLS(lap_times, x)
            results = model.fit()
            slope = results.params[1]  # Slope coefficient
            
            # Plot the regression line
            x_line = np.array([min(tyre_life), max(tyre_life)])
            y_line = results.predict(sm.add_constant(x_line))
            ax1.plot(x_line, y_line, '--', color=color, alpha=0.7)
            
            # Calculate degradation in seconds per lap
            degradation = slope
            
            # Add annotation for degradation
            ax1.text(max(tyre_life), y_line[-1], 
                   f"{degradation:+.3f}s/lap", 
                   color=color, fontweight='bold', 
                   ha='right', va='bottom')
