# 8 november 2023 - Sablina Vis
import pandas as pd
import requests
import time

excel_file_path = input('Documentpad (in de vorm /home/user/Documents/excel.xlsx): ')
df = pd.read_excel(excel_file_path)

# base URL
base_url = input('API: ')

# Bot credentials
bot_user_name = input('Gebruikersnaam: ')
bot_password = input('Wachtwoord: ')

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
# Met dit functie wordt de pagina in de juiste format geplaatst om geimporteerd te worden in de kennisbank.
# Functie wordt hier geplaatst omdat het ervoor zorgt dat de volgende functie deze kan gebruiken om ieder afzonderlijk pagina te importeren.
# Toevoegen van categorie aan begin van pagina. Hierdoor wordt de pagina in de gewenst categorie geplaatst.

def fun_batch_import(page_name, page_text):
    edit_params = {
        'title': page_name,
        'text': page_text,
        'Category': 'Beschermde_stads-_en_dorpsgezichten',
        'Element[elementtype]': 'Gezicht',
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
    df['trefwoord'] = df['trefwoord'].astype(str)
    uniek_gezicht = df['paginanaam'].unique()

    # Loop over elk uniek gezicht
    for paginanaam in uniek_gezicht:
        gezicht_df = df[df['paginanaam'] == paginanaam]   # Filter de DataFrame om alleen rijen met het huidige gezicht te krijgen
        first_row = gezicht_df.iloc[0]    # Haal de gegevens van de eerste rij op (voor later gebruik)

        for _ , row in gezicht_df.iterrows():    # Loop over elke rij in het huidige gezicht
            # Genereer geformatteerde tekst voor alle secties
            formatted_text = (
            f"{{{{#element:\n"
            f"|Elementtype={first_row['elementtype']}\n"    # let op spellingsfout in bron!
            f"|Status={first_row['status']}\n"
            f"|Gezichtnummer={first_row['gezichtnummer']}\n"
            f"|Plaatsnaam={'' if ((pd.isna(first_row['plaatsnaam'])) | (first_row['plaatsnaam'] == 'nan')) else row['plaatsnaam']}\n"  # Leeg als geen plaatsnaam in zit
            f"|Naam gezicht={'' if ((pd.isna(first_row['naam_gezicht'])) | (first_row['naam_gezicht'] == 'nan')) else row['naam_gezicht']}\n" # Mag nooit leeg zijn.
            f"|Provincie={first_row['provincie']}\n"
            f"|Kaart={first_row['kaart']}\n"
            f"|Omschrijving===Besluit==\n"
            f"{first_row['omschrijving']}\n"

            f"|Gerelateerd aan artikel={first_row['gerelateerd_aan_artikel']}\n"
            f"|Trefwoord={' ' if ((pd.isna(first_row['trefwoord'])) | (first_row['trefwoord'] == 'nan')) else (first_row['trefwoord'])}\n"
            f"|Specialisten={first_row['specialisten']}\n"
            f"}}}}\n"

            # 1 - Besluit aanwijzing
            f"{{{{SourceDocument\n"
            f"|Is onderdeel van={first_row['is_onderdeel_van_besluit']}\n"
            f"|Voorkeurslabel={first_row['voorkeurslabel_besluit']}\n"
            f"|Bron={first_row['bron_besluit']}\n"
            f"|Bron text={first_row['bron_tekst_besluit']}\n"
            f"}}}}\n"

            # 2 - Begrenzingskaart aanwijzing
            f"{{{{SourceDocument\n"
            f"|Is onderdeel van={first_row['is_onderdeel_van_kaart']}\n"
            f"|Voorkeurslabel={first_row['voorkeurslabel_kaart']}\n"
            f"|Bron={first_row['bron_kaart']}\n"
            f"|Bron text={first_row['bron_tekst_kaart']}\n"
            f"}}}}\n"


            # 3 - Toelichting aanwijzing
            f"{{{{SourceDocument\n"
            f"|Is onderdeel van={first_row['is_onderdeel_van_toelichting']}\n"
            f"|Voorkeurslabel={first_row['voorkeurslabel_toelichting']}\n"
            f"|Bron={first_row['bron_toelichting']}\n"
            f"|Bron text={first_row['bron_tekst_toelichting']}\n"
            f"}}}}\n"
            )
        # Loop over elke rij in het huidige gezicht (voor sectie 3)
            for idx, (_, row) in enumerate(gezicht_df.iterrows()):
                if idx != 0:
                    formatted_text += (
                    f"{{{{SourceDocument\n"
                    f"|Is onderdeel van={row['is_onderdeel_van_kaart']}\n"
                    f"|Voorkeurslabel={row['voorkeurslabel_kaart']}\n"
                    f"|Bron={row['bron_kaart']}\n"
                    f"|Bron text={row['bron_tekst_kaart']}\n"
                    f"}}}}\n"
                )

        
       
        # Import the page using fun_batch_import function
        edit_status = fun_batch_import(paginanaam, formatted_text)

        # Resultaat voor de user uitprinten.

        print(f"Edit Status voor Beschermde_stads-_en_dorpsgezicht {paginanaam}: {edit_status}")

        # Sleep for 1 second
        time.sleep(1)


#--------------------------------------
# Functie dat alles automatiseert; let op dat 'df' naam is dat gegeven is aan de excel file, wellicht is dit voor later handiger met een user input.
xlsx_to_markup_kennisbank(df)
