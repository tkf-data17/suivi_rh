# 🏥 Suivi des Arrivées et Départs - INH

Application de gestion des pointages pour le suivi des arrivées et des départs du personnel. Développée en Python avec **Streamlit**, cette application offre une interface moderne et intuitive pour la gestion quotidienne des ressources humaines.

![Logo](logo_inh.jpg)

## 🚀 Fonctionnalités Principales

### 1. 📝 Saisie des Mouvements
- **Enregistrement rapide** des arrivées et départs quotidiens.
- **Sélection facile** du personnel via une liste déroulante (recherche par nom).
- **Date du jour** par défaut avec possibilité de sélection manuelle.
- **Heures modifiables** (format `HH:MM`).
- **Départ par défaut** pré-rempli à `17:30` (modifiable).

### 2. ➕ Gestion du Personnel
- **Ajout de nouveaux employés** :
  - Champs séparés pour le **Nom** (automatiquement mis en majuscule) et le **Prénom**.
  - Sélection du **Sexe** (M/F) et du **Service** (Prélèvements, Parc Auto, Comptabilité, etc.).
- **Modification et Suppression** :
  - Possibilité de corriger les informations d'un employé existant (Service, Sexe).
  - Suppression d'un employé avec **confirmation de sécurité** pour éviter les erreurs.

### 3. 📊 Visualisation et Export
- **Tableau de bord** listant tous les mouvements enregistrés.
- **Tri automatique** : Les enregistrements les plus récents apparaissent en premier.
- **Recherche globale** : Filtrage par nom, service ou date.
- **Export Excel** : Téléchargement des données filtrées au format `.xlsx`.

### 4. 🛡️ Sécurité et Fiabilité
- **Sauvegarde automatique** : Chaque modification génère une copie de sauvegarde au format JSON (`suivi_employes.json`) en plus du fichier Excel principal.
- **Validation des données** : Contrôle du format des heures saisies.

## 🛠️ Installation et Lancement

### Prérequis
- Python 3.8 ou supérieur.

### Installation

1. **Cloner le projet** ou extraire les fichiers.
2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

### Lancement de l'application
Exécutez la commande suivante dans votre terminal :
```bash
streamlit run app.py
```

L'application s'ouvrira automatiquement dans votre navigateur par défaut (généralement à l'adresse `http://localhost:8501`).

## 📂 Structure du Projet

- `app.py` : Point d'entrée principal de l'application Streamlit.
- `database.py` : Gestion de la base de données (lecture/écriture Excel et JSON).
- `style.py` : Feuille de style CSS personnalisée pour l'interface.
- `personnel.json` : Base de données des employés.
- `suivi_employes.xlsx` : Base de données principale des mouvements.
- `suivi_employes.json` : Sauvegarde automatique des mouvements.

## 🔄 Migration de Données (Optionnel)
Des scripts utilitaires sont inclus pour la maintenance :
- `reset_db.py` : Permet de réinitialiser complètement la base de données (Attention : supprime toutes les données !).
- `migrate_script.py` : Script utilisé pour importer les données historiques depuis un ancien format (`base_old.xlsx`).

## 👤 Auteur
Application développée pour la gestion interne RH.
