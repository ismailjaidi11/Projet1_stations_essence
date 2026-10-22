import pandas as pd
import sqlite3
from pathlib import Path 
import matplotlib.pyplot as plt
import numpy as np

conn = sqlite3.connect("data/carburants.db")
df = pd.read_sql("SELECT * FROM stations WHERE date_collecte = (SELECT MAX(date_collecte) FROM stations)", conn)
conn.close()

#on regroupe les stations par departements et on regarde l'effet du departement sur les prix du gazole
par_dept = df.groupby("departement")["gazole_prix"].agg(["mean", "count"])
par_dept=par_dept.sort_values("mean")
par_dept["mean"]=par_dept["mean"].round(3)
print(f"les 5 departements les moins chers : {par_dept.head(5)}\n")
print(f"les 5 departements les plus chers : {par_dept.tail(5)}\n")

#On refait la meme chose mais avec un groupeby(type_route)
par_type_route=df.groupby("type_route")["gazole_prix"].agg(["mean", "count"])
par_type_route=par_type_route.sort_values("mean")
par_type_route["mean"]=par_type_route["mean"].round(3)
print("Comparaison des prix entre autoroutes et routes")
print(f" {par_type_route}\n")

#On regarde si les autoroutes n'ont pas trop d'effets sur les prix par departements en ne considerant que les routes dans la df
df_route = df[df["type_route"] == "route"]
par_dept_route = df_route.groupby("departement")["gazole_prix"].agg(["mean", "count"])
par_dept_route=par_dept_route.sort_values("mean")
par_dept_route["mean"]=par_dept_route["mean"].round(3)
print(f"les 5 departements les moins chers : {par_dept_route.head(5)}\n")
print(f"les 5 departements les plus chers : {par_dept_route.tail(5)}\n")

#dessiner la carte des stations de France en distinguant le prix du gazole de chaque region par une couleur 
df_carte = df.dropna(subset=["gazole_prix"])
plt.scatter(x=df_carte["longitude"],y=df_carte["latitude"],s=5,c=df_carte["gazole_prix"],cmap="RdYlGn_r",vmin=df_carte["gazole_prix"].quantile(0.05),vmax=df_carte["gazole_prix"].quantile(0.95))
plt.colorbar()
plt.title("Prix du gazole par station")
plt.savefig(Path("images")/ "carte_gazole.png")
plt.show()

#Un carburant moins cher fait-il plus d'economie ?

CARBURANTS = ("sp98", "e10", "gplc", "e85", "sp95", "gazole")
PLEIN = 50  # litres

# 1. Prix moyen de chaque carburant
colonnes_prix = [c + "_prix" for c in CARBURANTS]
prix_moyens = df[colonnes_prix].mean().sort_values().round(3)
print("Prix moyen par carburant (€/L) :")
print(prix_moyens, "\n")

# 2. Économie E10 vs SP98, calculée sur les moyennes globales
ecart_global = prix_moyens["sp98_prix"] - prix_moyens["e10_prix"]
print(f"Écart moyen SP98 - E10 (moyennes globales) : {ecart_global * 100:.1f} cts/L, soit {ecart_global * PLEIN:.2f} € sur un plein de {PLEIN} L")

# 3. Comparaison rigoureuse : seulement les stations qui vendent les deux
df_both = df.dropna(subset=["e10_prix", "sp98_prix"]).copy()
df_both["ecart"] = df_both["sp98_prix"] - df_both["e10_prix"]
ecart_pareil = df_both["ecart"].mean()
print(f"Écart moyen SP98 - E10 (mêmes stations, {len(df_both)} stations) : {ecart_pareil * 100:.1f} cts/L, soit {ecart_pareil * PLEIN:.2f} € sur un plein de {PLEIN} L")

#Quelles sont les stations les moins cher en gazole autour de cergy ?

# Position de Cergy et rayon de recherche
CERGY_LAT, CERGY_LON = 49.036, 2.076
RAYON_KM = 10

# Distance entre chaque station et Cergy (formule de haversine)
lat1, lon1 = np.radians(CERGY_LAT), np.radians(CERGY_LON)
lat2, lon2 = np.radians(df["latitude"]), np.radians(df["longitude"])
a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
df["distance_km"] = 6371 * 2 * np.arcsin(np.sqrt(a))

# Stations proches avec un prix de gazole, triées du moins cher au plus cher
proches = df[df["distance_km"] <= RAYON_KM].dropna(subset=["gazole_prix"])
proches = proches.sort_values("gazole_prix")

print(f"{len(proches)} stations à moins de {RAYON_KM} km de Cergy")
print(proches[["ville", "adresse", "type_route", "gazole_prix", "distance_km"]].head(10).round(2))
