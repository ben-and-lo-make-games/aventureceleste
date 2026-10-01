# aventureceleste

Site public du jeu **Avent’ure céleste**, servi par GitHub Pages sur
<https://bhrousseau.github.io/aventureceleste/>.

Il n'existe que pour porter les deux adresses que l'App Store et Google Play
exigent de toute application :

| Page | Rôle |
|---|---|
| `confidentialite.html` | La politique de confidentialité, obligatoire même sans collecte de données |
| `assistance.html` | La page d'assistance, que les relecteurs d'Apple ouvrent réellement |

Le code du jeu vit dans un dépôt privé séparé. Ce dépôt-ci ne contient que des
pages statiques.

## Règle de rédaction

Aucune ressource externe : ni police distante, ni script tiers, ni mesure de
fréquentation. Une page qui affirme ne rien collecter ne doit pas faire de
requête vers un tiers.

Un seul thème, clair. Le registre est celui de l’atlas céleste gravé : papier
vergé, encre de Prusse, rubriques au vermillon.

## La planche

La planche d’Orion de l’accueil est tracée par `outils/planche.py` depuis les
données du jeu, et non dessinée :

    python3 outils/planche.py ../avent-ure-celeste/rive/star Ori

La sortie remplace le `<svg class="planche">` de `index.html`. Les données sont
sous licence CC BY-SA, et la légende de la planche porte leur attribution.

## Apres chaque modification du site

    python3 outils/version.py

GitHub Pages laisse les navigateurs garder pages et feuille de style dix
minutes en cache, sans qu'on puisse le regler. Le script ajoute a chaque adresse
interne l'empreinte du site, pour qu'un visiteur deja venu voie aussitot la
nouvelle version en suivant un lien.
