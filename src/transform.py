import pandas as pd
from datetime import datetime 
import sqlite3
from pathlib import Path


#On prend le fichier le plus recent de toutes mes collectes
fichiers=list(Path("data").glob(pattern="data_*.json"))
fichier=str(max(fichiers))

# On definit nos constantes et la date de la collecte des données 

df=pd.read_json(fichier)
SEUIL=7
CARBURANTS="sp98","e10","gplc","e85","sp95","gazole"
texte_date = Path(fichier).stem.replace("data_", "") #.stem supprime le dossier et le .json du nom du fichier
date_collecte = datetime.strptime(texte_date, "%Y-%m-%d_%Hh%M")
date_collecte = pd.Timestamp(date_collecte).tz_localize("Europe/Paris").tz_convert("UTC")
print("Date de collecte (UTC) :", date_collecte)

#on visualise la data
print("Visualisons la data \n ")
print(f"{df.info()} \n")
print("columnNames : ")
print(f"{df.columns} \n")
print("nbLigne,nbColonne : ")
print(f"{df.shape} \n")
print("valeurs manquantes :")
print(f"{df.isna().sum()} \n")


#on supprime les colonnes redondantes
print("Verifions si aucune donnée n'a été perdue apres suppression des colonnes redondantes \n")
columnsToDelete=["latitude","longitude","horaires","services","rupture","prix","carburants_rupture_temporaire","carburants_rupture_definitive","horaires_jour"]
df=df.drop(columns=columnsToDelete)
df["latitude"]=df["geom"].apply(lambda g: g["lat"])
df["longitude"]=df["geom"].apply(lambda g: g["lon"])
df=df.drop(columns="geom")
print(f"{df.columns}\n")
print(f"{df.shape}\n")

#verification si ya des stations hors france metropolitaine 
print("verifions si il y'a des stations hors france metropolitaine \n")
print(df["latitude"].min(), df["latitude"].max())
print(f"{df["longitude"].min(), df["longitude"].max()} \n ")

#convertissons les colonnes qui contiennent les dates en vraie type date (on peut rajouter .dt.tz_convert("Europe/Paris") pour regle le fuseau horaire)
print("convertissons les colonnes qui contiennent les dates en vraie type date \n")
print(df["gazole_maj"][0] )

for column in df.columns:
    if column.endswith("_maj"):
        df[column]=pd.to_datetime(df[column])
print(f"{df.info()} \n")

#nous alons maintenant rajouter une colonne age pour chaque type de carburant pour calculer lage de la derniere mise a jour puis ecarter les stations ayant un age superieur au seuil qu on determinera
#on fera une comparaison d un avant apres aussi 
for carburant in (CARBURANTS) :
    prix=carburant+"_prix"
    print(df[prix].isna().sum())
print("\n")

#75% des ages sont inferieurs a 6 jours(.describe()) .En general uen station met a jour les prix en moins 1 fois par semaine (7 jours max) on a pris donc le seuil=7
for carburant in (CARBURANTS) :
    age=carburant+"_age"
    prix=carburant+"_prix"
    date=carburant+"_maj"
    df[age]= date_collecte - df[date]
    df[age]=df[age].dt.days
    df.loc[df[age]>SEUIL, prix] = None
    print(df[prix].isna().sum())
print("\n")

#il reste a changer les valeurs de pop r et a en route et autouroute
#on checke dabord toutes les valeurs possibles de pop et leur nbr dapparitions
print(df["pop"].value_counts(dropna=False,normalize=True))

df["pop"]=df["pop"].map({"R":"route","A":"autoroute"})
df=df.rename(columns={"pop":"type_route"})
print(df["type_route"].value_counts(dropna=False,normalize=True))

#par la methode des quartiles on detecte les valeurs suspectes
for carburant in CARBURANTS :
    print(df[carburant+"_prix"].describe())

for carburant in CARBURANTS :
    colonne = df[carburant + "_prix"]
    q1 = colonne.quantile(0.25)
    q3 = colonne.quantile(0.75)
    iqr = q3-q1
    borne_sup  = q3 + 1.5 * iqr   
    borne_inf  = q1 - 1.5 * iqr
    print(carburant + "_prix")
    print(f"{((colonne>borne_sup )| (colonne<borne_inf)).sum()} valeurs suspectes !! ")

#nous allons ajouter une colonne date_collecte a notre df pour savoir quand esqu on a collecter chaque donnee du fichier puuis enleve les colonnes que sqlLite ne peut pa slire comme les listes

df["date_collecte"]=date_collecte
df = df.drop(columns=["carburants_disponibles", "carburants_indisponibles"])
df["services_service"] = df["services_service"].str.join(";")

#Connectons notre tableau a une base sqlite et securiser la base des doublons de tableaux 

conn = sqlite3.connect("data/carburants.db")
try :
    tab_dates_existantes=pd.read_sql("SELECT DISTINCT date_collecte FROM stations ", conn)
    colonne_dates=pd.to_datetime(tab_dates_existantes["date_collecte"],utc=True)
except Exception:
    colonne_dates = pd.Series(dtype="datetime64[ns, UTC]")
if (colonne_dates== date_collecte).any() :
    print("cette collecte existe dèja dans la base !!! \n")
else :
    df.to_sql("stations",conn,if_exists="append",index=False)
print(pd.read_sql("SELECT date_collecte, COUNT(*) AS nb FROM stations GROUP BY date_collecte", conn))
conn.close()

 






























