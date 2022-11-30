import scipdf
import os
import json
from tqdm import tqdm
directory = 'papers'
for filename in tqdm(os.listdir(directory)):
	print(filename)
    # f = os.path.join(directory, filename)
	json_filename = "".join(filename.split(".pdf")[0])
	output_filename = f"json-retry/{json_filename}.json"
	os.makedirs(os.path.dirname(output_filename), exist_ok=True)
	article_dict = scipdf.parse_pdf_to_dict(f'{directory}/{filename}') # return dictionary
	with open(output_filename, "w") as out_f:
		json.dump(article_dict, out_f)
