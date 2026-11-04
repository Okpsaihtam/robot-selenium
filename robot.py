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


# ---------- Fonctions de vérification ----------
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


# ---------- Fonctions d'action (elles attendent TOUJOURS que l'élément soit prêt) ----------
def trouver(par, valeur):
    """Attend qu'un élément soit visible, puis le renvoie."""
    return wait.until(EC.visibility_of_element_located((par, valeur)))


def trouver_tous(par, valeur):
    """Attend qu'au moins un élément soit visible, puis les renvoie tous."""
    trouver(par, valeur)
    return driver.find_elements(par, valeur)


def cliquer(par, valeur):
    """Attend qu'un élément soit cliquable, puis clique dessus."""
    wait.until(EC.element_to_be_clickable((par, valeur))).click()


def ecrire(par, valeur, texte):
    """Attend qu'un champ soit visible, puis tape le texte dedans."""
    trouver(par, valeur).send_keys(texte)


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
    trouver(By.ID, "login-button")
    verifier(driver.title == "Swag Labs", "Le site est bien ouvert")
    pause()

    # ---------- 2. Se connecter ----------
    print("2. Connexion")
    ecrire(By.ID, "user-name", "standard_user")
    pause()
    ecrire(By.ID, "password", "secret_sauce")
    pause()
    cliquer(By.ID, "login-button")

    produits = trouver_tous(By.CLASS_NAME, "inventory_item")
    verifier("inventory" in driver.current_url, "On est sur la page des produits")
    verifier(len(produits) == 6, "Les 6 produits sont affichés")
    pause()

    # ---------- 3. Trier les produits par prix ----------
    print("3. Tri des produits du moins cher au plus cher")
    Select(trouver(By.CLASS_NAME, "product_sort_container")).select_by_value("lohi")
    pause()

    prix = [prix_en_nombre(p.text) for p in trouver_tous(By.CLASS_NAME, "inventory_item_price")]
    print("   Prix affichés :", prix)
    verifier(prix == sorted(prix), "Les prix sont bien triés du moins cher au plus cher")

    # ---------- 4. Ajouter 2 produits au panier ----------
    print("4. Ajout de 2 produits au panier")
    cliquer(By.ID, "add-to-cart-sauce-labs-backpack")
    pause()
    cliquer(By.ID, "add-to-cart-sauce-labs-bike-light")
    pause()
    nombre = trouver(By.CLASS_NAME, "shopping_cart_badge").text
    verifier(nombre == "2", "Le panier affiche 2 articles")

    # ---------- 5. Ouvrir le panier ----------
    print("5. Ouverture du panier")
    cliquer(By.CLASS_NAME, "shopping_cart_link")
    trouver(By.ID, "checkout")  # on attend que la page du panier soit affichée
    pause()

    noms_panier = [n.text for n in trouver_tous(By.CLASS_NAME, "inventory_item_name")]
    print("   Produits dans le panier :", noms_panier)
    verifier("Sauce Labs Backpack" in noms_panier, "Le sac à dos est dans le panier")
    verifier("Sauce Labs Bike Light" in noms_panier, "La lampe de vélo est dans le panier")

    # On calcule nous-mêmes le total attendu
    prix_panier = [prix_en_nombre(p.text) for p in trouver_tous(By.CLASS_NAME, "inventory_item_price")]
    total_attendu = round(sum(prix_panier), 2)

    # ---------- 6. Passer commande ----------
    print("6. Remplissage du formulaire de commande")
    cliquer(By.ID, "checkout")
    pause()
    ecrire(By.ID, "first-name", "Jean")
    pause()
    ecrire(By.ID, "last-name", "Dupont")
    pause()
    ecrire(By.ID, "postal-code", "75001")
    pause()
    cliquer(By.ID, "continue")

    sous_total = trouver(By.CLASS_NAME, "summary_subtotal_label").text
    print("   Affiché par le site :", sous_total, "| Calculé par le robot :", total_attendu)
    verifier(sous_total == f"Item total: ${total_attendu}", "Le montant de la commande est correct")
    pause()
    cliquer(By.ID, "finish")

    # ---------- 7. Lire la confirmation ----------
    message = trouver(By.CLASS_NAME, "complete-header").text
    print("7. Message affiché :", message)
    verifier(message == "Thank you for your order!", "La commande est confirmée")
    pause()

    # ---------- 8. Retour à l'accueil et déconnexion ----------
    print("8. Retour à l'accueil et déconnexion")
    cliquer(By.ID, "back-to-products")
    trouver(By.CLASS_NAME, "inventory_list")  # on attend le retour sur la page produits
    pause()
    verifier(len(driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")) == 0,
             "Le panier est vide après la commande")
    cliquer(By.ID, "react-burger-menu-btn")
    cliquer(By.ID, "logout_sidebar_link")
    bouton = trouver(By.ID, "login-button")
    verifier(bouton.is_displayed(), "On est bien déconnecté")

# Si une vérification ou une action a échoué, on arrive ici
except Exception as erreur:
    code_sortie = 1
    driver.save_screenshot("erreur.png")
    print()
    print("❌ TEST ÉCHOUÉ")
    # .splitlines()[0] garde seulement la première ligne de l'erreur (sans le long "Stacktrace")
    detail = str(erreur).splitlines()[0] if str(erreur) else ""
    print("   Problème :", type(erreur).__name__, "-", detail)
    print("   Capture d'écran enregistrée : erreur.png")

# Si tout s'est bien passé, on arrive ici
else:
    print()
    print(f"✅ TEST RÉUSSI : {nombre_verifications} vérifications réussies")

# Dans tous les cas, on ferme le navigateur
finally:
    driver.quit()
    sys.exit(code_sortie)