
# Comparar los resultados de R W-NOMINATE con los resultados de Python pynominate

# Cargar resultados de R  
r_coords <- read.csv("wnominate_coordinates.csv")

# Cargar resultados de Python (ajustar la ruta según sea necesario)
# python_file <- "../all_votes_dwnominate.json"
# python_results <- jsonlite::fromJSON(python_file)

# TODO: Agregar el análisis de Procrustes para alinear los dos sistemas de coordenadas
# TODO: Calcular la correlación entre las coordenadas de R y Python
# TODO: Identificar discrepancias importantes

cat("Utilizar este script para comparar los resultados de R y Python después de ejecutar ambos análisis.\n")
