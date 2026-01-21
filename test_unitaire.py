import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from datetime import date

# --- CORRECTION DES IMPORTS ---
# On utilise les noms EXACTS présents dans votre fichier poc_global.py
from poc_global import (
    insert_demandes,
    insert_solutions,
    insert_full_entretien,
    get_data_for_reporting,
    save_configuration,
    upsert_rubrique  # <--- C'est le nom correct (remplace upsert_rubrique)
)

# --- 1. TESTS DES INSERTIONS ---

@patch('poc_global.connection')
def test_insert_demandes_success(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    insert_demandes(10, [1, 2, 3])

    # On vérifie que executemany a été appelé
    mock_cursor.executemany.assert_called_once()
    args, _ = mock_cursor.executemany.call_args
    query, params = args
    
    assert "INSERT INTO demande" in query
    assert len(params) == 3 
    assert params[0] == (10, 1, 1) 
    mock_conn.commit.assert_called_once()


@patch('poc_global.connection')
def test_insert_solutions_success(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    insert_solutions(5, [10, 20])

    mock_cursor.executemany.assert_called_once()
    mock_conn.commit.assert_called_once()


@patch('poc_global.connection')
def test_insert_full_entretien_success(mock_conn):
    mock_cursor = MagicMock()
    # Simule le retour de l'ID 99 après insertion
    mock_cursor.fetchone.return_value = [99]
    mock_conn.cursor.return_value = mock_cursor

    data = {
        "mode": 1, "duree": 45, "sexe": 1, "age": 38,
        "vient_pr": 1, "sit_fam": 2, "enfant": 0,
        "modele_fam": None, "profession": 3, "ress": 2,
        "origine": 1, "commune": "Nantes", "partenaire": None
    }

    new_id = insert_full_entretien(data)

    assert new_id == 99
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()


# --- 2. TEST DU REPORTING ---

@patch('poc_global.connection')
def test_get_data_for_reporting_decoding(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simulation des 3 appels SQL successifs faits par la fonction
    raw_data = [{"num": 100, "sexe": 1, "age": 2, "commune": "Paris"}] 
    var_mapping = [{"pos": 10, "lib": "Sexe"}, {"pos": 20, "lib": "Age"}]
    mod_mapping = [{"pos": 10, "code": "1", "lib_m": "Homme"}, {"pos": 20, "code": "2", "lib_m": "18-25 ans"}]

    # side_effect permet de renvoyer une valeur différente à chaque appel de fetchall
    mock_cursor.fetchall.side_effect = [raw_data, var_mapping, mod_mapping]

    df = get_data_for_reporting()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    # Vérification que le décodage a bien eu lieu
    assert df.iloc[0]["sexe"] == "Homme" 
    assert df.iloc[0]["age"] == "18-25 ans"


# --- 3. TESTS CONFIGURATION ---

@patch('poc_global.connection')
def test_upsert_rubrique(mock_conn):
    mock_cursor = MagicMock()
    # Simule que la rubrique n'existe pas (None), donc on fera un INSERT
    mock_cursor.fetchone.return_value = None 
    mock_conn.cursor.return_value = mock_cursor
    
    # Appel de la nouvelle fonction (old_pos, new_pos, lib)
    # On imagine qu'on crée une rubrique à la position 5
    result = upsert_rubrique(5, 5, "Nouvelle Rubrique")

    assert result is True
    # Vérifie qu'une requête INSERT a bien été préparée
    args, _ = mock_cursor.execute.call_args
    assert "INSERT INTO rubrique" in args[0]
    mock_conn.commit.assert_called_once()


@patch('poc_global.connection')
def test_save_configuration_entretien(mock_conn):
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    success = save_configuration(
        context='ENTRETIEN',
        is_new_var=False,
        var_pos=10,
        var_lib="Ma Question",
        var_type="MOD",
        rub_id=1,
        comment="Test",
        modalites=["Choix A", "Choix B"]
    )

    assert success is True
    # Vérifie qu'il y a eu au moins une exécution SQL
    assert mock_cursor.execute.call_count >= 1