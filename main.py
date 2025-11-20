from fpdf import FPDF
from dokusan import generators, solvers, stats
import math

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
    def __init__(self):
        super().__init__()
        self.nb_puzzle_pages = 0  # Initialisation de l'attribut
    
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
        self.cell(TAILLE_GRILLE, 8, f"Puzzle N°{numero_puzzle} (Difficulté: {difficulte_score})", align='L')
        
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

MIN_RANK = 150  # Difficulté minimale

i = 0
tentatives = 0
max_tentatives = NOMBRE_PUZZLES * 20

while i < NOMBRE_PUZZLES and tentatives < max_tentatives:
    tentatives += 1
    
    # Génération d'un sudoku difficile (avg_rank entre 150 et 450)
    sudoku = generators.random_sudoku(avg_rank=200)
    
    # Calcul du score de difficulté
    score = stats.rank(sudoku)
    
    if score < MIN_RANK:
        continue 
    
    # RÉSOLUTION du sudoku avec la bonne fonction : backtrack()
    solution = solvers.backtrack(sudoku)
    
    liste_puzzles.append({
        "grid": str(sudoku),
        "solution": str(solution),
        "score": score
    })
    print(f"   - Validé puzzle {i+1}/{NOMBRE_PUZZLES} (Difficulté: {score})")
    i += 1 

if i < NOMBRE_PUZZLES:
    print(f"⚠️  Attention : seulement {i} puzzles générés sur {NOMBRE_PUZZLES} demandés")

liste_puzzles.sort(key=lambda x: x['score'])
print("✅ Tri effectué par difficulté croissante.")

# --- 2. CRÉATION DU PDF ET MISE EN PAGE ---
pdf = PDF()
pdf.set_auto_page_break(False)

# Calcule le nombre de pages de puzzles AVANT de créer les pages
pdf.nb_puzzle_pages = math.ceil(len(liste_puzzles) / 4)

# Page de titre
pdf.add_page()
pdf.set_font('helvetica', 'B', 24)
pdf.ln(80)
pdf.cell(0, 10, 'SUDOKU CHALLENGE', align='C', ln=True)
pdf.set_font('helvetica', '', 14)
pdf.cell(0, 10, 'Du Difficile à l\'Extrême', align='C')

# --- SECTION PUZZLES (4 PAR PAGE) ---
pdf.add_page() 

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
        if index < len(liste_puzzles) - 1:
            pdf.add_page()
        compteur_pos = 0

# --- SECTION SOLUTIONS (4 PAR LIGNE) ---
pdf.add_page()
pdf.set_font('helvetica', 'B', 20)
pdf.cell(0, 10, 'SOLUTIONS', ln=True, align='C')
pdf.ln(10)

# Positions pour 4 solutions par ligne
ESPACE_INTER_SOL = (210 - 2*MARGE_GAUCHE - 4*TAILLE_MINI_GRILLE) / 3
PUZZLES_PAR_LIGNE = 4
PUZZLES_PAR_PAGE = 8

positions_solutions = []
y_depart_solutions = MARGE_HAUT + 10

for row in range(2):
    for col in range(PUZZLES_PAR_LIGNE):
        x = MARGE_GAUCHE + col * (TAILLE_MINI_GRILLE + ESPACE_INTER_SOL)
        y = y_depart_solutions + row * (TAILLE_MINI_GRILLE + ESPACE_LIGNE_SOL + 4)
        positions_solutions.append((x, y))

compteur_pos_sol = 0

for index, data in enumerate(liste_puzzles):
    x, y = positions_solutions[compteur_pos_sol % PUZZLES_PAR_PAGE]
    
    row_in_page = compteur_pos_sol // PUZZLES_PAR_LIGNE
    y_adjusted = y_depart_solutions + (row_in_page * (TAILLE_MINI_GRILLE + ESPACE_LIGNE_SOL + 4))
    
    pdf.dessiner_solution(x, y_adjusted, data['grid'], data['solution'], index + 1)
    compteur_pos_sol += 1
    
    if compteur_pos_sol % PUZZLES_PAR_PAGE == 0 and index < len(liste_puzzles) - 1:
        pdf.add_page()

# --- 3. EXPORT ---
pdf.output("Livre_Sudoku_Complet.pdf")
print("✅ PDF généré : 'Livre_Sudoku_Complet.pdf'")
