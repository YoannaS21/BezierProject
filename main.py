import streamlit as st
import numpy as np
import plotly.graph_objects as go

def calculate_blossom_level(points, t_params):
    current_points = np.copy(points).astype(float)
    levels = [current_points]
    for t in t_params:
        if len(current_points) > 1:
            current_points = (1 - t) * current_points[:-1] + t * current_points[1:]
            levels.append(current_points)
    return levels

def get_bezier_curve(control_points, num_steps=100):
    if len(control_points) < 2:
        return control_points
    t_vals = np.linspace(0, 1, num_steps)
    curve = []
    for t in t_vals:
        temp = np.copy(control_points).astype(float)
        for k in range(1, len(control_points)):
            temp = (1 - t) * temp[:-1] + t * temp[1:]
        curve.append(temp[0])
    return np.array(curve)

st.set_page_config(page_title="Крива на Безие и Поляри", layout="wide")
st.title("Поляри на крива на Безие")

st.sidebar.header("Конфигурация")
num_points = st.sidebar.slider("Брой контролни точки", 2, 8, 4)
n_degree = num_points - 1

st.sidebar.subheader("Параметри")
t_params = [st.sidebar.slider(f"t{i+1}", 0.0, 1.0, 0.5, key=f"t{i}") for i in range(n_degree)]

st.sidebar.subheader("Координати на точките")
pts = []
defaults = [[-6, -4], [-3, 6], [3, 6], [6, -4]]
for i in range(num_points):
    col1, col2 = st.sidebar.columns(2)
    def_x = defaults[i][0] if i < len(defaults) else float(i*2)
    def_y = defaults[i][1] if i < len(defaults) else float((i%2)*4)
    x = col1.number_input(f"P{i}.x", value=float(def_x), key=f"x{i}")
    y = col2.number_input(f"P{i}.y", value=float(def_y), key=f"y{i}")
    pts.append([x, y])
pts = np.array(pts)

st.sidebar.subheader("Видимост")
visibility = {0: True} 

for i in range(1, n_degree):
    visibility[i] = st.sidebar.checkbox(f"Поляра ниво {i}", value=True)

visibility[n_degree] = st.sidebar.checkbox(f"Ниво {n_degree} (Blossom)", value=True)

all_control_levels = calculate_blossom_level(pts, t_params)

fig = go.Figure()
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

for i, ctrl_pts in enumerate(all_control_levels):
    if visibility.get(i, False):
        
        if i == n_degree:
            fig.add_trace(go.Scatter(
                x=[ctrl_pts[0][0]], y=[ctrl_pts[0][1]],
                mode='markers',
                name=f"Ниво {i} (Blossom)",
                marker=dict(size=15, color='black', symbol='star')
            ))
        
        else:
            curve_pts = get_bezier_curve(ctrl_pts)
            name_label = "Крива на Безие" if i == 0 else f"Поляра ниво {i}"
            fig.add_trace(go.Scatter(
                x=curve_pts[:, 0], y=curve_pts[:, 1],
                mode='lines',
                name=name_label,
                line=dict(color=colors[i % len(colors)], width=4 if i==0 else 2.5)
            ))
            
            fig.add_trace(go.Scatter(
                x=ctrl_pts[:, 0], y=ctrl_pts[:, 1],
                mode='markers+lines',
                name=f"Полигон {i}",
                line=dict(color=colors[i % len(colors)], dash='dot', width=1),
                marker=dict(size=8, symbol='circle-open')
            ))

fig.update_layout(
    height=800, 
    template="plotly_white", 
    yaxis=dict(scaleanchor="x", scaleratio=1),
    xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='LightGray'),
    legend=dict(x=1.02, y=1, traceorder="normal")
)

st.plotly_chart(fig, use_container_width=True)