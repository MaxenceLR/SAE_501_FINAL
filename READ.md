# SAE 501 - [Nom de ton Projet ici]

## 📌 Description du projet
Ce projet a été réalisé dans le cadre de la SAE 501. Il vise à [expliquer brièvement l'objectif, ex: automatiser la gestion des données de la Maison du Droit].

Il comprend des scripts d'automatisation en Python, des analyses via Jupyter Notebook et la gestion de données exportées sous format Excel.

## 📂 Structure des fichiers
Voici le rôle des principaux fichiers présents dans ce dépôt :

* **Scripts Python (`.py`) :**
    * `formulaire_ajout_variable.py` : Script pour gérer l'ajout de variables.
    * `poc_formulaire_alimantation.py` : Preuve de concept pour l'alimentation des données via un formulaire.
    * `poc_reporting.py` : Génération automatique de rapports.
* **Analyses :**
    * `Partie2sae.ipynb` : Analyse de données et visualisation (Notebook).
* **Données (`.xlsx` & `.backup`) :**
    * `Maison_droit_decembre.xlsx` : Données sources de décembre.
    * `Sae_dubois_e2302355.backup` : Sauvegarde de la base de données.
    * Les fichiers `*_export.xlsx` : Résultats des traitements et exports de données.

## 🛠️ Installation et Prérequis
Pour faire fonctionner les scripts Python, vous aurez besoin de :
1. Installer Python (version 3.x recommandée).
2. Installer les dépendances nécessaires (si tu en as, par exemple Pandas) :
   ```bash
   pip install pandas openpyxl