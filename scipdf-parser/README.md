# Summary
We used ![SciPDF Parser](https://github.com/titipata/scipdf_parser) to extract meaningful text from research papers of arXiv datasets. This library leverages ![GROBID](https://github.com/kermitt2/grobid), a machine learning software for extracting information from scolarly documents, and convert PDF to JSON objects that contains metadata and sections including headings and texts.

# Install
- Clone the repository of scipdf_parser
- Download GROBID ver 0.6.2 and put it to the scipdf repo
- Put papers to be parsed under "/papers" folder
- Run parse-sample.py which generates .json files
