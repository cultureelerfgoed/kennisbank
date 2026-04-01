import json
import os
import logging
import requests
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SDO
from _CEO import CEO
 
GRAPH_ID = os.getenv('GRAPH_ID', 'default')
OUTPUT_FILE_FORMAT = os.getenv('OUTPUT_FILE_FORMAT', 'json-ld')
TARGET_FILEPATH = os.getenv('TARGET_FILEPATH', 'monumenten_kennisbank.jsonld')
SRC_URI = os.getenv('SRC_URI', 'https://kennis.cultureelerfgoed.nl/api.php')
ENCODING = os.getenv('ENCODING', 'utf-8')

KB_MO_QUERY = '[[Categorie:Monumenten]]|limit=2000|?Batch|?Status|?Monumentnummer|?Complex|?Plaatsnaam' \
'|?Adres|?Naam monument|?Introductie|?Kenmerken|?Omschrijving|?Kennis|?Afbeelding (extern)|?Gerelateerd aan monument|?Gerelateerd aan artikel' \
'|?Gerelateerd aan gezicht|?Gerelateerd aan thema'

logger = logging.getLogger(__name__)

def get_mwquery_response_as_json(from_url: str, query: str):
    """ Get query response from URI """
    get_params = {
        'action': 'ask',
        'query': query,
        'format': 'json'
    }
    response = requests.get(from_url, params=get_params, timeout=100)
    logger.info('Query response from %s received', from_url)
    return json.loads(response.text)

def parse_json_to_graph(mo_json: dict, graph_id: str) -> Graph:
    """ Return graph from query response as JSON dict """

    graph = Graph(identifier=graph_id)

    for result in mo_json['query']['results']:
        monument_properties = mo_json['query']['results'][result]['printouts']
        rm = URIRef(mo_json['query']['results'][result]['fullurl'])

        for mprop in monument_properties:
            if monument_properties[mprop]:
                if 'Complex' in mprop and 'Nee' in monument_properties[mprop][0]:
                    graph.add((rm, RDF.type, CEO.Rijksmonument))
                elif 'Complex' in mprop and 'Ja' in monument_properties[mprop][0]:
                    graph.add((rm, RDF.type, CEO.Complex))
                elif 'Monumentnummer' in mprop:
                    graph.add((rm, CEO.rijksmonumentnummer, Literal(monument_properties[mprop][0])))
                elif 'Plaatsnaam' in mprop:
                    graph.add((rm, CEO.heeftLocatieAanduiding, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Adres' in mprop:
                    graph.add((rm, SDO.address, Literal(monument_properties[mprop][0])))
                elif 'Naam monument' in mprop:
                    graph.add((rm, CEO.heeftNaam, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Introductie' in mprop:
                    graph.add((rm, SDO.disambiguatingDescription, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Kenmerken' in mprop:
                    graph.add((rm, CEO.heeftStijlEnCultuur, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Omschrijving' in mprop:
                    graph.add((rm, CEO.heeftOmschrijving, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Afbeelding (extern)' in mprop:
                    graph.add((rm, SDO.image, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Gerelateerd aan monument' in mprop:
                    pass
                elif 'Gerelateerd aan artikel' in mprop:
                    graph.add((rm, SDO.subjectOf, Literal(monument_properties[mprop][0], lang='nl')))
                elif 'Gerelateerd aan gezicht' in mprop:
                    pass
                elif 'Gerelateerd aan thema' in mprop:
                    pass
                elif not 'Batch' in mprop and not 'Status' in mprop:
                    logger.info('Found unmapped field %s containing %s', mprop, monument_properties[mprop][0])
            
    return graph

def main():
    """ main runner for workflow """
    logging.basicConfig(
        format='%(asctime)s %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')

    try:
        kennisbank_monumenten_json = get_mwquery_response_as_json(SRC_URI, KB_MO_QUERY)
        with open('monumenten_kennisbank.json', 'w', encoding=ENCODING) as file:
            json.dump(kennisbank_monumenten_json, file)
        graph = parse_json_to_graph(kennisbank_monumenten_json, GRAPH_ID)
        logger.info("Writing  %s", f"{OUTPUT_FILE_FORMAT} file to {TARGET_FILEPATH}")
        graph.serialize(format=OUTPUT_FILE_FORMAT, destination=TARGET_FILEPATH, encoding=ENCODING, auto_compact=True)  
        logger.info("Filesize:  %s", f"{os.path.getsize(TARGET_FILEPATH)} bytes")
    except OSError as oe:
        logger.warning('Failed to write monumenten from Kennisbank to file: %s', oe)

if __name__ == '__main__':
    main()