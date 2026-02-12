# 14 maart 2024 - Sablina Vis / Dick van Mersbergen
import pandas as pd
import requests
import time
import getpass

excel_file_path = input('Documentpad (in de vorm /home/user/Documents/excel.xlsx): ')
df = pd.read_excel(excel_file_path)

# base URL
base_url = input('API: ')

# Bot credentials
bot_user_name = input('Gebruikersnaam: ')
bot_password = getpass(prompt='Wachtwoord: ')

# Initieren sessie met requests
session = requests.Session()

# Ophalen login token
login_token_url = f"{base_url}?action=query&meta=tokens&type=login&format=json"
login_token_response = session.get(login_token_url)
login_token = login_token_response.json()["query"]["tokens"]["logintoken"]

# Login
login_url = f"{base_url}?action=login&format=json"
login_params = {
    'lgtoken': login_token,
    'lgname': bot_user_name,
    'lgpassword': bot_password
}
login_response = session.post(login_url, data=login_params)
login_result = login_response.json()["login"]["result"]

# Get the edit token
edit_token_url = f"{base_url}?action=query&meta=tokens&type=csrf&format=json"
edit_token_response = session.get(edit_token_url)
edit_token = edit_token_response.json()["query"]["tokens"]["csrftoken"]

print("Login Token:", login_token)
print("Edit Token:", edit_token)

#----------------------------------------
# Met deze functie wordt de pagina in txt gemaakt.
# Functie daarna wordt elke afzonderlijk pagina geimporteerd.

def fun_batch_import(page_name, page_text):
    edit_params = {
        'title': page_name,
        'text': page_text,
        'Category': 'Monumenten',
        'Element[elementtype]': 'Monument',
        'token': edit_token,
        'format': 'json'
    }
    edit_url = f"{base_url}?action=edit&format=json"
    edit_response = session.post(edit_url, data=edit_params)

    edit_status = edit_response.json()["edit"]["result"]
    return edit_status

#----------------------------------------
#Functie om excel om te zetten naar de juiste format voor de kennisbank pagina.
def xlsx_to_markup_kennisbank(df):
    df['paginanaam'] = df['paginanaam'].astype(str)
    uniek_monument = df['paginanaam'].unique()

    # Loop over elk monument
    for paginanaam in uniek_monument:
        monument_df = df[df['paginanaam'] == paginanaam]   # Filter de DataFrame om alleen rijen met het huidige monument te krijgen
        first_row = monument_df.iloc[0]    # Haal de gegevens van de eerste rij op (voor later gebruik)

        for _ , row in monument_df.iterrows():    # Loop over elke rij in het huidige monument
            # Genereer geformatteerde tekst voor alle secties
            formatted_text = (
            f"{{{{#element:\n"
            f"|Elementtype={first_row['elementtype']}\n"
            f"|Batch={first_row['batch']}\n"
            f"|Status={first_row['status']}\n"
            f"|Monumentnummer={first_row['monumentnummer']}\n"
            f"|Complex={first_row['complex']}\n"
            f"|Fase bescherming={' ' if ((pd.isna(first_row['fase_bescherming'])) | (first_row['fase_bescherming'] == '')) else (first_row['fase_bescherming'])}\n"
            f"|Plaatsnaam={' ' if ((pd.isna(first_row['plaatsnaam'])) | (first_row['plaatsnaam'] == '')) else (first_row['plaatsnaam'])}\n"
            f"|Adres={' ' if ((pd.isna(first_row['adres'])) | (first_row['adres'] == '')) else (first_row['adres'])}\n"
            f"|Naam monument={' ' if ((pd.isna(first_row['naam_monument'])) | (first_row['naam_monument'] == '')) else (first_row['naam_monument'])}\n"
            f"|Introductie={' ' if ((pd.isna(first_row['introductie'])) | (first_row['introductie'] == '')) else (first_row['introductie'])}\n"
            f"|Kenmerken={' ' if ((pd.isna(first_row['kenmerken'])) | (first_row['kenmerken'] == '')) else (first_row['kenmerken'])}\n"
            f"|Omschrijving={' ' if ((pd.isna(first_row['omschrijving'])) | (first_row['omschrijving'] == '')) else (first_row['omschrijving'])}\n"
            f"|Afbeelding (extern)={' ' if ((pd.isna(first_row['afbeelding_extern'])) | (first_row['afbeelding_extern'] == '')) else (first_row['afbeelding_extern'])}\n"
            f"|Gerelateerd aan monument={' ' if ((pd.isna(first_row['gerelateerd_aan_monument'])) | (first_row['gerelateerd_aan_monument'] == '')) else (first_row['gerelateerd_aan_monument'])}\n"
            f"|Gerelateerd aan artikel={' ' if ((pd.isna(first_row['gerelateerd_aan_artikel'])) | (first_row['gerelateerd_aan_artikel'] == '')) else (first_row['gerelateerd_aan_artikel'])}\n"
            f"|Gerelateerd aan gezicht={' ' if ((pd.isna(first_row['gerelateerd_aan_gezicht'])) | (first_row['gerelateerd_aan_gezicht'] == '')) else (first_row['gerelateerd_aan_gezicht'])}\n"
            f"|Gerelateerd aan thema={' ' if ((pd.isna(first_row['gerelateerd_aan_thema'])) | (first_row['gerelateerd_aan_thema'] == '')) else (first_row['gerelateerd_aan_thema'])}\n"
            f"}}}}\n"
            f"{' ' if ((pd.isna(first_row['bronnen'])) | (first_row['bronnen'] == '')) else (first_row['bronnen'])}\n"
            )

        edit_status = fun_batch_import(paginanaam, formatted_text)

        # Import the page using fun_batch_import function
        print(f"Edit Status voor {paginanaam}: {edit_status}")

        # Sleep for 1 second
        time.sleep(1)


#--------------------------------------
# Functie dat alles automatiseert; let op dat 'df' naam is dat gegeven is aan de excel file, wellicht is dit voor later handiger met een user input.
xlsx_to_markup_kennisbank(df)
