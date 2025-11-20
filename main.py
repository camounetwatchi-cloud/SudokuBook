from fpdf import FPDF
from dokusan import generators, solvers
import random

# --- CONFIGURATION ---
NOMBRE_PUZZLES = 12  # Pour le test (doit être un multiple de 4 idéalement)
TAILLE_GRILLE = 80   # Taille du carré de la grille en mm
MARGE_GAUCHE = 15    # Marge de sécurité KDP
MARGE_HAUT = 30      # Espace pour le titre

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1: # Pas de header sur la couverture
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
        """
        Dessine une grille complète à la position (x, y)
        """
        self.set_xy(x, y)
        
        # 1. Titre du puzzle (au-dessus de la grille)
        self.set_font('helvetica', 'B', 10)
        self.cell(TAILLE_GRILLE, 8, f"Puzzle N°{numero_puzzle} (Niveau {difficulte_score})", align='L')
        
        # 2. Dessiner les cases et les nombres
        taille_case = TAILLE_GRILLE / 9
        self.set_font('helvetica', '', 12)
        
        # On transforme la chaine de 81 chiffres en liste de lignes
        str_data = str(data) # Assure que c'est une string
        
        for i in range(9): # Lignes
            for j in range(9): # Colonnes
                char = str_data[i*9 + j]
                pos_x = x + (j * taille_case)
                pos_y = y + 8 + (i * taille_case) # +8 pour le titre
                
                # Dessiner le cadre de la case (fin)
                self.set_line_width(0.1)
                self.rect(pos_x, pos_y, taille_case, taille_case)
                
                # Ecrire le chiffre si ce n'est pas un '0' ou '.'
                if char != '0' and char != '.':
                    # Astuce pour centrer le texte dans la case
                    self.set_xy(pos_x, pos_y + 2) 
                    self.cell(taille_case, taille_case - 4, char, align='C')

        # 3. Dessiner les bordures épaisses (Blocs 3x3)
        self.set_line_width(0.8) # Trait épais
        # Contour extérieur
        self.rect(x, y + 8, TAILLE_GRILLE, TAILLE_GRILLE)
        # Lignes verticales épaisses
        self.line(x + 3*taille_case, y+8, x + 3*taille_case, y+8+TAILLE_GRILLE)
        self.line(x + 6*taille_case, y+8, x + 6*taille_case, y+8+TAILLE_GRILLE)
        # Lignes horizontales épaisses
        self.line(x, y+8 + 3*taille_case, x+TAILLE_GRILLE, y+8 + 3*taille_case)
        self.line(x, y+8 + 6*taille_case, x+TAILLE_GRILLE, y+8 + 6*taille_case)

# --- 1. GÉNÉRATION ET TRI DES DONNÉES ---
print(f"⏳ Génération de {NOMBRE_PUZZLES} puzzles en cours... (ça peut prendre un moment)")

liste_puzzles = []

for i in range(NOMBRE_PUZZLES):
    # On demande un rang min de 150 (Difficile)
    # dokusan retourne un objet, on le convertit en string
    sudoku = generators.random_sudoku(rank=random.randint(150, 450))
    
    # On récupère le score réel (rank) pour le tri
    score = sudoku.rank() 
    
    # On stocke tout dans un dictionnaire
    liste_puzzles.append({
        "grid": str(sudoku),
        "score": score
    })
    print(f"   - Généré puzzle {i+1}/{NOMBRE_PUZZLES} (Score: {score})")

# LE TRI MAGIQUE : On trie la liste par 'score' croissant
liste_puzzles.sort(key=lambda x: x['score'])
print("✅ Tri effectué par difficulté croissante.")

# --- 2. CRÉATION DU PDF ---
pdf = PDF()
pdf.set_auto_page_break(False)

# Page de titre
pdf.add_page()
pdf.set_font('helvetica', 'B', 24)
pdf.ln(80)
pdf.cell(0, 10, 'SUDOKU CHALLENGE', align='C', ln=True)
pdf.set_font('helvetica', '', 14)
pdf.cell(0, 10, 'Du Difficile à l\'Extrême', align='C')

# --- 3. PLACEMENT DES GRILLES (4 PAR PAGE) ---
pdf.add_page() 

# Positions pour 4 grilles (A4)
# Pos 1 (Haut Gauche), Pos 2 (Haut Droite), Pos 3 (Bas Gauche), Pos 4 (Bas Droite)
positions = [
    (MARGE_GAUCHE, MARGE_HAUT),                      # Pos 1
    (MARGE_GAUCHE + TAILLE_GRILLE + 10, MARGE_HAUT), # Pos 2
    (MARGE_GAUCHE, MARGE_HAUT + TAILLE_GRILLE + 25), # Pos 3
    (MARGE_GAUCHE + TAILLE_GRILLE + 10, MARGE_HAUT + TAILLE_GRILLE + 25) # Pos 4
]

compteur_pos = 0 # Pour savoir où on est sur la page (0, 1, 2 ou 3)

for index, data in enumerate(liste_puzzles):
    # Récupérer les coordonnées x, y actuelles
    x, y = positions[compteur_pos]
    
    # Dessiner le sudoku
    # index + 1 car on veut commencer au Puzzle N°1, pas 0
    pdf.dessiner_sudoku(x, y, data['grid'], index + 1, data['score'])
    
    compteur_pos += 1
    
    # Si on a rempli les 4 positions, on change de page et on remet le compteur à 0
    if compteur_pos == 4:
        pdf.add_page()
        compteur_pos = 0

# Si la dernière page est vide (cas rare où le compte tombe pile), on la supprime ou on laisse
# Ici fpdf gère bien, si on n'appelle pas add_page, on reste sur la courante.

pdf.output("Livre_Sudoku_Trie.pdf")
print("✅ PDF généré : 'Livre_Sudoku_Trie.pdf'")
