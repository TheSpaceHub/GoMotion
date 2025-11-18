import pandas as pd
import barri_manager
import networkx as nx
import math

distance_graph = barri_manager.create_graph(draw=False)

barri_list = list(distance_graph.nodes)

# phi_df holds all phi_m(X) and phi_m for all m
phi_df = pd.DataFrame(columns=["day", "Barcelona"] + barri_list)
phi_df.set_index("day")


def l(t):
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


def load_phis(data_df: pd.DataFrame):
    # store index
    day = data_df["day"].iloc[0]

    # define parameters
    alpha = 5
    beta = 20

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
            c += 1
            A = barri_list[a]
            B = barri_list[b]
            # get the beta shortest paths and add to the gammas
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
            # for every trajectory, we add to the intensities of the corresponding barris
            for i in range(len(trajectories)):
                for j in range(len(trajectories[i]) - 1):
                    if (
                        trajectories[i][j] == "Sant Gervasi - Galvany"
                        and trajectories[i][j + 1] == "la Marina de Port"
                    ):
                        print("AAAAAAAAAAAAAAAAAAAAa")
                        exit()
                    gamma[barri_to_index[trajectories[i][j]]][
                        barri_to_index[trajectories[i][j + 1]]
                    ] += (p_dist[i] * N[a][b])
            print(math.floor(10000 * c / (n * n - n)) / 100)
    phi = [0] * n
    for x in range(len(barri_list)):
        phi[x] = sum([gamma[x][y] + gamma[y][x] for y in range(len(barri_list))])
        print(barri_list[x], phi[x])

    big_phi = sum(phi) / 2
    print(big_phi)


csv = pd.read_csv("data/test.csv")
load_phis(csv[csv["day"] == "2023-01-01"])
