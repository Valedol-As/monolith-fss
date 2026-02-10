import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
import time

# --- НАСТРОЙКИ СИСТЕМЫ ---
st.set_page_config(layout="wide", page_title="FSS: Emergence Engine")

# Исправленный блок CSS для темной темы
st.markdown("""
    <style>
    .stApp { background-color: #05050a; }
    </style>
    """, unsafe_allow_html=True)

if 'entities' not in st.session_state:
    st.session_state.entities = []
    st.session_state.clusters = []

class Entity:
    def __init__(self, id, x, y):
        self.id = id
        self.pos = np.array([float(x), float(y)])
        self.P = 100.0
        self.cluster_id = None
        self.connections = []

    def move(self):
        # Движение: хаос или тяга к системе
        step = np.array([random.uniform(-1.5, 1.5), random.uniform(-1.5, 1.5)])
        self.pos += step
        self.pos = np.clip(self.pos, 0, 100)
        self.P -= 0.3

class Cluster:
    def __init__(self, id, members):
        self.id = id
        self.members = members
        self.center = np.mean([e.pos for e in members], axis=0)
        
    def regulate(self):
        self.center = np.mean([e.pos for e in self.members], axis=0)
        for e in self.members:
            # Регуляция: тянем точку к центру системы
            e.pos += (self.center - e.pos) * 0.15
            e.P += 0.2 # Система поддерживает жизнь своих членов

# --- ИНТЕРФЕЙС ---
st.title("🔗 МОНОЛИТ: СИНТЕЗ СЛОЖНОСТИ")
st.sidebar.markdown("### Настройка Реальности")
conn_dist = st.sidebar.slider("Радиус связи (S)", 5.0, 25.0, 12.0)
pop_size = st.sidebar.slider("Популяция", 10, 100, 40)

if st.sidebar.button("ПЕРЕЗАПУСК"):
    st.session_state.entities = [Entity(i, random.random()*100, random.random()*100) for i in range(pop_size)]
    st.session_state.clusters = []
    st.rerun()

# --- ЛОГИКА ---
def update_world():
    ents = st.session_state.entities
    if not ents: return

    for e in ents: e.move()

    # Построение связей (Уровень 2)
    new_clusters = []
    
    for i, e1 in enumerate(ents):
        e1.connections = []
        e1.cluster_id = None
        for j, e2 in enumerate(ents):
            if i != j:
                if np.linalg.norm(e1.pos - e2.pos) < conn_dist:
                    e1.connections.append(e2)

    # Формирование эмерджентных групп (Уровень 3)
    visited = set()
    for e in ents:
        if e.id not in visited and len(e.connections) >= 3:
            group = [e] + e.connections
            for m in group: visited.add(m.id)
            c = Cluster(len(new_clusters), group)
            new_clusters.append(c)
            for m in group: m.cluster_id = c.id
            
    st.session_state.clusters = new_clusters
    for c in st.session_state.clusters: c.regulate()
    st.session_state.entities = [e for e in ents if e.P > 0]

# --- ОТРИСОВКА (Plotly) ---
placeholder = st.empty()

# Начальный запуск, если сущностей еще нет
if not st.session_state.entities:
    st.session_state.entities = [Entity(i, random.random()*100, random.random()*100) for i in range(pop_size)]

# Цикл анимации (30 шагов)
for _ in range(30):
    update_world()
    
    fig = go.Figure()

    # 1. Линии Истины (Связи) - Синий неон
    for e in st.session_state.entities:
        for target in e.connections:
            fig.add_trace(go.Scatter(
                x=[e.pos[0], target.pos[0]], y=[e.pos[1], target.pos[1]],
                mode='lines',
                line=dict(color='rgba(0, 255, 255, 0.4)', width=1),
                hoverinfo='none', showlegend=False
            ))

    # 2. Сущности - Желтые (Хаос) / Розовые (Система)
    if st.session_state.entities:
        x_coords = [e.pos[0] for e in st.session_state.entities]
        y_coords = [e.pos[1] for e in st.session_state.entities]
        # Используем HEX-коды цветов для точности
        colors = ['#FF00FF' if e.cluster_id is not None else '#FFFF00' for e in st.session_state.entities]
        sizes = [max(2, e.P/4) for e in st.session_state.entities]
        
        fig.add_trace(go.Scatter(
            x=x_coords, y=y_coords,
            mode='markers',
            marker=dict(
                size=sizes, 
                color=colors, 
                line=dict(width=1, color='white')
            ),
            showlegend=False
        ))

    # 3. Ауры Кластеров - Пурпурный туман
    for c in st.session_state.clusters:
        fig.add_trace(go.Scatter(
            x=[c.center[0]], y=[c.center[1]],
            mode='markers',
            marker=dict(size=80, color='rgba(255, 0, 255, 0.15)', symbol='hexagon'),
            showlegend=False
        ))

    fig.update_layout(
        paper_bgcolor='#05050a',
        plot_bgcolor='#05050a',
        margin=dict(l=0, r=0, t=0, b=0),
        height=700,
        xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
        yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, visible=False),
        showlegend=False
    )
    
    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.05)

st.sidebar.write(f"Живых сущностей: {len(st.session_state.entities)}")
st.sidebar.write(f"Кластеров: {len(st.session_state.clusters)}")
