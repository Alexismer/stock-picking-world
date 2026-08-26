# 📤 Upload rapide vers GitHub (5 minutes, sans Git)

## Méthode "Web upload" (la plus simple)

### 1. Va sur ton repo
https://github.com/Alexismer/stock-picking-world

### 2. Upload les fichiers
- Clique **Add file** (bouton vert en haut) → **Upload files**
- **Drag-drop tous les fichiers** du dossier `stock-picking-world/` de ton PC :
  - `streamlit_app.py`
  - `requirements.txt`
  - `README.md`
  - `.gitignore`
  - Le dossier `pages/` (avec ses 4 fichiers)

⚠️ **Important** : garde bien la structure. Le dossier `pages/` doit être un dossier, pas fusionné à la racine. GitHub Web permet de drag le dossier entier.

### 3. Commit
- En bas : **Commit changes**
- Message : "Initial upload stock picking dashboard"
- Clique **Commit changes**

### 4. Vérification
Tu dois voir dans ton repo :
```
stock-picking-world/
├── .gitignore
├── README.md
├── requirements.txt
├── streamlit_app.py
└── pages/
    ├── 1_🌍_Pays.py
    ├── 2_🏭_Secteurs.py
    ├── 3_🎯_Stock_Picks.py
    └── 4_📈_Backtest.py
```

## Déploiement Streamlit Cloud (2 minutes)

### 1. Va sur https://share.streamlit.io

### 2. Clique **Create app** → **Deploy a public app from GitHub**

### 3. Remplis
- **Repository** : `Alexismer/stock-picking-world`
- **Branch** : `main`
- **Main file path** : `streamlit_app.py`
- **App URL** (optionnel) : personnalise l'URL, ex `alexis-stock-picking`

### 4. Clique **Deploy**
Streamlit Cloud installe les dépendances (2-3 min) puis lance ton app.

### 5. Bookmark l'URL finale
Ton app est en ligne à `https://<ton-url>.streamlit.app` — accessible depuis n'importe quel appareil.

## Mises à jour futures

Pour modifier l'app :
1. Sur GitHub, ouvre le fichier à modifier → clique le crayon ✏️
2. Modifie → Commit
3. Streamlit Cloud rebuild automatiquement en 30 sec

## Troubleshooting

- **App plante au démarrage** : va dans **Manage app** → **Logs** pour voir l'erreur
- **Import error** : ajoute la lib manquante dans `requirements.txt`
- **Timeout Yahoo Finance** : normal en heures de pointe, refresh dans 2-3 min
