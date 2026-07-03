"""
Application Streamlit - iHeart Radio Analytics
Consomme l'API Flask (app.py) qui doit tourner sur http://127.0.0.1:5000
"""

import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="iHeart Radio Analytics", layout="wide")
st.title("📻 iHeart Radio Analytics")

# Vérification de la connexion à l'API
try:
    health = requests.get(f"{API_URL}/api/health", timeout=3).json()
    st.sidebar.success(f"API connectée — {health['database']}")
except Exception:
    st.sidebar.error("API non joignable. Lance `python app.py` d'abord.")
    st.stop()

menu = st.sidebar.radio(
    "Choisir une analyse",
    [
        "1. Stations par genre",
        "2. Top morceaux d'une station",
        "3. Genres dominants par état",
        "4. Top artistes par ville",
        "5. Artistes d'un morceau",
        "6. Stations les plus diffusées",
        "7. État avec le + de stations",
        "8. Marchés sans un genre",
        "9. Diversité de programmation",
        "10. Top artistes global",
        "11. Format le + diffusé",
        "12. Morceaux les + longs/courts",
    ],
)

# -----------------------------------------------------------
# 1. Stations par genre
# -----------------------------------------------------------
if menu.startswith("1."):
    st.header("Stations par genre")
    genre = st.text_input("Genre", "Country")
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/stations/by-genre", params={"genre": genre}).json()
        st.dataframe(pd.DataFrame(data))

# -----------------------------------------------------------
# 2. Top morceaux d'une station
# -----------------------------------------------------------
elif menu.startswith("2."):
    st.header("Morceaux les plus joués sur une station")
    station_name = st.text_input("Nom exact de la station", "Ke Buena 97.5 FM")
    limit = st.slider("Nombre de résultats", 1, 20, 10)
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/stations/{station_name}/top-tracks", params={"limit": limit}).json()
        if isinstance(data, dict) and "error" in data:
            st.warning(data["error"])
        else:
            st.dataframe(pd.DataFrame(data))
            if data:
                st.bar_chart(pd.DataFrame(data).set_index("title")["playCount"])

# -----------------------------------------------------------
# 3. Genres dominants par état
# -----------------------------------------------------------
elif menu.startswith("3."):
    st.header("Genres dominants dans un état")
    state = st.text_input("Code état (ex: CA, NY, TX)", "CA")
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/genres/by-state", params={"state": state}).json()
        df = pd.DataFrame(data)
        st.dataframe(df)
        if not df.empty:
            st.bar_chart(df.set_index("_id")["count"])

# -----------------------------------------------------------
# 4. Top artistes par ville
# -----------------------------------------------------------
elif menu.startswith("4."):
    st.header("Artistes les plus diffusés dans une ville")
    city = st.text_input("Ville", "Los Angeles")
    limit = st.slider("Nombre de résultats", 1, 20, 10)
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/artists/by-city", params={"city": city, "limit": limit}).json()
        st.dataframe(pd.DataFrame(data))

# -----------------------------------------------------------
# 5. Artistes d'un morceau
# -----------------------------------------------------------
elif menu.startswith("5."):
    st.header("Artistes associés à un morceau")
    title = st.text_input("Titre exact du morceau", "Last Night")
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/tracks/{title}/artists").json()
        if isinstance(data, dict) and "error" in data:
            st.warning(data["error"])
        else:
            st.json(data)

# -----------------------------------------------------------
# 6. Stations les plus diffusées
# -----------------------------------------------------------
elif menu.startswith("6."):
    st.header("Stations avec le plus grand nombre de plays")
    limit = st.slider("Nombre de résultats", 1, 20, 10)
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/stations/top-plays", params={"limit": limit}).json()
        df = pd.DataFrame(data)
        st.dataframe(df)
        if not df.empty:
            st.bar_chart(df.set_index("name")["totalPlays"])

# -----------------------------------------------------------
# 7. État avec le plus de stations
# -----------------------------------------------------------
elif menu.startswith("7."):
    st.header("État avec le plus de stations actives")
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/states/top-station-count").json()
        st.dataframe(pd.DataFrame(data))

# -----------------------------------------------------------
# 8. Marchés sans un genre
# -----------------------------------------------------------
elif menu.startswith("8."):
    st.header("Marchés sans aucune station d'un genre donné")
    genre = st.text_input("Genre recherché (absence)", "Classic Rock")
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/markets/without-genre", params={"genre": genre}).json()
        st.dataframe(pd.DataFrame(data))

# -----------------------------------------------------------
# 9. Diversité de programmation
# -----------------------------------------------------------
elif menu.startswith("9."):
    st.header("Diversité de programmation par station")
    order = st.radio("Tri", ["desc (plus variées)", "asc (plus répétitives)"])
    order_param = "desc" if order.startswith("desc") else "asc"
    limit = st.slider("Nombre de résultats", 1, 20, 10)
    if st.button("Chercher"):
        data = requests.get(
            f"{API_URL}/api/stations/diversity", params={"order": order_param, "limit": limit}
        ).json()
        st.dataframe(pd.DataFrame(data))

# -----------------------------------------------------------
# 10. Top artistes global
# -----------------------------------------------------------
elif menu.startswith("10."):
    st.header("Artistes avec la plus forte audience globale")
    limit = st.slider("Nombre de résultats", 1, 20, 10)
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/artists/top-played", params={"limit": limit}).json()
        df = pd.DataFrame(data)
        st.dataframe(df)
        if not df.empty:
            st.bar_chart(df.set_index("name")["totalPlays"])

# -----------------------------------------------------------
# 11. Format le plus diffusé
# -----------------------------------------------------------
elif menu.startswith("11."):
    st.header("Format de station générant le plus de diffusions")
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/formats/top-plays").json()
        df = pd.DataFrame(data)
        st.dataframe(df)
        if not df.empty:
            st.bar_chart(df.set_index("format")["totalPlays"])

# -----------------------------------------------------------
# 12. Morceaux les plus longs / courts
# -----------------------------------------------------------
elif menu.startswith("12."):
    st.header("Morceaux les plus longs / les plus courts")
    limit = st.slider("Nombre de résultats par catégorie", 1, 10, 5)
    if st.button("Chercher"):
        data = requests.get(f"{API_URL}/api/tracks/duration-extremes", params={"limit": limit}).json()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Les plus longs")
            st.dataframe(pd.DataFrame(data.get("longest", [])))
        with col2:
            st.subheader("Les plus courts")
            st.dataframe(pd.DataFrame(data.get("shortest", [])))
