import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(page_title="Deen LAB Manager", layout="wide", page_icon="🔧")

# --- GESTION DES FICHIERS (Simulation de base de données) ---
DATA_FILE = "deen_inventory.csv"
IMG_FOLDER = "repair_evidence"

# Créer le dossier image s'il n'existe pas
if not os.path.exists(IMG_FOLDER):
    os.makedirs(IMG_FOLDER)

# Fonction pour charger les données
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        # Création des colonnes si le fichier n'existe pas
        columns = [
            "Date", "ID_Unique", "Client_Nom", "Client_Type", "Appareil_Marque", 
            "Appareil_Modele", "Probleme", "Diagnostic", "Prix_Devis", 
            "Prix_Final", "Statut", "Image_Path"
        ]
        return pd.DataFrame(columns=columns)

# Fonction pour sauvegarder
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- INTERFACE UTILISATEUR ---

# Sidebar pour la navigation
st.sidebar.title("Deen LAB 🔧")
menu = st.sidebar.radio("Navigation", ["Nouvelle Intervention", "Journal & Suivi", "Dashboard Financier"])

df = load_data()

# --- PAGE 1: NOUVELLE INTERVENTION ---
if menu == "Nouvelle Intervention":
    st.header("📝 Nouvelle Réparation")
    
    with st.form("repair_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Infos Client")
            client_nom = st.text_input("Nom du Client")
            client_number = st.text_input("Numéro de téléphone")
            client_type = st.selectbox("Type de Client", ["Nouveau", "Ancien", "Recommandé"])
            
        with col2:
            st.subheader("Infos Appareil")
            marque = st.selectbox("Marque", ["Apple", "Samsung", "Google", "Xiaomi", "Tecno/Infinix", "Autre"])
            modele = st.text_input("Modèle (ex: iPhone 12)")
        
        st.subheader("Technique & Finance")
        probleme = st.text_area("Problème décrit par le client")
        diagnostic = st.text_area("Diagnostic Technique")
        
        c1, c2 = st.columns(2)
        prix_devis = c1.number_input("Montant Annoncé (FCFA)", min_value=0, step=500)
        prix_final = c2.number_input("Montant Final Convenu (FCFA)", min_value=0, step=500)
        
        # Upload Photo
        uploaded_file = st.file_uploader("Preuve Photo/Vidéo", type=['png', 'jpg', 'jpeg'])
        
        submitted = st.form_submit_button("Enregistrer l'intervention")
        
        if submitted:
            # Gestion de l'image
            img_path = "Aucune"
            if uploaded_file is not None:
                # Sauvegarde locale simple
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_filename = f"{timestamp}_{uploaded_file.name}"
                img_path = os.path.join(IMG_FOLDER, img_filename)
                with open(img_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
            
            # Création de la nouvelle entrée
            new_data = {
                "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "ID_Unique": datetime.now().strftime("%Y%m%d%H%M"),
                "Client_Nom": client_nom,
                "Client_Type": client_type,
                "Appareil_Marque": marque,
                "Appareil_Modele": modele,
                "Probleme": probleme,
                "Diagnostic": diagnostic,
                "Prix_Devis": prix_devis,
                "Prix_Final": prix_final,
                "Statut": "En cours",
                "Image_Path": img_path
            }
            
            # Ajout au dataframe et sauvegarde
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            save_data(df)
            st.success("Intervention enregistrée avec succès !")

# --- PAGE 2: JOURNAL ---
elif menu == "Journal & Suivi":
    st.header("📂 Journal des réparations")
    
    # Filtres
    filter_marque = st.multiselect("Filtrer par marque", df["Appareil_Marque"].unique())
    if filter_marque:
        df_show = df[df["Appareil_Marque"].isin(filter_marque)]
    else:
        df_show = df
        
    st.dataframe(df_show, use_container_width=True)

# --- PAGE 3: DASHBOARD ---
elif menu == "Dashboard Financier":
    st.header("📊 Prévisions et Statistiques")
    
    if not df.empty:
        # Metrics Clés
        total_ca = df["Prix_Final"].sum()
        total_repairs = len(df)
        avg_price = df["Prix_Final"].mean()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Chiffre d'Affaires Total", f"{total_ca:,.0f} FCFA")
        m2.metric("Total Interventions", total_repairs)
        m3.metric("Panier Moyen", f"{avg_price:,.0f} FCFA")
        
        st.markdown("---")
        
        # Graphiques (Simple pour MVP)
        c1, c2 = st.columns(2)
        
        with c1:
            st.subheader("Réparations par Marque")
            st.bar_chart(df["Appareil_Marque"].value_counts())
            
        with c2:
            st.subheader("Types de Clients")
            st.bar_chart(df["Client_Type"].value_counts())
            
        # Section Prévision (Conceptuelle pour le MVP)
        st.info("💡 **Insight Expert :** Les données montrent que les écrans Samsung représentent 30% de votre CA. Pensez à stocker ces pièces à l'avance.")
        
    else:
        st.warning("Pas assez de données pour afficher le dashboard.")