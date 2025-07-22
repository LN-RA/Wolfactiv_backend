
from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import base64
import matplotlib.pyplot as plt
import io
from unidecode import unidecode

app = Flask(__name__)

# Chargement des fichiers
def load_data():
    def safe_read_excel(path):
        try:
            return pd.read_excel(path, index_col=0)
        except Exception as e:
            print(f"Erreur lecture Excel {path}:", e)
            return pd.DataFrame()

    def safe_read_csv(path):
        try:
            return pd.read_csv(path, index_col=0)
        except Exception as e:
            print(f"Erreur lecture CSV {path}:", e)
            return pd.DataFrame()

    return {
        "encoding_perso": safe_read_excel("data/encoding_perso.xlsx"),
        "similarite_matrice": safe_read_csv("data/similarite_matrice.csv"),
        "parfums_df": safe_read_csv("data/parfums_enrichi.csv"),
        "id_olfactive": safe_read_excel("data/carte_identite_olfactive.xlsx")
    }

data_files = load_data()

OLF_KEYS = [
    "Ambree", "Boisee Mousse", "Cuir", "Aromatique", "Florale", "Hesperidee", "Boisee",
    "Florale Fraiche", "Balsamique", "Verte", "Florale Rosee", "Musquee", "Fruitee",
    "Florale Poudree", "Marine", "Fleur D'Oranger", "Conifere Terpenique", "Aldehydee"
]

def normalize_key(k):
    return unidecode(str(k)).replace(" ", "").lower()

OLF_KEYS_NORMALIZED = [normalize_key(k) for k in OLF_KEYS]

def get_mbti_from_answers(answers):
    return "ENFJ"

def get_vector_u(mbti, encoding_perso):
    try:
        return encoding_perso.loc[mbti].values
    except:
        return np.zeros(len(OLF_KEYS))

def get_u_final(base_u):
    return np.clip(base_u + np.random.normal(0, 0.05, size=len(base_u)), 0, 1)

def get_top5_parfums(u_final, similarite_matrice, parfums_df):
    try:
        sim_scores = similarite_matrice.apply(lambda row: np.dot(u_final, row.values), axis=1)
        top5_idx = sim_scores.sort_values(ascending=False).head(5).index
        top5_df = parfums_df.loc[top5_idx]
        top5_df["score"] = sim_scores.loc[top5_idx].values
        return top5_df[["Nom du Parfum", "Marque", "score"]].to_dict(orient="records")
    except:
        return []

def make_radar_image(u_final):
    try:
        labels = OLF_KEYS
        values = u_final.tolist()
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        values += values[:1]
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
        ax.plot(angles, values, 'o-', linewidth=2)
        ax.fill(angles, values, alpha=0.25)
        ax.set_yticklabels([])
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=8)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")
    except Exception as e:
        print("Erreur radar:", e)
        return ""

@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    answers = request.get_json()
    mbti = get_mbti_from_answers(answers)
    u = get_vector_u(mbti, data_files["encoding_perso"])
    u_final = get_u_final(u)
    radar_img = make_radar_image(u_final)
    top5 = get_top5_parfums(u_final, data_files["similarite_matrice"], data_files["parfums_df"])

    try:
        perso_nom = data_files["id_olfactive"].loc[mbti, "Nom"]
        citation = data_files["id_olfactive"].loc[mbti, "Citation"]
    except:
        perso_nom, citation = "", ""

    return jsonify({
        "MBTI": mbti,
        "perso_nom": perso_nom,
        "citation": citation,
        "radar": radar_img,
        "top5": top5
    })

@app.route("/test", methods=["GET"])
def test_quiz():
    dummy_data = {
        "souvenir": "L'odeur du linge propre",
        "perception": "Mystérieuse",
        "fière": "Ma persévérance",
        "défi": "Je veux être calme et courageux"
    }
    return submit_quiz()

@app.route("/images/<path:filename>")
def get_image(filename):
    return send_from_directory("Images-test-gout", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
