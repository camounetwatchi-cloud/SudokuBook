from fpdf import FPDF
from dokusan import generators, solvers
import random

# --- CONFIGURATION ---
NOMBRE_PUZZLES = 12  # Nombre de puzzles (Multiple de 4 conseillé)
TAILLE_GRILLE = 80   # Taille en mm
MARGE_GAUCHE = 15    # Marge KDP
MARGE_HAUT = 30      # Espace titre

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

    def dessiner_sudoku(self, x, y, data, numero_puzzle, difficulte_score):
        self.set_xy(x, y)
        
        # Titre
        self.set_font('helvetica', 'B', 10)
        self.set_text_color(0)
        # On affiche un label "Niveau" basé sur le score
        label_niveau = "Difficile"
        if difficulte_score > 250: label_niveau = "Extrême"
        elif difficulte_score > 150: label_niveau = "Très Difficile"
            
        self.cell(TAILLE_GRILLE, 8, f"Puzzle N°{numero_puzzle} ({label_niveau})", align='L')
        
        # Grille
        taille_case = TAILLE_GRILLE / 9
        self.set_font('helvetica', '', 12)
        str_data = str(data)
        
        for i in range(9):
            for j in range(9):
                char = str_data[i*9 + j]
                pos_x = x + (j * taille_case)
                pos_y = y + 8 + (i * taille_case)
                
                self.set_line_width(0.1)
                self.rect(pos_x, pos_y, taille_case, taille_case)
                
                if char != '0' and char != '.':
                    self.set_xy(pos_x, pos_y + 2) 
                    self.cell(taille_case, taille_case - 4, char, align='C')

        # Bordures épaisses
        self.set_line_width(0.8)
        self.rect(x, y + 8, TAILLE_GRILLE, TAILLE_GRILLE)
        self.line(x + 3*taille_case, y+8, x + 3*taille_case, y+8+TAILLE_GRILLE)
        self.line(x + 6*taille_case, y+8, x + 6*taille_case, y+8+TAILLE_GRILLE)
        self.line(x, y+8 + 3*taille_case, x+TAILLE_GRILLE, y+8 + 3*taille_case)
        self.line(x, y+8 + 6*taille_case, x+TAILLE_GRILLE, y+8 + 6*taille_case)

# --- 1. GÉNÉRATION (MÉTHODE ROBUSTE) ---
print(f"⏳ Génération de {NOMBRE_PUZZLES} puzzles en cours...")

liste_puzzles = []

for i in range(NOMBRE_PUZZLES):
    # Au lieu de calculer le rang après, on choisit une difficulté cible AVANT.
    # 150 = Difficile, 450 = Extreme
    target_rank = random.randint(150, 400) 
    
    try:
        # On demande à dokusan de générer un puzzle autour de ce rang
        sudoku = generators.random_sudoku(avg_rank=target_rank)
        
        liste_puzzles.append({
            "grid": str(sudoku),
            "score": target_rank # On utilise la difficulté demandée comme score de tri
        })
        print(f"   - Puzzle {i+1}/{NOMBRE_PUZZLES} généré (Difficulté cible: {target_rank})")
        
    except Exception as e:
        print(f"Erreur sur un puzzle, on réessaie... {e}")
        i -= 1 # On recule le compteur pour réessayer

# TRI : On trie du plus "facile" (parmi les difficiles) au plus dur
liste_puzzles.sort(key=lambda x: x['score'])
print("✅ Tri effectué.")

# --- 2. PDF ---
pdf = PDF()
pdf.set_auto_page_break(False)
pdf.add_page()
pdf.set_font('helvetica', 'B', 24)
pdf.ln(80)
pdf.cell(0, 10, 'SUDOKU CHALLENGE', align='C', ln=True)
pdf.set_font('helvetica', '', 14)
pdf.cell(0, 10, 'Niveau Difficile à Extrême', align='C')

pdf.add_page() 

positions = [
    (MARGE_GAUCHE, MARGE_HAUT),
    (MARGE_GAUCHE + TAILLE_GRILLE + 10, MARGE_HAUT),
    (MARGE_GAUCHE, MARGE_HAUT + TAILLE_GRILLE + 25),
    (MARGE_GAUCHE + TAILLE_GRILLE + 10, MARGE_HAUT + TAILLE_GRILLE + 25)
]

compteur_pos = 0

for index, data in enumerate(liste_puzzles):
    x, y = positions[compteur_pos]
    pdf.dessiner_sudoku(x, y, data['grid'], index + 1, data['score'])
    compteur_pos += 1
    
    if compteur_pos == 4:
        if index < len(liste_puzzles) - 1:
            pdf.add_page()
            compteur_pos = 0

pdf.output("Livre_Sudoku_Final.pdf")
print("✅ PDF généré : 'Livre_Sudoku_Final.pdf'")
