import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit.components.v1 as components
import requests
from bs4 import BeautifulSoup

# --- Caricamento dati ---
def carica_dati():

    dati = pd.read_excel("https://github.com/Charon04/Progetto_Sardegna/raw/refs/heads/main/Incendi-completo-sardegna.xlsx")

    dati = dati.dropna(subset=["COMUNE DI INSORGENZA"])
    dati["COMUNE DI INSORGENZA"] = dati["COMUNE DI INSORGENZA"].str.strip().str.upper() 
    dati["DATA"] = pd.to_datetime(dati["DATA"])
    dati["Year"] = dati["DATA"].dt.year
    dati["Month"] = dati["DATA"].dt.month
    dati["Month"] = dati["Month"].astype('Int64')

    dati_completo = dati.copy()
 
    incendi_per_comune = dati["COMUNE DI INSORGENZA"].value_counts().reset_index()
    incendi_per_comune.columns = ["Comune", "Numero_Incendi"]
 
    incendi_per_comune["Rischio"] = pd.qcut(
        incendi_per_comune["Numero_Incendi"], 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)
 
    mappa_rischio = dict(zip(incendi_per_comune["Comune"], incendi_per_comune["Rischio"]))
    return dati_completo, incendi_per_comune, mappa_rischio
 
dati, df_comuni, mappa_rischio = carica_dati()
 
def tendeza():
    
    incendi_per_anno = dati["Year"].value_counts().sort_index()
    fig = px.line(
        x=incendi_per_anno.index,
        y=incendi_per_anno.values,
        markers=True,
        labels={'x': 'Anno', 'y': 'Numero di incendi'},
        title="Tendenza degli incendi annuale"
    )
    st.plotly_chart(fig)

def stagione():
    
    incendi_per_mese = dati.groupby('Month').size()
    mesi = ["Gen", "Feb", "Mar", "Apr", "Mag", "Giu", "Lug", "Ago", "Set", "Ott", "Nov", "Dic"]
    fig = px.bar(
        x=mesi,
        y=incendi_per_mese.values,
        labels={'x': 'Mese', 'y': 'Numero di incendi'},
        title="Distribuzione mensile degli incendi"
    )
    st.plotly_chart(fig)

def causa():
    
    causa_counts = dati["CAUSA PRESUNTA"].value_counts()
    fig = px.bar(
        x=causa_counts.index,
        y=causa_counts.values,
        labels={'x': 'Causa Presunta', 'y': 'Numero di Incendi'},
        title="Distribuzione delle cause presunte degli incendi"
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)


# --- Inizializza sessione per pagina ---
if "pagina" not in st.session_state:
    st.session_state.pagina = "Home"

# --- Stile CSS per navbar ---
st.markdown("""
    <style>
    .navbar {
        display: flex;
        justify-content: space-around;
        background-color: #333;
        padding: 10px;
        border-radius: 8px;
    }
    .navbar button {
        background: none;
        border: none;
        color: white;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
    }
    .navbar button:hover {
        color: #00cc99;
    }
    </style>
""", unsafe_allow_html=True)

# --- Navbar personalizzata ---
col1, col2, col3, col4= st.columns(4)
with col1:
    if st.button("Home"):
        st.session_state.pagina = "Home"
with col2:
    if st.button("Analisi"):
        st.session_state.pagina = "Analisi"
with col3:
    if st.button("🤖 Chatbot"):
        st.session_state.pagina = "Chatbot"
with col4:
    if st.button("Mappa"):
        st.session_state.pagina = "Mappa" 

# --- Contenuto in base alla pagina selezionata ---
url="https://github.com/Charon04/Progetto_Sardegna/raw/refs/heads/main/testo.txt" 
testo=requests.get(url).text

if st.session_state.pagina == "Home":
    st.title("Rischio Incendi")
    st.write(testo)

elif st.session_state.pagina == "Analisi":
    st.title("Analisi Dati Incendi")
    st.write("Tabella dei comuni con numero incendi e rischio:")
    st.dataframe(dati)
    tendeza()
    stagione()
    causa()

elif st.session_state.pagina == "Chatbot":
    st.title("🤖 Chatbot Antincendio")
    st.write("Chiedimi il rischio nel tuo comune o cosa fare in caso di incendio.")
    domanda = st.text_input("Scrivi la tua domanda qui:")

    def consigli_incendio(input_utente):
        input_utente = input_utente.lower()
        if "cosa fare" in input_utente or "incendio" in input_utente:
            return (
                "In caso di incendio:\n"
                "- Allontanati subito dalla zona\n"
                "- Chiama il **112**\n"
                "- Non cercare di spegnere l'incendio da solo\n"
                "- Segui sempre le istruzioni delle autorità"
            )

        for comune in mappa_rischio.keys():
            if comune.lower() in input_utente:
                rischio = mappa_rischio[comune]
                livelli = {1:"molto basso", 2:"basso", 3:"medio", 4:"alto", 5:"molto alto"}
                return f"A **{comune.title()}**, il rischio incendi è **{rischio} ({livelli[rischio]})**."

        if "rischio" in input_utente or "zona" in input_utente:
            return "Dimmi il nome del comune e ti dirò il livello di rischio."

        return "Non ho capito la domanda. Prova con:\n- *Cosa fare in caso di incendio*\n- *Qual è il rischio nel comune X*"

    if domanda:
        risposta = consigli_incendio(domanda)
        st.success(risposta)

elif st.session_state.pagina == "Mappa":
    st.title("Mappa")
    response = requests.get("https://github.com/Charon04/Progetto_Sardegna/raw/refs/heads/main/mappa_incendi_sardegna_cluster.html")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        mappa_html = str(soup)
        components.html(mappa_html, height=600, scrolling=True)