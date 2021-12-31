from bs4 import BeautifulSoup
import requests
import os
import pdfkit
import qrcode
import base64
import io
import logging
import sys
from datetime import datetime

# -----------------------------------------------------------------------------
# Logging to file and STDOUT
# -----------------------------------------------------------------------------
logger = logging.getLogger('instapaper2pdf')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(formatter)
stdout_handler.setLevel(logging.INFO)
logger.addHandler(stdout_handler)

file_handler = logging.FileHandler('instapaper2pdf.log')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
articles_to_fetch = 25
output_file_name = f'instapaper-{datetime.now().strftime("%Y-%m-%d-%H%M")}'
base_url = "https://www.instapaper.com"
# Instapaper login details from environment
username = os.environ['INSTA_USERNAME']
password = os.environ['INSTA_PASSWORD']

login_details = {
    "username": username,
    "password": password
}

# -----------------------------------------------------------------------------
# HTML Template 
# -----------------------------------------------------------------------------

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
  font-family: "Martel", "Georgia", serif;
  font-size: 18px;
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
    page-break-before: always;
}

@page {
    size: A4;
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

pdfkit_options = {
    'margin-top': '1cm',
    'margin-right': '1cm',
    'margin-bottom': '1cm',
    'margin-left': '1cm',
    'encoding': 'UTF-8',
    'javascript-delay': '9000',
    'no-stop-slow-scripts': '',
    'zoom': 1.5
}

# -----------------------------------------------------------------------------
# Start building up the document
# -----------------------------------------------------------------------------

logger.info(f'Procesing the most recent {articles_to_fetch} article(s) from Instapaper')

document = io.StringIO()
# write the header
document.write(html_template_head);

# Use requests.session() to keep logged in
with requests.session() as s:
    r = s.post(f'{base_url}/user/login', data = login_details)
    body = r.content

    soup = BeautifulSoup(body, 'html.parser')
    article_links = soup.find_all('a', attrs={"class" : "article_title"})

    # Heading
    document.write('<h1>Instapaper summary</h1>')
    document.write(f"<p>Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>")

    # TOC
    document.write('<div id="TOC">')
    document.write('<ul>')
    for l in article_links[0:articles_to_fetch]:
        article_id =l["href"][6:]
        document.write(f"<li><a href=\"#{article_id}\">{l['title']}</a></li>")

    document.write('</ul>')
    document.write('</div>')

    # For each article
    for l in article_links[0:articles_to_fetch]:
        logger.info(f'{l["href"]} - {l["title"]}')
        article_id =l["href"][6:]

        r = s.get(f'{base_url}{l["href"]}')
        # For debugging - write the original html in a file.
        with open(f'output/{article_id}-source.html', 'w') as f:
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
            logger.info(title)
            # Get the source
            link = metadata[0].find_all('a', class_='original')
            article_url = link[0]['href']
            logger.info(article_url)

            qrcode_file = f'./output/{article_id}.png'
            qrcode_img = qrcode.make(article_url, box_size=4)
            qrcode_img.save(qrcode_file)
            with (open(qrcode_file, 'rb')) as fh:
                qrcode_encoded = base64.b64encode(fh.read()).decode()
                qrcode_datablock = f'data:image/png;base64,{qrcode_encoded}'
                # print(qrcode_datablock)

        # Get the body of the article - the 'story'
        main = article_soup.find_all('div', class_='story')
        if len(main) > 0:
            # the extracted body
            article_body = '\n'.join(map(lambda d: str(d), main[0].contents))

            article_heading = f"""
<!-- Start: {article_id} -->
<div id="{article_id}" class="article">
<h1>{title}</h1>
<p>
{article_id}: <a href="{article_url}">{article_url}</a> 
</p>
<img src="{qrcode_datablock}">
"""
            # Write just the body to HTML
            with open(f'output/{article_id}-body.html', 'w') as f:
                f.write(article_body)

            # Construct a as standalone doc
            article_standalone = io.StringIO()

            # Title and links
            article_standalone.write(html_template_head)
            article_standalone.write(article_heading)
            article_standalone.write(article_body)
            article_standalone.write(html_template_foot)

            # write the whole doc to html
            with open(f'output/{article_id}-full.html', 'w') as f:
                    f.write(article_standalone.getvalue())

            # add the body to he main document
            article_embedded = io.StringIO()
            article_embedded.write(article_heading)
            article_embedded.write("""
<p>
<a href="#TOC">Back to the table of contents</a>
</p>
""")
            article_embedded.write(article_body)

            article_embedded.write(f"""
<!-- Finish: {article_id} -->
</div>
            """)
            document.write(article_embedded.getvalue())
        
# add the footer
document.write(html_template_foot);


# -----------------------------------------------------------------------------
# Write out the document to single file HTML and PDF
# -----------------------------------------------------------------------------
logger.info(f'Writing out HTML file: output/{output_file_name}.html')
# Write final version
with open(f'output/{output_file_name}.html', 'w') as f:
    f.write(document.getvalue())

logger.info(f'Converting to PDf')
pdfkit.from_string(document.getvalue(), f'output/{output_file_name}.pdf', options=pdfkit_options)

document.close()
logger.info(f'Done: output/{output_file_name}.pdf')