import json, pathlib
root=pathlib.Path(__file__).resolve().parent
data_path=root/'dist/data.json'
data=json.loads(data_path.read_text())
overrides=json.loads((root/'title-overrides.json').read_text())
for page in data['pages']:
    if page['id'] in overrides: page['title']=overrides[page['id']]
data_path.write_text(json.dumps(data,ensure_ascii=False))
