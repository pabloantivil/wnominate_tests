# Comparar los resultados de R W-NOMINATE con los resultados de Python pynominate

# Cargar resultados de R desde data/output
r_coords <- read.csv("../../data/output/wnominate_coordinates.csv")

# Cargar resultados de Python (ajustar la ruta seg�n sea necesario)
# python_file <- "../all_votes_dwnominate.json"
# python_results <- jsonlite::fromJSON(python_file)

# TODO: Agregar el an�lisis de Procrustes para alinear los dos sistemas de coordenadas
# TODO: Calcular la correlaci�n entre las coordenadas de R y Python
# TODO: Identificar discrepancias importantes

cat("Utilizar este script para comparar los resultados de R y Python despu�s de ejecutar ambos an�lisis.\n")
