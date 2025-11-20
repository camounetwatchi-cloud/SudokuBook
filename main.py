from fpdf import FPDF
from dokusan import generators, solvers # solvers a été ajouté
import random
import math # Pour le calcul des positions

# --- CONFIGURATION GLOBALE ---
NOMBRE_PUZZLES = 12  # Pour le test (doit être un multiple de 4 idéalement)
# Dimensions pour les puzzles (grilles d'exercice)
TAILLE_GRILLE = 80   # Taille en mm
MARGE_GAUCHE = 15
MARGE_HAUT = 30
# Dimensions pour les solutions (mini-grilles)
TAILLE_MINI_GRILLE = 40 # 40mm pour que 4 tiennent sur une ligne
ESPACE_LIGNE_SOL = 5    # Espace vertical entre les lignes de solutions

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font('helvetica', 'B', 10)
            self.set_text_color(150)
            
            # Gère le titre de la section "Puzzles" ou "Solutions"
            if self.page_no() <= self.nb_puzzle_pages + 1:
                self.cell(0, 10, 'Collection Logique - Niveau Difficile à Extrême', align='C')
            else:
                self.cell(0, 10, 'Solutions', align='C')
            
            self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', '', 8)
        self.set_text_color(0)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

    def dessiner_sudoku(self, x, y, data, numero_puzzle, difficulte_score):
        """ Dessine une grille complète de puzzle """
        self.set_xy(x, y)
        
        # 1. Titre du puzzle
        self.set_font('helvetica', 'B', 10)
        self.cell(TAILLE_GRILLE, 8, f"Puzzle N°{numero_puzzle} (Score: {difficulte_score})", align='L')
        
        # 2. Dessiner les cases et les nombres
        taille_case = TAILLE_GRILLE / 9
        self.set_font('helvetica', '', 12)
        str_data = str(data) 
        
        for i in range(9): # Lignes
            for j in range(9): # Colonnes
                char = str_data[i*9 + j]
                pos_x = x + (j * taille_case)
                pos_y = y + 8 + (i * taille_case) 
                
                # Dessiner le cadre
                self.set_line_width(0.1)
                self.rect(pos_x, pos_y, taille_case, taille_case)
                
                # Écrire le chiffre (en noir par défaut)
                if char != '0' and char != '.':
                    self.set_text_color(0) # Noir
                    self.set_xy(pos_x, pos_y + 2) 
                    self.cell(taille_case, taille_case - 4, char, align='C')

        # 3. Dessiner les bordures épaisses (Blocs 3x3)
        self.set_line_width(0.8) 
        self.rect(x, y + 8, TAILLE_GRILLE, TAILLE_GRILLE) # Contour extérieur
        # Lignes verticales/horizontales épaisses
        for k in [3, 6]:
            self.line(x + k*taille_case, y+8, x + k*taille_case, y+8+TAILLE_GRILLE)
            self.line(x, y+8 + k*taille_case, x+TAILLE_GRILLE, y+8 + k*taille_case)


    def dessiner_solution(self, x, y, puzzle_data, solution_data, numero_puzzle):
        """ Dessine une mini-grille de solution avec les chiffres résolus en rouge """
        self.set_xy(x, y)
        
        # 1. Titre de la solution
        self.set_font('helvetica', 'B', 8)
        self.cell(TAILLE_MINI_GRILLE, 4, f"Solution N°{numero_puzzle}", ln=True, align='L')
        self.set_xy(x, y + 4) # Redescendre après le titre
        
        # 2. Dessiner les cases et les nombres
        taille_case = TAILLE_MINI_GRILLE / 9
        self.set_font('helvetica', '', 7)
        
        for i in range(9): # Lignes
            for j in range(9): # Colonnes
                index = i*9 + j
                char_sol = solution_data[index]
                char_puzzle = puzzle_data[index]
                
                pos_x = x + (j * taille_case)
                pos_y = y + 4 + (i * taille_case)
                
                # Dessiner le cadre
                self.set_line_width(0.1)
                self.rect(pos_x, pos_y, taille_case, taille_case)
                
                # Écrire le chiffre
                if char_sol != '0' and char_sol != '.':
                    # Déterminer la couleur : Rouge si nouveau, Noir si original
                    if char_puzzle == '0' or char_puzzle == '.':
                        self.set_text_color(255, 0, 0) # Rouge
                    else:
                        self.set_text_color(0) # Noir
                        
                    # Centrer le texte dans la case
                    self.set_xy(pos_x, pos_y + 0.5) 
                    self.cell(taille_case, taille_case - 1, char_sol, align='C')

        # 3. Dessiner les bordures épaisses (Blocs 3x3)
        self.set_line_width(0.5) 
        self.set_text_color(0) # Remettre à Noir pour le reste du dessin
        self.rect(x, y + 4, TAILLE_MINI_GRILLE, TAILLE_MINI_GRILLE) # Contour extérieur
        # Lignes verticales/horizontales épaisses
        for k in [3, 6]:
            self.line(x + k*taille_case, y+4, x + k*taille_case, y+4+TAILLE_MINI_GRILLE)
            self.line(x, y+4 + k*taille_case, x+TAILLE_MINI_GRILLE, y+4 + k*taille_case)


# --- 1. GÉNÉRATION ET TRI DES DONNÉES ---
print(f"⏳ Génération de {NOMBRE_PUZZLES} puzzles en cours... (ça peut prendre un moment)")

liste_puzzles = []
MIN_SCORE = 150 
i = 0

while i < NOMBRE_PUZZLES:
    sudoku = generators.random_sudoku() 
    score = sudoku.rank() 
    
    if score < MIN_SCORE:
        # print(f"   - Rejeté (Score: {score}). Trop facile.")
        continue 
    
    # CALCUL DE LA SOLUTION et conversion en chaîne
    solution = solvers.solve(sudoku) 
    
    liste_puzzles.append({
        "grid": str(sudoku),
        "solution": str(solution), # STOCKAGE DE LA SOLUTION
        "score": score
    })
    print(f"   - Validé puzzle {i+1}/{NOMBRE_PUZZLES} (Score: {score})")
    i += 1 

liste_puzzles.sort(key=lambda x: x['score'])
print("✅ Tri effectué par difficulté croissante.")

# --- 2. CRÉATION DU PDF ET MISE EN PAGE ---
pdf = PDF()
pdf.set_auto_page_break(False)

# Page de titre (Non modifiée)
pdf.add_page()
pdf.set_font('helvetica', 'B', 24)
pdf.ln(80)
pdf.cell(0, 10, 'SUDOKU CHALLENGE', align='C', ln=True)
pdf.set_font('helvetica', '', 14)
pdf.cell(0, 10, 'Du Difficile à l\'Extrême', align='C')

# --- SECTION PUZZLES (4 PAR PAGE) ---
pdf.add_page() 

# Calcule le nombre de pages de puzzles pour l'utiliser dans le header du PDF
pdf.nb_puzzle_pages = math.ceil(NOMBRE_PUZZLES / 4)

positions_puzzles = [
    (MARGE_GAUCHE, MARGE_HAUT),                      
    (MARGE_GAUCHE + TAILLE_GRILLE + 10, MARGE_HAUT), 
    (MARGE_GAUCHE, MARGE_HAUT + TAILLE_GRILLE + 25), 
    (MARGE_GAUCHE + TAILLE_GRILLE + 10, MARGE_HAUT + TAILLE_GRILLE + 25)
]

compteur_pos = 0 

for index, data in enumerate(liste_puzzles):
    x, y = positions_puzzles[compteur_pos]
    pdf.dessiner_sudoku(x, y, data['grid'], index + 1, data['score'])
    compteur_pos += 1
    
    if compteur_pos == 4:
        # S'assure de ne pas ajouter une page après le dernier puzzle
        if index < NOMBRE_PUZZLES - 1:
            pdf.add_page()
        compteur_pos = 0

# --- SECTION SOLUTIONS (4 PAR LIGNE) ---
pdf.add_page() # Commence la section Solutions sur une nouvelle page

pdf.set_font('helvetica', 'B', 20)
pdf.cell(0, 10, 'SOLUTIONS', ln=True, align='C')
pdf.ln(10)

# Positions pour 4 solutions par ligne
ESPACE_INTER_SOL = (210 - 2*MARGE_GAUCHE - 4*TAILLE_MINI_GRILLE) / 3 # Espace à répartir entre les 3 trous
PUZZLES_PAR_LIGNE = 4
PUZZLES_PAR_PAGE = 8 # Deux lignes de 4

positions_solutions = []
y_depart_solutions = MARGE_HAUT + 10 # 10mm sous le titre "SOLUTIONS"

# Calcule les coordonnées pour 8 solutions (2 lignes de 4)
for row in range(2):
    for col in range(PUZZLES_PAR_LIGNE):
        # Coordonnée X : Marge + (colonne * (taille grille + espace inter))
        x = MARGE_GAUCHE + col * (TAILLE_MINI_GRILLE + ESPACE_INTER_SOL)
        # Coordonnée Y : Départ + (ligne * (taille grille + espace ligne))
        y = y_depart_solutions + row * (TAILLE_MINI_GRILLE + ESPACE_LIGNE_SOL + 4) # +4 pour le titre de la solution
        positions_solutions.append((x, y))

compteur_pos_sol = 0
y_current = y_depart_solutions

for index, data in enumerate(liste_puzzles):
    x, y = positions_solutions[compteur_pos_sol % PUZZLES_PAR_PAGE]

    # Pour les solutions, on réutilise le même code de dessin, mais en décalant la hauteur
    # car il y a potentiellement plus de 8 solutions
    
    # On calcule la ligne pour repositionner le Y si on passe à une nouvelle ligne de solutions
    row_in_page = compteur_pos_sol // PUZZLES_PAR_LIGNE
    y_adjusted = y_depart_solutions + (row_in_page * (TAILLE_MINI_GRILLE + ESPACE_LIGNE_SOL + 4))

    pdf.dessiner_solution(x, y_adjusted, data['grid'], data['solution'], index + 1)
    compteur_pos_sol += 1

    # Si on est à la fin de la page (après 8 solutions)
    if compteur_pos_sol % PUZZLES_PAR_PAGE == 0 and index < NOMBRE_PUZZLES - 1:
        pdf.add_page()
        # On ne remet pas le compteur à 0, le modulo gère les positions x,y

# --- 3. EXPORT ---
pdf.output("Livre_Sudoku_Complet.pdf")
print("✅ PDF généré : 'Livre_Sudoku_Complet.pdf'")
