# Kennisbank: Python scripts voor batch importeren, toevoegen of wijzigen
Deze scripts worden voor de Kennisbank van de Rijksdienst voor het Cultureel Erfgoed gebruikt worden om in bulk updates door ter voeren. 

## Installatie

### Bash
```
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

## Script lokaal uitvoeren 
```
python src/batch_add_pages.py
```

## Tests draaien
```
python -m src/batch_update_wikitext_test.py
```

## In Google Collabs

Open in browser: https://colab.research.google.com/github/cultureelerfgoed/beheer-scripts-kennisbank/blob/main/src/batch_add_pages.ipynb

## Functionaliteit 

| Veld? | Waarde? | batch_add_pages          | batch_edit_pages |
|-------|---------|--------------------------|------------------|
|  nee  |   nee   | veld + waarde toegevoegd | geen wijziging   |
|   ja  |   nee   | veld + waarde toegevoegd | geen wijziging   |
|   ja  |    ja   | geen wijziging           | waarde gewijzigd |
