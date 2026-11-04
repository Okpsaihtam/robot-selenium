# Robot Selenium : parcours d'achat automatisé

Script Python qui pilote Google Chrome avec **Selenium** pour réaliser tout seul un parcours d'achat complet sur le site de démonstration [saucedemo.com](https://www.saucedemo.com).

## Ce que fait le robot

1. Se connecte au site
2. Trie les produits par prix et les affiche dans le terminal
3. Ajoute 2 produits au panier
4. Remplit le formulaire de commande et valide
5. Lit le message de confirmation
6. Se déconnecte

## Technologies utilisées

- **Python 3**
- **Selenium 4** : pilotage du navigateur, recherche d'éléments (`By.ID`, `By.CLASS_NAME`), attentes explicites (`WebDriverWait`), menus déroulants (`Select`)

## Lancer le projet

Prérequis : Python 3 et Google Chrome installés.

```
git clone https://github.com/Okpsaihtam/robot-selenium.git
cd robot-selenium
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python robot.py
```

Une fenêtre Chrome s'ouvre et le robot réalise le parcours tout seul.