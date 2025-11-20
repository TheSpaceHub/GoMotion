import pandas as pd
import src.barri_manager as barri_manager
import networkx as nx
import math
import os

distance_graph = barri_manager.create_graph(draw=False)

barri_list = list(distance_graph.nodes)

# phi_df holds all phi_m(X) and phi_m for all m
phi_df = pd.DataFrame(columns=["day", "Barcelona"] + barri_list)
phi_df.set_index("day")


def l(t):
    """Calculates the length of a given trajectory"""
    sum = 0
    for i in range(len(t) - 1):
        sum += distance_graph[t[i]][t[i + 1]].get("weight")
    return sum


def probability_distribution(trajectories, alpha):
    p_dist = []
    sum = 0
    # get lengths
    for t in trajectories:
        p_dist.append(l(t))

    # get probabilities
    min_l = min(p_dist)
    for i in range(len(p_dist)):
        p_dist[i] = math.exp(-alpha * p_dist[i] / min_l)
        sum += p_dist[i]

    # normalize
    for i in range(len(p_dist)):
        p_dist[i] /= sum
    return p_dist


def create_trajectories():
    """This function computes the trajectories to be used"""
    # define parameters
    alpha = 5
    beta = 20

    n = len(barri_list)

    if os.path.exists("data/trajectories.csv") or  os.path.exists("../data/trajectories.csv"):
        print("Fetching trajectories and probability distributions")
        df = pd.read_csv("data/trajectories.csv")
        pre_trajectories = {}
        for _, row in df.iterrows():
            key = row["key"]
            trajectories = [x.split("->") for x in row["trajectories"].split("|")]
            p_dist = [float(p) for p in row["p_dist"].split("|")]
            pre_trajectories[key] = (trajectories, p_dist)
        return pre_trajectories

    pre_trajectories = {}
    print("Creating trajectories and probability distributions")

    c = 0
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            A = barri_list[a]
            B = barri_list[b]
            omega = nx.shortest_simple_paths(distance_graph, A, B, weight="weight")

            path_count = 0
            trajectories = []
            for path in omega:
                # print(path)
                trajectories.append(path)
                path_count += 1
                if path_count == beta:
                    break
            p_dist = probability_distribution(trajectories, alpha)
            pre_trajectories[f"{A}->{B}"] = (trajectories, p_dist)
            c += 1
            print("\r" + str(math.floor(10000 * c / (n * n - n)) / 100) + "%", end="")

    print("Saving trajectories and probability distributions")
    pd.DataFrame(
        {
            "key": pre_trajectories.keys(),
            "trajectories": [
                "|".join(["->".join(t) for t in x])
                for (x, y) in pre_trajectories.values()
            ],
            "p_dist": [
                "|".join([str(p) for p in y]) for (x, y) in pre_trajectories.values()
            ],
        }
    ).to_csv("data/trajectories.csv")

    return pre_trajectories


def load_phis(data_df: pd.DataFrame, pre_trajectories)->pd.DataFrame:
    # store index
    day = data_df["day"].iloc[0]
    df = pd.DataFrame({"day": [], "barri": [], "intensity":[]})

    n = len(barri_list)
    barri_to_index = {}
    for i in range(n):
        barri_to_index[barri_list[i]] = i
    # barri_list2 = data_df["barrio_origen_name"].unique() they are equal :)
    gamma = [[0] * n for _ in range(n)]

    # create and fill the matrix N
    N = [[0] * n for _ in range(n)]
    for row in data_df.itertuples():
        N[barri_to_index[row.barrio_origen_name]][
            barri_to_index[row.barrio_destino_name]
        ] = row.viajes

    c = 0
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            A = barri_list[a]
            B = barri_list[b]
            # get the beta shortest paths and add to the gammas
            trajectories, p_dist = pre_trajectories[f"{A}->{B}"]
            # for every trajectory, we add to the intensities of the corresponding barris
            for i in range(len(trajectories)):
                for j in range(len(trajectories[i]) - 1):
                    gamma[barri_to_index[trajectories[i][j]]][
                        barri_to_index[trajectories[i][j + 1]]
                    ] += (p_dist[i] * N[a][b])
            c += 1
            print("\r" + str(math.floor(10000 * c / (n * n - n)) / 100) + "%", end="")
    phi = [0] * n
    for x in range(len(barri_list)):
        phi[x] = sum([gamma[x][y] + gamma[y][x] for y in range(len(barri_list))])
        new_line = pd.DataFrame({"day": [day], "barri": [barri_list[x]], "intensity": [phi[x]]})
        df = pd.concat([df, new_line], ignore_index=True)

    return df


def process_df(df: pd.DataFrame, pre_trajectories=None)->pd.DataFrame:
    """This function takes in a DataFrame and divides it by days, later extracting the phis for every day. The trajectories can also be passed, as this helps a lot with efficiency"""
    if pre_trajectories is None:
        pre_trajectories = create_trajectories()
    
    df_results_list = []

    samples = df.groupby("day")
    for day_group in samples:
        (day, data_df) = day_group
        #print("Processing day " + day)
        df_results_list.append(load_phis(data_df, pre_trajectories))

    df = pd.concat(df_results_list, ignore_index=True) 
    df['day'] = pd.to_datetime(df['day'])
    return df
