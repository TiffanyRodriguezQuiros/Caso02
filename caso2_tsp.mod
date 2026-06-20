# ============================================================
# Caso 2 - Modelo TSP con formulacion MTZ
# II-1122 Modelos de Optimizacion Industrial - UCR Sede Alajuela
# ============================================================

set N;                          # nodos: deposito (0) + 12 clientes
param d {N, N} >= 0;            # distancias minimas en km

var x {i in N, j in N: i <> j} binary;          # 1 si se recorre arco i->j
var u {i in N diff {0}} >= 1, <= card(N) - 1;   # posicion en la ruta (MTZ)

# Objetivo: minimizar distancia total recorrida
minimize TotalDistance:
    sum {i in N, j in N: i <> j} d[i,j] * x[i,j];

# Salida unica: desde cada nodo se parte exactamente una vez
subject to Salida {i in N}:
    sum {j in N: j <> i} x[i,j] = 1;

# Entrada unica: a cada nodo se llega exactamente una vez
subject to Entrada {j in N}:
    sum {i in N: i <> j} x[i,j] = 1;

# Eliminacion de subciclos (Miller-Tucker-Zemlin)
# Garantiza una sola cadena que parte y regresa al deposito
subject to MTZ {i in N diff {0}, j in N diff {0}: i <> j}:
    u[i] - u[j] + (card(N) - 1) * x[i,j] <= card(N) - 2;
