import itertools
import random


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
       if self.count == len(self.cells):
          return self.cells
       else:
          return set()


    def known_safes(self):
        if self.count == 0:
          return self.cells
        else:
          return set()

    def mark_mine(self, cell):
        if cell in self.cells:
           self.cells.remove(cell)
           self.count -= 1


    def mark_safe(self, cell):
        if cell in self.cells:
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

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)

        neighbors = self.nearby_cells(cell)

        for n in neighbors.copy():
            if n in self.mines:
                neighbors.remove(n)
                count -= 1
            elif n in self.safes:
                neighbors.remove(n)

        # создаём новое логическое предложение
        new_sentence = Sentence(neighbors, count)

        # добавляем его в базу знаний ИИ
        self.knowledge.append(new_sentence)

        for sentence in self.knowledge.copy():  # идём по всем предложениям
            # если из предложения следует, что все клетки — мины
            if len(sentence.known_mines()) > 0:
                for cell in sentence.known_mines().copy():
                    self.mark_mine(cell)

            # если из предложения следует, что все клетки — безопасны
            if len(sentence.known_safes()) > 0:
                for cell in sentence.known_safes().copy():
                    self.mark_safe(cell)

        changed = True
        while changed:
            changed = False

            safes = set()
            mines = set()

            for sentence in self.knowledge:
                safes |= sentence.known_safes()
                mines |= sentence.known_mines()

            for s in safes:
                if s not in self.safes:
                    self.mark_safe(s)
                    changed = True
            for m in mines:
                if m not in self.mines:
                    self.mark_mine(m)
                    changed = True

            # добавляем новые выводы из подмножеств
            new_sentences = self.infer_new_sentences()
            if new_sentences:
                changed = True

    def infer_new_sentences(self):
        """
        Infers new sentences based on subset relationships
        between existing sentences in the knowledge base.
        """
        new_sentences = []

        for s1 in self.knowledge:
            for s2 in self.knowledge:
                if s1 == s2:
                    continue
                if s1.cells and s1.cells.issubset(s2.cells):
                    new_cells = s2.cells - s1.cells
                    new_count = s2.count - s1.count
                    new_sentence = Sentence(new_cells, new_count)
                    if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                        new_sentences.append(new_sentence)

        # Добавляем все новые предложения в базу знаний
        self.knowledge.extend(new_sentences)
        return new_sentences

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        possible_moves = self.safes - self.moves_made

        # исключаем те, которые вдруг оказались помечены как мины (на всякий случай)
        possible_moves -= self.mines

        # если есть безопасные ходы — выбираем любой
        if possible_moves:
            return possible_moves.pop()

        # если нет безопасных ходов — возвращаем None
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        all_cells = {(i, j) for i in range(self.height) for j in range(self.width)}
        possible_moves = all_cells - self.moves_made - self.mines

        if possible_moves:
            return random.choice(list(possible_moves))
        return None

    def nearby_cells(self, cell):
        """
        Returns a set of all cells adjacent to the given cell.
        Does not include the cell itself.
        """
        (i, j) = cell
        neighbors = set()

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                if di == 0 and dj == 0:
                    continue  # пропускаем саму клетку
                ni, nj = i + di, j + dj
                # проверяем, что сосед в пределах доски
                if 0 <= ni < self.height and 0 <= nj < self.width:
                    neighbors.add((ni, nj))

        return neighbors
