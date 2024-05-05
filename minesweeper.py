import itertools
import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # If the number of cells = number of mines -> All cells are mines
        if len(self.cells) == self.count:
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Check if cell is in sentence
        if cell in self.cells:
            # Remove cell + update count
            self.cells.remove(cell)
            self.count = self.count - 1
            
    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            # Remove cell 
            self.cells.remove(cell)
    

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width
        # Keep track of which cells have been clicked on
        self.moves_made = set()
        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()
        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def trivial_update(self):
        change = True
        while change:
            change = False
            copy_kb = self.knowledge.copy()
            for sentence in copy_kb:
                if len(sentence.cells) == 0:
                    self.knowledge.remove(sentence)
                    continue
                elif sentence.count == len(sentence.cells):
                    change = True
                    for cell in sentence.cells.copy():
                        self.mark_mine(cell)
                elif sentence.count == 0:
                    change = True
                    for cell in sentence.cells.copy():
                        self.mark_safe(cell)
                        
        return 0
    
    def inference_update(self):
        change = True
        while change:
            change = False
            kb_copy = self.knowledge.copy()
            for sentence_1 in kb_copy:
                for sentence_2 in kb_copy:
                    if sentence_1 == sentence_2:
                        continue
                    elif sentence_1.cells.issubset(sentence_2.cells):
                        new_sentence = Sentence(sentence_2.cells.difference(sentence_1.cells), sentence_2.count - sentence_1.count)
                        change = True
                        if new_sentence.count == 0:
                            for cell in new_sentence.cells:
                                self.mark_safe(cell)
                        elif new_sentence.count == len(new_sentence.cells):
                            for cell in new_sentence.cells:
                                self.mark_mine(cell)
                        else:
                            self.knowledge.append(new_sentence)
                        self.trivial_update()
        return 0
               
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # 1) mark the cell as a move that has been made
        self.moves_made.add(cell)
        # 2) mark the cell as safe
        self.mark_safe(cell=cell)
        # 3) add a new sentence to the AI's knowledge base
            #based on the value of `cell` and `count`      
        cells_to_store = set()
        # Form new sentence:
        for i in range(cell[0] - 1, cell[0]+2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # If the cell is not on the field skip
                if i < 0 or j < 0:
                    continue
                if i >= self.height  or j >= self.width :
                    continue 
                # If cell was already played, or is marked as a mine skip
                if (i,j) in self.moves_made:
                    continue
                if (i,j) in self.mines:
                    count = count - 1
                    continue
                if(i,j) in self.safes:
                    continue
                cells_to_store.add((i,j))    
        new_sentence = Sentence(cells= cells_to_store, count=count)
        # We want to append the new sentence if it is not consisting of mines/safe cells only
        if new_sentence.count == 0:
            for cell in new_sentence.cells:
                self.mark_safe(cell)
        elif new_sentence.count == len(new_sentence.cells):
            for cell in new_sentence.cells:
                self.mark_mine(cell)
        else:
            self.knowledge.append(new_sentence)   
        self.trivial_update()
        self.inference_update()
        
    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        safe_moves = self.safes.difference(self.moves_made)
        if len(safe_moves) == 0:
            return None
        else:
            return safe_moves.pop()
        

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = set()
        for i in range(0, self.height):
            for j in range(0, self.width):
                all_cells.add((i, j))
        cells_to_choose = all_cells.difference(self.moves_made).difference(self.mines)
        if len(cells_to_choose) != 0:
            return random.sample(list(cells_to_choose), 1)[0]
        else:
            return None
    
