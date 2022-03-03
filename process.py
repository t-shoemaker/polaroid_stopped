#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import spacy
import pandas as pd
from fpdf import FPDF

nlp = spacy.load('en_core_web_sm')
with open('data/iso_en_stoplist.txt', 'r') as f:
    stopwords = f.read().split('\n')

# Rough conversion between pixels (which the bounding boxes use) and mm
to_mm = 0.26
pg_size = (450 * to_mm, 650 * to_mm)

def remove_sw(text):
    """Remove stopwords."""
    doc = nlp(text)

    result = []
    for t in doc:
        if (len(t) > 2) and (t.is_alpha):
            if (t.is_stop is False) and (t.text not in stopwords) and (t.lemma_ not in stopwords):
                result.append(t.text)
            else:
                result.append('')
        else:
            result.append('')

    return ' '.join(result)

def to_pdf(pages):
    """Create a PDF using the bounding box data."""
    pdf = FPDF(unit='mm', format = pg_size)
    pdf.set_auto_page_break(False)

    # First, do the title
    title = ['POLAROID', 'BY', 'CLARK COOLIDGE']
    pdf.set_font('arial', '', 30)
    pdf.add_page()
    x, y = 10, 50
    for i in title:
        pdf.set_xy(x, y)
        pdf.cell(50, 5, txt=i, ln=1, align='L')
        y += 25

    # Now do the pages
    pdf.set_font('arial', '', 7)
    for idx, page in enumerate(pages):
        print("Creating page", idx)
        pdf.add_page()

        # Everything is stored in a dataframe
        df = pd.read_csv(page, index_col=0)
        df['x'] = df['x'] * to_mm
        df['y'] = df['y'] * to_mm

        # Make a page number
        pdf.set_xy(108, 5)
        pdf.cell(5, 5, txt=str(idx+1), ln=1)

        # Draw the bounding boxes for valid words
        for idx in df.index:
            w, h = df.at[idx, 'width'], df.at[idx, 'height']
            x, y = df.at[idx, 'x'], df.at[idx, 'y']
            text = df.at[idx, 'text']
            text = remove_sw(text)
            if text is not '':
                pdf.set_xy(x, y)
                pdf.cell(w, h, txt=text, ln=1, align='L')

    # Save
    pdf.output('polaroid_stopped.pdf', 'F')

def main():
    """Load a directory of pages with bounding boxes."""
    pages = glob.glob('pages/*.csv')
    pages.sort()

    # Remove the title and colophon
    pages = pages[2:-1]

    # Make the PDF
    to_pdf(pages)

if __name__ == '__main__':
    main()
