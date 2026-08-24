# M Motors

M Motors est une application web développée avec **Python et Django** dans le cadre du **Bloc 3 – Développer une solution digitale (spécialité Python)**.

Le projet a pour objectif de moderniser le parcours client d'une entreprise spécialisée dans la vente de véhicules d'occasion et de proposer également un service de **location longue durée (LLD)**.

L'application permet aux visiteurs de consulter les véhicules disponibles et aux clients de constituer et suivre leur dossier directement en ligne.

## Application déployée

Application :

https://m-motors-dntd.onrender.com/

## Fonctionnalités principales

### Catalogue de véhicules

* Consultation du catalogue
* Filtrage achat / location
* Filtres avancés
* Tri des résultats
* Consultation de la fiche détaillée d'un véhicule

### Espace client

* Création d'un compte
* Connexion et déconnexion
* Gestion du profil
* Réinitialisation du mot de passe
* Création d'une demande d'achat ou de LLD
* Consultation et suivi du dossier

### Dossier dématérialisé

* Dépôt de documents justificatifs
* Consultation des documents transmis
* Remplacement d'un document refusé
* Suivi du statut du dossier
* Timeline des différentes étapes
* Échanges liés au traitement du dossier

### Back-office métier

Les utilisateurs autorisés appartenant au groupe **Commercial**, ainsi que les administrateurs, disposent d'un accès au back-office.

Ils peuvent notamment :

* consulter les demandes clients ;
* examiner les dossiers ;
* vérifier les documents transmis ;
* accepter ou refuser un dossier ;
* ajouter des commentaires métier ;
* gérer les véhicules ;
* gérer leur disponibilité ;
* consulter les informations nécessaires au traitement des demandes.

---

## Technologies utilisées

### Back-end

* Python 3.12
* Django

### Front-end

* HTML
* CSS
* Bootstrap 5
* JavaScript
* Templates Django

### Base de données

**Développement :**

* SQLite

**Production :**

* PostgreSQL
* Neon

### Déploiement

* Render
* Gunicorn
* WhiteNoise

### Qualité et intégration continue

* Git
* GitHub
* GitHub Actions
* Ruff
* Django TestCase
* Coverage.py

### Services externes

* Brevo pour l'envoi des e-mails transactionnels
* UptimeRobot pour la surveillance de disponibilité
* Sentry pour le suivi des erreurs applicatives

---

## Organisation Git

Le projet utilise plusieurs types de branches :

* `main` : version stable de référence ;
* `develop` : branche d'intégration utilisée pour la version actuellement déployée ;
* `feature/*` : développement des nouvelles fonctionnalités ;
* `fix/*` : correction de bugs ;
* `chore/*` : tâches techniques ou de configuration.

Les nouvelles fonctionnalités sont développées sur une branche dédiée puis intégrées dans `develop` à l'aide d'une **Pull Request**.

Le workflow général est :

1. création d'une branche depuis `develop` ;
2. développement de la fonctionnalité ;
3. tests locaux ;
4. contrôle du code avec Ruff ;
5. commit et push vers GitHub ;
6. création d'une Pull Request ;
7. vérification de GitHub Actions ;
8. fusion dans `develop` ;
9. déploiement automatique sur Render ;
10. vérification de la fonctionnalité déployée.

---

## Installation locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/Ysaeka/M-Motors.git
cd M-Motors
```

### 2. Se placer sur la branche develop

```bash
git checkout develop
```

### 3. Créer un environnement virtuel

Sous Windows :

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 4. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 5. Configurer les variables d'environnement

Créer un fichier `.env` avec les variables nécessaires au fonctionnement de Django.

Les informations sensibles ne doivent pas être ajoutées au dépôt Git.

### 6. Appliquer les migrations

```bash
python manage.py migrate
```

### 7. Lancer l'application

```bash
python manage.py runserver
```

L'application est alors accessible localement à l'adresse indiquée par Django.

---

## Tests

Les tests automatisés utilisent le framework de tests intégré à Django.

Pour lancer les tests :

```bash
python manage.py test
```

Pour vérifier la qualité du code :

```bash
ruff check .
```

Pour mesurer la couverture :

```bash
coverage run manage.py test
coverage report -m
```

L'objectif du projet est d'obtenir une couverture de code d'au moins **80 %**.

---

## Déploiement

La version de démonstration est déployée automatiquement sur **Render** à partir de la branche `develop`.

Après validation et fusion d'une Pull Request :

1. GitHub Actions exécute les vérifications prévues ;
2. Render détecte les nouvelles modifications ;
3. une nouvelle version de l'application est déployée ;
4. la route `/health/` permet de vérifier que le service répond correctement.

---

## Monitoring

La surveillance de l'application repose sur plusieurs outils :

* **Render** pour les logs de déploiement et d'exécution ;
* **UptimeRobot** pour surveiller la disponibilité de l'application via `/health/` ;
* **Sentry** pour centraliser les erreurs applicatives et faciliter leur diagnostic.

---

## Limites du MVP

Certaines fonctionnalités envisagées lors de la conception n'ont volontairement pas été intégrées au MVP.

### Stockage des documents

Les fichiers transmis par les utilisateurs sont actuellement stockés dans le répertoire `media`.

Pour une application réelle en production, un stockage externe privé tel qu'**AWS S3** serait préférable.

### Paiement

Aucun paiement en ligne n'est intégré au MVP.

La contractualisation et le règlement sont considérés comme des étapes réalisées après validation du dossier et restent hors du périmètre de l'application.

### Sauvegarde

Une procédure complète de sauvegarde automatique et de restauration de la base de données n'a pas été mise en œuvre dans le MVP étudiant.

Elle constitue une évolution nécessaire pour une exploitation réelle du service.

---

## Gestion du projet

Le développement du projet a été organisé à partir de User Stories et d'un backlog.

Backlog produit :

https://trello.com/b/9joXEC3p/m-motors-backlog-produit

Les fonctionnalités présentées comme **Done** correspondent aux User Stories développées, testées et déployées.

---

## Auteur

**Karine FALLETTA**

Projet réalisé dans le cadre du Bloc 3 – Développer une solution digitale, spécialité Python.
