import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    N = len(corpus)
    links = corpus[page]
    PR = {}

    # Если нет исходящих ссылок — равномерное распределение
    if len(links) == 0:
        for p in corpus:
            PR[p] = 1 / N
        return PR

    # Если ссылки есть
    for p in corpus:
        if p in links:
            PR[p] = (1 - damping_factor) / N + damping_factor / len(links)
        else:
            PR[p] = (1 - damping_factor) / N

    return PR



import random

def sample_pagerank(corpus, damping_factor, n):
    pos = {page: 0 for page in corpus}     # счётчик посещений
    now_page = random.choice(list(corpus)) # первая страница случайна

    for _ in range(n):
        pos[now_page] += 1
        model = transition_model(corpus, now_page, damping_factor)
        pages = list(model.keys())
        probs = list(model.values())
        now_page = random.choices(pages, weights=probs, k=1)[0]

    # нормализация
    for page in pos:
        pos[page] /= n

    return pos



def iterate_pagerank(corpus, damping_factor):
    N = len(corpus)
    # Начальные ранги: 1/N
    ranks = {page: 1 / N for page in corpus}

    while True:
        new_ranks = {}
        for page in corpus:
            # Базовый вклад (случайный выбор)
            new_rank = (1 - damping_factor) / N

            # Суммируем вклад всех страниц, которые ведут на текущую
            for possible_page, links in corpus.items():
                # Если страница без исходящих ссылок — считаем, что она ведёт на все
                if len(links) == 0:
                    links = set(corpus.keys())
                if page in links:
                    new_rank += damping_factor * ranks[possible_page] / len(links)

            new_ranks[page] = new_rank

        # Проверка сходимости
        diff = max(abs(new_ranks[p] - ranks[p]) for p in corpus)
        ranks = new_ranks
        if diff < 0.001:
            break

    # Нормализация (на случай накопления ошибки)
    total = sum(ranks.values())
    for p in ranks:
        ranks[p] /= total

    return ranks



if __name__ == "__main__":
    main()
