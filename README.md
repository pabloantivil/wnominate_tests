# W-NOMINATE y DW-NOMINATE - Congreso de Chile

Análisis de puntos ideales de legisladores del Congreso de Chile (2018-2022) usando métodos NOMINATE en R y Python.

## 📋 Contenido

- [¿Qué es esto?](#-qué-es-esto)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Cómo Ejecutar](#-cómo-ejecutar)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🎯 ¿Qué es esto?

Herramientas para calcular posiciones ideológicas de legisladores basándose en sus patrones de votación:

**W-NOMINATE** (Análisis Estático)

- Período completo 2018-2022 como una unidad
- 163 legisladores, 2,215 votaciones
- Snapshot ideológico general

**DW-NOMINATE** (Análisis Dinámico)

- Divide en 5 períodos temporales
- 152 legisladores consistentes
- Detecta evolución y cambios ideológicos

**Resultado**: Coordenadas (x, y) en espacio político 2D

- **Eje X**: Izquierda ← → Derecha
- **Eje Y**: Segunda dimensión (social/valórico)

---

## ⚙️ Requisitos

### Python 3.8+

```bash
pip install pymongo pandas numpy matplotlib
```

### R 4.0+

```r
install.packages(c("pscl", "wnominate", "dplyr", "ggplot2"))
install.packages("remotes")
remotes::install_github("wmay/dwnominate")
```

### MongoDB (local)

- Debe estar corriendo en `localhost:27017`
- Base de datos: `votaciones_chile`

---

## 🚀 Cómo Ejecutar

### OPCIÓN A: Solo W-NOMINATE (Análisis Estático)

#### 1. Exportar datos desde MongoDB

```bash
python rnominate_interface.py --db-name votaciones_chile
```

**Genera**: `data/wnominate/input/` con 3 archivos CSV

#### 2. Ejecutar análisis en R

```bash
cd r_wnominate_data
Rscript r_wnominate_script.R
cd ..
```

**Genera**: `data/wnominate/output/wnominate_coordinates.csv`

#### 3. Corregir polaridad (si es necesario)

```bash
cd r_wnominate_data
Rscript correct_polarity.R
cd ..
```

**Genera**: `wnominate_coordinates_corrected.csv` + gráficos de verificación

#### 4. Visualizar

```bash
python csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates_corrected.csv --output results/wnominate_2018_2022.png
```

**Con nombres de legisladores:**

```bash
python csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates_corrected.csv --labels --output results/wnominate_labeled.png
```

---

### OPCIÓN B: Solo DW-NOMINATE (Análisis Dinámico)

**Prerequisito**: Debe existir `data/wnominate/input/` (ejecutar Opción A, paso 1)

#### 1. Dividir datos en 5 períodos

```bash
python export_votes_for_dwnominate.py --input-dir data/wnominate/input --output-dir data/dwnominate/input
```

**Genera**: 5 matrices `votes_matrix_p1.csv` a `p5.csv`

#### 2. Ejecutar análisis DW-NOMINATE

```bash
cd r_wnominate_data
Rscript r_dwnominate_script.R
cd ..
```

**Genera**: Coordenadas para cada período (p1-p5) en `data/dwnominate/output/`

#### 3. Corregir polaridad

```bash
cd r_wnominate_data
Rscript correct_polarity_dwnominate.R
cd ..
```

**Genera**: Archivos `*_corrected.csv` para cada período

#### 4. Visualizar resultados

**Mapa de un período específico:**

```bash
python csv_dwnominate_graph.py --csv-file data/dwnominate/output/dwnominate_coordinates_p5_corrected.csv --output results/dwnominate_2021.png
```

**Evolución temporal (5 períodos):**

```bash
python csv_dwnominate_graph.py --evolution --csv-dir data/dwnominate/output --output results/dwnominate_evolution.png
```

**Comparación entre períodos:**

```bash
python csv_dwnominate_graph.py --compare P1 P5 --csv-dir data/dwnominate/output --output results/comparison_2018_vs_2021.png
```

**Con etiquetas:**

```bash
python csv_dwnominate_graph.py --csv-file data/dwnominate/output/dwnominate_coordinates_p5_corrected.csv --labels --output results/dwnominate_2021_labeled.png
```

---

## 📁 Estructura del Proyecto

```
wnominate_tests/
├── rnominate_interface.py              # MongoDB → CSV
├── export_votes_for_dwnominate.py      # Dividir en períodos
├── csv_wnominate_graph.py              # Visualizar W-NOMINATE
├── csv_dwnominate_graph.py             # Visualizar DW-NOMINATE
│
├── r_wnominate_data/                   # Scripts R
│   ├── r_wnominate_script.R            # Análisis W-NOMINATE
│   ├── correct_polarity.R              # Corrección W-NOMINATE
│   ├── r_dwnominate_script.R           # Análisis DW-NOMINATE
│   └── correct_polarity_dwnominate.R   # Corrección DW-NOMINATE
│
├── data/
│   ├── wnominate/
│   │   ├── input/                      # CSVs exportados (163 leg., 2215 votos)
│   │   └── output/                     # Coordenadas calculadas
│   └── dwnominate/
│       ├── input/                      # CSVs por período (152 leg.)
│       └── output/                     # Coordenadas por período
│
└── results/                            # Gráficos PNG
```

### Archivos Clave

| Archivo                       | Descripción                            |
| ----------------------------- | -------------------------------------- |
| `votes_matrix.csv`            | Matriz legisladores × votaciones       |
| `legislator_metadata.csv`     | Nombres, partidos, regiones            |
| `*_coordinates.csv`           | Resultados: coord1D (izq-der), coord2D |
| `*_coordinates_corrected.csv` | Con polaridad corregida                |

---

## 📧 Información

**Proyecto**: Análisis ideológico Congreso de Chile 2018-2022  
**Métodos**: W-NOMINATE (estático) y DW-NOMINATE (dinámico)

## 📜 Licencia

Este proyecto es de código abierto para fines académicos y de investigación.

**Paquetes utilizados:**

- `wnominate` (R) - GPL-2
- `dwnominate` (R) - GPL-2
- `pscl` (R) - GPL-2
- Python: MIT License (pandas, matplotlib, numpy, pymongo)

---

**Última actualización**: Noviembre 2025  
**Versión**: 2.0 (incluye DW-NOMINATE dinámico)
