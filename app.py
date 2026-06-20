import streamlit as st
import pandas as pd

# ── configuracion ──────────────────────────────────────────────
st.set_page_config(page_title="Caso 2 – TSP", layout="wide")

# ── datos ──────────────────────────────────────────────────────
NODES = [0, 3, 10, 21, 22, 35, 40, 41, 47, 65, 71, 76, 77]
N = len(NODES)

D = [
 [ 0, 29, 18, 16, 24, 32, 17, 28, 29, 27, 27, 33, 34],
 [29,  0, 38, 40, 29, 48, 15, 57, 27, 53, 55, 24, 44],
 [18, 38,  0, 31, 42, 49, 22, 27, 21, 19, 36, 50, 16],
 [16, 40, 31,  0, 21, 18, 32, 25, 45, 30, 16, 34, 47],
 [24, 29, 42, 21,  0, 20, 30, 46, 46, 48, 36, 14, 56],
 [32, 48, 49, 18, 20,  0, 45, 40, 60, 47, 25, 33, 65],
 [17, 15, 22, 32, 30, 45,  0, 44, 16, 39, 45, 32, 30],
 [28, 57, 27, 25, 46, 40, 44,  0, 48, 11, 17, 59, 41],
 [29, 27, 21, 45, 46, 60, 16, 48,  0, 40, 54, 48, 18],
 [27, 53, 19, 30, 48, 47, 39, 11, 40,  0, 26, 60, 30],
 [27, 55, 36, 16, 36, 25, 45, 17, 54, 26,  0, 50, 52],
 [33, 24, 50, 34, 14, 33, 32, 59, 48, 60, 50,  0, 62],
 [34, 44, 16, 47, 56, 65, 30, 41, 18, 30, 52, 62,  0],
]

# ── solver Held-Karp ───────────────────────────────────────────
@st.cache_data
def held_karp():
    INF = float("inf")
    dp     = [[INF] * N for _ in range(1 << N)]
    parent = [[-1]  * N for _ in range(1 << N)]
    dp[1][0] = 0

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

    path, mask, cur = [], full, last
    while cur != -1:
        path.append(cur)
        prev = parent[mask][cur]
        mask ^= (1 << cur)
        cur = prev
    path.reverse()
    path.append(0)
    return best, path

dist_total, idx_path = held_karp()
real_path = [NODES[i] for i in idx_path]

# ── UI ─────────────────────────────────────────────────────────
st.title("Caso 2 – Empresa de Distribución: TSP Exacto")
st.caption("II-1122 Modelos de Optimización Industrial · UCR Sede Alajuela")

tab1, tab2, tab3, tab4 = st.tabs(["Solución", "Matriz de distancias", "Modelo AMPL", "Preguntas"])

# ────────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Resultado óptimo")

    col1, col2, col3 = st.columns(3)
    col1.metric("Distancia total", f"{dist_total} km")
    col2.metric("Clientes visitados", 12)
    col3.metric("Nodos totales", 13)

    st.markdown("**Secuencia de visita:**")
    st.info(" → ".join(str(n) for n in real_path))

    st.markdown("**Arcos seleccionados:**")
    rows = []
    for k in range(len(idx_path) - 1):
        i, j = idx_path[k], idx_path[k+1]
        rows.append({"Paso": k+1, "Desde": NODES[i], "Hacia": NODES[j], "Distancia (km)": D[i][j]})
    df_arcos = pd.DataFrame(rows)
    st.dataframe(df_arcos, use_container_width=True, hide_index=True)
    st.markdown(f"**Total: {dist_total} km**")

# ────────────────────────────────────────────────────────────────
with tab2:
    st.subheader("Matriz de distancias mínimas (km)")
    st.caption("Simétrica · diagonal = 0 · fila/columna 0 es el depósito")
    df_matrix = pd.DataFrame(D, index=NODES, columns=NODES)
    st.dataframe(df_matrix.style.highlight_min(axis=None, color="#d4edda")
                                .highlight_max(axis=None, color="#f8d7da"),
                 use_container_width=True)

# ────────────────────────────────────────────────────────────────
with tab3:
    st.subheader("Modelo AMPL – Formulación MTZ")

    st.markdown("**Conjunto y parámetros**")
    st.code("set N;               # deposito (0) + 12 clientes\nparam d {N, N} >= 0; # distancias minimas en km", language="text")

    st.markdown("**Variables**")
    st.code(
        "var x {i in N, j in N: i <> j} binary;         # 1 si se recorre arco i->j\n"
        "var u {i in N diff {0}} >= 1, <= card(N) - 1;  # posicion en la ruta (MTZ)",
        language="text"
    )

    st.markdown("**Función objetivo**")
    st.code(
        "minimize TotalDistance:\n"
        "    sum {i in N, j in N: i <> j} d[i,j] * x[i,j];",
        language="text"
    )

    st.markdown("**Restricciones**")
    st.code(
        "subject to Salida {i in N}:\n"
        "    sum {j in N: j <> i} x[i,j] = 1;\n\n"
        "subject to Entrada {j in N}:\n"
        "    sum {i in N: i <> j} x[i,j] = 1;\n\n"
        "subject to MTZ {i in N diff {0}, j in N diff {0}: i <> j}:\n"
        "    u[i] - u[j] + (card(N) - 1) * x[i,j] <= card(N) - 2;",
        language="text"
    )

    st.markdown("**Tamaño del modelo (n = 13)**")
    df_size = pd.DataFrame({
        "Elemento": ["Variables binarias x[i,j]", "Variables continuas u[i]", "Total variables",
                     "Restricciones salida única", "Restricciones entrada única",
                     "Restricciones MTZ", "Total restricciones"],
        "Fórmula": ["n²", "n", "n²+n", "n", "n", "n(n−1)", "n²+n + n(n−1)"],
        "Valor (n=13)": [169, 13, 182, 13, 13, 156, 182],
    })
    st.dataframe(df_size, use_container_width=True, hide_index=True)

# ────────────────────────────────────────────────────────────────
with tab4:
    st.subheader("Respuestas a las preguntas del caso")

    with st.expander("Parte I – Comprensión del enfoque (30 pts)"):
        st.markdown("**Pregunta 1 (10 pts)**")
        st.write(
            "La red vial real contiene cientos de nodos y miles de arcos. Si se formulara el TSP "
            "directamente sobre ella, el número de variables binarias explotaría, haciendo el modelo "
            "intratable. Al calcular primero el camino más corto entre los 13 puntos relevantes "
            "(depósito + 12 clientes) mediante Dijkstra o Floyd-Warshall, se reduce el problema a "
            "una matriz 13×13. Esto es válido porque el segmento óptimo entre cualquier par de "
            "clientes siempre será el camino más corto de la red vial, sin importar las calles intermedias."
        )
        st.markdown("**Pregunta 2 (10 pts)**")
        st.write(
            "Una solución representa la secuencia óptima de visita: el vehículo parte del depósito "
            "(nodo 0), pasa exactamente una vez por cada uno de los 12 clientes y regresa al depósito, "
            "recorriendo la menor distancia total posible. En la práctica, indica al repartidor el orden "
            "exacto en que debe visitar cada punto para minimizar los kilómetros recorridos en la jornada."
        )
        st.markdown("**Pregunta 3 (10 pts)**")
        st.write(
            "Con la formulación MTZ para n = 13: 169 variables binarias + 13 continuas = 182 variables; "
            "13 + 13 + 156 = 182 restricciones. La versión estudiantil de AMPL admite hasta ~500 de cada "
            "uno, por lo que esta instancia entra con holgura. Una red vial completa generaría decenas de "
            "miles de variables, lo que requeriría licencia comercial con CPLEX o Gurobi."
        )

    with st.expander("Parte II – Implementación en AMPL (45 pts)"):
        st.markdown("**Pregunta 4 (10 pts)**")
        st.write("Minimiza la suma de las distancias de todos los arcos recorridos, incluyendo el regreso al depósito.")
        st.code("minimize TotalDistance:\n    sum {i in N, j in N: i <> j} d[i,j] * x[i,j];", language="text")

        st.markdown("**Pregunta 5 (10 pts)**")
        st.code(
            "subject to Salida {i in N}:\n    sum {j in N: j <> i} x[i,j] = 1;\n\n"
            "subject to Entrada {j in N}:\n    sum {i in N: i <> j} x[i,j] = 1;",
            language="text"
        )

        st.markdown("**Pregunta 6 (15 pts)**")
        st.write(
            "Sin restricciones MTZ el solver puede devolver subtours separados (ej. 0→65→41→0 y 3→40→47→3) "
            "que no tienen sentido operativo. Las restricciones MTZ asignan un número de orden a cada visita, "
            "forzando una única cadena que parte y regresa al depósito."
        )
        st.code(
            "var u {i in N diff {0}} >= 1, <= card(N) - 1;\n\n"
            "subject to MTZ {i in N diff {0}, j in N diff {0}: i <> j}:\n"
            "    u[i] - u[j] + (card(N) - 1) * x[i,j] <= card(N) - 2;",
            language="text"
        )

        st.markdown("**Pregunta 7 (10 pts)**")
        st.success(f"Distancia total óptima: {dist_total} km")
        st.write("Secuencia: " + " → ".join(str(n) for n in real_path))

    with st.expander("Parte III – Análisis y escenarios (25 pts)"):
        st.markdown("**Pregunta 8 (10 pts)**")
        import math
        df_q8 = pd.DataFrame({
            "Elemento": ["Variables binarias", "Variables continuas", "Restricciones MTZ"],
            "n = 13": [169, 13, 156],
            "n = 14": [196, 14, 182],
            "Incremento": ["+27", "+1", "+26"],
        })
        st.dataframe(df_q8, use_container_width=True, hide_index=True)
        st.write(
            f"El espacio de soluciones crece factorialmente: 12! ≈ {math.factorial(12):,} rutas → "
            f"13! ≈ {math.factorial(13):,}. Para n > 25 los solvers exactos dejan de ser viables."
        )

        st.markdown("**Pregunta 9 (5 pts)**")
        st.write(
            "Si el arco afectado pertenece a la ruta óptima (ej. 65→41 con 11 km), al aumentar su costo "
            "el solver puede encontrar una ruta alternativa más barata. Si el arco no está en la solución "
            "óptima, la ruta no cambia. En cualquier caso se debe actualizar la matriz y re-ejecutar el modelo."
        )

        st.markdown("**Pregunta 10 (10 pts)**")
        st.write(
            "La matriz 13×13 guarda solo la distancia mínima, no el trayecto real. Para reconstruir la "
            "ruta vial completa sería necesario guardar: (1) la matriz de predecesores next[i][j] "
            "(resultado de Dijkstra/Floyd-Warshall) para reconstruir el path paso a paso, y (2) los "
            "atributos geográficos de cada arco (nombre de calle, coordenadas, sentido de circulación)."
        )
