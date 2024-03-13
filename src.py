from bs4 import BeautifulSoup
import requests
import os
import shutil
from os.path import basename
from googlesearch import search

class Opening:
    name = '' 
    img_source = ''
    img_path = ''
    description = ''
    famous_games = []

    def download_image(self, dir_path):
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)

        self.img_path = os.path.join(dir_path, basename(self.img_source))
        if os.path.exists(self.img_path):
            return

        with open(self.img_path, 'wb') as f:
            f.write(requests.get(self.img_source).content)

    def is_text(self, text):
        c = text[0]
        if not (c.isalpha() or c.isdigit()):
            return False

        if 'watch' in text.lower():
            return False

        return True


    def __init__(self, name, img_source, site_url):
        self.name = name
        self.img_source = img_source

        r = requests.get(site_url)
        soup = BeautifulSoup(r.content, 'html.parser')

        header = soup.find('h1')
        paragraph = header.find_next('p') # image
        paragraph = paragraph.find_next('p') # first paragraph

        while (self.is_text(paragraph.text)):
            self.description += paragraph.text
            self.description += '\n\n'
            paragraph = paragraph.find_next('p')


    def __str__(self):
        return f'(name: {self.name}, img: {self.img_source})'

    def __repr__(self):
        return str(self)

def duckduckgo_search(query, max_results = 5):
    search_results = DDGS().text(query, max_results = max_results)
    result_list = []
    for result in search_results:
        title = result.text
        link = result['href']
        results_list.append((title, link))

    return results_list

def google_search(query, max_results = 5):
    results = []

    for url in search(query, stop = max_results):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                print(f'Failed to fetch {url}')
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.text.strip()
            results.append((title, url))
        except Exception as e:
            print(f'Error occurred while fetching {url}: {str(e)}')

    return results


class MarkdownGenerator:
    url = 'https://www.thechesswebsite.com/chess-openings/'
    soup = None
    content = ''
    opeings = None

    def get_openings_list(self):
        tags = self.soup.find_all('h5')
        openings = []
        for tag in tags[:10]:
            name = tag.string
            # discard MEMBERS ONLY openings
            if tag.next_element.next_element.next_element.text == 'MEMBERS ONLY':
                continue

            img_tag = tag.find_previous('img')
            img_source = img_tag['src']

            subpage_url = tag.find_previous('a')['href']

            opening = Opening(name, img_source, subpage_url)
            openings.append(opening)

        return openings 

    def generate_opening_page(self, opening, page_path):
        opening_page = f'{opening.name}\n===\n'
        opening_page += f'<img src="{opening.img_path}" width="200">\n\n'
        opening_page += '\n' + opening.description + '\n'

        # guides
        opening_page += 'Opening guides (from google):\n===\n'
        guides = google_search(f'{opening.name} "chess" guide')
        for title, link in guides:
            opening_page += f'+ [{title}]({link})\n'

        with open(page_path, 'w') as f:
            f.write(opening_page)


    def generate_list_page(self):
        self.content += 'Chess openings list\n===\n'

        for opening in self.openings:
            print(f'Downloading image for: {opening.name}')
            opening.download_image('img')
        
            page_path = f'{os.path.splitext(basename(opening.img_path))[0]}.md'
            self.generate_opening_page(opening, page_path)

            # link to opening subpage
            self.content += f'+ [{opening.name}]({page_path})\n\n'

            # html for image
            self.content += f'\t<img src="{opening.img_path}" width="200">\n\n'


        with open('site.md', 'w') as f:
            f.write(self.content)


    def generate(self):
        main_site = 'Chess openings\n===\n'
        # paragraph generated by chatgpt
        main_site += "Chess openings serve as the gateway to strategic exploration on the chessboard, laying the foundation for the intricate dance of pieces that unfolds in every game. They encompass a vast array of maneuvers, plans, and tactical ideas, each with its own unique flavor and strategic implications. From the classical elegance of the Ruy Lopez to the dynamic complexities of the Sicilian Defense, chess openings offer players the opportunity to express their creativity, adaptability, and strategic vision. By studying openings, players can deepen their understanding of chess principles, hone their tactical skills, and gain insight into the rich tapestry of possibilities that the game has to offer. Whether you're a beginner exploring the basics or a seasoned player delving into advanced theory, the world of chess openings is a fascinating journey of discovery and mastery.\n\n"

        self.generate_list_page()
        main_site += '+ [List of chess openings](site.md)'
        with open('index.md', 'w') as f:
            f.write(main_site)


    def __init__(self):
        r = requests.get(self.url)
        self.soup = BeautifulSoup(r.content, 'html.parser')
        self.openings = self.get_openings_list()


def main():
    generator = MarkdownGenerator()
    generator.generate()

if __name__ == '__main__':
    main()
