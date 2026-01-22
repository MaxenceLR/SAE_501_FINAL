import pytest
from unittest.mock import MagicMock, patch
from datetime import date
import pandas as pd
import backend  # On importe le module backend

# =================================================================
#  TESTS INITIALISATION & CONNEXION (Pour couvrir le haut du fichier)
# =================================================================

@patch('psycopg2.connect')
def test_init_connection_fail(mock_connect):
    """Test le bloc except de init_connection"""
    # On simule une erreur de connexion (ex: mauvais mot de passe)
    mock_connect.side_effect = Exception("Erreur de connexion")
    
    # On appelle manuellement la fonction pour vérifier qu'elle renvoie None
    # et qu'elle passe bien dans le 'except'
    conn = backend.init_connection()
    assert conn is None

# =================================================================
#  TESTS CAS NOMINAUX
# =================================================================

@patch('backend.connection')
def test_save_configuration_update(mock_conn):
    """Test UPDATE configuration"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    result = backend.save_configuration('ENTRETIEN', False, 1, "Lib", "CHAINE", 1, "Com", [])
    assert result is True
    assert "UPDATE variable" in mock_cursor.execute.call_args_list[0][0][0]

@patch('backend.connection')
def test_save_configuration_insert(mock_conn):
    """Test INSERT configuration"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    result = backend.save_configuration('ENTRETIEN', True, 2, "New", "MOD", 1, "Com", ["A", "B"])
    assert result is True
    assert "INSERT INTO variable" in mock_cursor.execute.call_args_list[0][0][0]

@patch('backend.connection')
def test_get_questionnaire_structure(mock_conn):
    """Test structure complète"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.fetchall.side_effect = [
        [{'pos': 1, 'lib': 'Rub'}], # Rubriques
        [{'pos': 1, 'lib': 'V1', 'type_v': 'CHAINE', 'rubrique': 1, 'commentaire': 'Test Com'}], # Vars
        [{'lib': 'Opt'}] # Options CHAINE
    ]
    res = backend.get_questionnaire_structure()
    assert 'Rub' in res

@patch('backend.connection')
def test_get_demande_solution_modalites(mock_conn):
    """Test listes déroulantes"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.side_effect = [[{'code':'A','lib_m':'A'}], [{'code':'B','lib_m':'B'}]]
    d, s = backend.get_demande_solution_modalites()
    assert 'A' in d and 'B' in s

@patch('backend.connection')
def test_insert_full_entretien_success(mock_conn):
    """Test insertion succès"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [[98], [99]] 
    mock_conn.cursor.return_value = mock_cursor
    data = {"mode": 1, "duree": 45, "sexe": 1, "age": 38, "vient_pr": 1, "sit_fam": 2, 
            "enfant": 0, "modele_fam": None, "profession": 3, "ress": 2, 
            "origine": 1, "commune": "Nantes", "partenaire": None}
    assert backend.insert_full_entretien(data) == 99

@patch('backend.connection')
def test_insert_demandes_solutions(mock_conn):
    """Test insertion demandes et solutions"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    backend.insert_demandes(10, ['A'])
    backend.insert_solutions(10, ['B'])
    assert mock_cursor.executemany.call_count == 2

@patch('backend.connection')
def test_upsert_rubrique_cases(mock_conn):
    """Test Création ET Modification rubrique"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Cas 1 : Création
    mock_cursor.fetchone.return_value = None 
    backend.upsert_rubrique(1, 1, "New")
    assert "INSERT INTO" in mock_cursor.execute.call_args_list[-1][0][0]

    # Cas 2 : Modification
    mock_cursor.fetchone.return_value = [1] 
    backend.upsert_rubrique(1, 1, "Update")
    assert "UPDATE rubrique" in mock_cursor.execute.call_args_list[-1][0][0]

@patch('backend.connection')
def test_add_variable_sql(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    assert backend.add_variable_sql("L", "T", 1, 1, "C") is True

@patch('backend.connection')
def test_get_data_for_reporting_complex(mock_conn):
    """Test reporting avec colonnes mixtes (mappées et non mappées)"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Données : 'sexe' (à decoder), 'ville' (texte simple), 'inconnu' (pas dans les variables)
    data = [{'sexe': '1', 'ville': 'Paris', 'inconnu': 'X'}]
    
    mock_cursor.fetchall.side_effect = [
        data, # Retour du SELECT * FROM entretien
        [{'pos': 10, 'lib': 'Sexe'}, {'pos': 20, 'lib': 'Ville'}], # Mapping Variables
        [{'pos': 10, 'code': '1', 'lib_m': 'Homme'}] # Mapping Modalités (Seulement pour Sexe)
    ]

    df = backend.get_data_for_reporting()
    
    # Vérifications
    assert not df.empty
    # 'sexe' doit être traduit de '1' à 'Homme'
    assert df.iloc[0]['sexe'] == 'Homme'
    # 'ville' est dans vars_map mais pas dans decodage_map -> doit rester 'Paris'
    assert df.iloc[0]['ville'] == 'Paris'
    # 'inconnu' n'est pas dans vars_map -> doit rester 'X'
    assert df.iloc[0]['inconnu'] == 'X'

# =================================================================
#  TESTS DE GESTION D'ERREURS
# =================================================================

@patch('backend.connection')
def test_db_exceptions(mock_conn):
    """Vérifie que le code ne plante pas si la BDD renvoie une erreur"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    mock_cursor.execute.side_effect = Exception("Boom BDD")
    
    assert backend.insert_full_entretien({}) is None
    assert backend.save_configuration('ENTRETIEN', False, 1, 'B', 'C', 1, 'D', []) is False
    assert backend.upsert_rubrique(1, 1, "A") is False
    assert backend.add_variable_sql("A", "B", 1, 1, "C") is False
    assert backend.get_data_for_reporting().empty

def test_connection_none():
    """Vérifie le comportement si la connexion est perdue (None)"""
    with patch('backend.connection', None):
        assert backend.save_configuration('A', False, 1, 'B', 'C', 1, 'D', []) is False
        assert backend.get_questionnaire_structure() == {}
        assert backend.get_demande_solution_modalites() == ({}, {})
        assert backend.insert_full_entretien({}) is None
        assert backend.insert_demandes(1, []) is None 
        assert backend.insert_solutions(1, []) is None
        assert backend.upsert_rubrique(1, 1, "A") is False
        assert backend.add_variable_sql("A", "B", 1, 1, "C") is False
        assert backend.get_data_for_reporting().empty