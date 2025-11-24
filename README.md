# Análisis de Puntos Ideales - Congreso de Chile

Análisis de puntos ideales de legisladores del Congreso de Chile (2018-2022) usando métodos **W-NOMINATE** y **DW-NOMINATE** con múltiples configuraciones temporales.

## 📋 Contenido

- [¿Qué es esto?](#-qué-es-esto)
- [Métodos Disponibles](#-métodos-disponibles)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Cómo Ejecutar](#-cómo-ejecutar)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🎯 ¿Qué es esto?

Herramientas para calcular posiciones ideológicas de legisladores basándose en sus patrones de votación, con análisis estáticos y dinámicos en diferentes escalas temporales.

**Resultado**: Coordenadas (x, y) en espacio político 2D

- **Eje X**: Izquierda ← → Derecha (económica)
- **Eje Y**: Segunda dimensión (social/valórico)

---

## 🔬 Métodos y Configuraciones Disponibles

### W-NOMINATE (Análisis Estático)

**Configuración 1: Período Completo (Original)**

- Todo el 55º PL (2018-2022) como una unidad
- 163 legisladores, 2,215 votaciones
- Snapshot ideológico general
- ⚡ **Rápido:** 1-3 minutos

**Configuración 2: 3 Períodos (Hitos Políticos)**

- **P1:** 11/03/2018 - 18/10/2019 (Inicio PL → Estallido Social)
- **P2:** 18/10/2019 - 25/10/2020 (Estallido Social → Plebiscito 2020)
- **P3:** 25/10/2020 - 10/03/2022 (Plebiscito 2020 → Fin PL)
- Permite comparar posiciones ideológicas en momentos políticos clave
- Genera análisis de trayectorias entre períodos

### DW-NOMINATE (Análisis Dinámico)

**Configuración 1: 5 Períodos (Original)**

- División temporal equitativa del período legislativo
- 152 legisladores consistentes
- Detecta evolución gradual

**Configuración 2: 6 Períodos (Hitos Políticos)** ⭐ **RECOMENDADO**

- Combina división por eventos políticos con granularidad temporal
- Cada período político dividido en 2 subperíodos:
  - **P1a, P1b:** Inicio PL → Estallido Social (~571 días c/u)
  - **P2a, P2b:** Estallido → Plebiscito (~187 días c/u)
  - **P3a, P3b:** Plebiscito → Fin PL (~250 días c/u)
- Permite análisis detallado de evolución en contextos políticos específicos
- Genera trayectorias en espacio 2D (coord1D vs coord2D)

### Visualizaciones de Trayectorias

**Gráficos Disponibles:**

- **Trayectorias 2D (DW-NOMINATE 6 períodos):** Evolución de partidos en espacio bidimensional
- **Trayectorias W-NOMINATE (3 períodos):** Movimiento entre hitos políticos clave
- Visualización con flechas direccionales y etiquetas de períodos

---

## ⚙️ Requisitos

### Python 3.8+

```bash
pip install pymongo pandas numpy matplotlib
```

### R 4.0+

```r
# Paquetes básicos
install.packages(c("pscl", "wnominate", "dplyr", "ggplot2"))

# DW-NOMINATE
install.packages("remotes")
remotes::install_github("wmay/dwnominate")
```

### MongoDB (local)

- Debe estar corriendo en `localhost:27017`
- Base de datos: `votaciones_chile`

---

## 🚀 Cómo Ejecutar

### OPCIÓN A: W-NOMINATE - Período Completo (Análisis Estático)

#### 1. Exportar datos desde MongoDB

```bash
python src/rnominate_interface.py --db-name votaciones_chile
```

**Genera**: `data/wnominate/input/` con 3 archivos CSV:

- `votes_matrix.csv` (163 legisladores × 2,215 votaciones)
- `legislator_metadata.csv`
- `vote_metadata.csv`

#### 2. Ejecutar análisis en R

```bash
cd scripts/r
Rscript r_wnominate_script.R
cd ../..
```

**Genera**: `data/wnominate/output/wnominate_coordinates.csv`

#### 3. Corregir polaridad (si es necesario)

```bash
cd scripts/r
Rscript correct_polarity_wnominate.R
cd ../..
```

**Genera**: `wnominate_coordinates_corrected.csv` + gráficos de verificación

#### 4. Visualizar

```bash
python src/csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates_corrected.csv --output results/wnominate_2018_2022.png
```

**Con nombres de legisladores:**

```bash
python src/csv_wnominate_graph.py --csv-file data/wnominate/output/wnominate_coordinates_corrected.csv --labels --output results/wnominate_labeled.png
```

---

### OPCIÓN B: DW-NOMINATE - 5 Períodos (Análisis Dinámico Original)

**Prerequisito**: Debe existir `data/wnominate/input/` (ejecutar Opción A, paso 1)

#### 1. Dividir datos en 5 períodos temporales

```bash
python src/export_votes_for_dwnominate.py --input-dir data/wnominate/input --output-dir data/dwnominate/input
```

**Genera**: 5 matrices `votes_matrix_p1.csv` a `p5.csv` (división temporal equitativa)

#### 2. Ejecutar análisis DW-NOMINATE

```bash
cd scripts/r
Rscript r_dwnominate_script.R
cd ../..
```

**Genera**: Coordenadas para cada período (p1-p5) en `data/dwnominate/output/`

#### 3. Corregir polaridad

```bash
cd scripts/r
Rscript correct_polarity_dwnominate.R
cd ../..
```

**Genera**: Archivos `*_corrected.csv` para cada período

#### 4. Visualizar resultados

**Mapa de un período específico:**

```bash
python src/csv_dwnominate_graph.py --csv-file data/dwnominate/output/dwnominate_coordinates_p5_corrected.csv --output results/dwnominate_2021.png
```

**Evolución temporal (5 períodos):**

```bash
python src/csv_dwnominate_graph.py --evolution --csv-dir data/dwnominate/output --output results/dwnominate_evolution.png
```

**Comparación entre períodos:**

```bash
python src/csv_dwnominate_graph.py --compare P1 P5 --csv-dir data/dwnominate/output --output results/comparison_2018_vs_2021.png
```

**Con etiquetas:**

```bash
python src/csv_dwnominate_graph.py --csv-file data/dwnominate/output/dwnominate_coordinates_p5_corrected.csv --labels --output results/dwnominate_2021_labeled.png
```

---

### OPCIÓN C: W-NOMINATE - 3 Períodos (Hitos Políticos)

**Prerequisito**: Debe existir `data/wnominate/input/` (ejecutar Opción A, paso 1)

#### 1. Dividir datos en 3 períodos según eventos políticos

```bash
python src/export_votes_for_wnominate_3periods.py
```

**Genera**: `data/wnominate_3periods/input/` con matrices para 3 períodos:

- **P1:** 11/03/2018 - 18/10/2019 (Inicio → Estallido Social)
- **P2:** 18/10/2019 - 25/10/2020 (Estallido → Plebiscito 2020)
- **P3:** 25/10/2020 - 10/03/2022 (Plebiscito → Fin PL)

#### 2. Ejecutar análisis W-NOMINATE para cada período

```bash
cd scripts/r
Rscript r_wnominate_3periods_script.R
cd ../..
```

**Genera**: Coordenadas para P1, P2, P3 en `data/wnominate_3periods/output/`

#### 3. Corregir polaridad

```bash
cd scripts/r
Rscript correct_polarity_wnominate_3periods.R
cd ../..
```

**Genera**: Archivos `coordinates_p*_corrected.csv` para cada período

#### 4. Visualizar trayectorias temporales

**Gráfico de trayectorias con flechas:**

```bash
python grafico_trayectorias_wnominate_3periods.py
```

**Genera**:

- `results/trayectorias_wnominate_3periods_flechas.png` - Evolución de partidos con vectores direccionales
- `results/trayectorias_wnominate_3periods_inicio_fin.png` - Comparación posición inicial vs final
- `results/posiciones_coord1D_3periods.csv` - Tabla de coordenadas por partido y período
- `results/posiciones_coord2D_3periods.csv`

**Visualizar período específico:**

```bash
python src/csv_wnominate_graph.py --csv-file data/wnominate_3periods/output/coordinates_p2_corrected.csv --output results/wnominate_p2_estallido.png
```

---

### OPCIÓN D: DW-NOMINATE - 6 Períodos (Hitos Políticos + Granularidad) 🎯 **MÁS COMPLETO**

**Prerequisito**: Debe existir `data/wnominate/input/` (ejecutar Opción A, paso 1)

#### 1. Dividir datos en 6 subperíodos

```bash
python src/export_votes_for_dwnominate_6periods.py --input-dir data/wnominate/input --output-dir data/dwnominate_6periods/input
```

**Genera**: `data/dwnominate_6periods/input/` con matrices para 6 subperíodos:

- **P1a, P1b:** División del período Inicio → Estallido Social
- **P2a, P2b:** División del período Estallido → Plebiscito 2020
- **P3a, P3b:** División del período Plebiscito → Fin PL

#### 2. Ejecutar análisis DW-NOMINATE

```bash
cd scripts/r
Rscript r_dwnominate_6periods_script.R
cd ../..
```

**Genera**: Coordenadas para P1a-P3b en `data/dwnominate_6periods/output/`

#### 3. Corregir polaridad

```bash
cd scripts/r
Rscript correct_polarity_dwnominate_6periods.R
cd ../..
```

**Genera**: Archivos `coordinates_P*_6periods_corrected.csv`

#### 4. Visualizar trayectorias en espacio 2D

**Gráfico de evolución temporal bidimensional:**

```bash
python grafico_trayectorias_2d.py
```

**Genera**:

- `results/trayectorias_flechas_6periods.png` - Trayectorias de partidos en espacio coord1D × coord2D
- Muestra evolución completa a través de los 6 períodos
- Visualiza cambios en ambas dimensiones ideológicas simultáneamente

**Visualizar período específico:**

```bash
python src/csv_dwnominate_graph.py --csv-file data/dwnominate_6periods/output/coordinates_P2a_6periods_corrected.csv --output results/dw_6p_estallido.png
```

---

## 📁 Estructura del Proyecto

```
wnominate_tests/
├── grafico_trayectorias_2d.py                      # Trayectorias DW-NOMINATE 6 períodos
├── grafico_trayectorias_wnominate_3periods.py      # Trayectorias W-NOMINATE 3 períodos
│
├── src/
│   ├── rnominate_interface.py                      # MongoDB → CSV
│   ├── export_votes_for_dwnominate.py              # Dividir en 5 períodos (original)
│   ├── export_votes_for_dwnominate_6periods.py     # Dividir en 6 períodos (hitos políticos)
│   ├── export_votes_for_wnominate_3periods.py      # Dividir en 3 períodos (hitos políticos)
│   ├── csv_wnominate_graph.py                      # Visualizar W-NOMINATE
│   └── csv_dwnominate_graph.py                     # Visualizar DW-NOMINATE
│
├── scripts/r/
│   ├── r_wnominate_script.R                        # W-NOMINATE período completo
│   ├── r_wnominate_3periods_script.R               # W-NOMINATE 3 períodos
│   ├── r_dwnominate_script.R                       # DW-NOMINATE 5 períodos
│   ├── r_dwnominate_6periods_script.R              # DW-NOMINATE 6 períodos
│   ├── correct_polarity_wnominate.R                # Corrección W-NOMINATE
│   ├── correct_polarity_wnominate_3periods.R       # Corrección W-NOMINATE 3 períodos
│   ├── correct_polarity_dwnominate.R               # Corrección DW-NOMINATE 5 períodos
│   └── correct_polarity_dwnominate_6periods.R      # Corrección DW-NOMINATE 6 períodos
│
├── data/
│   ├── wnominate/                                  # W-NOMINATE período completo
│   │   ├── input/                                  # 163 legisladores, 2,215 votaciones
│   │   └── output/
│   ├── wnominate_3periods/                         # W-NOMINATE por hitos políticos
│   │   ├── input/                                  # P1, P2, P3
│   │   └── output/
│   ├── dwnominate/                                 # DW-NOMINATE 5 períodos
│   │   ├── input/                                  # División temporal equitativa
│   │   └── output/
│   └── dwnominate_6periods/                        # DW-NOMINATE 6 subperíodos
│       ├── input/                                  # P1a, P1b, P2a, P2b, P3a, P3b
│       └── output/
│
└── results/                                        # Gráficos PNG y CSVs de análisis
    ├── wnominate_*.png
    ├── dwnominate_*.png
    ├── trayectorias_*.png
    └── posiciones_*.csv
```

### Archivos Clave

| Archivo                                 | Descripción                             | Configuración           |
| --------------------------------------- | --------------------------------------- | ----------------------- |
| `votes_matrix.csv`                      | Matriz legisladores × votaciones        | Base (todos)            |
| `legislator_metadata.csv`               | Nombres, partidos, regiones             | Base (todos)            |
| `wnominate_coordinates.csv`             | Resultados W-NOMINATE período completo  | W-NOMINATE completo     |
| `coordinates_p*_corrected.csv`          | W-NOMINATE por hito político            | W-NOMINATE 3 períodos   |
| `dwnominate_coordinates_p*.csv`         | DW-NOMINATE división temporal           | DW-NOMINATE 5 períodos  |
| `coordinates_P*_6periods_corrected.csv` | DW-NOMINATE por hitos con granularidad  | DW-NOMINATE 6 períodos  |
| `*_corrected.csv`                       | Archivos con polaridad corregida        | Todos                   |
| `trayectorias_*.png`                    | Gráficos de evolución temporal          | Análisis de trayectoria |
| `posiciones_coord*D_3periods.csv`       | Tabla de posiciones por partido/período | W-NOMINATE 3 períodos   |

---

## 📧 Información

**Proyecto**: Análisis ideológico Congreso de Chile 2018-2022 (55º Período Legislativo)

**Configuraciones disponibles**:

- **W-NOMINATE:** Período completo | 3 períodos por hitos políticos
- **DW-NOMINATE:** 5 períodos equitativos | 6 subperíodos por hitos políticos

**Visualizaciones**:

- Mapas ideológicos estáticos
- Trayectorias temporales en 2D
- Comparaciones entre períodos

## 📜 Licencia

Este proyecto es de código abierto para fines académicos y de investigación.

**Paquetes utilizados:**

- `wnominate` (R) - GPL-2
- `dwnominate` (R) - GPL-2
- `pscl` (R) - GPL-2
- Python: MIT License (pandas, matplotlib, numpy, pymongo, seaborn)

---

**Última actualización**: Noviembre 2025  
**Versión**: 2.5 (incluye análisis temporal con múltiples configuraciones)
