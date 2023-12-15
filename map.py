# import
import csv
import json
import doctest
import pandas as pd
import folium
from branca.colormap import LinearColormap
from folium import Choropleth
import geopandas as gpd
import numpy as np



def map_accidents_precis(deps : any, lats : any, longs : any, occurences : any) -> None:
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

def map_accidents_dep (velo_csv : any, geojson_file : any) -> None:

    # Agréger les données pour obtenir le nombre d'accidents par département
    nombre_accidents_par_departement = velo_csv['dep'].value_counts().reset_index()
    nombre_accidents_par_departement.columns = ['dep', 'nombre_accidents']

    # Fusionner les données agrégées avec le GeoJSON
    geojson_data = pd.read_json(geojson_file)

    geojson_data_flat = pd.json_normalize(geojson_data['features'])
    merged_data = pd.merge(geojson_data_flat, nombre_accidents_par_departement, left_on='properties.code', right_on='dep', how='left')
    # Fusionner avec le DataFrame velo_csv pour obtenir les données relatives au sexe
    merged_data = pd.merge(merged_data, velo_csv[['dep', 'sexe']], left_on='dep', right_on='dep', how='left')

    
    merged_data['nombre_accidents'].fillna(0, inplace=True)

    # Création d'une carte centrée sur la France
    map_center = [46.6031, 1.8883]  # Coordonnées géographiques du centre de la France
    my_map = folium.Map(location=map_center, zoom_start=6)

    # Appliquer le logarithme au nombre d'accidents pour une meilleur visibilité sur la carte, Paris ayant trop d'accident par rapport au autre département
    merged_data['nombre_accidents_log'] = merged_data['nombre_accidents'].apply(lambda x: 0 if x == 0 else np.log10(x + 1))

    # Calculer la proportion homme-femme par département
    merged_data['proportion_homme_femme'] = merged_data.groupby('dep')['sexe'].apply(lambda x: (x == '1').sum() / (x == '2').sum() if (x == '2').sum() > 0 else 0)

    # Ajouter la choroplèthe avec le nombre d'accidents par département
    choropleth = folium.Choropleth(
        geo_data=geojson_file,
        name='choropleth',
        data=merged_data,
        columns=['dep', 'nombre_accidents_log'],
        key_on='feature.properties.code',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.9,
        legend_name="Nombre d\'accidents de vélo par département",
        bins=100
    ).add_to(my_map)

    my_map.save("carte_interactive.html")



# Fonction pour afficher des informations au survol d'un département
def on_each_feature(feature, layer):
    popup_content = f"Nom du département : {feature['properties']['nom_du_departement']}"  # Remplacez 'nom_du_departement' par le champ que vous avez dans votre GeoJSON
    layer.add_child(folium.Popup(popup_content))


def main():
    velo_csv = pd.read_csv("accidents_velos_raw.csv")
    deps = velo_csv["dep"]

    lats = velo_csv["lat"].str.replace(',','.').astype(float)
    longs = velo_csv["long"].str.replace(',','.').astype(float)

    # on remplace les , par des . et on converti en float pour la map

    occurences = deps.value_counts()
    map_accidents_precis(deps=deps, lats=lats, longs=longs, occurences=occurences)

    geojson_file = 'departements.geojson'
    map_accidents_dep(velo_csv=velo_csv, geojson_file=geojson_file)
    #c

if __name__ == '__main__':
    main()