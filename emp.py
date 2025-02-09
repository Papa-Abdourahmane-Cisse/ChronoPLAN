import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import time
import pygame
import sqlite3
import json
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Initialiser le mixer de pygame
pygame.mixer.init()

# Configuration de la page
st.set_page_config(page_title="Gestionnaire d’Emploi du Temps et d’Activités", layout="wide", page_icon="📊")

# Ajouter des styles CSS personnalisés
st.markdown(
    """
    <style>
    /* Style pour le menu */
    .menu {
        background-color: #007BFF; /* Couleur bleu */
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        font-family: Arial, sans-serif;
    }

    .menu ul {
        list-style-type: none;
        padding: 0;
        margin: 0;
    }

    .menu li {
        margin: 10px 0;
    }

    .menu a {
        text-decoration: none;
        color: #FFFFFF; /* Couleur blanche pour le texte */
        font-weight: bold;
        transition: color 0.3s ease;
    }

    .menu a:hover {
        color: #FFD700; /* Couleur dorée pour le hover */
    }

    /* Style pour les sections */
    .section {
        border: 2px solid #007BFF; /* Couleur bleu */
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        background-color: #ffffff;
    }

    .section h2 {
        color: #007BFF; /* Couleur bleu */
    }

    /* Forcer l'affichage des styles CSS */
    .stApp {
        background-color: #f0f8ff; /* Couleur de fond bleu clair */
    }

    .stButton>button {
        background-color: #007BFF; /* Couleur bleu pour les boutons */
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        width: 100%; /* Largeur complète pour les boutons */
        margin-bottom: 10px; /* Espacement entre les boutons */
    }

    .stButton>button:hover {
        background-color: #0056b3; /* Couleur bleu plus foncé pour le hover des boutons */
    }

    .stForm {
        background-color: #ffffff; /* Couleur de fond blanc pour les formulaires */
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .stForm input, .stForm select, .stForm textarea {
        width: 100%;
        padding: 10px;
        margin-bottom: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
    }

    .stForm button {
        width: 100%;
        padding: 15px;
        font-size: 18px;
    }

    /* Style pour les écritures en couleur marron */
    .brown-text {
        color: #8B4513; /* Couleur marron */
    }

    /* Style pour les titres en couleur bleu */
    .blue-title {
        color: #007BFF; /* Couleur bleu */
    }

    /* Style pour l'encadrement avec fond gris */
    .gray-background {
        background-color: #f0f0f0; /* Couleur gris clair */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
    }

    /* Style pour la page d'accueil */
    .home-section {
        background: linear-gradient(135deg, #ff9a9e, #fad0c4);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 3px 3px 12px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease-in-out, box-shadow 0.3s ease-in-out;
    }
    .home-section:hover {
        transform: scale(1.02);
        box-shadow: 4px 4px 15px rgba(0, 0, 0, 0.15);
    }
    .blue-title {
        color: #ffffff;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 12px;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
    }
    .brown-text {
        color: #ffffff;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 15px;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
    }
    .cta-button {
        background-color: #ff6b6b;
        color: white;
        padding: 12px 20px;
        font-size: 16px;
        border: none;
        border-radius: 8px;
        cursor: pointer;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        transition: background-color 0.3s ease-in-out, transform 0.2s ease-in-out;
    }
    .cta-button:hover {
        background-color: #e63946;
        transform: scale(1.05);
    }
    .cta-icon {
        display: inline-block;
        transition: transform 0.3s ease-in-out;
    }
    .cta-button:hover .cta-icon {
        transform: translateX(5px);
    }

    /* Style pour le cercle décoratif */
    .circle {
        width: 150px;
        height: 150px;
        background-color: #ff9a9e;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 20px auto;
        position: relative;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .circle::before {
        content: '🌸';
        font-size: 80px;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }
    .emoji {
        font-size: 30px;
        position: absolute;
    }
    .emoji-1 {
        top: -10px;
        left: -10px;
    }
    .emoji-2 {
        top: -10px;
        right: -10px;
    }
    .emoji-3 {
        bottom: -10px;
        left: -10px;
    }
    .emoji-4 {
        bottom: -10px;
        right: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Charger les données existantes
@st.cache_data
def load_data():
    try:
        data = pd.read_csv("emploi_du_temps.csv")
        data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
        return data
    except FileNotFoundError:
        return pd.DataFrame(columns=["Date", "Matière", "Durée", "Priorité"])

# Initialiser emploi_du_temps
emploi_du_temps = load_data()

# Fonction pour enregistrer les données au format CSV
def save_to_csv(data, file_name="emploi_du_temps.csv"):
    data.to_csv(file_name, index=False)
    st.success(f"🌸 Les données ont été enregistrées dans {file_name} 🌸")

# Fonction pour réinitialiser les données
def reset_data():
    save_to_csv(pd.DataFrame(columns=["Date", "Matière", "Durée", "Priorité"]))
    st.success("🌸 Toutes les données ont été réinitialisées ! 🌸")

# Fonction pour envoyer des notifications (simulé ici par un message Streamlit)
def send_notification(message):
    st.success(message)

# Fonction pour générer des rapports hebdomadaires/mensuels
def generate_report(emploi_du_temps, period="weekly"):
    now = datetime.now()
    if period == "hebdomadaire":
        start_date = now - timedelta(days=now.weekday() + 7)
    elif period == "mensuel":
        start_date = now.replace(day=1)
    else:
        st.error("Période invalide. Veuillez sélectionner 'hebdomadaire' ou 'mensuel'.")
        return pd.DataFrame()  # Retourne un DataFrame vide en cas d'erreur

    filtered_data = emploi_du_temps[emploi_du_temps["Date"] >= start_date]
    report = filtered_data.groupby("Matière")["Durée"].sum().reset_index()
    return report

# Fonction pour exporter les données en Excel
def export_to_excel(data, file_name="emploi_du_temps.xlsx"):
    data.to_excel(file_name, index=False)
    st.success(f"🌸 Les données ont été exportées dans {file_name} 🌸")

# Fonction pour évaluer l'emploi du temps
def evaluate_time_management():
    st.subheader("📝 Évaluation de l'Emploi du Temps 🌸")

    questions = {
        "Avez-vous respecté toutes les activités prévues pour aujourd'hui ?": {"Oui": 2, "Partiellement": 1, "Non": 0},
        "Avez-vous terminé toutes les tâches importantes ?": {"Oui": 2, "Partiellement": 1, "Non": 0},
        "Avez-vous évité les distractions pendant vos activités ?": {"Oui": 2, "Partiellement": 1, "Non": 0},
        "Avez-vous pris des pauses régulières ?": {"Oui": 2, "Partiellement": 1, "Non": 0},
        "Avez-vous respecté les durées allouées pour chaque activité ?": {"Oui": 2, "Partiellement": 1, "Non": 0},
    }

    total_score = 0
    max_score = len(questions) * 2

    # Initialiser les réponses dans st.session_state
    if "responses" not in st.session_state:
        st.session_state.responses = {}

    for i, (question, options) in enumerate(questions.items()):
        st.write(question)
        key = f"q_{i}"  # Clé unique basée sur l'indice de la question
        response = st.radio(question, list(options.keys()), key=key)
        st.session_state.responses[key] = response
        total_score += options[response]

    st.subheader("Résultats de l'Évaluation 🌸")
    st.write(f"Votre score est : {total_score}/{max_score}")

    if total_score == max_score:
        st.success("🎉 Parfait ! Vous avez parfaitement géré votre emploi du temps aujourd'hui.")
        st.balloons()
    elif total_score >= max_score / 2:
        st.info("👍 Vous avez bien géré votre temps, mais vous pouvez encore vous améliorer.")
    else:
        st.warning("⚠️ Essayez de mieux planifier et suivre votre emploi du temps.")

    # Enregistrer le score quotidien
    if "daily_scores" not in st.session_state:
        st.session_state.daily_scores = pd.DataFrame(columns=["Date", "Score"])
    st.session_state.daily_scores = pd.concat([st.session_state.daily_scores, pd.DataFrame({"Date": [datetime.now().date()], "Score": [total_score]})], ignore_index=True)

    # Graphique pour visualiser la performance
    st.subheader("📈 Graphique de performance")
    if not st.session_state.daily_scores.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(st.session_state.daily_scores["Date"], st.session_state.daily_scores["Score"], marker="o", linestyle="-")
        ax.set_xlabel("Date")
        ax.set_ylabel("Score")
        ax.set_title("Scores quotidiens de l'emploi du temps")
        ax.grid(True)
        st.pyplot(fig)

# Fonction pour ajouter des cours et des expressions mathématiques
def add_course():
    st.subheader("Ajouter un cours 📚")
    matiere = st.selectbox("Sélectionnez la matière", emploi_du_temps["Matière"].unique(), key="add_course_matiere")
    cours = st.text_area("Contenu du cours", key="add_course_contenu")
    expression = st.text_input("Expression mathématique (utilisez LaTeX)", key="add_course_expression")
    color = st.color_picker("Choisir la couleur du texte", "#000000", key="add_course_color")
    underline = st.checkbox("Souligner le texte", key="add_course_underline")

    if st.button("Ajouter le cours", key="add_course_button"):
        if matiere and cours:
            # Sauvegarder le cours dans un fichier JSON
            course_data = {
                "Matière": matiere,
                "Contenu": cours,
                "Expression": expression,
                "Couleur": color,
                "Souligné": underline
            }
            save_course(course_data)
            st.success("Cours ajouté avec succès !")
            if expression:
                st.latex(expression)

# Fonction pour sauvegarder les cours dans un fichier JSON
def save_course(course_data):
    try:
        with open("cours.json", "r") as file:
            courses = json.load(file)
    except FileNotFoundError:
        courses = []

    courses.append(course_data)

    with open("cours.json", "w") as file:
        json.dump(courses, file, indent=4)

# Fonction pour charger les cours depuis un fichier JSON
def load_courses():
    try:
        with open("cours.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer un cours
def delete_course(index):
    courses = load_courses()
    if 0 <= index < len(courses):
        del courses[index]
        with open("cours.json", "w") as file:
            json.dump(courses, file, indent=4)
        st.success("Cours supprimé avec succès !")
    else:
        st.error("Index de cours invalide.")

# Fonction pour afficher les cours sauvegardés
def view_courses():
    st.subheader("Cours sauvegardés 📚")
    courses = load_courses()
    for index, course in enumerate(courses):
        st.write(f"**Matière:** {course['Matière']}")
        st.write(f"**Contenu:** {course['Contenu']}")
        if course["Expression"]:
            st.latex(course["Expression"])
        st.markdown(f"<p style='color:{course['Couleur']}; text-decoration:{'underline' if course['Souligné'] else 'none'}'>{course['Contenu']}</p>", unsafe_allow_html=True)
        if st.button(f"Supprimer le cours {index + 1}", key=f"delete_course_{index}"):
            delete_course(index)
            st.rerun()
        st.write("---")

# Fonction pour ajouter une tâche à la To-Do List
def add_task():
    st.subheader("Ajouter une tâche 📋")
    with st.form(key="add_task_form"):
        task = st.text_input("Nom de la tâche", key="add_task_name")
        date = st.date_input("Date d'échéance", key="add_task_date")
        time = st.time_input("Heure d'échéance", key="add_task_time")
        priority = st.selectbox("Priorité", ["Faible", "Moyenne", "Élevée"], key="add_task_priority")
        reminder_email = st.checkbox("Envoyer un rappel par email", key="add_task_reminder")
        submitted = st.form_submit_button("Ajouter la tâche")

        if submitted:
            if task and date and time:
                task_data = {
                    "Nom": task,
                    "Date": date.strftime("%Y-%m-%d"),
                    "Heure": time.strftime("%H:%M:%S"),
                    "Priorité": priority,
                    "Rappel": reminder_email
                }
                save_task(task_data)
                st.success("Tâche ajoutée avec succès !")
                if reminder_email:
                    send_email(
                        subject="Rappel de tâche",
                        body=f"Vous avez une tâche '{task}' à compléter avant le {date} à {time}.",
                        to_email="your_email@gmail.com",  # Remplacez par votre email
                        is_reminder=True
                    )

# Fonction pour sauvegarder les tâches dans un fichier JSON
def save_task(task_data):
    try:
        with open("tasks.json", "r") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []

    tasks.append(task_data)

    with open("tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)

# Fonction pour charger les tâches depuis un fichier JSON
def load_tasks():
    try:
        with open("tasks.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une tâche
def delete_task(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        del tasks[index]
        with open("tasks.json", "w") as file:
            json.dump(tasks, file, indent=4)
        st.success("Tâche supprimée avec succès !")
    else:
        st.error("Index de tâche invalide.")

# Fonction pour afficher les tâches sauvegardées
def view_tasks():
    st.subheader("Tâches sauvegardées 📋")
    tasks = load_tasks()
    for index, task in enumerate(tasks):
        st.write(f"**Nom:** {task['Nom']}")
        st.write(f"**Date d'échéance:** {task['Date']} {task['Heure']}")
        st.write(f"**Priorité:** {task['Priorité']}")
        if st.button(f"Supprimer la tâche {index + 1}", key=f"delete_task_{index}"):
            delete_task(index)
            st.rerun()
        st.write("---")

# Fonction pour ajouter un projet
def add_project():
    st.subheader("Ajouter un projet 📚")
    project_name = st.text_input("Nom du projet", key="add_project_name")
    steps = st.text_area("Étapes du projet (une par ligne)", key="add_project_steps")

    if st.button("Ajouter le projet", key="add_project_button"):
        if project_name and steps:
            project_data = {
                "Nom": project_name,
                "Étapes": steps.split("\n")
            }
            save_project(project_data)
            st.success("Projet ajouté avec succès !")

# Fonction pour sauvegarder les projets dans un fichier JSON
def save_project(project_data):
    try:
        with open("projects.json", "r") as file:
            projects = json.load(file)
    except FileNotFoundError:
        projects = []

    projects.append(project_data)

    with open("projects.json", "w") as file:
        json.dump(projects, file, indent=4)

# Fonction pour charger les projets depuis un fichier JSON
def load_projects():
    try:
        with open("projects.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer un projet
def delete_project(index):
    projects = load_projects()
    if 0 <= index < len(projects):
        del projects[index]
        with open("projects.json", "w") as file:
            json.dump(projects, file, indent=4)
        st.success("Projet supprimé avec succès !")
    else:
        st.error("Index de projet invalide.")

# Fonction pour afficher les projets sauvegardés
def view_projects():
    st.subheader("Projets sauvegardés 📚")
    projects = load_projects()
    for index, project in enumerate(projects):
        st.write(f"**Nom:** {project['Nom']}")
        st.write("**Étapes:**")
        for step in project["Étapes"]:
            st.write(f"- {step}")
        if st.button(f"Supprimer le projet {index + 1}", key=f"delete_project_{index}"):
            delete_project(index)
            st.rerun()
        st.write("---")

# Fonction pour changer le thème
def change_theme(theme):
    if theme == "Sombre":
        st.markdown(
            """
            <style>
            .main {
                background-color: #1E1E1E;
                color: #FFFFFF;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            .main {
                background-color: #FFFFFF;
                color: #000000;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

# Fonction pour sauvegarder les préférences utilisateur
def save_preferences(theme):
    preferences = {
       "theme": theme
    }
    with open("preferences.json", "w") as file:
       json.dump(preferences, file, indent=4)

# Fonction pour charger les préférences utilisateur
def load_preferences():
    try:
        with open("preferences.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"theme": "Clair"}

# Fonction pour définir des objectifs personnels
def set_goals():
    st.subheader("Définir des objectifs personnels 🎯")
    goal_name = st.text_input("Nom de l'objectif", key="set_goals_name")
    goal_description = st.text_area("Description de l'objectif", key="set_goals_description")
    goal_target = st.number_input("Cible (en heures)", min_value=0, step=1, key="set_goals_target")
    goal_deadline = st.date_input("Date limite", key="set_goals_deadline")

    if st.button("Ajouter l'objectif", key="set_goals_button"):
        if goal_name and goal_description and goal_target and goal_deadline:
            goal_data = {
                "Nom": goal_name,
                "Description": goal_description,
                "Cible": goal_target,
                "Date limite": goal_deadline.strftime("%Y-%m-%d")
            }
            save_goal(goal_data)
            st.success("Objectif ajouté avec succès !")

# Fonction pour sauvegarder les objectifs dans un fichier JSON
def save_goal(goal_data):
    try:
        with open("goals.json", "r") as file:
            goals = json.load(file)
    except FileNotFoundError:
        goals = []

    goals.append(goal_data)

    with open("goals.json", "w") as file:
        json.dump(goals, file, indent=4)

# Fonction pour charger les objectifs depuis un fichier JSON
def load_goals():
    try:
        with open("goals.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour afficher les objectifs sauvegardés
def view_goals():
    st.subheader("Objectifs sauvegardés 🎯")
    goals = load_goals()
    for index, goal in enumerate(goals):
        st.write(f"**Nom:** {goal['Nom']}")
        st.write(f"**Description:** {goal['Description']}")
        st.write(f"**Cible:** {goal['Cible']} heures")
        st.write(f"**Date limite:** {goal['Date limite']}")
        if st.button(f"Supprimer l'objectif {index + 1}", key=f"delete_goal_{index}"):
            delete_goal(index)
            st.rerun()
        st.write("---")

# Fonction pour supprimer un objectif
def delete_goal(index):
    goals = load_goals()
    if 0 <= index < len(goals):
        del goals[index]
        with open("goals.json", "w") as file:
            json.dump(goals, file, indent=4)
        st.success("Objectif supprimé avec succès !")
    else:
        st.error("Index d'objectif invalide.")

# Fonction pour générer un rapport de progression
def generate_progress_report(emploi_du_temps, goals):
    now = datetime.now()
    report = []

    for goal in goals:
        goal_deadline = datetime.strptime(goal["Date limite"], "%Y-%m-%d")
        if now.date() <= goal_deadline.date():
            filtered_data = emploi_du_temps[emploi_du_temps["Date"] <= goal_deadline]
            total_hours = filtered_data["Durée"].sum()
            progress = (total_hours / goal["Cible"]) * 100
            report.append({
                "Nom": goal["Nom"],
                "Description": goal["Description"],
                "Cible": goal["Cible"],
                "Heures réelles": total_hours,
                "Progression": progress
            })

    return pd.DataFrame(report)

# Fonction pour ajouter des notes et des coefficients
def manage_grades_and_coefficients():
    st.subheader("Gestion des Notes et Coefficients 📈")

    # Ajouter une note
    st.subheader("Ajouter une note 📈")
    matiere = st.selectbox("Sélectionnez la matière", emploi_du_temps["Matière"].unique(), key="add_grades_matiere")
    grade = st.number_input("Note", min_value=0.0, max_value=20.0, step=0.1, key="add_grades_grade")
    date = st.date_input("Date de la note", key="add_grades_date")

    if st.button("Ajouter la note", key="add_grades_button"):
        if matiere and grade and date:
            grade_data = {
                "Matière": matiere,
                "Note": grade,
                "Date": date.strftime("%Y-%m-%d")
            }
            save_grade(grade_data)
            st.success("Note ajoutée avec succès !")

    # Définir un coefficient
    st.subheader("Définir un coefficient 📚")
    matiere_coef = st.selectbox("Sélectionnez la matière", emploi_du_temps["Matière"].unique(), key="set_coefficients_matiere")
    coefficient = st.number_input("Coefficient", min_value=0.0, step=0.1, key="set_coefficients_coefficient")

    if st.button("Ajouter le coefficient", key="set_coefficients_button"):
        if matiere_coef and coefficient:
            coefficient_data = {
                "Matière": matiere_coef,
                "Coefficient": coefficient
            }
            save_coefficient(coefficient_data)
            st.success("Coefficient ajouté avec succès !")

    # Afficher les notes et coefficients sauvegardés
    st.subheader("Notes et Coefficients sauvegardés 📚")
    grades = load_grades()
    coefficients = load_coefficients()

    for index, grade in enumerate(grades):
        st.write(f"**Matière:** {grade['Matière']}")
        st.write(f"**Note:** {grade['Note']}")
        st.write(f"**Date:** {grade['Date']}")
        if st.button(f"Supprimer la note {index + 1}", key=f"delete_grade_{index}"):
            delete_grade(index)
            st.rerun()
        st.write("---")

    for index, coefficient in enumerate(coefficients):
        st.write(f"**Matière:** {coefficient['Matière']}")
        st.write(f"**Coefficient:** {coefficient['Coefficient']}")
        if st.button(f"Supprimer le coefficient {index + 1}", key=f"delete_coefficient_{index}"):
            delete_coefficient(index)
            st.rerun()
        st.write("---")

    # Calculer la moyenne pondérée
    calculate_weighted_average()

# Fonction pour sauvegarder les notes dans un fichier JSON
def save_grade(grade_data):
    try:
        with open("grades.json", "r") as file:
            grades = json.load(file)
    except FileNotFoundError:
        grades = []

    grades.append(grade_data)

    with open("grades.json", "w") as file:
        json.dump(grades, file, indent=4)

# Fonction pour charger les notes depuis un fichier JSON
def load_grades():
    try:
        with open("grades.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une note
def delete_grade(index):
    grades = load_grades()
    if 0 <= index < len(grades):
        del grades[index]
        with open("grades.json", "w") as file:
            json.dump(grades, file, indent=4)
        st.success("Note supprimée avec succès !")
    else:
        st.error("Index de note invalide.")

# Fonction pour sauvegarder les coefficients dans un fichier JSON
def save_coefficient(coefficient_data):
    try:
        with open("coefficients.json", "r") as file:
            coefficients = json.load(file)
    except FileNotFoundError:
        coefficients = []

    coefficients.append(coefficient_data)

    with open("coefficients.json", "w") as file:
        json.dump(coefficients, file, indent=4)

# Fonction pour charger les coefficients depuis un fichier JSON
def load_coefficients():
    try:
        with open("coefficients.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer un coefficient
def delete_coefficient(index):
    coefficients = load_coefficients()
    if 0 <= index < len(coefficients):
        del coefficients[index]
        with open("coefficients.json", "w") as file:
            json.dump(coefficients, file, indent=4)
        st.success("Coefficient supprimé avec succès !")
    else:
        st.error("Index de coefficient invalide.")

# Fonction pour calculer la moyenne totale des notes avec coefficients
def calculate_weighted_average():
    st.subheader("Calculer la moyenne totale des notes avec coefficients 📈")
    grades = load_grades()
    coefficients = load_coefficients()

    if not grades or not coefficients:
        st.warning("Veuillez ajouter des notes et des coefficients avant de calculer la moyenne.")
        return

    total_weighted_sum = 0
    total_weight = 0

    for grade in grades:
        matiere = grade["Matière"]
        note = grade["Note"]
        coefficient = next((c["Coefficient"] for c in coefficients if c["Matière"] == matiere), 1)
        total_weighted_sum += note * coefficient
        total_weight += coefficient

    if total_weight > 0:
        weighted_average = total_weighted_sum / total_weight
        st.success(f"La moyenne totale pondérée est : {weighted_average:.2f}")
    else:
        st.warning("Les coefficients totaux sont égaux à zéro. Veuillez vérifier les coefficients.")

# Fonction pour démarrer le minuteur Pomodoro
def start_pomodoro_timer(work_duration, break_duration):
    work_duration_seconds = work_duration * 60
    break_duration_seconds = break_duration * 60

    st.session_state.pomodoro_state = "work"
    st.session_state.duration_seconds = work_duration_seconds
    st.session_state.elapsed_time = 0

    while st.session_state.pomodoro_state == "work" and st.session_state.elapsed_time < st.session_state.duration_seconds:
        time.sleep(1)
        st.session_state.elapsed_time += 1
        remaining_time = st.session_state.duration_seconds - st.session_state.elapsed_time
        st.write(f"Temps restant : {remaining_time // 60} minutes {remaining_time % 60} secondes")

    st.success("Temps de travail écoulé ! Prenez une pause.")
    pygame.mixer.music.load("notification_sound.mp3")  # Assurez-vous d'avoir un fichier sonore
    pygame.mixer.music.play()

    st.session_state.pomodoro_state = "break"
    st.session_state.duration_seconds = break_duration_seconds
    st.session_state.elapsed_time = 0

    while st.session_state.pomodoro_state == "break" and st.session_state.elapsed_time < st.session_state.duration_seconds:
        time.sleep(1)
        st.session_state.elapsed_time += 1
        remaining_time = st.session_state.duration_seconds - st.session_state.elapsed_time
        st.write(f"Temps restant : {remaining_time // 60} minutes {remaining_time % 60} secondes")

    st.success("Pause terminée ! Reprenez le travail.")
    pygame.mixer.music.load("notification_sound.mp3")
    pygame.mixer.music.play()

# Fonction pour mettre en pause le minuteur Pomodoro
def pause_pomodoro_timer():
    if st.session_state.pomodoro_state in ["work", "break"]:
        st.session_state.pomodoro_state = "paused"
        remaining_time = st.session_state.duration_seconds - st.session_state.elapsed_time
        st.write(f"Temps restant : {remaining_time // 60} minutes {remaining_time % 60} secondes")

# Fonction pour arrêter le son
def stop_sound():
    pygame.mixer.music.stop()

# Fonction pour enregistrer le temps passé sur une activité
def log_time_spent(activity, start_time, end_time):
    # Convertir les heures en objets datetime
    start_time = datetime.strptime(start_time, "%H:%M:%S")
    end_time = datetime.strptime(end_time, "%H:%M:%S")

    # Calculer la durée
    duration = end_time - start_time

    # Enregistrer dans un fichier JSON
    time_data = {
        "Activity": activity,
        "Start Time": start_time.strftime("%H:%M:%S"),
        "End Time": end_time.strftime("%H:%M:%S"),
        "Duration": str(duration)
    }

    try:
        with open("time_log.json", "r") as file:
            time_logs = json.load(file)
    except FileNotFoundError:
        time_logs = []

    time_logs.append(time_data)

    with open("time_log.json", "w") as file:
        json.dump(time_logs, file, indent=4)

    st.success("Temps passé enregistré avec succès !")

# Fonction pour afficher le temps passé sur les activités
def view_time_log():
    st.subheader("Temps passé sur les activités 📈")
    try:
        with open("time_log.json", "r") as file:
            time_logs = json.load(file)
    except FileNotFoundError:
        time_logs = []

    if time_logs:
        df = pd.DataFrame(time_logs)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucune activité enregistrée pour le moment.")

# Fonction pour convertir les heures en minutes
def convert_hours_to_minutes(hours):
    return hours * 60

# Fonction pour supprimer les activités d'une date spécifique
def delete_activities_by_date(date):
    global emploi_du_temps
    emploi_du_temps = emploi_du_temps[emploi_du_temps["Date"] != date]
    save_to_csv(emploi_du_temps)
    st.success(f"Les activités du {date} ont été supprimées avec succès !")

# Fonction pour générer un diagramme circulaire de l'emploi du temps
def generate_pie_chart(selected_date):
    # Connexion à la base de données
    conn = sqlite3.connect("emploi_du_temps.db")
    cursor = conn.cursor()

    # Chargement des activités depuis la base
    df = pd.read_sql_query("SELECT * FROM activites", conn)
    conn.close()

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")  # Formatage des dates

        filtered_data = df[df["date"] == selected_date.strftime("%Y-%m-%d")]
        if not filtered_data.empty:
            matiere_counts = filtered_data["nom"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(matiere_counts, labels=matiere_counts.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')  # Assure que le diagramme est un cercle.
            st.pyplot(fig)
        else:
            st.info(f"Aucune donnée disponible pour la date {selected_date}.")
    else:
        st.info("Aucune donnée disponible pour générer le diagramme circulaire.")

# Fonction pour ajouter un examen
def add_exam():
    st.subheader("Ajouter un examen 📚")
    exam_name = st.text_input("Nom de l'examen", key="add_exam_name")
    exam_date = st.date_input("Date de l'examen", key="add_exam_date")
    exam_time = st.time_input("Heure de l'examen", key="add_exam_time")

    if st.button("Ajouter l'examen", key="add_examen_button"):
        if exam_name and exam_date and exam_time:
            exam_data = {
                "Nom": exam_name,
                "Date": exam_date.strftime("%Y-%m-%d"),
                "Heure": exam_time.strftime("%H:%M:%S")
            }
            save_exam(exam_data)
            st.success("Examen ajouté avec succès !")

# Fonction pour sauvegarder les examens dans un fichier JSON
def save_exam(exam_data):
    try:
        with open("exams.json", "r") as file:
            exams = json.load(file)
    except FileNotFoundError:
        exams = []

    exams.append(exam_data)

    with open("exams.json", "w") as file:
        json.dump(exams, file, indent=4)

# Fonction pour charger les examens depuis un fichier JSON
def load_exams():
    try:
        with open("exams.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour afficher les examens sauvegardés
def view_exams():
    st.subheader("Examens sauvegardés 📚")
    exams = load_exams()
    for index, exam in enumerate(exams):
        st.write(f"**Nom:** {exam['Nom']}")
        st.write(f"**Date:** {exam['Date']}")
        st.write(f"**Heure:** {exam['Heure']}")
        if st.button(f"Supprimer l'examen {index + 1}", key=f"delete_exam_{index}"):
            delete_exam(index)
            st.rerun()
        st.write("---")

# Fonction pour supprimer un examen
def delete_exam(index):
    exams = load_exams()
    if 0 <= index < len(exams):
        del exams[index]
        with open("exams.json", "w") as file:
            json.dump(exams, file, indent=4)
        st.success("Examen supprimé avec succès !")
    else:
        st.error("Index d'examen invalide.")

# Fonction pour ajouter une tâche récurrente
def add_recurring_task():
    st.subheader("Ajouter une tâche récurrente 📅")
    task_name = st.text_input("Nom de la tâche", key="add_recurring_task_name")
    frequency = st.selectbox("Fréquence", ["Hebdomadaire", "Mensuelle"], key="add_recurring_task_frequency")

    if st.button("Ajouter la tâche récurrente", key="add_recurring_task_button"):
        if task_name and frequency:
            task_data = {
                "Nom": task_name,
                "Fréquence": frequency
            }
            save_recurring_task(task_data)
            st.success("Tâche récurrente ajoutée avec succès !")

# Fonction pour sauvegarder les tâches récurrentes dans un fichier JSON
def save_recurring_task(task_data):
    try:
        with open("recurring_tasks.json", "r") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []

    tasks.append(task_data)

    with open("recurring_tasks.json", "w") as file:
        json.dump(tasks, file, indent=4)

# Fonction pour charger les tâches récurrentes depuis un fichier JSON
def load_recurring_tasks():
    try:
        with open("recurring_tasks.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour afficher les tâches récurrentes sauvegardées
def view_recurring_tasks():
    st.subheader("Tâches récurrentes sauvegardées 📅")
    tasks = load_recurring_tasks()
    for index, task in enumerate(tasks):
        st.write(f"**Nom:** {task['Nom']}")
        st.write(f"**Fréquence:** {task['Fréquence']}")
        if st.button(f"Supprimer la tâche {index + 1}", key=f"delete_recurring_task_{index}"):
            delete_recurring_task(index)
            st.rerun()
        st.write("---")

# Fonction pour supprimer une tâche récurrente
def delete_recurring_task(index):
    tasks = load_recurring_tasks()
    if 0 <= index < len(tasks):
        del tasks[index]
        with open("recurring_tasks.json", "w") as file:
            json.dump(tasks, file, indent=4)
        st.success("Tâche récurrente supprimée avec succès !")
    else:
        st.error("Index de tâche invalide.")

# Fonction pour ajouter une ressource pédagogique
def add_educational_resource():
    st.subheader("Ajouter une ressource pédagogique 📚")
    resource_name = st.text_input("Nom de la ressource", key="add_resource_name")
    resource_type = st.selectbox("Type de ressource", ["Lien", "Vidéo", "Livre", "Article"], key="add_resource_type")
    resource_link = st.text_input("Lien de la ressource", key="add_resource_link")
    resource_description = st.text_area("Description de la ressource", key="add_resource_description")

    if st.button("Ajouter la ressource", key="add_resource_button"):
        if resource_name and resource_type and resource_link and resource_description:
            resource_data = {
                "Nom": resource_name,
                "Type": resource_type,
                "Lien": resource_link,
                "Description": resource_description
            }
            save_educational_resource(resource_data)
            st.success("Ressource pédagogique ajoutée avec succès !")
        else:
            st.error("Veuillez remplir tous les champs.")

# Fonction pour sauvegarder les ressources pédagogiques dans un fichier JSON
def save_educational_resource(resource_data):
    try:
        with open("educational_resources.json", "r") as file:
            resources = json.load(file)
    except FileNotFoundError:
        resources = []

    resources.append(resource_data)

    with open("educational_resources.json", "w") as file:
        json.dump(resources, file, indent=4)

# Fonction pour charger les ressources pédagogiques depuis un fichier JSON
def load_educational_resources():
    try:
        with open("educational_resources.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour afficher les ressources pédagogiques sauvegardées
def view_educational_resources():
    st.subheader("Ressources pédagogiques sauvegardées 📚")
    resources = load_educational_resources()
    for index, resource in enumerate(resources):
        st.write(f"**Nom:** {resource['Nom']}")
        st.write(f"**Type:** {resource['Type']}")
        st.write(f"**Lien:** {resource['Lien']}")
        st.write(f"**Description:** {resource['Description']}")
        if st.button(f"Supprimer la ressource {index + 1}", key=f"delete_resource_{index}"):
            delete_educational_resource(index)
            st.rerun()
        st.write("---")

# Fonction pour supprimer une ressource pédagogique
def delete_educational_resource(index):
    resources = load_educational_resources()
    if 0 <= index < len(resources):
        del resources[index]
        with open("educational_resources.json", "w") as file:
            json.dump(resources, file, indent=4)
        st.success("Ressource pédagogique supprimée avec succès !")
    else:
        st.error("Index de ressource invalide.")

# Fonction pour gérer les finances personnelles
def manage_personal_finances():
    st.subheader("Gestion des Finances Personnelles 💸")

    # Ajouter une transaction
    st.subheader("Ajouter une transaction 💸")
    transaction_type = st.selectbox("Type de transaction", ["Revenu", "Dépense"], key="add_transaction_type")
    amount = st.number_input("Montant", min_value=0.0, step=0.01, key="add_transaction_amount")
    category = st.text_input("Catégorie", key="add_transaction_category")
    date = st.date_input("Date de la transaction", key="add_transaction_date")

    if st.button("Ajouter la transaction", key="add_transaction_button"):
        if transaction_type and amount and category and date:
            transaction_data = {
                "Type": transaction_type,
                "Montant": amount,
                "Catégorie": category,
                "Date": date.strftime("%Y-%m-%d")
            }
            save_transaction(transaction_data)
            st.success("Transaction ajoutée avec succès !")

    # Afficher les transactions sauvegardées
    st.subheader("Transactions sauvegardées 💸")
    transactions = load_transactions()
    for index, transaction in enumerate(transactions):
        st.write(f"**Type:** {transaction['Type']}")
        st.write(f"**Montant:** {transaction['Montant']}")
        st.write(f"**Catégorie:** {transaction['Catégorie']}")
        st.write(f"**Date:** {transaction['Date']}")
        if st.button(f"Supprimer la transaction {index + 1}", key=f"delete_transaction_{index}"):
            delete_transaction(index)
            st.rerun()
        st.write("---")

    # Afficher le rapport financier
    st.subheader("Rapport Financier 📈")
    generate_financial_report(transactions)

# Fonction pour sauvegarder les transactions dans un fichier JSON
def save_transaction(transaction_data):
    try:
        with open("transactions.json", "r") as file:
            transactions = json.load(file)
    except FileNotFoundError:
        transactions = []

    transactions.append(transaction_data)

    with open("transactions.json", "w") as file:
        json.dump(transactions, file, indent=4)

# Fonction pour charger les transactions depuis un fichier JSON
def load_transactions():
    try:
        with open("transactions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une transaction
def delete_transaction(index):
    transactions = load_transactions()
    if 0 <= index < len(transactions):
        del transactions[index]
        with open("transactions.json", "w") as file:
            json.dump(transactions, file, indent=4)
        st.success("Transaction supprimée avec succès !")
    else:
        st.error("Index de transaction invalide.")

# Fonction pour générer un rapport financier
def generate_financial_report(transactions):
    if transactions:
        df = pd.DataFrame(transactions)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Mois"] = df["Date"].dt.to_period("M")
        report = df.groupby(["Mois", "Type"])["Montant"].sum().unstack().fillna(0)
        report["Solde"] = report["Revenu"] - report["Dépense"]
        st.dataframe(report, use_container_width=True)
    else:
        st.info("Aucune transaction enregistrée pour le moment.")

# Fonction pour suivre la santé
def track_health():
    st.subheader("Suivi de la Santé 🏋️‍♂️")

    # Ajouter une entrée de santé
    st.subheader("Ajouter une entrée de santé 🏋️‍♂️")
    activity_type = st.selectbox("Type d'activité", ["Exercice", "Sommeil", "Alimentation"], key="add_health_type")
    duration = st.number_input("Durée (en minutes)", min_value=0, step=1, key="add_health_duration")
    notes = st.text_area("Notes", key="add_health_notes")
    date = st.date_input("Date de l'activité", key="add_health_date")

    if st.button("Ajouter l'entrée de santé", key="add_health_button"):
        if activity_type and duration and date:
            health_data = {
                "Type": activity_type,
                "Durée": duration,
                "Notes": notes,
                "Date": date.strftime("%Y-%m-%d")
            }
            save_health_entry(health_data)
            st.success("Entrée de santé ajoutée avec succès !")

    # Afficher les entrées de santé sauvegardées
    st.subheader("Entrées de Santé sauvegardées 🏋️‍♂️")
    health_entries = load_health_entries()
    for index, entry in enumerate(health_entries):
        st.write(f"**Type:** {entry['Type']}")
        st.write(f"**Durée:** {entry['Durée']} minutes")
        st.write(f"**Notes:** {entry['Notes']}")
        st.write(f"**Date:** {entry['Date']}")
        if st.button(f"Supprimer l'entrée {index + 1}", key=f"delete_health_{index}"):
            delete_health_entry(index)
            st.rerun()
        st.write("---")

    # Afficher le rapport de santé
    st.subheader("Rapport de Santé 📈")
    generate_health_report(health_entries)

# Fonction pour sauvegarder les entrées de santé dans un fichier JSON
def save_health_entry(health_data):
    try:
        with open("health_entries.json", "r") as file:
            health_entries = json.load(file)
    except FileNotFoundError:
        health_entries = []

    health_entries.append(health_data)

    with open("health_entries.json", "w") as file:
        json.dump(health_entries, file, indent=4)

# Fonction pour charger les entrées de santé depuis un fichier JSON
def load_health_entries():
    try:
        with open("health_entries.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une entrée de santé
def delete_health_entry(index):
    health_entries = load_health_entries()
    if 0 <= index < len(health_entries):
        del health_entries[index]
        with open("health_entries.json", "w") as file:
            json.dump(health_entries, file, indent=4)
        st.success("Entrée de santé supprimée avec succès !")
    else:
        st.error("Index d'entrée de santé invalide.")

# Fonction pour générer un rapport de santé
def generate_health_report(health_entries):
    if health_entries:
        df = pd.DataFrame(health_entries)
        df["Date"] = pd.to_datetime(df["Date"])
        df["Mois"] = df["Date"].dt.to_period("M")
        report = df.groupby(["Mois", "Type"])["Durée"].sum().unstack().fillna(0)
        st.dataframe(report, use_container_width=True)
    else:
        st.info("Aucune entrée de santé enregistrée pour le moment.")

# Fonction pour gérer les contacts
def manage_contacts():
    st.subheader("Gestion des Contacts 📞")

    # Ajouter un contact
    st.subheader("Ajouter un contact 📞")
    name = st.text_input("Nom", key="add_contact_name")
    email = st.text_input("Email", key="add_contact_email")
    phone = st.text_input("Téléphone", key="add_contact_phone")
    notes = st.text_area("Notes", key="add_contact_notes")

    if st.button("Ajouter le contact", key="add_contact_button"):
        if name and email and phone:
            contact_data = {
                "Nom": name,
                "Email": email,
                "Téléphone": phone,
                "Notes": notes
            }
            save_contact(contact_data)
            st.success("Contact ajouté avec succès !")

    # Afficher les contacts sauvegardés
    st.subheader("Contacts sauvegardés 📞")
    contacts = load_contacts()
    for index, contact in enumerate(contacts):
        st.write(f"**Nom:** {contact['Nom']}")
        st.write(f"**Email:** {contact['Email']}")
        st.write(f"**Téléphone:** {contact['Téléphone']}")
        st.write(f"**Notes:** {contact['Notes']}")
        if st.button(f"Supprimer le contact {index + 1}", key=f"delete_contact_{index}"):
            delete_contact(index)
            st.rerun()
        st.write("---")

# Fonction pour sauvegarder les contacts dans un fichier JSON
def save_contact(contact_data):
    try:
        with open("contacts.json", "r") as file:
            contacts = json.load(file)
    except FileNotFoundError:
        contacts = []

    contacts.append(contact_data)

    with open("contacts.json", "w") as file:
        json.dump(contacts, file, indent=4)

# Fonction pour charger les contacts depuis un fichier JSON
def load_contacts():
    try:
        with open("contacts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer un contact
def delete_contact(index):
    contacts = load_contacts()
    if 0 <= index < len(contacts):
        del contacts[index]
        with open("contacts.json", "w") as file:
            json.dump(contacts, file, indent=4)
        st.success("Contact supprimé avec succès !")
    else:
        st.error("Index de contact invalide.")

# Fonction pour définir des objectifs à long terme
def set_long_term_goals():
    st.subheader("Définir des Objectifs à Long Terme 🎯")

    # Ajouter un objectif à long terme
    st.subheader("Ajouter un objectif à long terme 🎯")
    goal_name = st.text_input("Nom de l'objectif", key="add_long_term_goal_name")
    goal_description = st.text_area("Description de l'objectif", key="add_long_term_goal_description")
    goal_deadline = st.date_input("Date limite", key="add_long_term_goal_deadline")

    if st.button("Ajouter l'objectif", key="add_long_term_goal_button"):
        if goal_name and goal_description and goal_deadline:
            goal_data = {
                "Nom": goal_name,
                "Description": goal_description,
                "Date limite": goal_deadline.strftime("%Y-%m-%d")
            }
            save_long_term_goal(goal_data)
            st.success("Objectif à long terme ajouté avec succès !")

    # Afficher les objectifs à long terme sauvegardés
    st.subheader("Objectifs à Long Terme sauvegardés 🎯")
    long_term_goals = load_long_term_goals()
    for index, goal in enumerate(long_term_goals):
        st.write(f"**Nom:** {goal['Nom']}")
        st.write(f"**Description:** {goal['Description']}")
        st.write(f"**Date limite:** {goal['Date limite']}")
        if st.button(f"Supprimer l'objectif {index + 1}", key=f"delete_long_term_goal_{index}"):
            delete_long_term_goal(index)
            st.rerun()
        st.write("---")

# Fonction pour sauvegarder les objectifs à long terme dans un fichier JSON
def save_long_term_goal(goal_data):
    try:
        with open("long_term_goals.json", "r") as file:
            long_term_goals = json.load(file)
    except FileNotFoundError:
        long_term_goals = []

    long_term_goals.append(goal_data)

    with open("long_term_goals.json", "w") as file:
        json.dump(long_term_goals, file, indent=4)

# Fonction pour charger les objectifs à long terme depuis un fichier JSON
def load_long_term_goals():
    try:
        with open("long_term_goals.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer un objectif à long terme
def delete_long_term_goal(index):
    long_term_goals = load_long_term_goals()
    if 0 <= index < len(long_term_goals):
        del long_term_goals[index]
        with open("long_term_goals.json", "w") as file:
            json.dump(long_term_goals, file, indent=4)
        st.success("Objectif à long terme supprimé avec succès !")
    else:
        st.error("Index d'objectif à long terme invalide.")

# Fonction pour suivre les compétences
def track_skills():
    st.subheader("Suivi des Compétences 📚")

    # Ajouter une compétence
    st.subheader("Ajouter une compétence 📚")
    skill_name = st.text_input("Nom de la compétence", key="add_skill_name")
    skill_level = st.selectbox("Niveau de compétence", ["Débutant", "Intermédiaire", "Avancé"], key="add_skill_level")
    skill_description = st.text_area("Description de la compétence", key="add_skill_description")

    if st.button("Ajouter la compétence", key="add_skill_button"):
        if skill_name and skill_level and skill_description:
            skill_data = {
                "Nom": skill_name,
                "Niveau": skill_level,
                "Description": skill_description
            }
            save_skill(skill_data)
            st.success("Compétence ajoutée avec succès !")

    # Afficher les compétences sauvegardées
    st.subheader("Compétences sauvegardées 📚")
    skills = load_skills()
    for index, skill in enumerate(skills):
        st.write(f"**Nom:** {skill['Nom']}")
        st.write(f"**Niveau:** {skill['Niveau']}")
        st.write(f"**Description:** {skill['Description']}")
        if st.button(f"Supprimer la compétence {index + 1}", key=f"delete_skill_{index}"):
            delete_skill(index)
            st.rerun()
        st.write("---")

# Fonction pour sauvegarder les compétences dans un fichier JSON
def save_skill(skill_data):
    try:
        with open("skills.json", "r") as file:
            skills = json.load(file)
    except FileNotFoundError:
        skills = []

    skills.append(skill_data)

    with open("skills.json", "w") as file:
        json.dump(skills, file, indent=4)

# Fonction pour charger les compétences depuis un fichier JSON
def load_skills():
    try:
        with open("skills.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une compétence
def delete_skill(index):
    skills = load_skills()
    if 0 <= index < len(skills):
        del skills[index]
        with open("skills.json", "w") as file:
            json.dump(skills, file, indent=4)
        st.success("Compétence supprimée avec succès !")
    else:
        st.error("Index de compétence invalide.")

# Fonction pour suivre les lectures
def track_reading():
    st.subheader("Suivi des Lectures 📚")

    # Ajouter une lecture
    st.subheader("Ajouter une lecture 📚")
    book_title = st.text_input("Titre du livre", key="add_reading_title")
    author = st.text_input("Auteur", key="add_reading_author")
    genre = st.text_input("Genre", key="add_reading_genre")
    start_date = st.date_input("Date de début", key="add_reading_start_date")
    end_date = st.date_input("Date de fin", key="add_reading_end_date")
    rating = st.number_input("Note (sur 5)", min_value=0, max_value=5, step=1, key="add_reading_rating")
    review = st.text_area("Avis", key="add_reading_review")

    if st.button("Ajouter la lecture", key="add_reading_button"):
        if book_title and author and genre and start_date and end_date and rating:
            reading_data = {
                "Titre": book_title,
                "Auteur": author,
                "Genre": genre,
                "Date de début": start_date.strftime("%Y-%m-%d"),
                "Date de fin": end_date.strftime("%Y-%m-%d"),
                "Note": rating,
                "Avis": review
            }
            save_reading(reading_data)
            st.success("Lecture ajoutée avec succès !")

    # Afficher les lectures sauvegardées
    st.subheader("Lectures sauvegardées 📚")
    readings = load_readings()
    for index, reading in enumerate(readings):
        st.write(f"**Titre:** {reading['Titre']}")
        st.write(f"**Auteur:** {reading['Auteur']}")
        st.write(f"**Genre:** {reading['Genre']}")
        st.write(f"**Date de début:** {reading['Date de début']}")
        st.write(f"**Date de fin:** {reading['Date de fin']}")
        st.write(f"**Note:** {reading['Note']}")
        st.write(f"**Avis:** {reading['Avis']}")
        if st.button(f"Supprimer la lecture {index + 1}", key=f"delete_reading_{index}"):
            delete_reading(index)
            st.rerun()
        st.write("---")

# Fonction pour sauvegarder les lectures dans un fichier JSON
def save_reading(reading_data):
    try:
        with open("readings.json", "r") as file:
            readings = json.load(file)
    except FileNotFoundError:
        readings = []

    readings.append(reading_data)

    with open("readings.json", "w") as file:
        json.dump(readings, file, indent=4)

# Fonction pour charger les lectures depuis un fichier JSON
def load_readings():
    try:
        with open("readings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une lecture
def delete_reading(index):
    readings = load_readings()
    if 0 <= index < len(readings):
        del readings[index]
        with open("readings.json", "w") as file:
            json.dump(readings, file, indent=4)
        st.success("Lecture supprimée avec succès !")
    else:
        st.error("Index de lecture invalide.")

# Fonction pour intégrer des applications de méditation
def integrate_meditation_apps():
    st.subheader("Intégration avec les Applications de Méditation 🧘")

    # Ajouter une session de méditation
    st.subheader("Ajouter une session de méditation 🧘")
    meditation_type = st.selectbox("Type de méditation", ["Mindfulness", "Respiration", "Corps Scan"], key="add_meditation_type")
    duration = st.number_input("Durée (en minutes)", min_value=0, step=1, key="add_meditation_duration")
    notes = st.text_area("Notes", key="add_meditation_notes")
    date = st.date_input("Date de la session", key="add_meditation_date")

    if st.button("Ajouter la session", key="add_meditation_button"):
        if meditation_type and duration and date:
            meditation_data = {
                "Type": meditation_type,
                "Durée": duration,
                "Notes": notes,
                "Date": date.strftime("%Y-%m-%d")
            }
            save_meditation_session(meditation_data)
            st.success("Session de méditation ajoutée avec succès !")

    # Afficher les sessions de méditation sauvegardées
    st.subheader("Sessions de Méditation sauvegardées 🧘")
    meditation_sessions = load_meditation_sessions()
    for index, session in enumerate(meditation_sessions):
        st.write(f"**Type:** {session['Type']}")
        st.write(f"**Durée:** {session['Durée']} minutes")
        st.write(f"**Notes:** {session['Notes']}")
        st.write(f"**Date:** {session['Date']}")
        if st.button(f"Supprimer la session {index + 1}", key=f"delete_meditation_{index}"):
            delete_meditation_session(index)
            st.rerun()
        st.write("---")

# Fonction pour sauvegarder les sessions de méditation dans un fichier JSON
def save_meditation_session(meditation_data):
    try:
        with open("meditation_sessions.json", "r") as file:
            meditation_sessions = json.load(file)
    except FileNotFoundError:
        meditation_sessions = []

    meditation_sessions.append(meditation_data)

    with open("meditation_sessions.json", "w") as file:
        json.dump(meditation_sessions, file, indent=4)

# Fonction pour charger les sessions de méditation depuis un fichier JSON
def load_meditation_sessions():
    try:
        with open("meditation_sessions.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer une session de méditation
def delete_meditation_session(index):
    meditation_sessions = load_meditation_sessions()
    if 0 <= index < len(meditation_sessions):
        del meditation_sessions[index]
        with open("meditation_sessions.json", "w") as file:
            json.dump(meditation_sessions, file, indent=4)
        st.success("Session de méditation supprimée avec succès !")
    else:
        st.error("Index de session de méditation invalide.")

# Fonction pour suivre les progrès en langues
def track_language_progress():
    st.subheader("Suivi des Progrès en Langues 🌐")

    # Ajouter un progrès en langue
    st.subheader("Ajouter un progrès en langue 🌐")
    language = st.text_input("Langue", key="add_language_progress_language")
    level = st.selectbox("Niveau", ["Débutant", "Intermédiaire", "Avancé"], key="add_language_progress_level")
    progress_notes = st.text_area("Notes de progrès", key="add_language_progress_notes")
    date = st.date_input("Date du progrès", key="add_language_progress_date")

    if st.button("Ajouter le progrès", key="add_language_progress_button"):
        if language and level and date:
            progress_data = {
                "Langue": language,
                "Niveau": level,
                "Notes": progress_notes,
                "Date": date.strftime("%Y-%m-%d")
            }
            save_language_progress(progress_data)
            st.success("Progrès en langue ajouté avec succès !")

    # Afficher les progrès en langues sauvegardés
    st.subheader("Progrès en Langues sauvegardés 🌐")
    language_progress = load_language_progress()
    for index, progress in enumerate(language_progress):
        st.write(f"**Langue:** {progress['Langue']}")
        st.write(f"**Niveau:** {progress['Niveau']}")
        st.write(f"**Notes:** {progress['Notes']}")
        st.write(f"**Date:** {progress['Date']}")
        if st.button(f"Supprimer le progrès {index + 1}", key=f"delete_language_progress_{index}"):
            delete_language_progress(index)
            st.rerun()
        st.write("---")

# Fonction pour sauvegarder les progrès en langues dans un fichier JSON
def save_language_progress(progress_data):
    try:
        with open("language_progress.json", "r") as file:
            language_progress = json.load(file)
    except FileNotFoundError:
        language_progress = []

    language_progress.append(progress_data)

    with open("language_progress.json", "w") as file:
        json.dump(language_progress, file, indent=4)

# Fonction pour charger les progrès en langues depuis un fichier JSON
def load_language_progress():
    try:
        with open("language_progress.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Fonction pour supprimer un progrès en langue
def delete_language_progress(index):
    language_progress = load_language_progress()
    if 0 <= index < len(language_progress):
        del language_progress[index]
        with open("language_progress.json", "w") as file:
            json.dump(language_progress, file, indent=4)
        st.success("Progrès en langue supprimé avec succès !")
    else:
        st.error("Index de progrès en langue invalide.")

# Interface utilisateur
st.title("🌸📚 Gestionnaire d’Emploi du Temps et d’Activités ⏰🌸")

# Charger les préférences utilisateur
preferences = load_preferences()
change_theme(preferences["theme"])
#logo
st.logo("Sans titre.jpg")

# Afficher le cercle décoratif avec des emojis
st.markdown(
    """
    <div class="circle">
        <span class="emoji emoji-1">✨</span>
        <span class="emoji emoji-2">🌟</span>
        <span class="emoji emoji-3">💫</span>
        <span class="emoji emoji-4">🌠</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Menu de navigation avec des boutons verticaux
selected_choice = st.sidebar.radio("Menu", [
    "🏠 Accueil",
    "📅 Gestion du Temps",
    "🏋️‍♂️ Suivi Personnel",
    "🛠️ Outils Académiques",
    "🛠️ Outils de Productivité",
    "🛠️ Outils Personnels"
], index=0)

if selected_choice == "🏠 Accueil":
    st.markdown("""
    <div class='home-section'>
        <h2 class='blue-title'>📚 Gestionnaire d’Emploi du Temps et d’Activités ⏰🌸</h2>
        <p class='brown-text'>🌸 Bienvenue dans votre outil de gestion d’emploi du temps ! 🌸</p>
        <p class='brown-text'>
            Organisez facilement vos cours, tâches, projets et examens. Suivez vos activités et optimisez votre productivité en un clic !
        </p>
        <a href="#" class="cta-button">
            🚀 <span class="cta-icon">➡️</span> Commencer
        </a>
    </div>
    """, unsafe_allow_html=True)

elif selected_choice == "📅 Gestion du Temps":
    st.subheader("📅 Gestion du Temps 🌸")
    st.write("Ajoutez, modifiez et supprimez vos activités quotidiennes ici.")

    # Connexion à la base de données
    conn = sqlite3.connect("emploi_du_temps.db")
    cursor = conn.cursor()

    # Création de la table si elle n'existe pas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            date TEXT NOT NULL,
            duree INTEGER NOT NULL
        )
    """)
    conn.commit()

    # Ajouter une nouvelle activité
    st.subheader("Ajouter une nouvelle activité 📅")
    with st.form(key="add_activity_form"):
        date = st.date_input("Date", key="add_activity_date")
        matiere = st.selectbox("Matière", emploi_du_temps["Matière"].unique(), key="add_activity_matiere")
        duree = st.number_input("Durée (en heures)", min_value=0.0, step=0.1, key="add_activity_duree")
        priorite = st.selectbox("Priorité", ["Faible", "Moyenne", "Élevée"], key="add_activity_priorite")
        submitted = st.form_submit_button("Ajouter l'activité")

        if submitted:
            if date and matiere and duree and priorite:
                # Convertir la durée en minutes
                duree_minutes = convert_hours_to_minutes(duree)
                new_activity = pd.DataFrame({
                    "Date": [date],
                    "Matière": [matiere],
                    "Durée": [duree_minutes],  # Utiliser la durée en minutes
                    "Priorité": [priorite]
                })
                emploi_du_temps = pd.concat([emploi_du_temps, new_activity], ignore_index=True)
                save_to_csv(emploi_du_temps)
                st.success("Activité ajoutée avec succès !")

                # Enregistrer dans la base de données
                cursor.execute("""
                    INSERT INTO activites (nom, date, duree) VALUES (?, ?, ?)
                """, (matiere, date.strftime("%Y-%m-%d"), duree_minutes))
                conn.commit()
            else:
                st.error("Veuillez remplir tous les champs.")

    # Chargement des activités depuis la base
    st.subheader("Activités existantes 📅")
    df = pd.read_sql_query("SELECT * FROM activites", conn)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")  # Formatage des dates
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucune activité enregistrée pour le moment.")

    conn.close()

    # Ajouter un bouton pour supprimer les activités d'une journée spécifique
    st.subheader("Supprimer les activités d'une journée spécifique")
    delete_date = st.date_input("Sélectionnez la date pour supprimer les activités", value=datetime.now().date())
    if st.button("Supprimer les activités"):
        delete_activities_by_date(delete_date)

    # Ajouter le diagramme circulaire
    st.subheader("Diagramme circulaire de l'emploi du temps")
    selected_date = st.date_input("Sélectionnez la date pour le diagramme circulaire", value=datetime.now().date())
    generate_pie_chart(selected_date)

elif selected_choice == "🏋️‍♂️ Suivi Personnel":
    st.subheader("🏋️‍♂️ Suivi Personnel 🌸")
    st.write("Suivez vos progrès personnels et améliorez vos compétences.")

    # Sous-menu pour le suivi personnel
    personal_choice = st.sidebar.radio("Suivi Personnel", [
        "🎯 Objectifs",
        "📚 Suivi des Compétences",
        "📚 Suivi des Lectures",
        "🌐 Suivi des Progrès en Langues",
        "🏋️‍♂️ Suivi de la Santé",
        "📞 Gestion des Contacts",
        "🎯 Objectifs à Long Terme"
    ], index=0)

    if personal_choice == "🎯 Objectifs":
        set_goals()
        view_goals()

    elif personal_choice == "📚 Suivi des Compétences":
        track_skills()

    elif personal_choice == "📚 Suivi des Lectures":
        track_reading()

    elif personal_choice == "🌐 Suivi des Progrès en Langues":
        track_language_progress()

    elif personal_choice == "🏋️‍♂️ Suivi de la Santé":
        track_health()

    elif personal_choice == "📞 Gestion des Contacts":
        manage_contacts()

    elif personal_choice == "🎯 Objectifs à Long Terme":
        set_long_term_goals()

elif selected_choice == "🛠️ Outils Académiques":
    st.subheader("🛠️ Outils Académiques 🌸")

    # Sous-menu pour les outils académiques
    academic_tools_choice = st.sidebar.radio("Outils Académiques", [
        "📚 Cours",
        "📋 Tâches",
        "📈 Notes et Coefficients",
        "📚 Examens",
        "📅 Tâches Récurrentes",
        "📚 Ressources Pédagogiques"
    ], index=0)

    if academic_tools_choice == "📚 Cours":
        add_course()
        view_courses()

    elif academic_tools_choice == "📋 Tâches":
        add_task()
        view_tasks()

    elif academic_tools_choice == "📈 Notes et Coefficients":
        manage_grades_and_coefficients()

    elif academic_tools_choice == "📚 Examens":
        add_exam()
        view_exams()

    elif academic_tools_choice == "📅 Tâches Récurrentes":
        add_recurring_task()
        view_recurring_tasks()

    elif academic_tools_choice == "📚 Ressources Pédagogiques":
        add_educational_resource()
        view_educational_resources()

elif selected_choice == "🛠️ Outils de Productivité":
    st.subheader("🛠️ Outils de Productivité 🌸")

    # Sous-menu pour les outils de productivité
    productivity_tools_choice = st.sidebar.radio("Outils de Productivité", [
        "📈 Rapports",
        "📝 Évaluation",
        "🌸 Préférences",
        "📈 Temps Passé",
        "🕒 Minuteur Pomodoro"
    ], index=0)

    if productivity_tools_choice == "📈 Rapports":
        st.subheader("📈 Rapports 🌸")
        period = st.selectbox("Période", ["Hebdomadaire", "Mensuelle"], key="report_period")
        if st.button("Générer le rapport", key="generate_report_button"):
            report = generate_report(emploi_du_temps, period.lower())
            if not report.empty:
                st.dataframe(report, use_container_width=True)
            else:
                st.info("Aucune donnée disponible pour cette période.")

        st.subheader("Rapport de progression 📈")
        progress_report = generate_progress_report(emploi_du_temps, load_goals())
        if not progress_report.empty:
            st.dataframe(progress_report, use_container_width=True)
        else:
            st.info("Aucune donnée disponible pour le rapport de progression.")

    elif productivity_tools_choice == "📝 Évaluation":
        evaluate_time_management()

    elif productivity_tools_choice == "🌸 Préférences":
        st.subheader("🌸 Préférences 🌸")
        theme = st.selectbox("Thème", ["Clair", "Sombre"], key="preferences_theme")
        if st.button("Enregistrer les préférences", key="save_preferences_button"):
            save_preferences(theme)
            change_theme(theme)
            st.success("Préférences enregistrées avec succès !")

    elif productivity_tools_choice == "📈 Temps Passé":
        st.subheader("📈 Temps Passé sur les Activités 🌸")
        activity = st.text_input("Nom de l'activité")
        start_time = st.time_input("Heure de début")
        end_time = st.time_input("Heure de fin")
        if st.button("Enregistrer le temps passé"):
            log_time_spent(activity, start_time.strftime("%H:%M:%S"), end_time.strftime("%H:%M:%S"))
        view_time_log()

    elif productivity_tools_choice == "🕒 Minuteur Pomodoro":
        st.subheader("🕒 Minuteur Pomodoro 🌸")
        work_duration = st.number_input("Durée de travail (en minutes)", min_value=1, step=1, key="pomodoro_work_duration")
        break_duration = st.number_input("Durée de pause (en minutes)", min_value=1, step=1, key="pomodoro_break_duration")
        if st.button("Démarrer le minuteur Pomodoro", key="start_pomodoro_timer_button"):
            start_pomodoro_timer(work_duration, break_duration)

        if st.button("Mettre en pause le minuteur Pomodoro", key="pause_pomodoro_timer_button"):
            pause_pomodoro_timer()

        if st.button("Arrêter le son", key="stop_sound_button"):
            stop_sound()

elif selected_choice == "🛠️ Outils Personnels":
    st.subheader("🛠️ Outils Personnels 🌸")

    # Sous-menu pour les outils personnels
    personal_tools_choice = st.sidebar.radio("Outils Personnels", [
        "💸 Gestion des Finances Personnelles",
        "📸 Intégration avec les Réseaux Sociaux",
        "🧘 Applications de Méditation"
    ], index=0)

    if personal_tools_choice == "💸 Gestion des Finances Personnelles":
        manage_personal_finances()

    elif personal_tools_choice == "📸 Intégration avec les Réseaux Sociaux":
        integrate_with_social_media()

    elif personal_tools_choice == "🧘 Applications de Méditation":
        integrate_meditation_apps()
