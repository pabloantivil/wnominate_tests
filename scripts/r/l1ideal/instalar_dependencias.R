# INSTALACIÓN DE DEPENDENCIAS PARA L1IDEAL CON MONGODB
# Instala mongolite (equivalente a pymongo en Python)

cat("📦 INSTALANDO DEPENDENCIAS PARA MONGODB\n\n")

# Verificar dependencias existentes
cat("✓ Verificando paquetes ya instalados...\n")
paquetes_instalados <- installed.packages()[, "Package"]

dependencias <- c("mongolite", "l1ideal", "pscl", "ggplot2", "coda")

for (pkg in dependencias) {
    if (pkg %in% paquetes_instalados) {
        cat(sprintf("  ✅ %s ya instalado\n", pkg))
    } else {
        cat(sprintf("  ⏳ Instalando %s...\n", pkg))

        if (pkg == "l1ideal") {
            # l1ideal desde GitHub
            if (!require("devtools", quietly = TRUE)) {
                install.packages("devtools")
            }
            devtools::install_github("sooahnshin/l1ideal", force = TRUE)
        } else {
            # Otros paquetes desde CRAN
            install.packages(pkg)
        }

        cat(sprintf("  ✅ %s instalado exitosamente\n", pkg))
    }
}

cat("\nTODAS LAS DEPENDENCIAS INSTALADAS\n\n")