#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spacy
from fpdf import FPDF
import textwrap

nlp = spacy.load('en_core_web_sm')

def extract(doc, stopwords):
    """Remove stopwords and punctuation."""
    doc = [t for t in doc if t.is_alpha or t.pos_ is 'NUM']
    # Two passes on the stopwords: first, just the text, then check for any plurals with the lemmas
    doc = [t for t in doc if (t.is_stop == False) and (t.text not in stopwords)]
    doc = [t for t in doc if t.lemma_ not in stopwords]
    return doc

def page_align(stopped):
    """Use the remaining page numbers as an index for the remaining text."""
    page_num = {idx: t for idx, t in enumerate(stopped) if t.pos_ is 'NUM'}
    page_idx = list(page_num.keys())

    pages = []
    for i in range(len(page_idx) - 1):
        current_p = page_idx[i]
        next_p = page_idx[i+1]
        pages.append(stopped[current_p:next_p])
        
    # Don't forget the last page
    pages.append(stopped[page_idx[-1]:])

    return pages

def write_pdf(pages):
    """Write the list of pages to a PDF file."""
    # Do the title
    title = ['POLAROID', 'BY', 'CLARK COOLIDGE']

    pdf = FPDF(format='A5')
    pdf.set_font('arial', '', 34)
    pdf.add_page()
    x, y = 10, 15
    for i in title:
        pdf.set_xy(x, y)
        pdf.cell(50, 5, txt=i, ln=1, align='L')
        y += 50

    # Do the pages
    for idx, page in enumerate(pages):
        if len(page) == 0:
            pages[idx] = [' ']
        page = ' '.join(pages[idx])
        page = textwrap.wrap(page, 36)

        pdf.set_font('arial', '', 12)
        pdf.add_page()
        pdf.set_xy(10, 5)
        for line in page:
            pdf.cell(50, 5, txt=line, ln=1, align='L')

    pdf.output("polaroid_stopped.pdf", 'F')

def main():
    # Load stopwords
    with open('data/iso_en_stoplist.txt', 'r') as f:
        stopwords = f.read().split('\n')
    
    # Load the plaintext version of Polaroid
    with open('data/polaroid.txt', 'r') as f:
        polaroid = f.read()

    # Convert plaintext to SpaCy doc and remove the stopwords
    doc = nlp(polaroid)
    stopped = extract(doc, stopwords)

    # Align the remaining strings on pages and remove the page numbers
    pages = page_align(stopped)
    pages = [[t.text for t in p if (t.pos_ is not 'NUM') and (len(t) > 2)] for p in pages]

    # Write out the final PDF
    write_pdf(pages)

if __name__ == '__main__':
    main()
