from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# Temps de pause entre chaque action (en secondes), pour bien voir ce qui se passe
PAUSE = 0.8


def pause():
    time.sleep(PAUSE)


# ---------- Préparation de Chrome ----------
options = webdriver.ChromeOptions()
# Désactive les popups de mots de passe de Chrome, qui gênent le robot
options.add_experimental_option("prefs", {
    "credentials_enable_service": False,
    "profile.password_manager_enabled": False,
    "profile.password_manager_leak_detection": False,
})

driver = webdriver.Chrome(options=options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)  # attend jusqu'à 10 secondes maximum qu'un élément apparaisse

try:
    # ---------- 1. Ouvrir le site ----------
    print("1. Ouverture du site")
    driver.get("https://www.saucedemo.com")
    pause()

    # ---------- 2. Se connecter ----------
    print("2. Connexion")
    driver.find_element(By.ID, "user-name").send_keys("standard_user")
    pause()
    driver.find_element(By.ID, "password").send_keys("secret_sauce")
    pause()
    driver.find_element(By.ID, "login-button").click()

    # On attend que la liste des produits soit affichée
    wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))
    print("   Connecté ! Adresse actuelle :", driver.current_url)
    pause()

    # ---------- 3. Trier les produits par prix ----------
    print("3. Tri des produits du moins cher au plus cher")
    menu_tri = Select(driver.find_element(By.CLASS_NAME, "product_sort_container"))
    menu_tri.select_by_value("lohi")
    pause()

    noms = driver.find_elements(By.CLASS_NAME, "inventory_item_name")
    prix = driver.find_elements(By.CLASS_NAME, "inventory_item_price")
    for nom, p in zip(noms, prix):
        print("   -", nom.text, ":", p.text)

    # ---------- 4. Ajouter 2 produits au panier ----------
    print("4. Ajout de 2 produits au panier")
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    pause()
    driver.find_element(By.ID, "add-to-cart-sauce-labs-bike-light").click()
    pause()
    nombre = driver.find_element(By.CLASS_NAME, "shopping_cart_badge").text
    print("   Articles dans le panier :", nombre)

    # ---------- 5. Ouvrir le panier ----------
    print("5. Ouverture du panier")
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    wait.until(EC.url_contains("cart"))
    pause()

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

    total = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "summary_total_label"))).text
    print("   Récapitulatif ->", total)
    pause()
    driver.find_element(By.ID, "finish").click()

    # ---------- 7. Lire la confirmation ----------
    message = wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "complete-header"))).text
    print("7. Message affiché :", message)
    pause()

    # ---------- 8. Retour à l'accueil et déconnexion ----------
    print("8. Retour à l'accueil et déconnexion")
    driver.find_element(By.ID, "back-to-products").click()
    pause()
    driver.find_element(By.ID, "react-burger-menu-btn").click()
    wait.until(EC.element_to_be_clickable((By.ID, "logout_sidebar_link"))).click()
    pause()

    print("Terminé : le robot a fait tout le parcours !")

finally:
    # Quoi qu'il arrive (même en cas d'erreur), on ferme le navigateur
    driver.quit()