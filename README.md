# Caso 2 – TSP Exacto
**II-1122 Modelos de Optimización Industrial – UCR Sede Alajuela**

---

## Descripción

Empresa de distribución que parte del depósito (nodo 0), visita 12 clientes y regresa, minimizando la distancia total. Se resuelve en dos etapas:

1. **Caminos más cortos** → matriz de distancias 13×13
2. **TSP exacto** (Held-Karp / MTZ) → ruta óptima

---

## Archivos

| Archivo | Descripción |
|---|---|
| `caso2_solver.py` | **Ejecutar este** – resuelve el TSP y muestra todos los resultados |
| `caso2_tsp.mod` | Modelo AMPL (formulación MTZ) |
| `caso2_tsp.dat` | Datos AMPL (nodos + matriz de distancias) |
| `caso2_tsp.run` | Script de ejecución AMPL |
| `app.py` | **App web interactiva** – solución, matriz, modelo y preguntas en el navegador |
| `Caso2_Respuestas.md` | Respuestas a las 11 preguntas del caso (Markdown) |
| `Caso2_Respuestas.pdf` | Respuestas listas para entregar — **abrir directamente este** |

---

## Respuestas del caso

Las respuestas a las 11 preguntas están en `Caso2_Respuestas.md` (formato Markdown) y ya convertidas en `Caso2_Respuestas.pdf`.

Para abrir el PDF directamente desde la terminal:

```powershell
start Caso2_Respuestas.pdf
```

---

## Cómo ejecutar

### App web con Streamlit (recomendado)

```powershell
python -m streamlit run app.py
```

Se abre automáticamente en el navegador en `http://localhost:8501`.

### Solo Python (sin navegador)

```powershell
python caso2_solver.py
```

### Con AMPL (si está instalado)

```powershell
ampl caso2_tsp.run
```

---

## Resultado esperado

```
Distancia total óptima: 230 km

Secuencia: 0 → 65 → 41 → 71 → 21 → 35 → 22 → 76 → 3 → 40 → 47 → 77 → 10 → 0
```

---

## Nodos

| Nodo | Rol |
|---|---|
| 0 | Depósito |
| 3, 10, 21, 22, 35, 40, 41, 47, 65, 71, 76, 77 | Clientes |

---

## Modelo (formulación MTZ)

**Variables:**
- `x[i,j]` ∈ {0,1} — 1 si se recorre el arco i→j
- `u[i]` ∈ [1, n−1] — posición del nodo i en la ruta

**Objetivo:**
```
minimize  Σ d[i,j] · x[i,j]
```

**Restricciones:**
```
Σⱼ x[i,j] = 1   ∀i   (salida única)
Σᵢ x[i,j] = 1   ∀j   (entrada única)
u[i] - u[j] + (n-1)·x[i,j] ≤ n-2   (eliminación de subciclos MTZ)
```

---

## Tamaño del modelo (n = 13)

| Elemento | Valor |
|---|---|
| Variables binarias | 169 |
| Variables continuas | 13 |
| Restricciones MTZ | 156 |
| **Total variables** | **182** |
| **Total restricciones** | **182** |
