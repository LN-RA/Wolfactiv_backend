# Wolfactiv Backend

Backend Flask robuste pour générer une recommandation olfactive à partir d’un test de personnalité.

## Lancer localement

```
pip install -r requirements.txt
python app.py
```

Place tes fichiers ici :
- `data/encoding_perso.xlsx`
- `data/parfums_enrichi.csv`
- `data/similarite_matrice.csv`
- `data/carte_identite_olfactive.xlsx`
- `Images-test-gout/` pour les images sensorielle

## Endpoints

- `POST /submit_quiz` : envoie les réponses utilisateur
- `GET /test` : test de démonstration
- `GET /images/<nom>` : affiche une image goût
