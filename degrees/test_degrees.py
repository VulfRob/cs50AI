import unittest
from degrees import shortest_path, neighbors_for_person, people, movies, names

# Тестовая мини-база, похожая на ту, что мы делали вручную
names.clear()
people.clear()
movies.clear()

names.update({
    "tom hanks": {"1"},
    "kevin bacon": {"2"},
    "gary sinise": {"3"},
    "emma watson": {"4"}
})

people.update({
    "1": {"name": "Tom Hanks", "birth": "1956", "movies": {"10", "11"}},
    "2": {"name": "Kevin Bacon", "birth": "1958", "movies": {"12"}},
    "3": {"name": "Gary Sinise", "birth": "1955", "movies": {"10", "12"}},
    "4": {"name": "Emma Watson", "birth": "1990", "movies": {"13"}}
})

movies.update({
    "10": {"title": "Forrest Gump", "year": "1994", "stars": {"1", "3"}},
    "11": {"title": "Apollo 13", "year": "1995", "stars": {"1"}},
    "12": {"title": "Trapped", "year": "1996", "stars": {"2", "3"}},
    "13": {"title": "Harry Potter", "year": "2001", "stars": {"4"}}
})


class TestDegrees(unittest.TestCase):

    def test_neighbors_for_person(self):
        """Тест: соседи Тома Хэнкса должны включать Гарри Синиза"""
        n = neighbors_for_person("1")
        self.assertIn(("10", "3"), n)

    def test_direct_connection(self):
        """Тест: если актёры снимались вместе — путь длиной 1"""
        path = shortest_path("1", "3")
        self.assertEqual(len(path), 1)
        movie_id, person_id = path[0]
        self.assertEqual(movies[movie_id]["title"], "Forrest Gump")
        self.assertEqual(person_id, "3")

    def test_indirect_connection(self):
        """Тест: Том Хэнкс и Кевин Бейкон связаны через 1 промежуточного"""
        path = shortest_path("1", "2")
        self.assertEqual(len(path), 2)
        # 1 -> 3 -> 2
        first_movie, first_person = path[0]
        second_movie, second_person = path[1]
        self.assertEqual(first_person, "3")
        self.assertEqual(second_person, "2")
        self.assertEqual(movies[first_movie]["title"], "Forrest Gump")
        self.assertEqual(movies[second_movie]["title"], "Trapped")

    def test_no_connection(self):
        """Тест: актёры без общих связей — пути нет"""
        path = shortest_path("1", "4")
        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
