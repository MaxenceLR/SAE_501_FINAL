import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
import os

APP_URL = "http://localhost:8501/"
TIMEOUT = 20

# ==========================
# INIT FIREFOX
# ==========================
options = webdriver.FirefoxOptions()
#options.add_argument("--headless")  # mode sans affichage
options.add_argument("--width=1920")
options.add_argument("--height=1080")

profile_path = r"H:\Temp\FirefoxProfile"
os.makedirs(profile_path, exist_ok=True)
options.profile = profile_path

driver = webdriver.Firefox(
    service=Service(GeckoDriverManager().install()),
    options=options
)

wait = WebDriverWait(driver, TIMEOUT)

# ==========================
# HELPER POUR SELECTBOX STREAMLIT
# ==========================
def remplir_selectbox(label, valeur):
    """
    Remplit un selectbox Streamlit basé sur l'aria-label.
    """
    input_elem = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"input[aria-label=\"**{label}**\"]"))
    )
    input_elem.click()
    input_elem.clear()
    input_elem.send_keys(valeur)
    input_elem.send_keys(Keys.ENTER)

# ==========================
# TEST FORMULAIRE
# ==========================
try:
    print("Ouverture de l'app Streamlit...")
    driver.get(APP_URL)

    # Attendre le formulaire
    wait.until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(),\"Saisie d'un nouvel entretien\")]"))
    )

    # ==========================
    # REMPLISSAGE DES CHAMPS
    # ==========================
    remplir_selectbox("MODE", "RDV")
    remplir_selectbox("DUREE", "- de 15 min")
    remplir_selectbox("SEXE", "Homme")
    remplir_selectbox("AGE", "26-40 ans")
    remplir_selectbox("VIENT_PR", "Soi")
    remplir_selectbox("SIT_FAM", "Célibataire")
    remplir_selectbox("ENFANT", "2")

    # Si famille avec enfant, remplir le modèle familial
    enfant_val = int(driver.find_element(By.CSS_SELECTOR, "input[aria-label='**ENFANT**']").get_attribute("value"))
    if enfant_val > 0:
        remplir_selectbox("MODELE_FAM", "Famille traditionnelle")

    remplir_selectbox("PROFESSION", "Cadre")
    remplir_selectbox("RESS", "Salaire")
    remplir_selectbox("ORIGINE", "3949 NUAD")
    remplir_selectbox("COMMUNE", "Paris")
    remplir_selectbox("PARTENAIRE", "CAF")

    # ==========================
    # DEMANDES / SOLUTIONS (multiselect)
    # ==========================
    demande_input = driver.find_element(By.XPATH, "//div[contains(.,'Nature de la demande')]/following::input[1]")
    demande_input.send_keys("Droit administratif Droit des étrangers")
    demande_input.send_keys(Keys.ENTER)
    demande_input.send_keys("Droit administratif Autre")
    demande_input.send_keys(Keys.ENTER)

    solution_input = driver.find_element(By.XPATH, "//div[contains(.,'Réponse apportée')]/following::input[1]")
    solution_input.send_keys("Information")
    solution_input.send_keys(Keys.ENTER)

    # ==========================
    # BOUTON ENREGISTRER
    # ==========================
    submit_btn = driver.find_element(By.XPATH, "//button[contains(.,\"ENREGISTRER L'ENTRETIEN\")]")
    submit_btn.click()

    # ==========================
    # VERIFICATION DU SUCCÈS
    # ==========================
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'enregistré')]")))
    print("✅ Formulaire testé avec succès !")

except Exception as e:
    print("❌ Échec test formulaire :", e)
    driver.save_screenshot("erreur_test.png")
    print("📸 Screenshot enregistré : erreur_test.png")

finally:
    time.sleep(2)
    driver.quit()
