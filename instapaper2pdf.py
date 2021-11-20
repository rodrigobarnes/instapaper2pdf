from bs4 import BeautifulSoup
import requests
import os
import pdfkit
import io

username = os.environ['INSTA_USERNAME']
password = os.environ['INSTA_PASSWORD']

login_details = {
    "username": username,
    "password": password
}

base_url = "https://www.instapaper.com"

# line-size: 30px;
  
html_template_head = """
 <!DOCTYPE html>
<html>
<head>
<meta name="pdfkit-page-size" content="a4"/>
<meta name="pdfkit-orientation" content="Portrait"/>
<meta charset="UTF-8"> 
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Martel">
<style>
body {
  font-family: "Georgia", "Martel", serif;
  font-size: 18px;
  margin-left: 150px;
  margin-right: 150px;
}

p {
    margin-bottom: 10px;
}

a {
    text-decoration: none;
}

#TOC { 
    page-break-after:always;
}

.article {
    page-break-before:always;
}

</style>
</head>
<body>
<!-- start document -->
"""

html_template_foot = """
<!-- end document -->
</body>
</html> 
"""

document = io.StringIO()
# write the header
document.write(html_template_head);


with requests.session() as s:
    r = s.post(f'{base_url}/user/login', data = login_details)
    body = r.content

    soup = BeautifulSoup(body, 'html.parser')
    article_links = soup.find_all('a', attrs={"class" : "article_title"})

    # TOC
    document.write('<div id="TOC">')
    document.write('<ul>')
    for l in article_links[0:10]:
        article_id =l["href"][6:]
        document.write(f"<li><a href=\"#{article_id}\">{l['title']}</a></li>")

    document.write('</ul>')
    document.write('</div>')

    # Article bodie
    for l in article_links[0:10]:
        print(f'{l["href"]} - {l["title"]}')
        article_id =l["href"][6:]

        r = s.get(f'{base_url}{l["href"]}')
        # For debugging - write the original html in a file.
        with open(f'output/{article_id}.html', 'w') as f:
           f.write(r.text)




        article_html = r.text
        article_soup = BeautifulSoup(article_html, 'html.parser')

        metadata = article_soup.find_all('div', class_="metadata")
        
        if len(metadata) == 0:
            title = l['title']
            link = l['href']
        else:
            # Get the title
            title = metadata[0].find_all('header')[0].text
            print(title)
            # Get the source
            link = metadata[0].find_all('a', class_='original')
            article_url = link[0]['href']
            print(article_url)

        # Get the body of the article - the 'story'
        main = article_soup.find_all('div', class_='story')
        if len(main) > 0:


            # Title and links
            document.write(f"""
<!-- Start: {article_id} -->
<div id="{article_id}" class="article">
<h1>{title}</h1>
<p>
{article_id}: <a href="{article_url}">{article_url}</a> 
</p>
<p>
<a href="#TOC">Back to the table of contents</a>
</p>
""")
            # Add the story
            for d in main[0].descendants:
                fragment = str(d)
                document.write(fragment.encode('utf8'))
                document.write('\n')

            document.write(f"""
<!-- Finish: {article_id} -->
</div>
            """)
            
            # # Write to HTML
            # with open(f'output/{article_id}-main.html', 'wb') as f:
            #         f.write(document.getvalue().encode('utf8'))
            
# add the footer
document.write(html_template_foot);

# convert to PDF
pdfkit.from_string(document.getvalue(), f'output/summary.pdf')
document.close()
