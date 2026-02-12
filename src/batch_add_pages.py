# 20 november 2025 - Dick van Mersbergen / Jonathan Blok
# Dit script voegt in bulk een nieuw veld toe aan bestaande pagina's op de Kennisbank

import getpass
from urllib.error import URLError
from requests import JSONDecodeError, Session
import pandas as pd
import mwparserfromhell as mwp

TEST = True

def get_session(base_url: str, username: str, password: str) -> Session:
    """Iniates authenticated session"""
    session = Session()

    # Ophalen login token
    login_token_url = f'{base_url}?action=query&meta=tokens&type=login&format=json'
    login_token_response = session.get(login_token_url)
    login_token = login_token_response.json()['query']['tokens']['logintoken']

    # Login
    login_url = f'{base_url}?action=login&format=json'
    login_params = {
        'lgtoken': login_token,
        'lgname': username,
        'lgpassword': password
    }
    session.post(login_url, data=login_params)
    return session

def get_page_as_json(session: Session, base_url: str, page_name: str) -> list[str]:
    """"Gets wikitext page as json"""
    get_params = {
        'action': 'parse',
        'page': page_name,
        'prop': 'wikitext',
        'format': 'json'
    }
    response = session.get(base_url, params=get_params)
    json_data = response.json()
    # Extract the wikitext content and split it into lines
    if 'parse' in json_data and 'wikitext' in json_data['parse'] and '*' in json_data['parse']['wikitext']:
        wikitext = json_data['parse']['wikitext']['*']
        return wikitext
    # Handle cases where wikitext might not be found as expected
    raise URLError(f'Geen wiktext gevonden voor pagina {page_name}. Respons: {json_data}')

def post_edit(session: Session, base_url: str, page_name: str, edit_token, content: str, test_run=False) -> str:
    """"Posts an edit to an authenticated session"""
    edit_params = {
        'action': 'edit',
        'title': page_name,
        'format': 'json',
        'token': edit_token,
        'text': content,
        'minor': True,
        'nocreate': True,
        'contentmodel': 'wikitext' }
    if not test_run:
        edit_response = session.post(base_url, data=edit_params)
        return edit_response.json()["edit"]["result"]
    return "Test OK"

def add_field(txtwiki: str, kbank_field_name: str, kbank_field_val: str) -> str:
    """ Converts provided string to a Wikicode object and checks if field is absent or empty, then adds field and/or val """   
    wikicode = mwp.parse(txtwiki)
    template = wikicode.filter_templates()[0]
    node = template.get(kbank_field_name, None)
    if not node or len(list(filter(lambda a: not a.isspace(), filter(str.isprintable, node.value)))) == 0:
        template.add(kbank_field_name, kbank_field_val)
        wikicode.replace(wikicode.filter_templates()[0], template)
        return str(wikicode)
    else:
        raise AssertionError(f'Veld "{kbank_field_name}" is niet leeg, bevat "{''.join(list(filter(str.isprintable, node.value)))}"')

def main():
    """ main runner running as notebook """
    excel_file_path = input('Documentpad (in de vorm /home/user/Documents/excel.xlsx): ')
    try:
        df = pd.read_excel(excel_file_path)
        df = df.reset_index()  # make sure indexes pair with number of rows
    except FileNotFoundError as fne:
        print(f'Bestand niet gevonden: {str(fne)}')
        return 0

    base_url = input('API: ')
    username = input('Gebruikersnaam: ')
    password = getpass.getpass(prompt='Wachtwoord: ')
    kbank_field_name = input('Welk veld moet worden toegevoegd? (Zoals op de Kennisbank weergegeven, bv. "Gerelateerd aan gezicht" zonder quotes.): ')
    xls_field_name = input('In welk veld in de Excel sheet staat de data? (Bv. "gerelateerd_aan_gezicht" zonder quotes): ')
    session = get_session(base_url, username, password)
    # Get the edit token
    edit_token_url = f"{base_url}?action=query&meta=tokens&type=csrf&format=json"
    edit_token_response = session.get(edit_token_url)
    edit_token = edit_token_response.json()["query"]["tokens"]["csrftoken"]

    print(f'[ {len(df)} Kennisbank pagina\'s gevonden in Excel sheet, test-modus: {TEST}, API: {base_url} ]')

    for index, row in df.iterrows():
        try:
            page_name = (row['paginanaam']).rstrip().replace("\n","")
            page_data = get_page_as_json(session, base_url, page_name)
            new_page_content = add_field(page_data, kbank_field_name, row[xls_field_name])

            if new_page_content:                
                edit_status = post_edit(session, base_url, page_name, edit_token, new_page_content, TEST)
                new_page_data = get_page_as_json(session, base_url, page_name)
                assert (TEST or row[xls_field_name] in new_page_data), f"[{index+1}] <{page_name}> Fout bij valideren wijziging, pagina niet gewijzigd."
            else:
                edit_status = "Pagina niet gewijzigd"

            print(f"[{index+1}] <{page_name}> Edit status : {edit_status}")
        except KeyError as ke:
            print(f"[{index+1}] <{page_name}> Waarde niet in Excel bestand gevonden. {str(ke)}")
        except AssertionError as ae:
            print(f"[{index+1}] <{page_name}> Validatiefout: {str(ae)}")
        except TypeError as te: 
            print(f"[{index+1}] <{page_name}> Fout bij openen bronbestand: {str(te)}")
        except (URLError, JSONDecodeError) as ue:
            print(f"[{index+1}] <{page_name}> Fout bij het ophalen van pagina: {str(ue)}")

if __name__ == "__main__":
    main()
