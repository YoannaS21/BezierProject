import streamlit as st
import numpy as np
import plotly.graph_objects as go
from math import comb

# --- 1. DE CASTELJAU ---
def de_casteljau(points, t):
    temp_points = np.copy(points).astype(float)
    n = len(points)
    for k in range(1, n):
        for i in range(n - k):
            temp_points[i] = (1 - t) * temp_points[i] + t * temp_points[i + 1]
    return temp_points[0]

# --- 2. Аналитична производна ---
def bezier_derivative(points, t):
    n = len(points) - 1
    derivative = np.zeros(2)
    for i in range(n):
        derivative += comb(n-1, i) * ((1-t)**(n-1-i)) * (t**i) * (points[i+1] - points[i])
    derivative *= n
    if np.linalg.norm(derivative) < 1e-8:
        derivative = np.array([1e-6, 0])
    return derivative

# --- 3. Streamlit Конфигурация ---
st.set_page_config(page_title="Поляра на Безие", layout="wide")
st.title("🟦 Интерактивна Поляра на Безие")

# --- 4. Брой точки (Фиксираме 4 за перфектния старт) ---
num_points = st.sidebar.slider("Брой контролни точки", 2, 10, 4, 1)

# --- 5. ХАРДКОДНАТИ "ХУБАВИ" ТОЧКИ ЗА СТАРТ ---
# Тези координати създават перфектна примка и красива поляра
beautiful_defaults = [
    [5.0, 2.0],    # P0
    [15.0, 15.0],  # P1
    [0.0, 15.0],   # P2
    [10.0, 2.0]    # P3
]

# --- 6. Slider-и за координати ---
st.sidebar.header("Контролни точки")
points = []
for i in range(num_points):
    # Ако имаме дефинирани хубави точки за този индекс, ги ползваме, иначе смятаме нови
    if i < len(beautiful_defaults):
        def_x, def_y = beautiful_defaults[i]
    else:
        def_x, def_y = float(i * 3), float((i % 2) * 5)
        
    x = st.sidebar.slider(f"P{i} X", -25.0, 25.0, def_x, key=f"x_{i}")
    y = st.sidebar.slider(f"P{i} Y", -25.0, 25.0, def_y, key=f"y_{i}")
    points.append([x, y])
points = np.array(points)

# --- 7. Изчисления ---
t_values = np.linspace(0, 1, 400)
bezier_curve = np.array([de_casteljau(points, t) for t in t_values])

polar_curve = []
for t in t_values:
    p = de_casteljau(points, t)
    d = bezier_derivative(points, t)
    
    # ПРАВИЛНАТА ПОЛЯРНА ТРАНСФОРМАЦИЯ:
    # Допирателната е: A*x + B*y + C = 0
    A = -d[1]
    B = d[0]
    C = d[1]*p[0] - d[0]*p[1]
    
    # Полюсът е (A/-C, B/-C)
    if abs(C) > 1e-3:
        polar_curve.append([-A/C, -B/C])
polar_curve = np.array(polar_curve)

# --- 8. Plotly Визуализация ---
fig = go.Figure()

# Окръжност r=1 (Директриса)
theta = np.linspace(0, 2*np.pi, 200)
fig.add_trace(go.Scatter(x=np.cos(theta), y=np.sin(theta),
                         mode="lines", line=dict(color="lightgray", dash="dash"),
                         name="Директриса r=1"))

# Контролен полигон
fig.add_trace(go.Scatter(x=points[:,0], y=points[:,1], mode="lines+markers",
                         marker=dict(size=10, color="red"),
                         line=dict(color="rgba(255,0,0,0.2)"),
                         name="Полигон"))

# Безие крива (Синя)
fig.add_trace(go.Scatter(x=bezier_curve[:,0], y=bezier_curve[:,1], mode="lines",
                         line=dict(color="blue", width=4), name="Безие"))

# Полярна крива (Зелена)
if len(polar_curve) > 0:
    fig.add_trace(go.Scatter(x=polar_curve[:,0], y=polar_curve[:,1], mode="lines",
                             line=dict(color="green", width=4), name="Поляра"))

# Настройки на мащаба
fig.update_layout(
    xaxis=dict(range=[-20, 20], zeroline=True),
    yaxis=dict(range=[-20, 20], scaleanchor="x", scaleratio=1),
    height=850, template="plotly_white",
    title="Перфектна визуализация: Примка и нейната Поляра"
)

st.plotly_chart(fig, use_container_width=True)

st.success("Готово! Програмата се отваря с 'Примка' (Loop) – идеален пример за курсова работа.")