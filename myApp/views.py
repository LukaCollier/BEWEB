from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from myApp.config import DB_SERVER
import myApp.controller.function as f
import myApp.model.bdd as bdd

app = Flask(__name__)
app.template_folder = "template"
app.static_folder = "static"
app.layout_folder = "layout"
app.config.from_object("myApp.config")


def get_db_connection():
    return mysql.connector.connect(**DB_SERVER)


def get_flashcard_banks():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT c.idcategorie AS id,
               c.nomcategorie AS name,
               COUNT(carte.idcarte) AS card_count
        FROM categorie c
        LEFT JOIN carte ON carte.idcategorie = c.idcategorie
        GROUP BY c.idcategorie, c.nomcategorie
        ORDER BY c.nomcategorie
        """
    )
    banks = cursor.fetchall()
    cursor.close()
    conn.close()
    return banks


def get_flashcards_by_bank(bank_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT c.idcarte AS id,
               c.question,
               c.reponse,
               cat.nomcategorie AS category_name
        FROM carte c
        INNER JOIN categorie cat ON cat.idcategorie = c.idcategorie
        WHERE cat.idcategorie = %s
        ORDER BY c.idcarte
        """,
        (bank_id,)
    )
    cards = cursor.fetchall()
    cursor.close()
    conn.close()
    return cards


# ─── Pages publiques ───────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/team/camille")
def team_camille():
    return render_template("team/camille.html")

@app.route("/team/etienne")
def team_etienne():
    return render_template("team/etienne.html")

@app.route("/team/luka")
def team_luka():
    return render_template("team/luka.html")

@app.route("/team/darya")
def team_darya():
    return render_template("team/darya.html")


# ─── Authentification ──────────────────────────────────────────

@app.route("/signin", methods=["GET", "POST"])
def signin():
    return render_template("signin.html")

@app.route("/connecter", methods=["GET", "POST"])
def connect():
    if request.method == "POST":
        login = request.form['login']
        mdp = request.form['mdp']

        # Vérifie si le login existe
        user_login = bdd.verifLogin(login)
        if not user_login:
            flash("Ce login n'existe pas", "danger")
            return redirect("/signin")

        # Vérifie le mot de passe
        user = bdd.verifAuthData(login, mdp)
        if not user:
            flash("Mot de passe incorrect", "danger")
            return redirect("/signin")

        # Authentification réussie
        session["idUser"] = user["idutilisateur"]
        session["nom"] = user["nom"]
        session["prenom"] = user["prenom"]
        session["mail"] = user["mail"]
        session["login"] = user["login"]
        session["statut"] = user["statut"]
        session["avatar"] = user["avatar"]
        flash("Authentification réussie", "success")
        if session["statut"] == "administrateur":
            return redirect("/admin")
        return redirect("/gestion")

    return render_template("signin.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Vous avez été déconnecté", "success")
    return redirect("/signin")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        statut = request.form["statut"]

        if password != confirm_password:
            return render_template("signup.html", error="Les mots de passe ne correspondent pas")

        if not email or not password:
            return render_template("signup.html", error="Email et mot de passe obligatoires")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO utilisateur (nom, prenom, mail, login, mdp, statut, avatar) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (lastname, firstname, email, email, password, statut, "")
            )
            conn.commit()
            conn.close()
            return render_template("signup.html", success="Compte créé avec succès ! Vous pouvez vous connecter.")
        except:
            return render_template("signup.html", error="Cet email est déjà utilisé")

    return render_template("signup.html")


# ─── Pages privées ─────────────────────────────────────────────

@app.route("/banques")
@f.statuts_obligatoires()
def banques():
    error = None
    banks = []
    try:
        banks = get_flashcard_banks()
    except Exception:
        error = "Impossible de charger les banques de flashcards pour le moment."
    return render_template("banques.html", banks=banks, error=error)

@app.route("/banques/<int:bank_id>")
@f.statuts_obligatoires()
def banque_detail(bank_id):
    error = None
    banks = []
    cards = []
    selected_bank = None
    try:
        banks = get_flashcard_banks()
        selected_bank = next((bank for bank in banks if bank["id"] == bank_id), None)
        cards = get_flashcards_by_bank(bank_id)
    except Exception:
        error = "Impossible d'afficher cette banque pour le moment."
    return render_template(
        "banques.html",
        banks=banks,
        cards=cards,
        selected_bank=selected_bank,
        error=error,
    )

@app.route("/admin")
@f.statuts_obligatoires('administrateur')
def admin():
    return render_template("admin.html")

@app.route("/gestion")
@f.statuts_obligatoires('gestionnaire', 'administrateur')
def gestion():
    return render_template("gestion.html")