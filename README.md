# W-NOMINATE Analysis - Chilean Congress

Herramientas de análisis W-NOMINATE para votaciones del Congreso de Chile. Este repositorio contiene implementaciones de scripts R (wnominate) y codigos de python para calcular y visualizar puntos ideales de legisladores basados en sus patrones de votación.

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Guía de Uso](#-guía-de-uso)
- [Descripción de Archivos](#-descripción-de-archivos)
- [Flujos de Trabajo](#-flujos-de-trabajo)
- [Resultados](#-resultados)

## 📖 Descripción

W-NOMINATE (Weighted Nominal Three-Step Estimation) es un método estadístico para estimar puntos ideales de legisladores en un espacio político multidimensional basado en sus patrones de votación. Este proyecto proporciona:

- **Análisis en R**: Implementación oficial usando el paquete `wnominate` de R
- **Visualizaciones**: Mapas políticos interactivos que muestran el posicionamiento ideológico

### Dimensiones de Análisis

- **Primera Dimensión**: Espectro económico (Izquierda ← → Derecha)
- **Segunda Dimensión**: Temas sociales (Liberal ← → Conservador)

## 📁 Estructura del Proyecto

```
wnominate_tests/
│
├── src/                          # Código fuente Python
│   ├── wnominate_api.py         # API principal - Conexión MongoDB y cálculos
│   ├── wnominate_graph.py       # Generación de visualizaciones desde MongoDB
│   ├── csv_wnominate_graph.py   # Visualizaciones desde archivos CSV
│   └── rnominate_interface.py   # Exportador de datos para análisis R
│
├── scripts/                      # Scripts ejecutables
│   ├── python/
│   │   └── nominate_cli.py      # Interfaz de línea de comandos
│   └── r/
│       ├── r_wnominate_script.R              # Script principal de análisis R
│       ├── r_wnominate_with_polarity.R       # Análisis con anclajes de polaridad
│       ├── correct_polarity.R                # Corrección de orientación política
│       ├── compare_results.R                 # Comparación R vs Python
│       └── r_wnominate_script_backup.R       # Respaldo del script principal
│
├── data/                         # Datos de entrada y salida
│   ├── input/                   # Datos de entrada (CSVs exportados)
│   │   ├── votes_matrix.csv           # Matriz de votaciones
│   │   ├── legislator_metadata.csv    # Metadatos de legisladores
│   │   └── vote_metadata.csv          # Metadatos de votaciones
│   └── output/                  # Resultados generados
│       ├── wnominate_coordinates.csv         # Coordenadas calculadas
│       ├── wnominate_bill_parameters.csv     # Parámetros de votaciones
│       └── wnominate_coordinates_corrected.csv  # Coordenadas con polaridad corregida
│
├── results/                      # Visualizaciones generadas
│   └── images/                  # Mapas políticos (PNG)
│
├── requirements.txt              # Dependencias Python
└── README.md                     # Este archivo
```

## 🔧 Requisitos

### Python

- Python 3.8 o superior
- MongoDB (con datos de votaciones cargados)

### R

- R 4.0 o superior
- RStudio (opcional, pero recomendado)

## 📦 Instalación

### 1. Clonar el Repositorio

```bash
git clone https://github.com/pabloantivil/wnominate_tests.git
cd wnominate_tests
```

### 2. Instalar Dependencias de Python

```bash
pip install -r requirements.txt
```

**Dependencias principales:**

- `pymongo`: Conexión a MongoDB
- `numpy`: Cálculos numéricos
- `matplotlib`: Visualizaciones
- `pandas`: Manipulación de datos

### 3. Instalar Paquetes de R

Abrir R o RStudio y ejecutar:

```r
install.packages("pscl")
install.packages("wnominate")
install.packages("dplyr")
install.packages("ggplot2")
```

### 4. Configurar MongoDB

Asegurarse de tener MongoDB ejecutándose con la base de datos de votaciones. Por defecto, el código espera:

- **Host**: `localhost:27017`
- **Base de datos**: `votaciones_chile`
- **Colecciones**: `legisladores`, `votaciones`, `votos`

## 🚀 Guía de Uso

### Análisis con R (Recomendado para mayor precisión)

#### Paso 1: Exportar Datos desde MongoDB

```bash
python src/rnominate_interface.py
```

Esto generará en `data/input/`:

- `votes_matrix.csv` - Matriz de votaciones (legisladores × votaciones)
- `legislator_metadata.csv` - Información de legisladores
- `vote_metadata.csv` - Información de votaciones

También creará un script R personalizado en `scripts/r/`.

#### Paso 2: Ejecutar Análisis W-NOMINATE en R

**Opción 2.1: Script con detección automática de polaridad**

```bash
cd scripts/r
Rscript r_wnominate_script.R
```

**Opción 2.2: Script con anclajes de polaridad específicos** (Opcional)

```bash
cd scripts/r
Rscript r_wnominate_with_polarity.R
```

Este script usa anclajes predefinidos:

- **Ancla izquierda**: Amaro Labra (PC - Partido Comunista)
- **Ancla derecha**: Enrique Van Rysselberghe (UDI - Unión Demócrata Independiente)

Resultados en `data/output/`:

- `wnominate_coordinates.csv` - Coordenadas ideales
- `wnominate_bill_parameters.csv` - Parámetros de votaciones

#### Paso 3: Corregir Polaridad de Opción 2.1 (Si es necesario)

Si los resultados tienen la polaridad invertida:

```bash
cd scripts/r
Rscript correct_polarity.R
```

Esto generará:

- `data/output/wnominate_coordinates_corrected.csv`
- `results/images/wnominate_map_corrected_polarity.png`
- `results/images/wnominate_polarity_comparison.png`

#### Paso 4: Visualizar Resultados desde CSV

```bash
python src/csv_wnominate_graph.py --csv-file data/output/wnominate_coordinates.csv --output results/images/mapa_wnominate_chile.png
```

**Con coordenadas corregidas:**

```bash
python src/csv_wnominate_graph.py --csv-file data/output/wnominate_coordinates_corrected.csv --output results/images/mapa_wnominate_chile_corrected.png

```

## 📄 Descripción de Archivos

### Código Fuente Python (`src/`)

| Archivo                  | Descripción                                                                                                       |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| `wnominate_api.py`       | Módulo principal con funciones para conectar a MongoDB, generar payloads, y calcular W-NOMINATE usando pynominate |
| `wnominate_graph.py`     | Genera visualizaciones de mapas políticos directamente desde resultados JSON o MongoDB                            |
| `csv_wnominate_graph.py` | Crea visualizaciones desde archivos CSV (resultados de R). Soporta comparaciones                                  |
| `rnominate_interface.py` | Exporta datos de MongoDB a formato CSV compatible con R, y genera scripts R automáticamente                       |

### Scripts (`scripts/`)

#### Python (`scripts/python/`)

| Archivo           | Descripción                                                                            |
| ----------------- | -------------------------------------------------------------------------------------- |
| `nominate_cli.py` | Interfaz de línea de comandos para ejecutar análisis W-NOMINATE completo desde MongoDB |

#### R (`scripts/r/`)

| Archivo                       | Descripción                                                                      |
| ----------------------------- | -------------------------------------------------------------------------------- |
| `r_wnominate_script.R`        | Script principal de análisis con detección automática de polaridad               |
| `r_wnominate_with_polarity.R` | Análisis con anclajes de polaridad predefinidos (Amaro Labra y Van Rysselberghe) |
| `correct_polarity.R`          | Corrige la orientación de las coordenadas (invierte ejes si es necesario)        |
| `compare_results.R`           | Plantilla para comparar resultados entre R y Python                              |

### Datos (`data/`)

#### Entrada (`data/input/`)

Archivos CSV generados por `rnominate_interface.py`:

- **votes_matrix.csv**: Matriz de votaciones (filas = legisladores, columnas = votaciones)
- **legislator_metadata.csv**: Nombres, partidos, regiones de legisladores
- **vote_metadata.csv**: Fechas, descripciones de votaciones

#### Salida (`data/output/`)

Resultados generados:

- **wnominate_coordinates.csv**: Coordenadas ideales de legisladores
- **wnominate_bill_parameters.csv**: Parámetros estimados de votaciones
- **wnominate_coordinates_corrected.csv**: Coordenadas con polaridad corregida

## 🔄 Flujos de Trabajo

### Flujo Recomendado: Análisis Profesional

```mermaid
MongoDB → rnominate_interface.py → CSV Files → r_wnominate_script.R → correct_polarity.R →
Resultados CSV → csv_wnominate_graph.py → Visualizaciones PNG
```

**Comandos:**

```bash
# 1. Exportar datos
python src/rnominate_interface.py

# 2. Ejecutar análisis R
cd scripts/r
Rscript r_wnominate_script.R
cd ../..

# 3. Ejecutar correción de polaridad del script "r_wnominate_script.R"

# 4. Generar visualización
python src/csv_wnominate_graph.py --csv-file data/output/wnominate_coordinates_corrected.csv --output results/images/mapa_final.png
```

## 📝 Notas Técnicas

### Codificación de Votos

- **1**: Voto "Sí"
- **0**: Voto "No"
- **9**: Abstención/Ausencia/Pareo
- **NA**: Dato faltante

### Anclajes de Polaridad

Para mantener consistencia en la orientación política:

- Se usan legisladores de ideología conocida como anclas
- Evita que el eje izquierda-derecha se invierta entre ejecuciones

## 📧 Contacto

**Autor**: Pablo Antivil  
**GitHub**: [@pabloantivil](https://github.com/pabloantivil)  
**Repositorio**: [wnominate_tests](https://github.com/pabloantivil/wnominate_tests)

---

**Última actualización**: Octubre 2025
