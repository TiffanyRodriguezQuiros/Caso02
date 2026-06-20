"""
Caso 2 - TSP Exacto
II-1122 Modelos de Optimizacion Industrial - UCR Sede Alajuela
Deposito: nodo 0 | Clientes: 3,10,21,22,35,40,41,47,65,71,76,77
"""

# -*- coding: utf-8 -*-
import sys
import os
os.environ.setdefault("PYTHONUTF8", "1")
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# --- DATOS ───────────────────────────────────────────────────────────────────

NODES = [0, 3, 10, 21, 22, 35, 40, 41, 47, 65, 71, 76, 77]
N = len(NODES)
IDX = {v: i for i, v in enumerate(NODES)}   # nodo real → indice

# Matriz de distancias minimas (km) - 13x13
D = [
 #  0   3  10  21  22  35  40  41  47  65  71  76  77
 [ 0, 29, 18, 16, 24, 32, 17, 28, 29, 27, 27, 33, 34],  #  0
 [29,  0, 38, 40, 29, 48, 15, 57, 27, 53, 55, 24, 44],  #  3
 [18, 38,  0, 31, 42, 49, 22, 27, 21, 19, 36, 50, 16],  # 10
 [16, 40, 31,  0, 21, 18, 32, 25, 45, 30, 16, 34, 47],  # 21
 [24, 29, 42, 21,  0, 20, 30, 46, 46, 48, 36, 14, 56],  # 22
 [32, 48, 49, 18, 20,  0, 45, 40, 60, 47, 25, 33, 65],  # 35
 [17, 15, 22, 32, 30, 45,  0, 44, 16, 39, 45, 32, 30],  # 40
 [28, 57, 27, 25, 46, 40, 44,  0, 48, 11, 17, 59, 41],  # 41
 [29, 27, 21, 45, 46, 60, 16, 48,  0, 40, 54, 48, 18],  # 47
 [27, 53, 19, 30, 48, 47, 39, 11, 40,  0, 26, 60, 30],  # 65
 [27, 55, 36, 16, 36, 25, 45, 17, 54, 26,  0, 50, 52],  # 71
 [33, 24, 50, 34, 14, 33, 32, 59, 48, 60, 50,  0, 62],  # 76
 [34, 44, 16, 47, 56, 65, 30, 41, 18, 30, 52, 62,  0],  # 77
]

# ─── ALGORITMO HELD-KARP (TSP exacto) ────────────────────────────────────────

INF = float("inf")

def held_karp():
    dp      = [[INF] * N for _ in range(1 << N)]
    parent  = [[-1]  * N for _ in range(1 << N)]
    dp[1][0] = 0   # inicio en nodo 0, mascara = {0}

    for mask in range(1 << N):
        for u in range(N):
            if dp[mask][u] == INF or not (mask >> u & 1):
                continue
            for v in range(N):
                if mask >> v & 1:
                    continue
                new_mask = mask | (1 << v)
                cost = dp[mask][u] + D[u][v]
                if cost < dp[new_mask][v]:
                    dp[new_mask][v] = cost
                    parent[new_mask][v] = u

    full = (1 << N) - 1
    best, last = INF, -1
    for u in range(1, N):
        c = dp[full][u] + D[u][0]
        if c < best:
            best, last = c, u

    # Reconstruir ruta
    path, mask, cur = [], full, last
    while cur != -1:
        path.append(cur)
        prev = parent[mask][cur]
        mask ^= (1 << cur)
        cur = prev
    path.reverse()
    path.append(0)

    return best, path

# ─── RESOLVER ────────────────────────────────────────────────────────────────

dist_total, idx_path = held_karp()
real_path = [NODES[i] for i in idx_path]

# ─── IMPRIMIR RESULTADOS ─────────────────────────────────────────────────────

SEP = "=" * 55

print(SEP)
print("  CASO 2 - SOLUCION OPTIMA TSP")
print("  II-1122 Modelos de Optimizacion Industrial")
print(SEP)

print(f"\nDistancia total optima: {dist_total} km\n")

print("Arcos seleccionados (i → j, distancia):")
print(f"  {'Desde':>5}  {'Hacia':>5}  {'km':>5}")
print(f"  {'-'*5}  {'-'*5}  {'-'*5}")
acumulado = 0
for k in range(len(idx_path) - 1):
    i, j = idx_path[k], idx_path[k+1]
    km = D[i][j]
    acumulado += km
    print(f"  {NODES[i]:>5}  →  {NODES[j]:>5}  {km:>5} km")
print(f"  {'':5}  {'TOTAL':>7}  {acumulado:>5} km")

print("\nSecuencia de visita:")
print("  " + " → ".join(str(n) for n in real_path))

# ─── VARIABLES Y RESTRICCIONES DEL MODELO MTZ ────────────────────────────────

print(f"\n{SEP}")
print("  TAMAÑO DEL MODELO (formulacion MTZ)")
print(SEP)
var_bin  = N * N
var_cont = N
total_var = var_bin + var_cont
rest_sal  = N
rest_ent  = N
rest_mtz  = N * (N - 1)
total_rest = rest_sal + rest_ent + rest_mtz

print(f"  Nodos (n)                    : {N}")
print(f"  Variables binarias  x[i,j]  : {var_bin}")
print(f"  Variables continuas u[i]    : {var_cont}")
print(f"  Total variables             : {total_var}")
print(f"  Restricciones salida unica  : {rest_sal}")
print(f"  Restricciones entrada unica : {rest_ent}")
print(f"  Restricciones MTZ           : {rest_mtz}")
print(f"  Total restricciones         : {total_rest}")
print(f"  (AMPL Student soporta hasta ~500 de cada uno → OK)")

print(f"\n{SEP}")
print("  ANALISIS DE ESCENARIOS")
print(SEP)

n2 = N + 1
print(f"\nQ8 - Si se agrega 1 cliente (n={N} → n={n2}):")
print(f"  Variables binarias : {N**2} → {n2**2}  (+{n2**2 - N**2})")
print(f"  Restricciones MTZ  : {N*(N-1)} → {n2*(n2-1)}  (+{n2*(n2-1) - N*(N-1)})")
print(f"  Espacio de busqueda: {N-1}! ≈ {__import__('math').factorial(N-1):,}  →  {n2-1}! ≈ {__import__('math').factorial(n2-1):,}")

print("\nQ9 - Si aumenta una distancia por cierre de carretera:")
print("  Si el arco afectado esta en la ruta optima, el costo sube")
print("  y el solver podria encontrar una ruta alternativa mas barata.")
print("  Si el arco NO esta en la ruta optima, la solucion no cambia.")

print("\nQ10 - Informacion adicional para reconstruir la ruta vial completa:")
print("  Guardar la matriz de predecesores next[i][j]: el siguiente nodo")
print("  en el camino mas corto de i hacia j (resultado de Dijkstra/Floyd).")
print("  Con eso se puede trazar cada segmento calle por calle.")

print(f"\n{SEP}\n")
