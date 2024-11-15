
import zipfile
import os
import rasterio
from rasterio.plot import show
import geopandas as gpd
import numpy as np
from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
import imageio

extraction_dir = "./dados"  # Diretório onde os arquivos serão extraídos
temp_dir = "./temp_animation"  # Diretório para armazenar imagens temporárias
gif_path = "./flood_simulation.gif"  # Caminho para salvar o GIF
gif_path_infinite = "./flood_simulation_infinite.gif"  # Caminho para o GIF infinito

# Etapa 1: Extrair os arquivos do ZIP
os.makedirs(extraction_dir, exist_ok=True)

# Etapa 2: Carregar os dados raster e shapefile
raster_path = os.path.join(extraction_dir, r'C:\02_work\Geoprocessamento\00_M\2024\01\Arquivo\raster.tif')
shapefile_path = os.path.join(extraction_dir, r'C:\02_work\Geoprocessamento\00_M\2024\01\Arquivo\novo_rio.shp')

raster_data = rasterio.open(raster_path)
river_data = gpd.read_file(shapefile_path)

# Etapa 3: Preparar os dados de elevação e calcular o hillshade
elevation_data = raster_data.read(1)
raster_transform = raster_data.transform
no_data_value = raster_data.nodata
elevation_data_masked = np.where(elevation_data == no_data_value, np.nan, elevation_data)

light_source = LightSource(azdeg=315, altdeg=45)
hillshade = light_source.hillshade(elevation_data_masked, vert_exag=1, dx=1, dy=1)

# Etapa 4: Gerar animação de inundação

os.makedirs(temp_dir, exist_ok=True)

# Intervalos de inundação
c_ini = 0
c_fim = 10
c_passo = 0.1
flood_levels = np.arange(c_ini, c_fim, c_passo)  # Intervalos de 0,5m até 10m
image_files = []

for level in flood_levels:
    flood_potential = elevation_data_masked <= level
    flood_map = np.where(flood_potential, 1, 0)

    fig, ax = plt.subplots(figsize=(10, 10))
    plt.imshow(hillshade, cmap='gray', extent=(raster_transform[2], raster_transform[2] + raster_data.width * raster_transform[0], 
                                               raster_transform[5] + raster_data.height * raster_transform[4], raster_transform[5]))
    river_data.plot(ax=ax, edgecolor='blue', label="River")
    plt.imshow(flood_map, cmap='Blues', alpha=0.5, extent=(raster_transform[2], raster_transform[2] + raster_data.width * raster_transform[0], 
                                                           raster_transform[5] + raster_data.height * raster_transform[4], raster_transform[5]))

    plt.title(f"Flood Potential Areas at {level:.1f}m Increase")
    plt.legend(["River"])

    frame_path = os.path.join(temp_dir, f"flood_level_{level:.1f}m.png")
    plt.savefig(frame_path, bbox_inches='tight')
    plt.close(fig)
    image_files.append(frame_path)

# Criar o GIF com loop infinito
with imageio.get_writer(gif_path_infinite, mode='I', duration=0.5, loop=0) as writer:
    for file in image_files:
        image = imageio.imread(file)
        writer.append_data(image)

# Limpar arquivos temporários
for file in image_files:
    os.remove(file)

print(f"GIF com repetição infinita salvo em: {gif_path_infinite}")
