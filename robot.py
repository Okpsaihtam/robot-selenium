from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import os

# Sur GitHub, la variable "CI" existe : pas besoin de pauses
PAUSE = 0 if os.getenv("CI") else 0.8


def pause():
    time.sleep(PAUSE)


# ---------- Fonctions utiles ----------
nombre_verifications = 0


def verifier(condition, description):
    """Vérifie qu'une condition est vraie. Sinon, le test s'arrête en échec."""
    global nombre_verifications
    if condition:
        nombre_verifications += 1
        print("   ✅", description)
    else:
        raise AssertionError(description)


def prix_en_nombre(texte):
    """Transforme un prix affiché ("$29.99") en nombre (29.99)."""
    return float(texte.replace("$", ""))


# ---------- Préparation de Chrome ----------
options = webdriver.ChromeOptions()
# Désactive les popups de mots de passe de Chrome, qui gênent le robot
options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
})

# Sur GitHub, il n'y a pas d'écran : Chrome tourne en mode invisible
if os.getenv("CI"):
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)  # attend jusqu'à 10 secondes maximum
code_sortie = 0  # 0 = réussite, 1 = échec

try:
    # ---------- 1. Ouvrir le site ----------
    print("1. Ouverture du site")
    driver.get("https://www.saucedemo.com")
    verifier(driver.title == "Swag Labs", "Le site est bien ouvert")
    pause()

    # ---------- 2. Se connecter ----------
    print("2. Connexion")
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    pause()
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    pause()
    driver.find_element(By.ID, "login-button").click()
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))

    verifier("inventory" in driver.current_url, "On est sur la page des produits")
    produits = driver.find_elements(By.CLASS_NAME, "inventory_item")
    verifier(len(produits) == 6, "Les 6 produits sont affichés")
    pause()

    # ---------- 3. Trier les produits par prix ----------
    print("3. Tri des produits du moins cher au plus cher")
    Select(driver.find_element(By.CLASS_NAME, "product_sort_container")).select_by_value("lohi")
    pause()

    prix = [prix_en_nombre(p.text) for p in driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
    print("   Prix affichés :", prix)
    verifier(prix == sorted(prix), "Les prix sont bien triés du moins cher au plus cher")

    # ---------- 4. Ajouter 2 produits au panier ----------
    print("4. Ajout de 2 produits au panier")
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    pause()
    driver.find_element(By.ID, "add-to-cart-sauce-labs-bike-light").click()
    pause()
    nombre = driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
    verifier(nombre == "2", "Le panier affiche 2 articles")

    # ---------- 5. Ouvrir le panier ----------
    print("5. Ouverture du panier")
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart"))
    pause()

    noms_panier = [n.text for n in driver.find_elements(By.CLASS_NAME, "inventory_item_name")]
    print("   Produits dans le panier :", noms_panier)
    verifier("Sauce Labs Backpack" in noms_panier, "Le sac à dos est dans le panier")
    verifier("Sauce Labs Bike Light" in noms_panier, "La lampe de vélo est dans le panier")

    # On calcule nous-mêmes le total attendu
    prix_panier = [prix_en_nombre(p.text) for p in driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
    total_attendu = round(sum(prix_panier), 2)

    # ---------- 6. Passer commande ----------
    print("6. Remplissage du formulaire de commande")
    driver.find_element(By.ID, "checkout").click()
    pause()
    driver.find_element(By.ID, "first-name").send_keys("Jean")
    pause()
    driver.find_element(By.ID, "last-name").send_keys("Dupont")
    pause()
    driver.find_element(By.ID, "postal-code").send_keys("75001")
    pause()
    driver.find_element(By.ID, "continue").click()

    sous_total = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "summary_subtotal_label"))).text
    print("   Affiché par le site :", sous_total, "| Calculé par le robot :", total_attendu)
    verifier(sous_total == f"Item total: ${total_attendu}", "Le montant de la commande est correct")
    pause()
    driver.find_element(By.ID, "finish").click()

    # ---------- 7. Lire la confirmation ----------
    message = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header"))).text
    print("7. Message affiché :", message)
    verifier(message == "Thank you for your order!", "La commande est confirmée")
    pause()

    # ---------- 8. Retour à l'accueil et déconnexion ----------
    print("8. Retour à l'accueil et déconnexion")
    driver.find_element(By.ID, "back-to-products").click()
    pause()
    verifier(len(driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")) == 0,
             "Le panier est vide après la commande")
    driver.find_element(By.ID, "react-burger-menu-btn").click()
    wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))).click()
    bouton = wait.until(EC.visibility_of_element_located((By.ID, "login-button")))
    verifier(bouton.is_displayed(), "On est bien déconnecté")

# Si une vérification ou une action a échoué, on arrive ici
except Exception as erreur:
    code_sortie = 1
    driver.save_screenshot("erreur.png")
    print()
    print("❌ TEST ÉCHOUÉ")
    print("   Problème :", type(erreur).__name__, "-", erreur)
    print("   Capture d'écran enregistrée : erreur.png")

# Si tout s'est bien passé, on arrive ici
else:
    print()
    print(f"✅ TEST RÉUSSI : {nombre_verifications} vérifications réussies")

# Dans tous les cas, on ferme le navigateur
finally:
    driver.quit()
    sys.exit(code_sortie)