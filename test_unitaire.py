import pytest
from unittest.mock import MagicMock, patch
from datetime import date
import backend  # On importe le module backend

# =================================================================
#  TESTS CAS NOMINAUX (Tout va bien)
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
    
    # --- CORRECTION 1 : Ajout de la clé 'commentaire' ---
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
    """Test insertion succès (ID calculé)"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [[98], [99]] # Max ID puis Returning ID
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
    
    # Cas 1 : Création (n'existe pas)
    mock_cursor.fetchone.return_value = None 
    backend.upsert_rubrique(1, 1, "New")
    assert "INSERT INTO" in mock_cursor.execute.call_args_list[-1][0][0]

    # Cas 2 : Modification (existe)
    mock_cursor.fetchone.return_value = [1] 
    backend.upsert_rubrique(1, 1, "Update")
    assert "UPDATE rubrique" in mock_cursor.execute.call_args_list[-1][0][0]

@patch('backend.connection')
def test_add_variable_sql(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    assert backend.add_variable_sql("L", "T", 1, 1, "C") is True

@patch('backend.connection')
def test_get_data_for_reporting(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.side_effect = [[{'sexe':'1'}], [{'pos':1,'lib':'Sexe'}], [{'pos':1,'code':'1','lib_m':'H'}]]
    df = backend.get_data_for_reporting()
    assert df.iloc[0]['sexe'] == 'H'

# =================================================================
#  TESTS DE GESTION D'ERREURS
# =================================================================

@patch('backend.connection')
def test_db_exceptions(mock_conn):
    """Vérifie que le code ne plante pas si la BDD renvoie une erreur"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # On configure le mock pour qu'il lève une erreur à chaque appel
    mock_cursor.execute.side_effect = Exception("Boom BDD")
    
    # Test Exception sur insert_full_entretien
    assert backend.insert_full_entretien({}) is None
    
    # Test Exception sur save_configuration
    # --- CORRECTION 2 : On utilise 'ENTRETIEN' pour forcer l'entrée dans le bloc SQL ---
    assert backend.save_configuration('ENTRETIEN', False, 1, 'B', 'C', 1, 'D', []) is False
    
    # Test Exception sur upsert_rubrique
    assert backend.upsert_rubrique(1, 1, "A") is False
    
    # Test Exception sur add_variable_sql
    assert backend.add_variable_sql("A", "B", 1, 1, "C") is False
    
    # Test Exception reporting
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