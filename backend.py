import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import date
import pandas as pd

# --- PARAMÈTRES DE CONNEXION ---
PG_HOST = "localhost"
PG_PORT = 5437
PG_DB = "db_maisondudroit"
PG_USER = "pgis"
PG_PASSWORD = "pgis"

# --- INITIALISATION DE LA CONNEXION ---
def init_connection():
    try:
        conn = psycopg2.connect(
            host=PG_HOST, port=PG_PORT, database=PG_DB,
            user=PG_USER, password=PG_PASSWORD
        )
        conn.autocommit = False 
        return conn
    except Exception:
        return None 

# On initialise la variable globale ici
connection = init_connection()

# =================================================================
#  FONCTIONS SQL (LOGIQUE MÉTIER)
# =================================================================

def save_configuration(context, is_new_var, var_pos, var_lib, var_type, rub_id, comment, modalites):
    if connection is None: return False
    cursor = connection.cursor()
    try:
        if context == 'ENTRETIEN':
            if not is_new_var:
                cursor.execute("UPDATE variable SET lib=%s, type_v=%s, rubrique=%s, commentaire=%s WHERE pos=%s AND tab='ENTRETIEN'", 
                             (var_lib, var_type, rub_id, comment, var_pos))
            else:
                cursor.execute("INSERT INTO variable (tab, pos, lib, type_v, rubrique, commentaire) VALUES ('ENTRETIEN', %s, %s, %s, %s, %s)", 
                             (var_pos, var_lib, var_type, rub_id, comment))

        if var_type == 'MOD':
            cursor.execute("DELETE FROM modalite WHERE tab=%s AND pos=%s", (context, var_pos))
            if modalites:
                values = []
                for idx, txt in enumerate(modalites):
                    code = txt[:15].upper().replace(" ", "_")
                    values.append((context, var_pos, idx+1, txt, code))
                cursor.executemany("INSERT INTO modalite (tab, pos, pos_m, lib_m, code) VALUES (%s, %s, %s, %s, %s)", values)

        connection.commit()
        return True
    except Exception:
        connection.rollback()
        return False
    finally:
        cursor.close()

def get_questionnaire_structure():
    if not connection: return {}
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    structure = {}
    try:
        cursor.execute("SELECT pos, lib FROM rubrique ORDER BY pos")
        rubriques = {row['pos']: row['lib'] for row in cursor.fetchall()}

        cursor.execute("SELECT pos, lib, commentaire, type_v, rubrique FROM variable WHERE tab = %s AND type_v IN ('MOD','NUM','CHAINE') ORDER BY rubrique, pos", ('ENTRETIEN',))
        variables = cursor.fetchall()

        for var in variables:
            rubrique_lib = rubriques.get(var['rubrique'], "Autres Champs")
            if rubrique_lib not in structure: structure[rubrique_lib] = []

            var_data = {'pos': var['pos'], 'lib': var['lib'], 'type': var['type_v'], 'comment': var['commentaire'], 'options': {}}
            
            if var['type_v'] == 'MOD':
                cursor.execute("SELECT code, lib_m FROM modalite WHERE tab = %s AND pos = %s ORDER BY pos_m", ('ENTRETIEN', var['pos']))
                var_data['options'] = {row['lib_m']: row['code'] for row in cursor.fetchall()}
            elif var['type_v'] == 'NUM':
                cursor.execute("SELECT val_min, val_max FROM plage WHERE tab = %s AND pos = %s", ('ENTRETIEN', var['pos']))
                plage = cursor.fetchone()
                if plage: var_data['options'] = {'min': plage['val_min'], 'max': plage['val_max']}
            elif var['type_v'] == 'CHAINE':
                cursor.execute("SELECT lib FROM valeurs_c WHERE tab = %s AND pos = %s ORDER BY pos_c", ('ENTRETIEN', var['pos']))
                var_data['options'] = [row['lib'] for row in cursor.fetchall()]
            
            structure[rubrique_lib].append(var_data)
        return structure
    finally:
        cursor.close()

def get_demande_solution_modalites():
    if not connection: return {}, {}
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT code, lib_m FROM modalite WHERE tab = %s AND pos = 3 ORDER BY pos_m", ('DEMANDE',))
        demande_modalites = {row['lib_m']: row['code'] for row in cursor.fetchall()}
        cursor.execute("SELECT code, lib_m FROM modalite WHERE tab = %s AND pos = 3 ORDER BY pos_m", ('SOLUTION',))
        solution_modalites = {row['lib_m']: row['code'] for row in cursor.fetchall()}
        return demande_modalites, solution_modalites
    finally:
        cursor.close()

def insert_full_entretien(data):
    if not connection: return None
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO entretien (date_ent, mode, duree, sexe, age, vient_pr, sit_fam, enfant, modele_fam, profession, ress, origine, commune, partenaire)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING num
        """, (date.today(), data.get('mode'), data.get('duree'), data.get('sexe'), data.get('age'), data.get('vient_pr'), data.get('sit_fam'), data.get('enfant'), data.get('modele_fam'), data.get('profession'), data.get('ress'), data.get('origine'), data.get('commune'), data.get('partenaire')))
        new_num = cursor.fetchone()[0]
        connection.commit()
        return new_num
    except Exception:
        connection.rollback()
        return None
    finally: cursor.close()

def insert_demandes(num, codes):
    if not codes or not connection: return
    cursor = connection.cursor()
    try:
        cursor.executemany("INSERT INTO demande (num, pos, nature) VALUES (%s,%s,%s)", [(num, i+1, c) for i,c in enumerate(codes)])
        connection.commit()
    finally: cursor.close()

def insert_solutions(num, codes):
    if not codes or not connection: return
    cursor = connection.cursor()
    try:
        cursor.executemany("INSERT INTO solution (num, pos, nature) VALUES (%s,%s,%s)", [(num, i+1, c) for i,c in enumerate(codes)])
        connection.commit()
    finally: cursor.close()

def upsert_rubrique(old_pos, new_pos, lib):
    if not connection: return False
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT 1 FROM rubrique WHERE pos = %s", (old_pos,))
        exists = cursor.fetchone()
        if exists:
            cursor.execute("UPDATE rubrique SET pos = %s, lib = %s WHERE pos = %s", (new_pos, lib, old_pos))
        else:
            cursor.execute("INSERT INTO rubrique (pos, lib) VALUES (%s, %s)", (new_pos, lib))
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        return False
    finally:
        cursor.close()

def add_variable_sql(libelle, type_v, rubrique_id, position, commentaire):
    if not connection: return False
    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO variable (tab, pos, lib, type_v, rubrique, commentaire) VALUES ('ENTRETIEN', %s, %s, %s, %s, %s)", 
                      (position, libelle, type_v, rubrique_id, commentaire))
        connection.commit()
        return True
    except Exception:
        connection.rollback()
        return False

def get_data_for_reporting():
    if not connection: return pd.DataFrame()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM entretien")
        data = cursor.fetchall()
        df = pd.DataFrame(data)
        if df.empty: return df

        cursor.execute("SELECT pos, lib FROM variable WHERE tab='ENTRETIEN'")
        vars_map = {row['lib'].lower(): row['pos'] for row in cursor.fetchall()}
        
        cursor.execute("SELECT pos, code, lib_m FROM modalite WHERE tab='ENTRETIEN'")
        modalites = cursor.fetchall()
        
        decodage_map = {}
        for row in modalites:
            pos = row['pos']
            code = row['code']
            lib = row['lib_m']
            if pos not in decodage_map: decodage_map[pos] = {}
            decodage_map[pos][str(code)] = lib

        for col_name in df.columns:
            if col_name in vars_map:
                pos_var = vars_map[col_name]
                if pos_var in decodage_map:
                    df[col_name] = df[col_name].astype(str).map(decodage_map[pos_var]).fillna(df[col_name].astype(str))
        return df
    except Exception:
        return pd.DataFrame()
    finally:
        cursor.close()