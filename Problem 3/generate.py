import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        # для каждой переменной в CSP
        for var in self.domains:
            # собираем все слова, которые не соответствуют длине переменной
            to_remove = set()
            for word in self.domains[var]:
                if len(word) != var.length:
                    to_remove.add(word)
            # удаляем неподходящие слова из домена
            for word in to_remove:
                self.domains[var].remove(word)

    def revise(self, x, y):
        revised = False
        overlap = self.crossword.overlaps[x, y]

        # если пересечения нет — ничего не делаем
        if overlap is None:
            return False

        i, j = overlap  # позиции пересекающихся букв
        to_remove = set()

        # проверяем каждое слово из домена x
        for word_x in self.domains[x]:
            # ищем хотя бы одно слово из y, которое согласуется
            compatible = False
            for word_y in self.domains[y]:
                if word_x[i] == word_y[j]:
                    compatible = True
                    break
            # если не нашли ни одного подходящего — удаляем word_x
            if not compatible:
                to_remove.add(word_x)

        # удаляем неподходящие слова
        for word in to_remove:
            self.domains[x].remove(word)
            revised = True

        return revised

    def ac3(self, arcs=None):
        # создаем очередь всех дуг (x, y)
        if arcs is None:
            queue = [
                (x, y)
                for x in self.domains
                for y in self.crossword.neighbors(x)
            ]
        else:
            queue = list(arcs)

        while queue:
            x, y = queue.pop(0)
            if self.revise(x, y):
                # если домен X опустел — CSP нерешаема
                if len(self.domains[x]) == 0:
                    return False
                # добавляем все соседние дуги (Z, X), кроме Y
                for z in self.crossword.neighbors(x) - {y}:
                    queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        for var in self.crossword.variables:
            if var not in assignment or assignment[var] is None:
                return False
        return True

    def consistent(self, assignment):
        # 1. Все слова должны быть уникальны
        words = list(assignment.values())
        if len(words) != len(set(words)):
            return False

        # 2. Каждое слово должно соответствовать длине переменной
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # 3. Проверить все пары пересекающихся переменных
        for x in assignment:
            for y in assignment:
                if x == y:
                    continue
                overlap = self.crossword.overlaps[x, y]
                if overlap is None:
                    continue
                i, j = overlap
                # если обе переменные имеют значения и буквы не совпадают — конфликт
                if word := assignment.get(x) and assignment.get(y):
                    if assignment[x][i] != assignment[y][j]:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        values = []
        for value in self.domains[var]:
            if value not in assignment.values():
                values.append(value)
        return values

    def select_unassigned_variable(self, assignment):
        unassigned = [v for v in self.crossword.variables if v not in assignment]
        return min(unassigned, key=lambda v: len(self.domains[v]))

    def backtrack(self, assignment):
        # если полное присвоение — вернуть результат
        if self.assignment_complete(assignment):
            return assignment

        # выбрать переменную
        var = self.select_unassigned_variable(assignment)

        # пройти по всем возможным значениям
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
