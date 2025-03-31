import streamlit as st
from fpdf import FPDF
import base64
from datetime import datetime

st.markdown(
    """
    <style>
        [data-testid="stSidebar"] {
            width: 250px !important;  /* Adjust width as needed */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar inputs
st.sidebar.header("Paramètres d'entrée")
Vs = st.sidebar.number_input("Tension nominale du système", value=24)
Rb = st.sidebar.number_input("Capacité du système batterie (% des besoins)", value=100)
ts = st.sidebar.number_input("Période d'autonomie", value=5)
kage = st.sidebar.number_input("Facteur de vieillissement des batteries", value=0.91)
KT = st.sidebar.number_input("Facteur de correction de température", value=1.0)
Qd1 = st.sidebar.number_input("Charge moyenne journalière", value=1053.1)
n = st.sidebar.number_input("Rendement du régulateur de tension", value=92)
Kd1 = st.sidebar.number_input("Profondeur de décharge maximale autorisée", value=20)
Kd3 = st.sidebar.number_input("Profondeur de décharge maximale autorisée", value=80)
Tch = st.sidebar.number_input("Temps maximum pour recharge complète", value=28)
td = st.sidebar.number_input("Heures de lumière solaire par jour", value=8)
Qb = st.sidebar.number_input("Capacité de la batterie (Ah)", value=4440)
Conf_batterie= st.sidebar.number_input("Configuration batterie((NBR X CP ) X  SB ))")
nombre_element=st.sidebar.number_input("Nombre d'éléments",value=90)

# Initialize global variables
Qd = Qd1 / (n / 100)  # Calculate Qd immediately
Qbd = None
Qbd_prime = None
Qbs_prime = None
Qd1_prime = None
tsact = None
QdLn = None

def create_pdf(results1, results2, results3, results4, results5):
    pdf = FPDF()
    pdf.add_page()
    
    # Use Helvetica font (not Arial)
    pdf.set_font('Helvetica', '', 12)
    
    pdf.cell(200, 10, txt="Rapport de Calcul du Système de Batterie", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1, align='C')
    pdf.ln(10)
    
    # Section 1
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(200, 10, txt="1. Dimensionnement des batteries - Cycle journalier", ln=1)
    pdf.set_font('Helvetica', '', 12)
    for key, value in results1.items():
        pdf.cell(110, 8, txt=f"{key}:", ln=0)
        pdf.cell(90, 8, txt=f"{value[1]:.2f} {value[2]}" if isinstance(value[1], (int, float)) else f"{value[1]} {value[2]}", ln=1)
    pdf.ln(5)
    
    # Section 2
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(200, 10, txt="2. Dimensionnement des batteries - Cycle de décharge complète", ln=1)
    pdf.set_font('Helvetica', '', 12)
    for key, value in results2.items():
        pdf.cell(110, 8, txt=f"{key}:", ln=0)
        pdf.cell(90, 8, txt=f"{value[1]:.2f} {value[2]}" if isinstance(value[1], (int, float)) else f"{value[1]} {value[2]}", ln=1)
    pdf.ln(5)
    
    # Section 3
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(200, 10, txt="3. Utilisation de la batterie par rapport à sa capacité nominale", ln=1)
    pdf.set_font('Helvetica', '', 12)
    for key, value in results3.items():
        pdf.cell(110, 8, txt=f"{key}:", ln=0)
        pdf.cell(90, 8, txt=f"{value[1]:.2f} {value[2]}" if isinstance(value[1], (int, float)) else f"{value[1]} {value[2]}", ln=1)
    pdf.ln(5)
    
    # Section 4
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(200, 10, txt="4. Utilisation de la batterie après vieillissement", ln=1)
    pdf.set_font('Helvetica', '', 12)
    for key, value in results4.items():
        pdf.cell(100, 8, txt=f"{key}:", ln=0)
        pdf.cell(90, 8, txt=f"{value[1]:.2f} {value[2]}" if isinstance(value[1], (int, float)) else f"{value[1]} {value[2]}", ln=1)
    pdf.ln(5)
    
    # Section 5
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(200, 10, txt="5. Exigences de puissance solaire", ln=1)
    pdf.set_font('Helvetica', '', 12)
    for key, value in results5.items():
        pdf.cell(110, 8, txt=f"{key}:", ln=0)
        pdf.cell(90, 8, txt=f"{value[1]:.2f} {value[2]}" if isinstance(value[1], (int, float)) else f"{value[1]} {value[2]}", ln=1)
    
    return pdf.output(dest="S")

def cycle_journale():
    global Qbd, Qbd_prime
    Nombre_heur_alimentes_batterie = 24 - td 
    Qbd = (24 - td) / 24 * Rb / 100 * Qd
    Capacite_minimale_requise_de_la_batterie = Qbd / (Kd1/100) / kage / KT
    Qbd_prime = Capacite_minimale_requise_de_la_batterie
    
    return {
        "Heures de lumière solaire par jour": ("td", td, "heures"),
        "Heures d'alimentation par batterie": ("", Nombre_heur_alimentes_batterie, "heures"),
        "Décharge journalière des batteries":("Qbd",Qbd,""),
        "Profondeur de décharge maximale autorisée": ("Kd1", Kd1, "%"),
        "Capacité batterie nécessaire (cycle journalier)": ("", Capacite_minimale_requise_de_la_batterie, "Ah")
    }

def cycle_de_decharge_complete():
    global Qbs_prime,Qb_prime
    Qs = (Rb/100) * Qd
    Id = Qs / (24-td)
    Qbs_prime = Qs * ts
    Qbc = Qbs_prime / (Kd3/100) / kage / KT
    Qb_prime = max(Qbd, Qbc) if Qbd is not None and Qbc is not None else 0
    Autonomie_obtenue_pour_7j = (Qb/Qb_prime)*100 if Qb_prime != 0 else 0
    
    return {
        "Charge journalière totale demandée à la batterie": ("Qs", Qs, "Ah"),
        "Courant moyen de décharge batterie": ("Id", Id, "A"),
        "Charge totale demandée sur la période de décharge": ("Qbs'", Qbs_prime, "Ah"),
        "Profondeur de décharge maximale autorisée": ("Kd3", Kd3, "%"),
        "Capacité batterie pour décharge complète": ("Qbc", Qbc, "Ah"),
        "Capacité minimale requise": ("Qb'", Qb_prime, "Ah"),
    }

def Utilisation_de_la_bat_par_rapport_sa_cap_nominale():
    capacite_sys=  Qb /Qb_prime * 100
    Autonomie_reelle_atteint=(capacite_sys * ts )/ 100
    return {
        f"Capacité du système atteinte pour l'autonomie de {ts} j  " : ( "",capacite_sys,"%"),
        "Autonomie réelle atteinte": ("",Autonomie_reelle_atteint,"") 
    }

def Utilisation_de_la_bat_apres_vieillissement():
    global QdLn
    QdLn = Qd * (24-td) / 24 
    Qd1_prime = QdLn/(Qb * KT)*100
    tsact = Qb * KT / Qd
    Qd1act = Qd1_prime/kage if Qd1_prime is not None else 0
    tsact_prime = tsact * kage if tsact is not None else 0
    
    return {
        "Charge nocturne distribuée": ("QdLn", QdLn, "Ah"),
        "Profondeur de décharge nocturne réelle": ("Qd1'", Qd1_prime, "%"),
        "Autonomie réelle sans dégradation": ("tsact", tsact, "jours"),
        "Profondeur de décharge réelle avec vieillissement": ("Qdiact", Qd1act, "%"),
        "Autonomie réelle avec vieillissement": ("Isact'", tsact_prime, "jours")
    }

def Exigences_de_puissance_solaire():
    Qd_prime = td/24 * Qd 
    Qbloss = 0.07 * QdLn if QdLn is not None else 0
    Qbdisch = 0.001 * Qb
    Qd_2prime = Qd + Qbloss + Qbdisch
    Qbloss_prime = 7/100 * Qbs_prime if Qbs_prime is not None else 0
    Qchr = (Qbs_prime + Qbloss_prime)/Tch if Qbs_prime is not None else 0
    average_solar_req_24h = Qchr + Qd_2prime if Qchr is not None else 0
    Besoin_total_en_energie_solaire_par_jour =  Qchr + Qd_2prime
    Surcapacite_du_systeme= (Besoin_total_en_energie_solaire_par_jour / Qd1 )*100
    
    return {
        "Temps maximum pour recharge complète": ("Tch", Tch, "heures"),
        "Charge nocturne journalière": ("QdLn", QdLn if QdLn is not None else 0, "Ah"),
        "Charge journalière diurne": ("Qd'", Qd_prime, "Ah"),
        "Pertes d'inefficacité de recharge (7%)": ("Qbloss", Qbloss, "Ah"),
        "Autodécharge journalière batterie (0.1%)": ("Qbdisch", Qbdisch, "Ah"),
        "Besoin total énergétique du système": ("Qd''", Qd_2prime, "Ah"),
        "Capacité à recharger": ("Qbs'", Qbs_prime if Qbs_prime is not None else 0, "Ah"),
        "Pertes d'inefficacité de recharge totale": ("Qbloss'", Qbloss_prime, "Ah"),
        "Charge journalière pour recharge complète": ("Qchr", Qchr, "Ah"),
        "Besoins énergétiques totaux": ("", average_solar_req_24h, "Ah"),
        "Surcapacité du système ":("",Surcapacite_du_systeme,"%"),
    }

def display_section(title, results):
    st.subheader(title)
    data = {
        "Paramètre": list(results.keys()),
        "Symbole": [v[0] for v in results.values()],
        "Valeur": [f"{v[1]:.2f}" if isinstance(v[1], (int, float)) else str(v[1]) for v in results.values()],
        "Unité": [v[2] for v in results.values()]
    }
    st.table(data)

st.title("Calcul du Système de Batterie")

if st.button("Calculer"):
    # Calculate in the correct order
    results1 = cycle_journale()
    results2 = cycle_de_decharge_complete()
    results3 = Utilisation_de_la_bat_par_rapport_sa_cap_nominale()
    results4 = Utilisation_de_la_bat_apres_vieillissement()
    results5 = Exigences_de_puissance_solaire()
    
    # Display results in tables
    display_section("1. Dimensionnement des batteries - Cycle journalier", results1)
    display_section("2. Dimensionnement des batteries - Cycle de décharge complète", results2)
    display_section("3. Utilisation de la batterie par rapport à sa capacité nominale", results3)
    display_section("4. Utilisation de la batterie après vieillissement", results4)
    display_section("5. Exigences de puissance solaire", results5)
    
    # Create PDF
    pdf_bytes = create_pdf(results1, results2, results3, results4, results5)
    if pdf_bytes:
        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="battery_report.pdf">Télécharger le rapport PDF</a>'
        st.markdown(href, unsafe_allow_html=True)