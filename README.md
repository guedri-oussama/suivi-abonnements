## 💳 Suivi des Abonnements

Une application pour suivre et visualiser vos abonnements récurrents (Netflix, Spotify, Adobe, etc.).

---

## 🎯 Objectif du projet
Beaucoup d’utilisateurs oublient leurs abonnements, ce qui provoque des paiements inutiles.
Cette application a pour objectif de centraliser, suivre et visualiser tous les abonnements récurrents de manière claire et interactive.

L’utilisateur peut :
- Ajouter ses abonnements (prix, fréquence, date de début, engagement, catégorie)
- Suivre les échéances à venir et les coûts mensuels
- Être alerté des paiements proches
- Visualiser ses dépenses sous forme de graphiques
- Gérer (supprimer / filtrer / trier) facilement ses abonnements

---

## 🧰 Technologies utilisées

| Outil | Rôle |
|-------|------|
| **Python** | Langage principal |
| **Streamlit** | Interface web interactive |
| **Pandas** | Gestion et traitement des données |
| **Matplotlib** | Visualisation (graphique barres et camembert) |

---

## ⚙️ Fonctionnalités principales

1) 🧾 Gestion complète des abonnements

Ajout avec : Nom, Prix (€), Fréquence (Mensuel/Annuel), Catégorie, Engagement (Sans/12/24 mois), Date de début

Suppression depuis une liste déroulante (mise à jour immédiate du CSV)

2) 📅 Échéances intelligentes

Calcul automatique de la prochaine échéance future (même si la précédente est passée)

Calcul de la fin d’engagement

3) 🚨 Alertes visuelles (7 prochains jours)

Sans engagement :
🟥 Urgent (≤2 jours) · 🟧 Bientôt (≤5 jours) · 🟨 À surveiller (≤7 jours)

Avec engagement : 🔁 Renouvelé Auto (information, pas d’action requise)

4) 📊 Visualisations et tableau pro

Graphique barres : répartition des coûts mensuels par abonnement

Graphique camembert : répartition par catégorie

5) 📈 Totaux mensuel & annuel

💰 Coût mensuel total (somme des équivalents mensuels)

📆 Coût annuel total (mensuel × 12)

Les deux totaux s’affichent dans la barre latérale et respectent les filtres actifs.

---

## 🗂️ Structure du projet

suivi\_abonnements/

├── app.py # Fichier principal

├── abonnements.csv # Fichier local de stockage, créé automatiquement s’il n’existe pas, pour enregistrer les abonnements

├── requirements.txt # Bibliothèques nécessaires

└── README.md # Description du projet

---

## 🚀 Installation et exécution

1️⃣ Cloner le projet :

git clone https://github.com/guedri-oussama/suivi-abonnements.git

2️⃣ Installer les librairies nécessaires :

pip install -r requirements.txt

3️⃣ Lancer l’application :

streamlit run app.py

4️⃣ Ouvrir ton navigateur sur http://localhost:8501

🧠 Auteurs

Projet réalisé par : GUEDRI Oussama , DRUI Bernard
