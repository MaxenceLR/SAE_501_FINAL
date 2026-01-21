import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date

# --- IMPORT DU MOTEUR SQL ---
# C'est ici qu'on récupère la connexion et les fonctions du fichier backend.py
from backend import * # --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Maison du Droit - Système Intégré", 
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CHARTE GRAPHIQUE & STYLE CSS ---
COLOR_NAVY = "#122B48"  # Bleu foncé
COLOR_GOLD = "#B09B5B"  # Doré
COLOR_BG_SIDEBAR = "#F0F2F6" # Gris très clair
COLOR_TEXT_GREY = "#666666"

st.markdown(f"""
    <style>
    /* Titres en Bleu Marine */
    h1, h2, h3, h4 {{ color: {COLOR_NAVY} !important; }}
    
    /* Navigation Sidebar (Radio buttons) */
    .stRadio > label {{ font-weight: bold; color: {COLOR_NAVY}; }}
    
    /* Boutons en style Doré */
    div.stButton > button {{
        background-color: {COLOR_NAVY};
        color: white;
        border-radius: 8px;
        border: 2px solid {COLOR_GOLD};
    }}
    div.stButton > button:hover {{
        background-color: {COLOR_GOLD};
        color: white;
        border-color: {COLOR_NAVY};
    }}
    
    /* Style de la sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_BG_SIDEBAR};
        border-right: 2px solid {COLOR_GOLD};
    }}

    /* --- NOUVEAU STYLE KPI (CARTES) --- */
    .kpi-card {{
        background-color: white;
        border: 2px solid {COLOR_GOLD};
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 10px;
    }}
    .kpi-title {{
        color: {COLOR_TEXT_GREY};
        font-size: 1.1rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 5px;
    }}
    .kpi-value {{
        color: {COLOR_NAVY};
        font-size: 3.5rem; /* TRES GROS */
        font-weight: 800;  /* TRES GRAS */
        line-height: 1.1;
        margin: 0;
    }}
    .kpi-sub {{
        color: {COLOR_GOLD};
        font-size: 0.9rem;
        font-weight: bold;
        margin-top: 5px;
    }}
    </style>
    """, unsafe_allow_html=True)

# =================================================================
#  MAIN APPLICATION LOGIC
# =================================================================

def main():  # pragma: no cover
    
    # Vérification critique de la connexion AVANT de lancer l'interface
    # La variable 'connection' vient de l'import backend
    if connection is None:
        st.error("❌ ERREUR CRITIQUE : Impossible de se connecter à la base de données PostgreSQL.")
        st.warning("Vérifiez que le serveur PostgreSQL est lancé et que les paramètres (HOST, PORT, USER) sont corrects.")
        st.stop() # Arrête tout ici si pas de DB

    # =================================================================
    #  SIDEBAR (NAVIGATION)
    # =================================================================
    with st.sidebar:
        try:
            st.image("logo.png", use_container_width=True)
        except:
            st.header("⚖️ Maison du Droit")
        
        st.markdown("---")
        
        # NAVIGATION MODIFIÉE : Radio Button au lieu des onglets
        menu_selection = st.radio(
            "NAVIGATION",
            ["ALIMENTATION", "VISUALISATION", "CONFIGURATION"],
            index=0
        )
        
        st.markdown("---")
        
        st.markdown(f"<div style='text-align: center; color: grey; font-size: 0.8em;'>Developed by</div>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center; color: {COLOR_NAVY}; margin:0;'> DYLAN | MAXENCE | JORDAN </h4>", unsafe_allow_html=True)
        st.markdown(f"<div style='text-align: center; margin-top: 10px;'>© {date.today().year} Maison du Droit</div>", unsafe_allow_html=True)

    # =================================================================
    #  ROUTAGE DES PAGES
    # =================================================================

    # --- PAGE 1 : ALIMENTATION ---
    if menu_selection == "ALIMENTATION":
        st.title(" Saisie d'un nouvel entretien")
        
        structure = get_questionnaire_structure()
        demande_opt, sol_opt = get_demande_solution_modalites()
        
        if structure:
            data_entretien = {}
            with st.form(key='main_form'):
                for rubrique, variables in structure.items():
                    st.markdown(f"<div style='background-color: #E8EBF0; padding: 10px; border-radius: 5px; margin-bottom: 10px;'><h4 style='color: {COLOR_NAVY}; margin:0;'>{rubrique}</h4></div>", unsafe_allow_html=True)
                    cols = st.columns(2)
                    for i, var in enumerate(variables):
                        lib, comment, type_v = var['lib'], var['comment'], var['type']
                        with cols[i % 2]:
                            label = f"**{lib}**"
                            if type_v == 'MOD':
                                opts = list(var['options'].keys())
                                sel = st.selectbox(label, opts, index=None, placeholder=comment, key=f"f_{lib}")
                                data_entretien[lib.lower()] = var['options'].get(sel) if sel else None
                            elif type_v == 'NUM':
                                val = st.number_input(label, min_value=var['options'].get('min',0), max_value=var['options'].get('max',99), key=f"f_{lib}")
                                data_entretien[lib.lower()] = val
                            elif type_v == 'CHAINE':
                                val = st.text_input(label, key=f"f_{lib}", help=comment)
                                data_entretien[lib.lower()] = val
                
                st.markdown("---")
                col_d, col_s = st.columns(2)
                with col_d:
                    st.subheader("Nature de la demande")
                    sel_dem = st.multiselect("Sélection (max 3)", list(demande_opt.keys()), max_selections=3)
                with col_s:
                    st.subheader("Réponse apportée")
                    sel_sol = st.multiselect("Sélection (max 3)", list(sol_opt.keys()), max_selections=3)

                st.write("")
                submit_col = st.columns([1,2,1])
                with submit_col[1]:
                    submitted = st.form_submit_button("💾 ENREGISTRER L'ENTRETIEN", use_container_width=True)

                if submitted:
                    if not sel_dem:
                        st.error("Sélectionnez au moins une demande.")
                    else:
                        new_id = insert_full_entretien(data_entretien)
                        if new_id:
                            insert_demandes(new_id, [demande_opt[l] for l in sel_dem])
                            insert_solutions(new_id, [sol_opt[l] for l in sel_sol])
                            st.success(f"Entretien N°{new_id} enregistré !")
                            st.balloons()
        else:
            st.error("Impossible de charger les rubriques.")
    # =================================================================
    # PAGE 2 : VISUALISATION (REFONDUE : GLOBAL vs CRÉATEUR)
    # =================================================================
    elif menu_selection == "VISUALISATION":
        st.title("Tableau de Bord Décisionnel")
        
        # Récupération des données
        df = get_data_for_reporting()
        
        if not df.empty:
            # Palette stricte Charte Graphique
            charter_colors = [COLOR_NAVY, COLOR_GOLD, '#5D738B', '#D4C5A3', '#829ab1']

            # CRÉATION DES SOUS-ONGLETS
            subtab_global, subtab_creator = st.tabs(["VUE GLOBALE", "CRÉATEUR DE GRAPHIQUES"])

            # ---------------------------------------------------------
            # SOUS-ONGLET 1 : TABLEAU DE BORD STANDARD
            # ---------------------------------------------------------
            with subtab_global:
                st.markdown("### Indicateurs de Performance")
                
                # --- KPIS (HTML CUSTOM) ---
                k1, k2, k3, k4 = st.columns(4)
                
                # Calculs
                total = len(df)
                top_commune = df["commune"].mode()[0] if not df["commune"].empty else "N/A"
                top_mode = df["mode"].mode()[0] if not df["mode"].empty else "N/A"
                
                # CORRECTION ICI : On prend le MODE (le plus fréquent) au lieu de la moyenne
                top_age = df["age"].mode()[0] if "age" in df.columns and not df["age"].empty else "N/A"
                
                # Rendu HTML
                with k1:
                    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Total Dossiers</div><div class="kpi-value">{total}</div><div class="kpi-sub">Entretiens réalisés</div></div>""", unsafe_allow_html=True)
                with k2:
                    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Top Commune</div><div class="kpi-value" style="font-size:2.2rem;">{top_commune}</div><div class="kpi-sub">Provenance majeure</div></div>""", unsafe_allow_html=True)
                with k3:
                    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Mode Dominant</div><div class="kpi-value" style="font-size:2.2rem;">{top_mode}</div><div class="kpi-sub">Type de contact</div></div>""", unsafe_allow_html=True)
                with k4:
                    # On adapte la taille de la police (font-size) car "26-40 ans" prend plus de place qu'un chiffre
                    st.markdown(f"""<div class="kpi-card"><div class="kpi-title">Âge Dominant</div><div class="kpi-value" style="font-size:2.2rem;">{top_age}</div><div class="kpi-sub">Tranche majoritaire</div></div>""", unsafe_allow_html=True)

                st.markdown("---")

                # --- GRAPHIQUES STANDARDS ---
                col_main1, col_main2 = st.columns([1, 1], gap="small")
                
                with col_main1:
                    fig_sex = px.pie(df, names="sexe", title="Répartition par Sexe", 
                                    hole=0.5, color_discrete_sequence=[COLOR_NAVY, COLOR_GOLD])
                    fig_sex.update_layout(height=320, margin=dict(t=40, b=0, l=0, r=0))
                    fig_sex.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_sex, use_container_width=True)
                    
                with col_main2:
                    # Correction : On vérifie juste que la colonne existe, sans forcer le type numérique
                    # car "26-40 ans" est du texte (String), ce qui est normal.
                    if "age" in df.columns:
                        fig_age = px.histogram(df, x="age", title="Distribution des Âges",
                                            color_discrete_sequence=[COLOR_GOLD])
                        
                        # Astuce : On force le tri par ordre de catégorie pour que "18-25" soit avant "26-40"
                        fig_age.update_xaxes(categoryorder='category ascending')
                        
                        fig_age.update_layout(height=320, margin=dict(t=40, b=0, l=0, r=0), bargap=0.1)
                        st.plotly_chart(fig_age, use_container_width=True)
                    else:
                        st.warning("Données d'âge non disponibles.")
                # Volume par commune (Bar chart)
                if "commune" in df.columns:
                    commune_counts = df["commune"].value_counts().reset_index()
                    commune_counts.columns = ['Commune', 'Nombre']
                    fig_commune = px.bar(commune_counts, x="Nombre", y="Commune", orientation='h',
                                        title="Fréquentation par Commune", text_auto=True,
                                        color="Nombre", color_continuous_scale=[COLOR_GOLD, COLOR_NAVY])
                    fig_commune.update_layout(height=400, margin=dict(t=40, b=0, l=0, r=0))
                    st.plotly_chart(fig_commune, use_container_width=True)

            # ---------------------------------------------------------
            # SOUS-ONGLET 2 : CRÉATEUR DE GRAPHIQUES (SELF-SERVICE)
            # ---------------------------------------------------------
            with subtab_creator:
                st.markdown("### Espace d'Analyse Personnalisée")
                st.info("Utilisez cet outil pour croiser les données et créer vos propres visualisations.")

                # Zone de configuration (Style carte grise)
                with st.container():
                    c1, c2, c3, c4 = st.columns(4)
                    
                    # 1. Axe X (Catégorie)
                    categ_cols = [c for c in df.columns if df[c].dtype == 'object']
                    var_x = c1.selectbox("1. Axe Horizontal (X)", options=df.columns, index=2)
                    
                    # 2. Axe Y (Valeur ou Compte)
                    # On ajoute une option "Compte (Lignes)" virtuelle
                    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
                    y_options = ["(Compte des dossiers)"] + numeric_cols
                    var_y = c2.selectbox("2. Axe Vertical (Y)", options=y_options)
                    
                    # 3. Segmentation (Couleur)
                    color_options = [None] + list(df.columns)
                    var_color = c3.selectbox("3. Grouper par (Couleur)", options=color_options, index=0)
                    
                    # 4. Type de Graphique
                    chart_types = ["Barres", "Lignes", "Aires", "Camembert", "Boîte à moustache", "Nuage de points"]
                    chart_type = c4.selectbox("4. Type de Graphique", options=chart_types)

                st.divider()

                # --- GÉNÉRATION DYNAMIQUE ---
                try:
                    title_text = f"Analyse : {var_x}"
                    if var_y != "(Compte des dossiers)": title_text += f" vs {var_y}"
                    if var_color: title_text += f" (par {var_color})"

                    fig_custom = None

                    # Logique de construction Plotly
                    if chart_type == "Barres":
                        if var_y == "(Compte des dossiers)":
                            # Histogramme simple (compte les occurrences de X)
                            fig_custom = px.histogram(df, x=var_x, color=var_color, 
                                                    barmode="group", title=title_text, 
                                                    color_discrete_sequence=charter_colors, text_auto=True)
                        else:
                            # Barres avec agrégation (Moyenne ou Somme selon besoins, ici par défaut histogramme somme)
                            fig_custom = px.histogram(df, x=var_x, y=var_y, color=var_color, 
                                                    barmode="group", title=title_text, histfunc='avg',
                                                    color_discrete_sequence=charter_colors, text_auto=True)
                            fig_custom.update_layout(yaxis_title=f"Moyenne de {var_y}")

                    elif chart_type == "Lignes":
                        # Pour les lignes, on a souvent besoin d'agréger avant
                        if var_y == "(Compte des dossiers)":
                            df_agg = df.groupby([var_x] + ([var_color] if var_color else [])).size().reset_index(name='Compte')
                            y_val = 'Compte'
                        else:
                            df_agg = df.groupby([var_x] + ([var_color] if var_color else []))[var_y].mean().reset_index()
                            y_val = var_y
                        
                        fig_custom = px.line(df_agg, x=var_x, y=y_val, color=var_color, markers=True,
                                            title=title_text, color_discrete_sequence=charter_colors)

                    elif chart_type == "Aires":
                        if var_y == "(Compte des dossiers)":
                            df_agg = df.groupby([var_x] + ([var_color] if var_color else [])).size().reset_index(name='Compte')
                            y_val = 'Compte'
                        else:
                            df_agg = df.groupby([var_x] + ([var_color] if var_color else []))[var_y].sum().reset_index()
                            y_val = var_y
                        
                        fig_custom = px.area(df_agg, x=var_x, y=y_val, color=var_color,
                                            title=title_text, color_discrete_sequence=charter_colors)

                    elif chart_type == "Camembert":
                        if var_color: st.warning("⚠️ Le groupement couleur est ignoré pour le Camembert (utilise l'axe X).")
                        fig_custom = px.pie(df, names=var_x, title=title_text, 
                                            color_discrete_sequence=charter_colors, hole=0.4)

                    elif chart_type == "Boîte à moustache":
                        if var_y == "(Compte des dossiers)":
                            st.error("❌ Impossible de faire une boîte à moustache sans variable numérique en Y (ex: Âge, Durée).")
                        else:
                            fig_custom = px.box(df, x=var_x, y=var_y, color=var_color, 
                                                title=title_text, color_discrete_sequence=charter_colors)

                    elif chart_type == "Nuage de points":
                        if var_y == "(Compte des dossiers)":
                            st.error("❌ Sélectionnez une variable numérique en Y pour le nuage de points.")
                        else:
                            fig_custom = px.scatter(df, x=var_x, y=var_y, color=var_color, 
                                                    title=title_text, color_discrete_sequence=charter_colors)

                    # Affichage final
                    if fig_custom:
                        fig_custom.update_layout(height=500, plot_bgcolor="white")
                        st.plotly_chart(fig_custom, use_container_width=True)
                        
                        # Option d'export des données du graphique
                        with st.expander("Voir les données de ce graphique"):
                            st.dataframe(df[[var_x] + ([var_y] if var_y != "(Compte des dossiers)" else []) + ([var_color] if var_color else [])].head(50))

                except Exception as e:
                    st.error(f"Impossible de générer ce graphique : {e}")

        else:
            st.info("Aucune donnée disponible pour le moment.")
    # =================================================================
    # PAGE 3 : CONFIGURATION (SÉQUENTIELLE & INTELLIGENTE)
    # =================================================================
    elif menu_selection == "CONFIGURATION":
        st.title("Gestion de la Structure")
        st.info("Suivez les étapes ci-dessous pour modifier le formulaire.")

        # --- PRÉPARATION DES DONNÉES ---
        cursor = connection.cursor()
        cursor.execute("SELECT pos, lib FROM rubrique ORDER BY pos")
        all_rubriques = cursor.fetchall() # [(1, 'Civil'), ...]
        cursor.close()
        
        dict_rubriques = {f"{r[1]}": r[0] for r in all_rubriques}
        
        # =========================================================
        # ÉTAPE 1 : LA RUBRIQUE
        # =========================================================
        st.markdown("### Choix de la Rubrique")
        
        col_r1, col_r2 = st.columns([1, 2])
        
        with col_r1:
            options_rub = ["➕ Créer nouvelle..."] + list(dict_rubriques.keys())
            choix_rubrique = st.selectbox("Sélectionner :", options_rub)

        # Variables de contexte pour l'étape 2
        selected_rub_id = None
        selected_rub_lib = ""
        is_special_context = False # Pour DEMANDE ou SOLUTION
        target_tab = 'ENTRETIEN'   # Par défaut
        
        with col_r2:
            if choix_rubrique == "➕ Créer nouvelle...":
                with st.form("new_rub_form"):
                    new_rub_lib = st.text_input("Nom de la nouvelle rubrique")
                    # Calc pos max
                    r_pos_def = (max(dict_rubriques.values()) + 1) if dict_rubriques else 1
                    new_rub_pos = st.number_input("Position", value=r_pos_def, step=1)
                    if st.form_submit_button("Créer"):
                        if upsert_rubrique(r_pos_def, new_rub_pos, new_rub_lib): # Fonction définie précédemment
                            st.success("Rubrique créée !")
                            st.rerun()
            else:
                # Mode édition rubrique existante
                selected_rub_id = dict_rubriques[choix_rubrique]
                selected_rub_lib = choix_rubrique
                
                # --- DÉTECTION INTELLIGENTE DU CONTEXTE ---
                # Si le nom contient "Demande" ou "Solution", on change le comportement
                rub_lower = selected_rub_lib.lower()
                if "demande" in rub_lower:
                    is_special_context = True
                    target_tab = 'DEMANDE'
                    st.info(f"💡 Mode détecté : Configuration des **Natures de Demande**.")
                elif "solution" in rub_lower or "réponse" in rub_lower:
                    is_special_context = True
                    target_tab = 'SOLUTION'
                    st.info(f"💡 Mode détecté : Configuration des **Types de Réponses/Solutions**.")
                
                # Formulaire léger pour renommer la rubrique si besoin
                with st.expander(f"Modifier le nom de '{selected_rub_lib}'"):
                    with st.form("edit_rub"):
                        edit_lib = st.text_input("Renommer", value=selected_rub_lib)
                        edit_pos = st.number_input("Position", value=selected_rub_id)
                        if st.form_submit_button("Mettre à jour Rubrique"):
                            upsert_rubrique(selected_rub_id, edit_pos, edit_lib)
                            st.rerun()

        st.markdown("---")

        # =========================================================
        # ÉTAPE 2 : LA VARIABLE (Si Rubrique sélectionnée)
        # =========================================================
        if selected_rub_id:
            st.markdown(f"### Configuration des Questions pour : *{selected_rub_lib}*")

            # A. CAS SPÉCIAL : DEMANDE / SOLUTION
            if is_special_context:
                # On force une variable unique "Nature"
                # Dans votre code précédent, ces données étaient stockées avec pos=3
                FIXED_POS = 3 
                
                # Chargement des modalités existantes
                cursor = connection.cursor()
                cursor.execute("SELECT lib_m FROM modalite WHERE tab=%s AND pos=%s ORDER BY pos_m", (target_tab, FIXED_POS))
                existing_mods = [m[0] for m in cursor.fetchall()]
                cursor.close()
                
                st.warning("⚠️ Pour cette rubrique, vous configurez directement la liste des choix disponibles.")
                
                # Interface simplifiée : Juste les modalités
                nb_init = len(existing_mods) if existing_mods else 3
                nb_choix = st.number_input("Nombre de choix possibles", min_value=1, value=nb_init, step=1)
                
                with st.form("special_var_form"):
                    cols = st.columns(2)
                    final_mods = []
                    all_ok = True
                    
                    for i in range(int(nb_choix)):
                        val_def = existing_mods[i] if i < len(existing_mods) else ""
                        with cols[i%2]:
                            val = st.text_input(f"Option {i+1}", value=val_def, key=f"sp_mod_{i}")
                            final_mods.append(val)
                            if not val.strip(): all_ok = False
                    
                    if st.form_submit_button(f"💾 ENREGISTRER LES {target_tab}S"):
                        if all_ok:
                            # On appelle la sauvegarde avec context spécial
                            save_configuration(
                                context=target_tab,
                                is_new_var=False, # Variable virtuelle
                                var_pos=FIXED_POS,
                                var_lib="Nature", # Nom fictif
                                var_type="MOD",
                                rub_id=selected_rub_id,
                                comment="Liste système",
                                modalites=final_mods
                            )
                            st.success("✅ Liste mise à jour avec succès !")
                            import time
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Remplissez tous les champs.")

            # B. CAS STANDARD : ENTRETIEN
            else:
                # Récupération des variables de cette rubrique
                cursor = connection.cursor(cursor_factory=RealDictCursor)
                cursor.execute("SELECT pos, lib, type_v, commentaire FROM variable WHERE rubrique=%s AND tab='ENTRETIEN' ORDER BY pos", (selected_rub_id,))
                vars_list = cursor.fetchall()
                cursor.close()
                
                dict_vars = {v['lib']: v for v in vars_list}
                opt_vars = ["➕ Ajouter une question"] + list(dict_vars.keys())
                
                choix_var = st.selectbox("Quelle question modifier ?", opt_vars)
                
                # Prépare les données par défaut
                if choix_var == "➕ Ajouter une question":
                    is_new = True
                    # Calcul ID variable (Max global + 1 pour éviter collisions)
                    cursor = connection.cursor()
                    cursor.execute("SELECT MAX(pos) FROM variable") 
                    curr_max = cursor.fetchone()[0] or 10
                    cursor.close()
                    
                    v_pos = curr_max + 1
                    v_lib = ""
                    v_type = "MOD"
                    v_com = ""
                    v_mods = []
                else:
                    is_new = False
                    curr_var = dict_vars[choix_var]
                    v_pos = curr_var['pos']
                    v_lib = curr_var['lib']
                    v_type = curr_var['type_v']
                    v_com = curr_var['commentaire'] or ""
                    
                    # Charger modalités si MOD
                    v_mods = []
                    if v_type == 'MOD':
                        cursor = connection.cursor()
                        cursor.execute("SELECT lib_m FROM modalite WHERE tab='ENTRETIEN' AND pos=%s ORDER BY pos_m", (v_pos,))
                        v_mods = [m[0] for m in cursor.fetchall()]
                        cursor.close()

                st.divider()
                
                # Formulaire Standard
                with st.container():
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        in_lib = st.text_input("Libellé de la question", value=v_lib)
                    with c2:
                        types = {"Liste déroulante": "MOD", "Texte": "CHAINE", "Chiffre": "NUM"}
                        idx = list(types.values()).index(v_type) if v_type in types.values() else 0
                        in_type_lbl = st.selectbox("Type", list(types.keys()), index=idx)
                        in_type = types[in_type_lbl]
                    
                    # --- CORRECTION ICI (Height passé à 100px) ---
                    in_com = st.text_area("Aide / Commentaire", value=v_com, height=100)
                    
                    final_mods_std = []
                    valid_mods = True
                    
                    if in_type == "MOD":
                        st.write("**Configuration des choix :**")
                        nb_def = len(v_mods) if v_mods else 2
                        nb_ch = st.number_input("Nombre d'options", min_value=1, value=nb_def, step=1)
                        
                        cc = st.columns(2)
                        for i in range(int(nb_ch)):
                            txt_val = v_mods[i] if i < len(v_mods) else ""
                            with cc[i%2]:
                                vv = st.text_input(f"Choix {i+1}", value=txt_val, key=f"std_m_{i}")
                                final_mods_std.append(vv)
                                if not vv.strip(): valid_mods = False
                    
                    st.write("")
                    if st.button("💾 SAUVEGARDER LA QUESTION", type="primary"):
                        if not in_lib:
                            st.error("Le libellé est obligatoire.")
                        elif in_type == "MOD" and not valid_mods:
                            st.error("Remplissez tous les choix.")
                        else:
                            save_configuration('ENTRETIEN', is_new, v_pos, in_lib, in_type, selected_rub_id, in_com, final_mods_std)
                            st.success("Enregistré !")
                            import time
                            time.sleep(1)
                            st.rerun()

        else:
            st.info("👈 Commencez par sélectionner ou créer une Rubrique ci-dessus.")

# =================================================================
#  POINT D'ENTRÉE DU SCRIPT
# =================================================================
if __name__ == "__main__":  # pragma: no cover
    main()