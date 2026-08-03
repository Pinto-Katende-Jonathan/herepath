# Contribuer

Merci de prendre le temps de contribuer. Ce projet est petit et accueillant, et
les contributions de toutes tailles sont les bienvenues : rapports de bugs,
documentation, tests et code. Les nouveaux·elles contributeur·rices sont aussi les
bienvenu·es.

!!! tip "Tu débutes dans l'open source ? Commence ici"
    Pas besoin d'être expert·e. Corriger une faute de frappe, traduire une phrase
    ou améliorer un exemple est une vraie contribution, et ça inscrit ton nom dans
    l'historique du projet comme contributeur·rice. Cette page t'accompagne dans
    tout le processus, depuis zéro.

## Comment devenir contributeur·rice reconnu·e

Sur GitHub, tu es crédité·e comme contributeur·rice quand un commit dont tu es
l'auteur·e est fusionné dans le projet. Le chemin est donc toujours le même :

1. Obtiens ta propre copie du code.
2. Fais une modification et commit-la sous ton nom.
3. Ouvre une pull request pour qu'elle soit fusionnée.

Une fois fusionnée, tu apparais dans la liste des contributeur·rices du dépôt.

## Étape 1 : configurer Git (une seule fois)

Si tu n'as jamais utilisé Git, dis-lui qui tu es pour que tes commits portent ton
nom :

```bash
git config --global user.name "Ton Nom"
git config --global user.email "toi@example.com"
```

!!! warning "Utilise la bonne adresse e-mail"
    GitHub relie un commit à ton compte via son adresse e-mail. Utilise la même
    adresse que ton compte GitHub (ou une adresse `noreply` GitHub) pour que tes
    commits te soient attribués.

## Étape 2 : forker et cloner

1. Clique sur **Fork** en haut à droite de la
   [page du dépôt](https://github.com/Pinto-Katende-Jonathan/herepath) pour en faire ta
   propre copie.
2. Clone *ton fork* sur ta machine :

```bash
git clone https://github.com/TON-NOM-UTILISATEUR/herepath
cd herepath
```

## Étape 3 : installer pour le développement

=== "Linux / macOS"

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install -e ".[dev]"
    pre-commit install        # optionnel mais recommandé
    ```

=== "Windows (PowerShell)"

    ```powershell
    python -m venv .venv
    .venv\Scripts\Activate.ps1
    pip install -e ".[dev]"
    pre-commit install        # optionnel mais recommandé
    ```

Pour travailler sur ce site de documentation, installe les extras docs et
prévisualise en direct :

```bash
pip install -e ".[docs]"
mkdocs serve     # ouvre http://127.0.0.1:8000
```

## Étape 4 : créer une branche

Ne travaille jamais directement sur `main`. Crée une branche nommée d'après ta
modification :

```bash
git switch -c docs/corrige-faute-tutoriel
```

## Étape 5 : faire ta modification et la commit

Modifie les fichiers, puis ajoute et commit. C'est le commit qui fait de toi un·e
contributeur·rice, alors écris-le sous ton nom avec un message clair :

```bash
git add .
git commit -m "docs: corrige une faute dans le tutoriel"
```

!!! note "De bons messages de commit"
    Écris à l'impératif (« Ajoute X », pas « Ajouté X »). Garde une seule
    modification logique par commit.

## Étape 6 : lancer les vérifications

Assure-toi que tout passe encore avant de pousser :

```bash
pytest                # tests
pytest --cov          # tests + couverture
ruff check .          # lint
ruff format .         # formatage automatique
mypy                  # vérification de types
```

Toutes ces vérifications tournent en CI sur chaque pull request, sur Python 3.8 à
3.13 sous Linux, macOS et Windows. Merci de t'assurer qu'elles passent en local
d'abord.

!!! info "Modification de doc uniquement ?"
    Si tu n'as touché qu'à du Markdown sous `docs/` ou aux tutoriels, tu n'as pas
    besoin de toute la suite de tests. Prévisualise simplement avec `mkdocs serve`
    et relis ta modification.

## Étape 7 : pousser et ouvrir une pull request

```bash
git push -u origin docs/corrige-faute-tutoriel
```

GitHub affichera un lien pour ouvrir une pull request. Clique dessus, remplis le
modèle, et envoie. Un·e mainteneur·e la relira, et une fois fusionnée, tu es
contributeur·rice.

## Règles pour les pull requests

- Garde des modifications ciblées : une seule modification logique par PR.
- Ajoute ou mets à jour les tests pour tout changement de comportement.
- Mets à jour `README.md` et `CHANGELOG.md` (sous un titre `## [Unreleased]`)
  quand un comportement visible par l'utilisateur change.
- Pour la documentation, garde les pages anglaise et française synchronisées : si
  tu modifies `docs/fr/tutorial.md`, répercute le changement dans
  `docs/en/tutorial.md` (et vice versa). Pareil pour le `TUTORIAL.md` racine
  (français) et `TUTORIAL.en.md` (anglais).

## Traduire la documentation

Ce projet existe en anglais et en français. La traduction est une bonne première
contribution :

- Les pages anglaises vivent dans `docs/en/`.
- Les pages françaises vivent dans `docs/fr/`.
- Les deux dossiers se reflètent page par page.

Tu n'as pas à tout traduire d'un coup ; même un seul paragraphe amélioré aide.

### Exemple A : améliorer une page dans ta langue

Disons que tu repères une phrase maladroite dans le tutoriel français. La
modification est petite :

```bash
git switch -c docs/ameliore-tutoriel-fr
# modifie docs/fr/tutorial.md dans ton éditeur
mkdocs serve         # vérifie sur http://127.0.0.1:8000 (passe en Français)
git add docs/fr/tutorial.md
git commit -m "docs(fr): clarifie la section i_am()"
git push -u origin docs/ameliore-tutoriel-fr
```

Ouvre la pull request, et c'est terminé.

### Exemple B : ajouter la doc dans ta langue maternelle

Tu veux la documentation dans ta propre langue ? Voici l'exemple complet, avec
l'espagnol (`es`). Remplace `es` et les noms ci-dessous par le
[code ISO 639-1](https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-1) de ta
langue et tes traductions.

**1. Crée le dossier de langue** en copiant le dossier anglais comme point de
départ :

```bash
git switch -c docs/ajoute-espagnol
cp -r docs/en docs/es        # Windows : xcopy /E /I docs\en docs\es
```

**2. Traduis les pages** dans `docs/es/` une par une. Garde tous les blocs de
code, les chemins de fichiers et les noms de fonctions exactement tels quels ; ne
traduis que le texte. Tu peux commencer par une seule page et ajouter le reste
plus tard.

**3. Déclare la langue** dans `mkdocs.yml`, sous `plugins > i18n > languages`, à
côté des entrées `en` et `fr` existantes :

```yaml
        - locale: es
          name: Español
          build: true
          nav_translations:
            Home: Inicio
            Installation: Instalación
            Tutorial: Tutorial
            "Advanced guide": "Guía avanzada"
            "Command line": "Línea de comandos"
            "API reference": "Referencia de la API"
            Contributing: Contribuir
```

Le bloc `nav_translations` traduit les libellés de la barre latérale. Si tu
l'omets, la navigation reste simplement en anglais pour ta langue.

**4. Prévisualise en local** et utilise le sélecteur de langue dans la barre du
haut pour vérifier tes pages :

```bash
mkdocs serve         # http://127.0.0.1:8000
```

**5. Commit et ouvre une pull request :**

```bash
git add docs/es mkdocs.yml
git commit -m "docs(es): ajoute la traduction espagnole"
git push -u origin docs/ajoute-espagnol
```

Une traduction partielle est la bienvenue : mieux vaut ajouter trois bonnes pages
que d'attendre que chaque page soit parfaite. Des contributeur·rices ultérieur·es
(peut-être toi) compléteront le reste, une page par pull request.

## Philosophie de conception

`herepath` reflète volontairement la surface petite et restreinte du paquet R
[`here`](https://here.r-lib.org/). Avant d'ajouter une nouvelle fonction publique,
demande-toi si elle correspond à cette philosophie minimale. Une recherche de
racine plus puissante a sa place dans le code utilisateur ou une bibliothèque
séparée.

## Signaler des bugs

Ouvre une issue avec le modèle de rapport de bug et inclus la sortie de
`herepath --report` pour qu'on voie comment la racine a été résolue.

## Code de conduite

En participant, tu acceptes de respecter notre
[Code de conduite](https://github.com/Pinto-Katende-Jonathan/herepath/blob/main/CODE_OF_CONDUCT.md).

## Remerciements

Un grand merci à nos meilleur·es contributeur·rices, dont le travail a façonné
`herepath` :

- **MWANZA LUBUKAYI Henock**
- **MUTONJI BUKAMA Arsène**
- **KHANG MATE ZULBAL Emmanuel**
- **MUKWIYO MUKALO Patrick**
