# Kennisbank Rijksmonumenten:Python script voor batch import in kennisbank
De kennisbank van de Rijksdienst voor het Cultureel Erfgoed wordt eind 2023 uitgebreid met ruim 2000 individuele kennispagina’s over Rijksmonumenten.
# Kennisbank scripts
Scripts die gebruikt worden om in bulk updates op de kennisbank door ter voeren. 

## Installatie

### Bash
```
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## How to run 
```
python src/batch_add_pages.py
```

## How to run tests
```
python -m src/batch_update_wikitext_test.py
```

## Run in Google Collabs

Open in browser: https://colab.research.google.com/github/cultureelerfgoed/beheer-scripts-kennisbank/blob/main/src/batch_add_pages.ipynb

## Functionaliteit 

| Veld? | Waarde? | batch_add_pages          | batch_edit_pages |
|-------|---------|--------------------------|------------------|
|  nee  |   nee   | veld + waarde toegevoegd | geen wijziging   |
|   ja  |   nee   | veld + waarde toegevoegd | geen wijziging   |
|   ja  |    ja   | geen wijziging           | waarde gewijzigd |
