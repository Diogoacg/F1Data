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


# a script that receives drivers and a session and plots their pace for comparison

def plot_pace_comparison(drivers, session):
    
    fig, ax = plt.subplots()
    for driver in drivers:
        print(driver)
        fast_driver = session.laps.pick_driver(driver).pick_fastest()
        print(fast_driver)
        driver_car_data = fast_driver.get_car_data()
        t = driver_car_data['Time']
        vCar = driver_car_data['Speed']
        ax.plot(t, vCar, label=driver)

    ax.set_xlabel('Time')
    ax.set_ylabel('Speed [Km/h]')
    ax.set_title('Pace comparison')
    ax.legend()
    plt.show()

# receives a list of drivesr and a session and gives me a graphic with the mean lap time of each driver in hard compound eliminating the outliers

def plot_mean_lap_time(race):
    # Carrega os dados da corrida

    # Cria uma figura e um eixo para o gráfico
    fig, ax = plt.subplots()

    # Dicionário para armazenar os tempos médios de volta de cada piloto
    mean_lap_times = {}
    drivers = race.results['Abbreviation'].values

    for driver in drivers:
        # Filtra os dados para o piloto e o composto de pneu especificado
        laps = race.laps.pick_quicklaps()
        driver_laps = laps.pick_driver(driver)


        # Calcula o tempo médio de volta, excluindo outliers
        lap_times = driver_laps['LapTime'].astype('int64').values / 1e3  # Converte para microssegundos
        mean_lap_times[driver] = np.mean(lap_times)

    # Ordena os pilotos por tempo médio de volta
    sorted_drivers = sorted(mean_lap_times, key=mean_lap_times.get)

    for driver in sorted_drivers:
        td = datetime.timedelta(microseconds=int(mean_lap_times[driver]))
        # Adiciona os dados ao gráfico
        bar = ax.bar(driver, td.total_seconds())

    # Configura o gráfico
    ax.set_xlabel('Driver')
    ax.set_ylabel('Mean Lap Time (s)')
    ax.set_title('Mean Lap Time per Driver on Hard Tyres')
    ax.grid(True)

    # Ajusta os limites do eixo y para "dar um zoom" nos dados
    min_time = min([bar.get_height() for bar in ax.containers[0]]) - 1
    max_time = max([bar.get_height() for bar in ax.containers[0]]) + 5
    ax.set_ylim([min_time, max_time])

    # Mostra o gráfico
    plt.show()

#get a graph of laps and lap times of a driver or a list of drivers
def plot_lap_times(drivers, session):
    fig, ax = plt.subplots()
    for driver in drivers:
        driver_laps= session.laps.pick_driver(driver)
        # print driver_car_data columns
        print(driver_laps.columns)
        lap_number = driver_laps['LapNumber']
        time = driver_laps['LapTime']
        ax.plot(lap_number, time, label=driver)

    ax.set_xlabel('Lap number')
    ax.set_ylabel('Lap time [s]')
    ax.set_title('Pace comparison')
    ax.legend()
    plt.show()
    
import matplotlib.pyplot as plt

import numpy as np

def plot_race_history(session):
    # cria um grafico que compara a soma dos tempos de volta de cada piloto com o delta do tempo de volta
    # volta de referencia para o delta é a media dos tempos de volta do piloto que ganhou a corrida
    #obter o piloto que ganhou a corrida
    drivers = session.results['Abbreviation'].values
    winner = session.results['Abbreviation'].iloc[0]
    print(session.results)
    driver_laps = session.laps.pick_driver(winner)
    
    time = session.results['Time'].iloc[0]
    #pandas time delta to seconds
    reference_lap_time = time.total_seconds()/session.total_laps

    print(session.total_laps)

    # a cada volta, calcular a diferença entre a soma do tempo das voltas dadas até a volta atual e a referência * numero de voltas até a volta atual
    # e plotar no gráfico
    fig, ax = plt.subplots()
    for driver in drivers:
        driver_laps = session.laps.pick_driver(driver)
        # se alguma volta for negativa, trocar o valor para a media da volta anterior com a volta seguinte
        # get lap times from nanoseconds to seconds
        lap_times = driver_laps['LapTime'].astype('int64').values / 1e9
        # se alguma volta for negativa, trocar o valor para a media da volta anterior com a volta seguinte
        for i in range(1, len(lap_times)-1):
            if lap_times[i] < 0:
                lap_times[i] = (lap_times[i-1] + lap_times[i+1]) / 2
        cumulative_times = np.cumsum(lap_times)
        
        delta_lap_times = np.array([reference_lap_time * i for i in range(1, len(cumulative_times)+1)])

            
        # em caso de abandono, retirar a ultima volta do piloto
        if len(cumulative_times) < session.total_laps - 1:
            cumulative_times = cumulative_times[:-1]
            delta_lap_times = delta_lap_times[:-1]
        
        if winner == driver:
            print(len(cumulative_times))

        ax.plot(range(1, len(cumulative_times) + 1), delta_lap_times - cumulative_times, label=driver)
    
    ax.set_xlabel('Lap number')
    ax.set_ylabel('Delta lap time [s]')
    ax.legend()
    plt.show()

import seaborn as sns
def plot_team_pace_comparison(session):
    fastf1.plotting.setup_mpl(mpl_timedelta_support=False, misc_mpl_mods=False)
    laps = session.laps.pick_quicklaps()
    transformed_laps = laps.copy()
    transformed_laps.loc[:, "LapTime (s)"] = laps["LapTime"].dt.total_seconds()

    # order the team from the fastest (lowest median lap time) tp slower
    team_order = (
        transformed_laps[["Team", "LapTime (s)"]]
        .groupby("Team")
        .median()["LapTime (s)"]
        .sort_values()
        .index
    )
    print(team_order)
    # make a color palette associating team names to hex codes
    team_palette = {team: fastf1.plotting.team_color(team) for team in team_order}
    fig, ax = plt.subplots(figsize=(15, 10))
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

    plt.title(session)
    plt.grid(visible=False)

    # x-label is redundant
    ax.set(xlabel=None)
    plt.tight_layout()
    plt.show()

    
def test_pace_comparison(year, n_test, session):
    session = fastf1.get_testing_session(year, n_test, session)
    session.load()
    plot_pace_comparison(session)
    plot_mean_lap_time(session)