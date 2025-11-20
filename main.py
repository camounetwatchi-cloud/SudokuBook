from fpdf import FPDF
from dokusan import generators, solvers
import random

# --- CONFIGURATION ---
NOMBRE_PUZZLES = 12  # Multiple de 4 conseillé
TAILLE_GRILLE_PRINCIPALE = 80   # Taille des exercices (mm)
TAILLE_GRILLE_SOLUTION = 40     # Taille des solutions (mm) - Plus petit
MARGE_GAUCHE = 15
MARGE_HAUT = 30

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1: 
            self.set_font('helvetica', 'B', 10)
            self.set_text_color(150)
            self.cell(0, 10, 'Collection Logique - Niveau Difficile à Extrême', align='C')
            self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', '', 8)
        self.set_text_color(0)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def dessiner_grille_generique(self, x, y, taille, data, numero, titre_prefixe="Puzzle", est_solution=False, data_initiale=None):
        """
        Fonction unique pour dessiner soit un exercice, soit une solution.
        """
        self.set_xy(x, y)
        
        # Titre
        self.set_font('helvetica', 'B', 9)
        self.set_text_color(0)
        self.cell(taille, 6, f"{titre_prefixe} {numero}", align='L')
        
        taille_case = taille / 9
        self.set_font('helvetica', '', 10 if est_solution else 12)
        
        str_data = str(data)
        str_initiale = str(data_initiale) if data_initiale else ""
        
        for i in range(9):
            for j in range(9):
                index = i*9 + j
                char = str_data[index]
                pos_x = x + (j * taille_case)
                pos_y = y + 7 + (i * taille_case)
                
                # Cadre fin
                self.set_line_width(0.1)
                self.set_draw_color(0) # Noir
                self.rect(pos_x, pos_y, taille_case, taille_case)
                
                # Logique des chiffres et couleurs
                if char != '0' and char != '.':
                    # Positionnement du texte
                    self.set_xy(pos_x, pos_y + (1 if est_solution else 2))
                    
                    if est_solution:
                        # Si c'est une solution, on vérifie si c'était un chiffre de départ
                        char_origine = str_initiale[index]
                        if char_origine == '0' or char_origine == '.':
                            self.set_text_color(255, 0, 0) # ROUGE (C'était une case vide)
                        else:
                            self.set_text_color(0, 0, 0) # NOIR (C'était un indice)
                    else:
                        self.set_text_color(0, 0, 0) # Tout noir pour l'exercice
                        
                    self.cell(taille_case, taille_case - (2 if est_solution else 4), char, align='C')

        # Bordures épaisses (Blocs 3x3)
        self.set_line_width(0.6 if est_solution else 0.8)
        self.set_draw_color(0)
        self.set_fill_color(0,0,0,0) # Transparent
        
        # Cadre extérieur
        self.rect(x, y + 7, taille, taille)
        
        # Lignes internes
        self.line(x + 3*taille_case, y+7, x + 3*taille_case, y+7+taille)
        self.line(x + 6*taille_case, y+7, x + 6*taille_case, y+7+taille)
        self.line(x, y+7 + 3*taille_case, x+taille, y+7 + 3*taille_case)
        self.line(x, y+7 + 6*taille_case, x+taille, y+7 + 6*taille_case)
        
        # Reset couleur texte à noir
        self.set_text_color(0)

# --- 1. GÉNÉRATION ET RÉSOLUTION ---
print(f"⏳ Génération et résolution de {NOMBRE_PUZZLES} puzzles...")

liste_puzzles = []

for i in range(NOMBRE_PUZZLES):
    target_rank = random.randint(150, 400)
    
    try:
        # 1. Créer le problème
        sudoku = generators.random_sudoku(avg_rank=target_rank)
        
        # 2. Trouver la solution immédiatement
        solution = solvers.backtrack(sudoku) 
        
        liste_puzzles.append({
            "grid": str(sudoku),        # Le problème (avec des zéros)
            "solution": str(solution),  # La solution complète
            "score": target_rank
        })
        print(f"   - Puzzle {i+1} prêt (Diff: {target_rank})")
        
    except Exception as e:
        print(f"   - Erreur génération, nouvel essai...")
        i -= 1

# Tri par difficulté
liste_puzzles.sort(key=lambda x: x['score'])
print("✅ Tri effectué.")

# --- 2. CRÉATION DU PDF ---
pdf = PDF()
pdf.set_auto_page_break(False)

# --- COUVERTURE ---
pdf.add_page()
pdf.set_font('helvetica', 'B', 24)
pdf.ln(80)
pdf.cell(0, 10, 'SUDOKU CHALLENGE', align='C', ln=True)
pdf.set_font('helvetica', '', 14)
pdf.cell(0, 10, 'Exercices & Solutions', align='C')

# --- PARTIE 1 : LES EXERCICES (GRANDS) ---
print("📄 Création des pages d'exercices...")
pdf.add_page() 
positions_ex = [
    (MARGE_GAUCHE, MARGE_HAUT),
    (MARGE_GAUCHE + TAILLE_GRILLE_PRINCIPALE + 10, MARGE_HAUT),
    (MARGE_GAUCHE, MARGE_HAUT + TAILLE_GRILLE_PRINCIPALE + 25),
    (MARGE_GAUCHE + TAILLE_GRILLE_PRINCIPALE + 10, MARGE_HAUT + TAILLE_GRILLE_PRINCIPALE + 25)
]

pos_idx = 0
for index, data in enumerate(liste_puzzles):
    x, y = positions_ex[pos_idx]
    # Dessin de l'exercice
    pdf.dessiner_grille_generique(
        x, y, TAILLE_GRILLE_PRINCIPALE, 
        data['grid'], index + 1, "Puzzle", est_solution=False
    )
    
    pos_idx += 1
    if pos_idx == 4 and index < len(liste_puzzles) - 1:
        pdf.add_page()
        pos_idx = 0

# --- PARTIE 2 : LES SOLUTIONS (PETITES, 4 PAR LIGNE, ROUGE) ---
print("📄 Création des pages de solutions...")
pdf.add_page()

# Titre de section
pdf.set_font('helvetica', 'B', 16)
pdf.cell(0, 10, "SOLUTIONS", align='C', ln=True)
pdf.ln(5)

# Configuration de la grille de solutions (4 colonnes x 5 lignes par exemple)
X_START = 10
Y_START = 40 # Un peu plus bas à cause du titre
ESPACE_X = 48 # 40mm taille + 8mm marge
ESPACE_Y = 55 # 40mm taille + 15mm marge (titre etc)
NB_COLONNES = 4

col = 0
row = 0

for index, data in enumerate(liste_puzzles):
    # Calcul position
    x = X_START + (col * ESPACE_X)
    y = Y_START + (row * ESPACE_Y)
    
    # Vérification saut de page
    if y + TAILLE_GRILLE_SOLUTION > 280:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 16)
        pdf.cell(0, 10, "SOLUTIONS (Suite)", align='C', ln=True)
        col = 0
        row = 0
        y = Y_START
        x = X_START

    # Dessin de la solution
    # On passe data['solution'] pour les chiffres, ET data['grid'] pour savoir quoi mettre en rouge
    pdf.dessiner_grille_generique(
        x, y, TAILLE_GRILLE_SOLUTION, 
        data['solution'], index + 1, "Sol.", 
        est_solution=True, data_initiale=data['grid']
    )
    
    # Incrémentation position
    col += 1
    if col >= NB_COLONNES:
        col = 0
        row += 1

pdf.output("Livre_Sudoku_Complet.pdf")
print("✅ PDF terminé : 'Livre_Sudoku_Complet.pdf'")
