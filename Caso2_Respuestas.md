# Caso 2 – Empresa de Distribución

II-1122 Modelos de Optimización Industrial – UCR Sede Alajuela


## Parte I – Comprensión del Enfoque

**Pregunta 1**

La red vial real contiene cientos de nodos y miles de arcos. Si se formulara el TSP directamente sobre ella, el número de variables binarias explotaría, haciendo el modelo intratable. Al calcular primero el camino más corto entre los 13 puntos relevantes (depósito + 12 clientes) mediante Dijkstra o Floyd-Warshall, se reduce el problema a una matriz 13×13. Esto es válido porque el segmento óptimo entre cualquier par de clientes siempre será el camino más corto de la red vial, sin importar las calles intermedias.

**Pregunta 2**

Una solución representa la secuencia óptima de visita: el vehículo parte del depósito (nodo 0), pasa exactamente una vez por cada uno de los 12 clientes y regresa al depósito, recorriendo la menor distancia total posible. En la práctica, indica al repartidor el orden exacto en que debe visitar cada punto para minimizar los kilómetros recorridos en la jornada.

**Pregunta 3**

Con la formulación MTZ para n = 13 nodos:

- Variables binarias x[i,j]: 169
- Variables continuas u[i]: 13
- Total variables: 182
- Restricciones salida única: 13
- Restricciones entrada única: 13
- Restricciones MTZ: 156
- Total restricciones: 182

La versión estudiantil de AMPL admite hasta ~500 variables y ~500 restricciones, por lo que esta instancia entra sin problema. Una red vial completa generaría decenas de miles de variables, lo que requeriría licencia comercial con CPLEX o Gurobi.

## Parte II – Implementación en AMPL

**Pregunta 4**

La función objetivo minimiza la suma de las distancias de todos los arcos recorridos:

```
minimize TotalDistance:
    sum {i in N, j in N: i <> j} d[i,j] * x[i,j];
```

Donde x[i,j] = 1 si el vehículo viaja del nodo i al nodo j, y d[i,j] es la distancia mínima en km. Incluye el regreso al depósito.

**Pregunta 5**

Salida única (desde cada nodo se parte exactamente una vez):

```
subject to Salida {i in N}:
    sum {j in N: j <> i} x[i,j] = 1;
```

Entrada única (a cada nodo se llega exactamente una vez):

```
subject to Entrada {j in N}:
    sum {i in N: i <> j} x[i,j] = 1;
```

**Pregunta 6**

Se utiliza la formulación MTZ (Miller-Tucker-Zemlin):

```
var u {i in N diff {0}} >= 1, <= card(N) - 1;

subject to MTZ {i in N diff {0}, j in N diff {0}: i <> j}:
    u[i] - u[j] + (card(N) - 1) * x[i,j] <= card(N) - 2;
```

Sin estas restricciones, el solver puede encontrar soluciones con varios subtours (circuitos separados que no pasan por el depósito). Por ejemplo, podría devolver los ciclos 0→65→41→0 y 3→40→47→3 como solución válida, lo que no tiene sentido operativo. Las restricciones MTZ fuerzan una única ruta que parte y regresa al depósito.

**Pregunta 7**

Distancia total óptima: 230 km

Arcos seleccionados:

- Nodo  0 → Nodo 65: 27 km
- Nodo 65 → Nodo 41: 11 km
- Nodo 41 → Nodo 71: 17 km
- Nodo 71 → Nodo 21: 16 km
- Nodo 21 → Nodo 35: 18 km
- Nodo 35 → Nodo 22: 20 km
- Nodo 22 → Nodo 76: 14 km
- Nodo 76 → Nodo  3: 24 km
- Nodo  3 → Nodo 40: 15 km
- Nodo 40 → Nodo 47: 16 km
- Nodo 47 → Nodo 77: 18 km
- Nodo 77 → Nodo 10: 16 km
- Nodo 10 → Nodo  0: 18 km

Secuencia de visita: 0 → 65 → 41 → 71 → 21 → 35 → 22 → 76 → 3 → 40 → 47 → 77 → 10 → 0


## Parte III – Análisis y Escenarios

**Pregunta 8**

Al pasar de n = 13 a n = 14 nodos:

- Variables binarias: 169 → 196 (+27)
- Variables continuas: 13 → 14 (+1)
- Restricciones MTZ: 156 → 182 (+26)

El incremento numérico parece modesto, pero el TSP es NP-difícil: el espacio de soluciones crece factorialmente. Con 13 nodos hay 12! ≈ 479 millones de rutas; con 14 nodos hay 13! ≈ 6,227 millones. Para instancias grandes (n > 25) los solvers exactos dejan de ser viables y se requieren heurísticas.

**Pregunta 9**

Si el arco afectado pertenece a la ruta óptima (por ejemplo, 65→41 con 11 km), al aumentar su costo el solver puede encontrar una ruta alternativa que antes era más cara. Si el arco no forma parte de la solución óptima, la ruta no cambia. En cualquier caso se debe actualizar la matriz y re-ejecutar el modelo.

**Pregunta 10**

La matriz 13×13 guarda solo la distancia mínima entre cada par de puntos, no el trayecto real. Para reconstruir la ruta vial completa sería necesario guardar:

1. La matriz de predecesores next[i][j]: indica el siguiente nodo en el camino más corto de i hacia j (resultado de Dijkstra o Floyd-Warshall). Con ella se reconstruye el path completo paso a paso.
2. Los atributos geográficos de cada arco (nombre de calle, coordenadas, sentido de circulación) para visualizar y navegar la ruta.

