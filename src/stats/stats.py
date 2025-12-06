import matplotlib.pyplot as plt
from peak_classifier import classify_peaks, z_score
import pandas as pd

df = pd.read_csv("data/final_data.csv")[["day", "barri", "intensity"]]

plt.figure(figsize=(10, 6))

for i, b in enumerate(df["barri"].unique()):
    plt.plot(
        sorted(list(z_score(df[df["barri"] == b]["intensity"]))),
        label="Intensity",
        color=(3 * i / 256, 3 * i / 256, 3 * i / 256),
    )

plt.axhline(y=1, color="r", label="Peak")
plt.axhline(y=1.5, color="r", label="Large peak")

large_percs = {}
mid_percs = {}

for b in df["barri"].unique():
    ddf = classify_peaks(df[df["barri"] == b], "intensity")
    large_percs[b] = 100 * len(ddf[ddf["peak_value"] == "Large peak"]) / len(ddf)
    mid_percs[b] = (
        100 * len(ddf[ddf["peak_value"] == "Peak"]) / len(ddf) + large_percs[b]
    )

# avg
print("Average threshold crossings")
print("Peaks:", sum(mid_percs.values()) / len(large_percs))
print("Large peaks:", sum(large_percs.values()) / len(large_percs))
print()

# max
print("Earliest threshold crossings")
print("Peaks:", max(mid_percs.values()), "barri:", max(mid_percs, key=mid_percs.get))
print("Large peaks:", max(large_percs.values()), "barri:", max(large_percs, key=large_percs.get))
print()

# min
print("Latest threshold crossings")
print("Peaks:", min(mid_percs.values()), "barri:", min(mid_percs, key=mid_percs.get))
print("Large peaks:", min(large_percs.values()), "barri:", min(large_percs, key=large_percs.get))
print()

plt.show()
