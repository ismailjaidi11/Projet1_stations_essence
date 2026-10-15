import requests
import json
from datetime import datetime

URL="https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/records"

#On lit les stations 100 par 100 et on les mets dans une liste 
liste=[]
r=requests.get(URL,params= {"limit" : 100 ,"offset":0},timeout=10)
data=r.json()
liste.extend(data["results"])
offset=100

while offset< data["total_count"] :
    r=requests.get(URL,params= {"limit" : 100 ,"offset":offset},timeout=10)
    if r.status_code != 200:
        raise SystemExit(f"Erreur API {r.status_code} à l'offset {offset}, collecte annulée") #on utilise cette fonction au lieu d un simple break car si lextraction echoue il faut arreter tout le programme completement et n'enregistre aucun nouveau fichier ca evitera une collecte partielle des données
    data=r.json()
    liste.extend(data["results"])
    offset+=100

#On enregistre la liste dans une fichier json avec la date et lheure de l'enregistrement

with open(f"data/data_{datetime.now().strftime('%Y-%m-%d_%Hh%M')}.json", "w", encoding="utf-8") as f:
    json.dump(liste,f, ensure_ascii=False,)

#Quelques verifications pour valider l'extraction
print(len(liste))
print(data["total_count"])

ids=[]
for station in liste:
    ids.append(station["id"])
if len(set(ids))!=len(liste):
    print("il ya des doublons")
        













