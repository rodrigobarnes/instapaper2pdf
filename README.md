# README - instapaper2pdf

## Introduction

This is a simple single script to read some recent articles from [Instapaper](https://www.instapaper.com) and convert them into a reasonably structured and layed out PDF for use in a [Remarkable](https://remarkable.com/) device (or similar)

It should be possible to bypass instapaper and just have a list of URLs but the text cleaning Instapaper does is nice plus the target workflow is:

- Log articles in Instapaper
- Periodically generate PDF
- Read at leisure on Remarkable

## Features

- Generate a PDF file with each article on a new page
- Interactive table of contents
- Display the link to the original file
- Link back to the table of contents
- QR code so you can go straight to the original article when reading the PDF on a device with no browser

## Usage

- Install Python 3.9 via [Anaconda](https://www.anaconda.com/products/individual)
- Recreate the environment: `conda env create --file environment.yaml`
- Activate the envoronment: `conda activate instapaper2pdf`
- Create an `.env` file with your Instapaper username and password - see [.env.template](./.env.template)
- Add the credentials to the environment e.g. `source .env`
- Run the script: `python instapaper2pdf.py`
- Output is logged to the console or to `instapaper2pdf.log`

## Known issues

The table of contents is good in HTML but doesn´t always work well in the PDF. 

## Acknowledgements

Many thanks to the maintainers of the open source libraries this depends on, especially:

- [`pdfkit`](https://github.com/JazzCore/python-pdfkit)
- [`qrcode`](https://github.com/lincolnloop/python-qrcode)
- [`requests`](https://docs.python-requests.org/en/master/index.html)
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/)

Take a look at [environment.yml](./environment.yml) for all the dependencies