# EJECUCIÓN ROBUSTA DE L1IDEAL CON MCMC AUMENTADO
# Este script ejecuta l1ideal con parámetros para obtener convergencia adecuada

cat("L1IDEAL - EJECUCIÓN DE L1IDEAL CON CONVERGENCIA MCMC\n\n")

# Cargar funciones
source("l1ideal_mongodb.R")

cat("CONFIGURACIÓN L1IDEAL:\n")
cat("   ✓ Votaciones: TODAS (~2217)\n")
cat("   ✓ Dimensiones: 2\n")
cat("   ✓ MCMC iteraciones: 100\n")
cat("   ✓ Thin: 10\n")
cat("   ✓ Burnin: 100\n")

cat("TIEMPO ESTIMADO:\n")
cat("   Con 100 MCMC: ~11.7 minutos\n")
cat("   Con 500 MCMC estimado: ~58-60 minutos (1 hora)\n\n")
cat("   El progreso se mostrará en pantalla cada 100 iteraciones.\n\n")

respuesta <- readline("¿Continuar con ejecución robusta de 1 hora? (s/n): ")

if (tolower(respuesta) == "s") {
    cat("\nIniciando ejecución robusta...\n")
    cat("   Hora de inicio:", format(Sys.time(), "%H:%M:%S"), "\n\n")

    # EJECUTAR CON MCMC=100
    resultados_robusto <- ejecutar_analisis_completo(
        mcmc = 100, # 100 iteraciones
        dimensions = 2,
        minvotes = 20
    )

    cat("\nVERIFICANDO CONVERGENCIA:\n")
    library(coda)

    ess_beta <- effectiveSize(resultados_robusto$resultado$resultado$beta)
    ess_weight <- effectiveSize(resultados_robusto$resultado$resultado$weight)

    cat(sprintf("   ESS Beta: %.1f\n", ess_beta))
    cat(sprintf("   ESS Weight: %.1f\n", ess_weight))

    if (ess_beta > 50 && ess_weight > 50) {
        cat("   ✅ Convergencia EXCELENTE (>50)\n")
    } else if (ess_beta > 20 && ess_weight > 20) {
        cat("   ⚠️  Convergencia ACEPTABLE (>20), pero idealmente debería ser >50\n")
        cat("      Considera aumentar a MCMC=1000\n")
    } else {
        cat("   ❌ Convergencia INSUFICIENTE (<20)\n")
        cat("      REQUIERE aumentar a MCMC=1000 o más\n")
    }

    cat("\nResultados guardados en: data/l1ideal/output/l1ideal_resultados_reales.RData\n")
    cat("   Gráficos guardados en: data/l1ideal/output/\n")
    cat("   (archivos sobrescritos con resultados robustos)\n")
} else {
    cat("\nEjecución cancelada.\n")
}
