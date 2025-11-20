from fpdf import FPDF

# On crée une "Classe" qui hérite de FPDF.
# Cela permet de définir un Header et Footer qui s'appliqueront AUTOMATIQUEMENT à toutes les pages.
class PDF(FPDF):
    def header(self):
        # Ne pas mettre de header sur la page de couverture (page 1)
        if self.page_no() > 1:
            self.set_font('helvetica', 'B', 12)
            # Titre grisé en haut
            self.set_text_color(128) 
            self.cell(0, 10, 'Livre de Logique - Niveau Moyen', align='C')
            self.ln(20) # Saut de ligne de 20mm pour laisser de la place

    def footer(self):
        # Positionnement à 1.5 cm du bas
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(0) # Noir
        # Numéro de page automatique : {self.page_no()}
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

# --- CONFIGURATION DU LIVRE ---

# Format A4 pour le test (KDP utilise souvent 6x9 pouces, on verra ça plus tard)
pdf = PDF(orientation='P', unit='mm', format='A4')
pdf.set_auto_page_break(auto=True, margin=15)

# --- PAGE 1 : TITRE ---
pdf.add_page()
pdf.set_font('helvetica', 'B', 24)
# On centre le titre verticalement et horizontalement (approximatif pour le test)
pdf.ln(80) 
pdf.cell(0, 10, 'SUDOKU MASTER', align='C', new_x="LMARGIN", new_y="NEXT")
pdf.set_font('helvetica', '', 14)
pdf.cell(0, 10, '100 Grilles pour s\'entraîner', align='C')

# --- PAGES PUZZLES (Simulation) ---
nb_puzzles = 5  # On génère 5 pages pour tester

for i in range(1, nb_puzzles + 1):
    pdf.add_page()
    
    # Titre du Puzzle
    pdf.set_font('helvetica', 'B', 16)
    pdf.cell(0, 10, f'Puzzle N°{i}', ln=True, align='C')
    
    # Placeholder pour la grille (Un carré vide)
    # x=55, y=60 : position de départ
    # w=100, h=100 : largeur et hauteur (carré de 10cm)
    pdf.rect(x=55, y=60, w=100, h=100)
    
    # Petit texte indicatif
    pdf.set_xy(55, 165)
    pdf.set_font('helvetica', '', 10)
    pdf.cell(100, 10, "Difficulté : Moyenne", align='C')

# --- EXPORT ---
nom_fichier = "mon_premier_livre.pdf"
pdf.output(nom_fichier)
print(f"✅ Succès ! Le fichier '{nom_fichier}' a été généré dans le dossier.")
