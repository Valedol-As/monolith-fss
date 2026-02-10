import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
import time

# --- НАСТРОЙКИ СИСТЕМЫ ---
st.set_page_config(layout="wide", page_title="FSS: Emergence Engine")

if 'world' not in st.session_state:
    st.session_state.entities = []
    st.session_state.clusters = []
    st.session_state.samsara = 0.0

class Entity:
    def __init__(self, id, x, y):
        self.id = id
        self.pos = np.array([float(x), float(y)])
        self.P = 100.0
        self.S = 1.0
        self.cluster_id = None
        self.connections = []

    def move(self):
        # Если нет кластера - хаотичное движение
        # Если есть кластер - движение к центру масс кластера (Регуляция)
        target = np.array([random.uniform(-2, 2), random.uniform(-2, 2)])
        self.pos += target
        self.pos = np.clip(self.pos, 0, 100)
        self.P -= 0.5 # Трата на движение

class Cluster:
    """ Эмерджентная форма: Кластер / Культ / Город """
    def __init__(self, id, members):
        self.id = id
        self.members = members # Список объектов Entity
        self.shared_P = sum(e.P for e in members)
        self.S = len(members) * 1.5 # Повышенная структурная сложность
        self.center = np.mean([e.pos for e in members], axis=0)
        
    def pulse(self):
        """ Общая регуляция: распределение ресурсов """
        avg_p = self.shared_P / len(self.members)
        for e in self.members:
            e.P = avg_p # Уравнивание (Социализм/Регуляция)
            # Притяжение к центру
            vec_to_center = (self.center - e.pos) * 0.1
            e.pos += vec_to_center
        self.shared_P -= self.S * 0.1 # Общие затраты системы

# --- ИНТЕРФЕЙС ---
st.title("🔗 Эмерджентность: От Хаоса к Регуляции")
st.sidebar.header("Параметры Синтеза")
connection_dist = st.sidebar.slider("Дистанция связи (Линия)", 1.0, 20.0, 10.0)
cluster_threshold = st.sidebar.slider("Порог кластеризации (Плоскость)", 2, 10, 3)

if st.sidebar.button("Заселить Мир"):
    st.session_state.entities = [Entity(i, random.random()*100, random.random()*100) for i in range(20)]
    st.session_state.clusters = []

# --- ГЛАВНЫЙ ЦИКЛ ---
def update_step():
    entities = st.session_state.entities
    
    # 1. Движение и обновление
    for e in entities:
        e.move()
    
    # 2. Поиск связей (Уровень 2)
    for i, e1 in enumerate(entities):
        e1.connections = []
        for j, e2 in enumerate(entities):
            if i != j:
                dist = np.linalg.norm(e1.pos - e2.pos)
                if dist < connection_dist:
                    e1.connections.append(e2.id)

    # 3. Формирование кластеров (Эмерджентность)
    # Используем простую логику: если у точки > N связей, она образует кластер
    new_clusters = []
    processed_ids = set()
    
    for e in entities:
        if e.id not in processed_ids and len(e.connections) >= cluster_threshold:
            # Находим всех участников группы
            group_ids = set([e.id] + e.connections)
            group_members = [ent for ent in entities if ent.id in group_ids]
            new_clusters.append(Cluster(len(new_clusters), group_members))
            processed_ids.update(group_ids)
            for m in group_members: m.cluster_id = len(new_clusters)
            
    st.session_state.clusters = new_clusters
    
    # 4. Пульс кластеров
    for c in st.session_state.clusters:
        c.pulse()

    # 5. Смерть
    st.session_state.entities = [e for e in entities if e.P > 0]

# --- ВИЗУАЛИЗАЦИЯ ---
placeholder = st.empty()

for _ in range(30):
    update_step()
    
    fig = go.Figure()

    # Рисуем связи (Линии)
    for e1 in st.session_state.entities:
        for e2_id in e1.connections:
            e2 = next((ent for ent in st.session_state.entities if ent.id == e2_id), None)
            if e2:
                fig.add_trace(go.Scatter(
                    x=[e1.pos[0], e2.pos[0]], y=[e1.pos[1], e2.pos[1]],
                    mode='lines', line=dict(color='rgba(100,255,100,0.2)', width=1),
                    showlegend=False
                ))

    # Рисуем сущности
    if st.session_state.entities:
        df = pd.DataFrame([{
            'x': e.pos[0], 'y': e.pos[1], 
            'P': e.P, 'in_cluster': e.cluster_id is not None
        } for e in st.session_state.entities])
        
        fig.add_trace(go.Scatter(
            x=df['x'], y=df['y'], mode='markers',
            marker=dict(
                size=df['P']/5, 
                color=df['in_cluster'].map({True: 'magenta', False: 'white'}),
                line=dict(width=1, color='white')
            ),
            showlegend=False
        ))

    # Рисуем границы кластеров (Эмерджентные формы)
    for c in st.session_state.clusters:
        fig.add_trace(go.Scatter(
            x=[c.center[0]], y=[c.center[1]],
            mode='markers', marker=dict(size=60, color='rgba(255,0,255,0.1)', symbol='hexagon'),
            name=f"Кластер {c.id}"
        ))

    fig.update_layout(template="plotly_dark", height=700, xaxis=dict(range=[0,100]), yaxis=dict(range=[0,100]))
    placeholder.plotly_chart(fig, use_container_width=True)
    time.sleep(0.05)

st.write(f"Активных кластеров: {len(st.session_state.clusters)}")
st.info("Когда белые точки сближаются, возникают зеленые связи. Если связей много, возникает розовый Кластер — он начинает притягивать точки к себе, регулируя их хаос.")
