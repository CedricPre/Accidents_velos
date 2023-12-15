# import
import csv
import doctest
import pandas as pd
import folium, branca
from folium import Choropleth
import geopandas as gpd


def map1(deps : any, lats : any, longs : any, occurences : any) -> None:
    #récupération des départements puis création d'un dashboard
    
    map = folium.Map(location=[48, 2],title = "OpenStreetMap", zoom_start=6)
    for i in range(len(deps)):
        
        dep_occurences = int(occurences.get(deps.iloc[i], 1))# forçage int sinon erreur int64 is not JSON serizlizable
        # accède à l'élément i dans deps, 1 utilisé comme valeur par défaut si occurences n'a pas de valeur associé

        if pd.notna(lats.iloc[i]) and pd.notna(longs.iloc[i]):    
            folium.CircleMarker(
                location=(lats.iloc[i],longs.iloc[i]),
                radius=2,
                color="crimson",
                fill = True,
                fill_color = 'crimson'
            ).add_to(map)

    map.save(outfile='map.html')


def count_zero_coordinates(velo_csv : any) -> int:

    # Compter le nombre de lignes avec des valeurs de latitude ou de longitude égale à zéro
    zero_coordinates_count = ((velo_csv["lat"] == 0) | (velo_csv["long"] == 0)).sum()

    return zero_coordinates_count

def map2(velo_csv : any):
    
    accidents_par_departement = velo_csv.groupby("dep").size()

    map = folium.Map(location=[48.8566, 2.3522],tiles='OpenStreetMap', zoom_start=6)

    for dep, accidents in accidents_par_departement.items():
        
        # Obtenir les données de latitude et de longitude pour le département
        dep_data=  velo_csv[velo_csv["dep"] == dep]
        lats = dep_data["lat"].str.replace(',', '.').astype(float)
        longs = dep_data["long"].str.replace(',', '.').astype(float)

        # Vérifier si les valeurs de latitude et longitude sont présentes et non nulles
        if not lats.isnull().all() and not longs.isnull().all():
            # Calculer la moyenne des latitudes et des longitudes
            avg_lat = lats.mean()
            avg_long = longs.mean()

            # Utiliser le nombre d'accidents pour définir le rayon et la couleur (ajustez selon vos besoins)
            radius = accidents * 0.010  # Ajustez selon vos besoins
            color = 'red' if accidents > 10 else 'green'

            folium.CircleMarker(
                location=(avg_lat, avg_long),
                radius=radius,
                color=color,
                fill=True,
                fill_color=color
            ).add_to(map)

    # Enregistrer la carte en HTML
    map.save(outfile='map_accidents.html')


def map3 (velo_csv : any, geojson_file : any) -> None:


    # Agréger le nombre d'accidents par département
    accidents_par_departement = velo_csv.groupby("dep").size().reset_index(name="nombre_accidents")

    # Fusionner les données agrégées avec le GeoJSON
    geo_data = pd.read_json(geojson_file)
    merged_data = geo_data.merge(accidents_par_departement, how='left', left_on='properties.code', right_on='dep')

    # Création d'une carte centrée sur la France
    map_center = [46.6031, 1.8883]  # Coordonnées géographiques du centre de la France
    my_map = folium.Map(location=map_center, zoom_start=6)
    # Ajouter la choroplèthe avec le nombre d'accidents par département
    Choropleth(
        geo_data=geojson_file,
        name='choropleth',
        data=velo_csv,
        columns=['dep', 'nombre_accidents'],
        key_on='feature.properties.code',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Nombre d\'accidents de vélo par département"
    ).add_to(my_map)

    my_map.save("carte_interactive")


def main():
    velo_csv = pd.read_csv("accidents_velos_raw.csv")
    deps = velo_csv["dep"]

    lats = velo_csv["lat"].str.replace(',','.').astype(float)
    longs = velo_csv["long"].str.replace(',','.').astype(float)

    #on remplace les , par des . et on converti en float pour la map

    occurences = deps.value_counts()
    #map1(deps=deps, lats=lats, longs=longs, occurences=occurences)

    c = count_zero_coordinates(velo_csv=velo_csv)
    #print(c)

    #map2(velo_csv=velo_csv)

    geojson_file = 'departements.geojson'
    map3(velo_csv=velo_csv, geojson_file=geojson_file)

if __name__ == '__main__':
    main()