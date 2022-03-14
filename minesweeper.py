import itertools
import random
import copy


class Minesweeper:
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


class Sentence:
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

    def is_empty(self):
        return len(self.cells) == 0

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        else:
            return None

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return None

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            return True
        else:
            return False

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            return True
        else:
            return False


class MinesweeperAI:
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
            # if a sentence is altered
            if sentence.mark_mine(cell):
                # remove sentence from knowledge and conclude_infer_integrate it
                self.knowledge.remove(sentence)
                self.conclude_infer_integrate(sentence)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            # if a sentence is altered
            if sentence.mark_safe(cell):
                # remove sentence from knowledge and conclude_infer_integrate it
                self.knowledge.remove(sentence)
                self.conclude_infer_integrate(sentence)

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
        # record as move made
        self.moves_made.add(cell)
        # record as safe
        self.mark_safe(cell)
        # create new knowledge of surrounding cells
        surrounding_unknowns = set()
        for i in range(cell[0] - 1, cell[0] + 2):
            if 0 <= i < self.height:
                for j in range(cell[1] - 1, cell[1] + 2):
                    if 0 <= j < self.width:
                        # ignore known safes, which includes current cell:
                        if (i, j) not in self.safes:
                            # lower count and ignore cell for known mine cell:
                            if (i, j) in self.mines:
                                count -= 1
                            else:
                                surrounding_unknowns.add((i, j))
        # conclude, infer, integrate new knowledge
        self.conclude_infer_integrate(Sentence(surrounding_unknowns, count))

    # check a sentence for safes or mines, if so, execute conclusions
    def is_conclusive(self, sentence):
        safes = copy.deepcopy(sentence.known_safes())
        if safes:
            for cell in safes:
                self.mark_safe(cell)
            return True
        else:
            mines = copy.deepcopy(sentence.known_mines())
            if mines:
                for cell in mines:
                    self.mark_mine(cell)
                return True
        # if inconclusive, return false
        return False

    # conclude sentances that are conclusive, draw inferences, add to knowlege
    def conclude_infer_integrate(self, sentence):
        # filter empty sentences and sentences that have already been through conclude_infer_integrate
        if sentence in self.knowledge or sentence.is_empty():
            return
        # if sentence is conclusive, execute conclusions; otherwise...
        if not self.is_conclusive(sentence):
            # prepare to build inferences
            inferences = []
            # compare sentence to all other sentences in knowledge
            for other_sentence in self.knowledge:
                # check for and make inferences
                if sentence.cells.issubset(other_sentence.cells):
                    inference = Sentence(
                        other_sentence.cells - sentence.cells,
                        other_sentence.count - sentence.count,
                    )
                elif other_sentence.cells.issubset(sentence.cells):
                    inference = Sentence(
                        sentence.cells - other_sentence.cells,
                        sentence.count - other_sentence.count,
                    )
                # try another sentence if no inferences have been made
                else:
                    continue
                # add inference if it is new
                if inference not in inferences and inference not in self.knowledge:
                    inferences.append(inference)
            # add sentence to knowledge
            self.knowledge.append(sentence)
            # if inferences were made, conclude_infer_integrate them
            if inferences:
                # integrate inferences into KB
                for inference in inferences:
                    self.conclude_infer_integrate(inference)

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.
        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    return (i, j)
        return None
