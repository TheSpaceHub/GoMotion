import pandas as pd
import src.barri_manager as barri_manager
import networkx as nx
import math
import os
from collections.abc import Generator

distance_graph = barri_manager.create_graph(draw=False)
barri_list = list(distance_graph.nodes)

def trajectory_length(t: list[str]) -> float:
    """Calculates the length of a given trajectory. A trajectory is an ordered list of visited nodes"""
    
    sum = 0
    for i in range(len(t) - 1):
        sum += distance_graph[t[i]][t[i + 1]].get("weight")
    return sum


def probability_distribution(trajectories: Generator[list[str], None, None], alpha: int|float = 5) -> list[float]:
    """Calulates the probability distributuion for a set of trajectories, all of which share origin and destination"""
    
    p_dist: list[float] = [trajectory_length(t) for t in trajectories]   # Get length of all trajectories
    sum = 0

    # apply function to distance of each trajectory
    min_dist = min(p_dist) 
    for i in range(len(p_dist)):
        p_dist[i] = math.exp(-alpha * p_dist[i] / min_dist)
        sum += p_dist[i]

    # normalize to get probabilities
    for i in range(len(p_dist)):
        p_dist[i] /= sum
    return p_dist


def create_trajectories() -> dict[str,tuple[list[list[str]],list[float]]]:
    """Returns a dict that stores all trajectories from A to B
    and their probability distribution for all A B in Vertices s.t. A != B"""
    
    # Parametres for probability distribution
    alpha = 5
    beta = 20   # Number of paths we consider that go from A to B

    n = len(barri_list)
    pre_trajectories: dict[str,tuple[list[list[str]],list[float]]] = {}

    if os.path.exists("data/trajectories.csv"):  # If we have already computed trajectories and prob distr we dont recalculate them
        print("Fetching trajectories and probability distributions")
        df = pd.read_csv("data/trajectories.csv")
        for _, row in df.iterrows():
            key = row["key"]
            trajectories = [x.split("->") for x in row["trajectories"].split("|")]
            p_dist = [float(p) for p in row["p_dist"].split("|")]
            pre_trajectories[key] = (trajectories, p_dist)  # Rebuild dictionary
            
        return pre_trajectories

    print("Creating trajectories and probability distributions")
    c = 0
    for a in range(n):  # Iterate over all pairs of barris
        for b in range(n):
            if a == b: continue
            A, B = barri_list[a], barri_list[b]
            omega = nx.shortest_simple_paths(distance_graph, A, B, weight="weight") # Get all paths from A to B
            path_count = 0
            trajectories: list[list[str]] = [] # List of all paths that go from A to B
            for path in omega:
                trajectories.append(path)
                path_count += 1
                if path_count == beta:
                    break
            p_dist = probability_distribution(trajectories, alpha)
            pre_trajectories[f"{A}->{B}"] = (trajectories, p_dist)
            c += 1
            print("\r" + str(math.floor(10000 * c / (n * n - n)) / 100) + "%", end="")

    print("")
    print("Saving trajectories and probability distributions")
    pd.DataFrame(   # Store trajectories and prob distr in .csv file
        {
            "key": pre_trajectories.keys(),
            "trajectories": ["|".join(["->".join(t) for t in traj]) for traj, _ in pre_trajectories.values()],
            "p_dist": [
                "|".join([str(p) for p in p_distr]) for _, p_distr in pre_trajectories.values()
            ],
        }
    ).to_csv("data/trajectories.csv")

    return pre_trajectories


def load_phis(data_df: pd.DataFrame, pre_trajectories: dict[str,tuple[list[list[str]],list[float]]]) -> pd.DataFrame:
    """Returns a DataFrame with columns: day (same for every row) barri and intensity"""
    
    # Day we are computing
    day = data_df["day"].iloc[0]
    df = pd.DataFrame({"day": [], "barri": [], "intensity":[]})

    n = len(barri_list)
    barri_to_index: dict[str,int] = {barri_list[i]: i for i in range(n)}
    
    # barri_list2 = data_df["barrio_origen_name"].unique() they are equal :)
    gamma = [[0] * n for _ in range(n)] # create matrix gamma where we will store all journeys that go through barris i and j (i, j adjacent) times the probability of taking that path

    # create and fill the matrix N where in each cell cij we store number of journeys from barri i to j
    N = [[0] * n for _ in range(n)]
    for row in data_df.itertuples():
        N[barri_to_index[row.barrio_origen_name]][
            barri_to_index[row.barrio_destino_name]
        ] = row.viajes

    c = 0
    for a in range(n):
        for b in range(n):
            if a == b: continue
            A, B = barri_list[a], barri_list[b]
            trajectories, p_dist = pre_trajectories[f"{A}->{B}"]
            # for every trajectory, we add to the intensities of the corresponding barris
            for i in range(len(trajectories)):
                for j in range(len(trajectories[i]) - 1):
                    gamma[barri_to_index[trajectories[i][j]]][  
                        barri_to_index[trajectories[i][j + 1]]
                    ] += (p_dist[i] * N[a][b])
            c += 1
            print("\r" + str(math.floor(10000 * c / (n * n - n)) / 100) + "%", end="")
    print("")       
    phi = [0] * n   # We will store phi of each barri here
    for x in range(n):
        phi[x] = sum([gamma[x][y] + gamma[y][x] for y in range(n)]) # Phi or Barri intensity will be the flow out and in of a barri
        new_line = pd.DataFrame({"day": [day], "barri": [barri_list[x]], "intensity": [phi[x]]})
        df = pd.concat([df, new_line], ignore_index=True)

    return df


def process_df(df: pd.DataFrame, pre_trajectories: dict[str,tuple[list[list[str]],list[float]]] = None, download: bool = False) -> pd.DataFrame:
    """This function takes in a DataFrame and divides it by days, later extracting the phis for every day. The trajectories can also be passed, as this helps a lot with efficiency"""
    
    if pre_trajectories is None:
        pre_trajectories = create_trajectories()
    
    if os.path.exists("data/intensities.csv") and not download:
        print("Fetching intensitats.csv")
        df = pd.read_csv("data/intensities.csv")
        df['day'] = pd.to_datetime(df['day'])
        return df
        
    df_results_list: list[pd.DataFrame] = []    # We store dataframes about intensity for each barri for each day

    samples = df.groupby("day")
    for day_group in samples:
        (day, data_df) = day_group
        print("Processing day " + day)
        df_results_list.append(load_phis(data_df, pre_trajectories))

    df = pd.concat(df_results_list, ignore_index=True) 
    df['day'] = pd.to_datetime(df['day'])
    if download: df.to_csv("data/intensities.csv")
    return df
