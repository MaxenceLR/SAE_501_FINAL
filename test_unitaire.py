import pytest
from unittest.mock import MagicMock, patch
from datetime import date
import backend  # On importe le module backend

# =================================================================
#  TESTS UNITAIRES (Backend)
# =================================================================

@patch('backend.connection')
def test_save_configuration_update(mock_conn):
    """Test de la mise à jour d'une configuration"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Appel de la fonction
    result = backend.save_configuration(
        context='ENTRETIEN', is_new_var=False, var_pos=1, 
        var_lib="Test Lib", var_type="CHAINE", rub_id=1, 
        comment="Commentaire", modalites=[]
    )

    # Vérifications
    assert result is True
    mock_cursor.execute.assert_called()
    mock_conn.commit.assert_called()

@patch('backend.connection')
def test_get_questionnaire_structure(mock_conn):
    """Test de récupération de la structure"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simulation des retours BDD
    # 1. Rubriques
    # 2. Variables
    # 3. Modalités (si besoin)
    mock_cursor.fetchall.side_effect = [
        [{'pos': 1, 'lib': 'Rubrique Test'}], # Rubriques
        [{'pos': 1, 'lib': 'Var 1', 'commentaire': 'Com', 'type_v': 'CHAINE', 'rubrique': 1}] # Variables
    ]

    structure = backend.get_questionnaire_structure()
    
    assert 'Rubrique Test' in structure
    assert len(structure['Rubrique Test']) == 1
    assert structure['Rubrique Test'][0]['lib'] == 'Var 1'

@patch('backend.connection')
def test_insert_full_entretien_success(mock_conn):
    """Test d'insertion d'un entretien (CORRIGÉ POUR LA NOUVELLE LOGIQUE)"""
    mock_cursor = MagicMock()
    
    # --- CORRECTION ICI ---
    # Le backend fait maintenant 2 appels 'fetchone' :
    # 1. Pour SELECT MAX(num) -> On simule qu'il trouve 98
    # 2. Pour le RETURNING num après l'insert -> On simule qu'il renvoie 99 (98+1)
    mock_cursor.fetchone.side_effect = [[98], [99]]
    
    mock_conn.cursor.return_value = mock_cursor

    data = {
        "mode": 1, "duree": 45, "sexe": 1, "age": 38,
        "vient_pr": 1, "sit_fam": 2, "enfant": 0,
        "modele_fam": None, "profession": 3, "ress": 2,
        "origine": 1, "commune": "Nantes", "partenaire": None
    }

    new_id = backend.insert_full_entretien(data)

    # Vérification que l'ID retourné est bien celui attendu
    assert new_id == 99
    
    # Vérification qu'il y a eu 2 exécutions SQL (Le SELECT MAX et l'INSERT)
    assert mock_cursor.execute.call_count == 2

@patch('backend.connection')
def test_insert_demandes(mock_conn):
    """Test d'insertion des demandes"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    backend.insert_demandes(10, ['CODE_A', 'CODE_B'])

    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called()

@patch('backend.connection')
def test_insert_solutions(mock_conn):
    """Test d'insertion des solutions"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    backend.insert_solutions(10, ['SOL_A'])

    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called()

@patch('backend.connection')
def test_upsert_rubrique_new(mock_conn):
    """Test création nouvelle rubrique"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Simule que la rubrique n'existe pas (fetchone renvoie None)
    mock_cursor.fetchone.return_value = None

    result = backend.upsert_rubrique(99, 99, "Nouvelle Rub")
    
    assert result is True
    # Vérifie qu'on a bien fait un INSERT
    assert "INSERT INTO" in mock_cursor.execute.call_args_list[-1][0][0]

@patch('backend.connection')
def test_add_variable_sql(mock_conn):
    """Test ajout variable"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    result = backend.add_variable_sql("Lib", "CHAINE", 1, 10, "Com")
    
    assert result is True
    mock_cursor.execute.assert_called()

@patch('backend.connection')
def test_get_data_for_reporting_empty(mock_conn):
    """Test reporting vide"""
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    # Simule aucun entretien
    mock_cursor.fetchall.return_value = []

    df = backend.get_data_for_reporting()
    
    assert df.empty

@patch('backend.connection')
def test_connection_failure(mock_conn):
    """Test gestion erreur connexion"""
    # On simule que la connexion est None
    with patch('backend.connection', None):
        result = backend.insert_full_entretien({})
        assert result is None