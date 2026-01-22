⚖️ Maison du Droit - Système de Gestion Intégré
📌 Description du projet
Ce projet a été réalisé dans le cadre de la SAE 501. Il s'agit d'une application web complète destinée à la Maison du Droit.

L'objectif est de centraliser et simplifier la gestion des entretiens juridiques via une interface unique permettant :

L'alimentation : Saisie des entretiens et des bénéficiaires.

La visualisation : Tableaux de bord décisionnels (KPIs, graphiques dynamiques).

La configuration : Gestion dynamique de la structure du questionnaire (ajout de variables, modification des listes déroulantes) sans toucher au code.

📂 Structure du projet
Voici l'architecture actuelle de l'application :

Application Principale :

poc_global.py : Point d'entrée de l'application (Interface Streamlit).

backend.py : Logique métier et gestion de la base de données PostgreSQL (CRUD).

Tests & Qualité :

test_unitaire.py : Tests unitaires complets (couverture > 90%) pour le backend.

test_web.py : Tests d'intégration automatisés avec Selenium (simulation utilisateur).

sonar-project.properties : Configuration pour l'analyse qualité SonarCloud.

Outils & Données :

reparer_compteur.py : Script utilitaire pour maintenance de la BDD.

requirements.txt : Liste des dépendances Python.

🛠️ Installation et Prérequis
1. Prérequis techniques
Python 3.8 ou supérieur.

Serveur PostgreSQL (local ou portable via D:/tools sur les postes IUT).

Navigateur Firefox (pour les tests Selenium).

2. Installation des dépendances
Ouvrez un terminal à la racine du projet et lancez :

Bash
pip install streamlit pandas psycopg2-binary plotly selenium webdriver-manager pytest pytest-cov
3. Configuration de la Base de Données
Le projet utilise des variables d'environnement pour sécuriser les accès (conforme SonarCloud). Sur votre poste local, avant de lancer l'application, configurez le mot de passe :

Windows (CMD) :

DOS
set PG_PASSWORD=pgis
Windows (PowerShell) :

PowerShell
$env:PG_PASSWORD="pgis"
🚀 Utilisation
Lancer l'application
Bash
streamlit run poc_global.py
L'application sera accessible sur http://localhost:8501.

Fonctionnalités Clés
Onglet Alimentation : Remplissez le formulaire. Les champs s'adaptent dynamiquement à la configuration BDD.

Onglet Visualisation : Consultez les stats globales ou créez vos propres graphiques via le "Créateur de graphiques".

Onglet Configuration : Ajoutez des questions ou modifiez les listes déroulantes (Demandes/Solutions) directement depuis l'interface.

🧪 Tests et Qualité
Le projet intègre une chaîne de tests rigoureuse.

Lancer les tests unitaires (Backend)

pytest test_unitaire.py --cov=. --cov-report=xml
Couverture actuelle : ~100%


Lancer les tests Web (Selenium)
Lancez l'application dans un premier terminal (streamlit run...).

Dans un second terminal, lancez le robot de test :

python test_web.py


👥 Auteurs
Projet développé par :

Dylan
Maxence
Jordan

© 2026 - SAE 501 - IUT de Vannes