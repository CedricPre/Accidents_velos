import requests

# url API pour téléchargé le fichier
url_accidents_velos = "https://koumoul.com/data-fair/api/v1/datasets/accidents-velos/raw"

url_departements = "https://france-geojson.gregoiredavid.fr/repo/departements.geojson"

response_velos = requests.get(url_accidents_velos)

if response_velos.status_code == 200:
    with open("accidents_velos_raw.csv", "wb") as csv_file:
        csv_file.write(response_velos.content)
        print("Le fichier CSV a été téléchargé avec succès.")
else:
    print(f"Erreur lors de la requête API : {response_velos.status_code}")

response_dep = requests.get( url_departements)
if response_dep.status_code == 200:
    with open("accidents_velos_raw.csv", "wb") as csv_file:
        csv_file.write(response_velos.content)
        print("Le fichier CSV a été téléchargé avec succès.")
else:
    print(f"Erreur lors de la requête API : {response_velos.status_code}")