import os
import json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

barangay_list_path = os.path.join(BASE_DIR, 'assets/jsons/barangay_list.json')
with open(barangay_list_path, 'r', encoding='utf-8') as f:
    barangay_list = json.load(f)

league_categories_list_path = os.path.join(BASE_DIR, 'assets/jsons/league_categories.json')
with open(league_categories_list_path, 'r', encoding='utf-8') as f:
    league_categories_list = json.load(f)

organization_type_list_path = os.path.join(BASE_DIR, 'assets/jsons/organization_types.json')
with open(organization_type_list_path, 'r', encoding='utf-8') as f:
    organization_type_list = json.load(f)