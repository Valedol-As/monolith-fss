import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import time

# --- Инициализация состояния (Ядро системы) ---
if 'entities' not in st.session_state:
    st.session_state.entities = []
    st.session_state.resources = [[random.uniform(0, 100), random.uniform(0, 100)] for _ in range(30)]
    st.session_state.global_faith = 100.0
    st.session_state.samsara_pool = 0.0

st.set_page_config(page_title="MONOLITH FSS", layout="wide")
st.title("🌌 MONOLITH: Functional Semantic System")

# --- Боковая панель (Управление Богом) ---
st.sidebar.header("Управление Миром")
if st.sidebar.button("✨ Создать Мага (Вера)"):
    st.session_state.entities.append({
        'x': random.uniform(0, 100), 'y': random.uniform(0, 100),
        'type': 'MAGE', 'P': 100 + st.session_state.samsara_pool,
        'V': random.uniform(1, 2), 'L': random.uniform(1, 2), 'S': 1.0
    })

if st.sidebar.button("⚙️ Создать Технолога (Истина)"):
    st.session_state.entities.append({
        'x': random.uniform(0, 100), 'y': random.uniform(0, 100),
        'type': 'TECH', 'P': 100 + st.session_state.samsara_pool,
        'N': random.uniform(1, 2), 'S': 1.0
    })

if st.sidebar.button("🔥 РАГНАРЁК (Сброс)"):
    st.session_state.entities = []
    st.session_state.global_faith = 100
    st.session_state.samsara_pool = 0
    st.rerun()

# --- Логика Симуляции ---
def update_world():
    # Потребление веры Богами
    st.session_state.global_faith -= 0.1
    
    for e in st.session_state.entities[:]:
        # Базовая трата потенциала P
        e['P'] -= 1.0
        
        # Сбор ресурсов
        reach = (e['V'] * e['L'] * 5) if e['type'] == 'MAGE' else 3
        for r in st.session_state.resources[:]:
            dist = ((e['x']-r[0])**2 + (e['y']-r[1])**2)**0.5
            if dist < reach:
                e['P'] += 10
                st.session_state.resources.remove(r)
                st.session_state.resources.append([random.uniform(0, 100), random.uniform(0, 100)])
                if e['type'] == 'MAGE': st.session_state.global_faith += 0.5

        # Движение
        e['x'] += random.uniform(-2, 2)
        e['y'] += random.uniform(-2, 2)
        
        # Смерть и Сансара
        if e['P'] <= 0:
            st.session_state.samsara_pool += e['S']
            st.session_state.entities.remove(e)

# --- Визуализация (Plotly) ---
def draw_map():
    fig = go.Figure()

    # Ресурсы (Потенциал)
    if st.session_state.resources:
        res_x, res_y = zip(*st.session_state.resources)
        fig.add_trace(go.Scatter(x=res_x, y=res_y, mode='markers', marker=dict(color='yellow', size=4), name='Потенциал'))

    # Сущности
    for e in st.session_state.entities:
        color = 'magenta' if e['type'] == 'MAGE' else 'cyan'
        symbol = 'circle' if e['type'] == 'MAGE' else 'square'
        size = max(5, e['P'] / 5)
        fig.add_trace(go.Scatter(
            x=[e['x']], y=[e['y']], 
            mode='markers', 
            marker=dict(color=color, size=size, symbol=symbol),
            name=e['type']
        ))

    fig.update_layout(width=800, height=600, showlegend=False, 
                      xaxis=dict(range=[0, 100]), yaxis=dict(range=[0, 100]),
                      template="plotly_dark")
    return fig

# --- Главный цикл ---
col1, col2 = st.columns([3, 1])

with col1:
    placeholder = st.empty()

with col2:
    st.metric("Мировая Вера", f"{st.session_state.global_faith:.1f}")
    st.metric("Пул Сансары", f"{st.session_state.samsara_pool:.1f}")
    st.metric("Живых", len(st.session_state.entities))

# Запуск цикла анимации
for _ in range(100): # 100 шагов симуляции за раз
    update_world()
    with placeholder.container():
        st.plotly_chart(draw_map(), use_container_width=True)
    time.sleep(0.1)

if st.button("Продолжить симуляцию"):
    st.rerun()
