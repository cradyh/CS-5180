from crawler import *


def create_professor(col, name, title, office, phone, email, website):
    document = {
        'name': name,
        'title': title,
        'office': office,
        'phone': phone,
        'email': email,
        'website': website
    }
    col.insert_one(document)


if __name__ == '__main__':
    db = connectDataBase()
    professors_db = db['professors']

    url = 'https://www.cpp.edu/sci/computer-science/'
    faculty_page = find_page(url, 'Permanent Faculty')

    html = urlopen(faculty_page)
    bs = BeautifulSoup(html.read(), "html.parser")
    professor_info = bs.find_all('div', {'class': 'clearfix'})
    for professor in professor_info:
        if professor.find('h2'):
            name = professor.find('h2').text.strip()
            title = professor.find('strong', string=re.compile('Title')).next_sibling.strip()
            title = re.sub(': ', '', title).strip()
            office = professor.find('strong', string=re.compile('Office')).next_sibling.strip()
            office = re.sub(': ', '', office).strip()
            phone = professor.find('strong', string=re.compile('Phone')).next_sibling.strip()
            phone = re.sub('[^\\d\\s()-]', '', phone).strip()
            email = professor.find('a', string=re.compile('(@cpp.edu)$')).text
            email = re.sub(': ', '', email).strip()
            web = professor.find('a', href=re.compile('http')).get('href') if professor.find('a', href=re.compile('http')) else None
            web = re.sub(': ', '', web).strip() if web else None
            create_professor(professors_db, name, title, office, phone, email, web)
