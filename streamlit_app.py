import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random
import time

# --- ТВОИ КЛАССЫ (DivineEntity и другие) ---
# (Я вставил упрощенную версию твоих классов для работы в вебе)

class DivineEntity:
    def __init__(self, name, domain):
        self.name = name
        self.domain = domain
        self.faith_pool = 100.0
        self.divine_rank = 1
        self.power = 0.1
        self.miracles_performed = 0

    def update_stats(self):
        # Ранг на основе веры (как в твоем коде)
        if self.faith_pool >= 1000: self.divine_rank = 4
        elif self.faith_pool >= 500: self.divine_rank = 3
        elif self.faith_pool >= 100: self.divine_rank = 2
        else: self.divine_rank = 1
        self.power = min(1.0, np.log10(self.faith_pool + 1) / 5)

# --- ДВИЖОК СИМУЛЯЦИИ ---

if 'world_init' not in st.session_state:
    st.session_state.gods = [
        DivineEntity("Арес", "Война"),
        DivineEntity("Афина", "Мудрость"),
        DivineEntity("Афродита", "Любовь")
    ]
    st.session_state.entities = []
    st.session_state.history = []
    st.session_state.samsara_pool = 0.0
    st.session_state.world_init = True

st.set_page_config(page_title="MONOLITH: Divine Edition", layout="wide")

# --- ИНТЕРФЕЙС ---
st.title("🌌 ПАНТЕОН МОНОЛИТА")

col1, col2 = st.columns([3, 1])

with col2:
    st.header("Пантеон")
    for god in st.session_state.gods:
        god.update_stats()
        with st.expander(f"✨ {god.name} (Ранг {god.divine_rank})"):
            st.write(f"Сфера: {god.domain}")
            st.progress(god.power, text=f"Сила: {round(god.power*100)}%")
            st.metric("Пул Веры", round(god.faith_pool, 1))
            if st.button(f"Молитва {god.name}", key=god.name):
                god.faith_pool += 50
                st.toast(f"Ваша вера питает {god.name}!")

with col1:
    # Кнопки создания сущностей
    c1, c2, c3 = st.columns(3)
    if c1.button("🧙 Создать Мага"):
        st.session_state.entities.append({
            'x': random.uniform(0, 100), 'y': random.uniform(0, 100),
            'type': 'MAGE', 'P': 100, 'S': 1.0, 'god': random.choice(st.session_state.gods)
        })
    
    # Визуализация мира
    placeholder = st.empty()

# --- ЦИКЛ СИМУЛЯЦИИ ---
def run_simulation():
    # 1. Сбор веры сущностями
    for e in st.session_state.entities[:]:
        e['P'] -= 1.0 # Базовый расход
        
        # Если маг жив, он генерирует веру своему богу
        if e['type'] == 'MAGE':
            generated = 0.5 * e['S']
            e['god'].faith_pool += generated
        
        # Движение
        e['x'] += random.uniform(-2, 2)
        e['y'] += random.uniform(-2, 2)
        
        # Смерть (Уход в Сансару)
        if e['P'] <= 0:
            st.session_state.samsara_pool += e['S']
            st.session_state.entities.remove(e)

    # 2. Отрисовка
    fig = go.Figure()
    
    # Отрисовка сущностей
    if st.session_state.entities:
        df = pd.DataFrame(st.session_state.entities)
        fig.add_trace(go.Scatter(
            x=df['x'], y=df['y'],
            mode='markers',
            marker=dict(
                size=df['P']/5 + 5,
                color=['magenta' if t=='MAGE' else 'cyan' for t in df['type']],
                line=dict(width=2, color='white')
            ),
            text=[f"Служит {e['god'].name}" for e in st.session_state.entities]
        ))

    fig.update_layout(
        template="plotly_dark", height=600,
        xaxis=dict(range=[0, 100], showgrid=False),
        yaxis=dict(range=[0, 100], showgrid=False)
    )
    placeholder.plotly_chart(fig, use_container_width=True)

# Запуск анимации
for _ in range(20):
    run_simulation()
    time.sleep(0.1)

st.button("Следующий такт времени")
