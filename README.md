==========PROYECTO DE SIMULACIÓN Y OPTIMIZACIÓN DE FÁBRICA==========

====DESCRIPCIÓN====
Este proyecto implementa un sistema completo de simulación y optimización para una fábrica, modelando máquinas, producción, asignación de operarios, costos de materiales, precios de venta, ganancias y redes de transporte. 
Desarrollado en Python, aplica algoritmos clásicos de optimización y teoría de grafos para maximizar la eficiencia productiva.

====CARACTERÍSTICAS PRINCIPALES====

----Modelado de Máquinas----
- Configuraciones múltiples por tipo de máquina (corte, recta, overlock, etc.)
- Velocidad de producción, tasa de desperdicio (depletion rate)
- Rango de operarios por máquina (mínimo y máximo)
- Función de productividad variable según cantidad de operarios

----Producción----
- Cálculo de producción por tiempo o por cantidad de objetos
- Consideración de habilidades de operarios (coeficientes)
- Desperdicio de materiales según tasa de la máquina

----Trazas de Producción----
- Definición de rutas de fabricación por producto
- Múltiples etapas (máquina + configuración) por producto

----Costos y Ganancias----
- Carga de precios de materiales
- Cálculo de costo por producto
- Carga de precios de venta
- Cálculo de ganancias por producto

----Optimización de Asignación de Operarios----
- Algoritmo personalizado para distribuir operarios entre máquinas
- Maximización de productividad según funciones individuales
- Identificación de operarios sobrantes (inutils)

----Optimización de Producción Diaria----
- Construcción de grafo de producción (etapas → productos)
- Algoritmo de Ford-Fulkerson para flujo máximo
- Cálculo de cantidad máxima de productos por día
- Optimización iterativa basada en análisis de grafo residual

----Red de Transporte----
- Carga de tiempos de traslado entre secciones
- Algoritmo de Prim para árbol de expansión mínima
- Visualización de redes con NetworkX y Matplotlib

----Planificación Temporal----
- Cálculo de producción en períodos específicos
- Consideración de días laborales (lunes a sábado)
- Manejo de días feriados
