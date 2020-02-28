### Commits : 
- Message de commit préfixé par le numéro de ticket sous la orme OSIS-XXXX
- Commiter seln les guidelines suivantes  (+ lien vers source)

### Coding style :
On se conforme au [guide PEP8](https://www.python.org/dev/peps/pep-0008/#indentation)

- Se référer aux uidelines Django (+ lien vers source)

- Le dernier élément de la structure a également une virgule. Cela permet d'éviter que cette ligne apparaisse dans le diff de git quand on rajoute un élément à la fin de structure.
```python
# Mauvais
fruits = [
    'banane',
    'pomme',
    'poire'
]
# Bon
légumes = {
    '1': 'carotte', 
    '2': 'courgette', 
    '3': 'salade',
}
```

- Voir en plus le [Coding Style de Django](https://docs.djangoproject.com/en/1.11/internals/contributing/writing-code/coding-style/).

- Utiliser des ChoiceEnum plutôt que des CONST contenant des tuples.
Exemple : 
```python
from base.models.utils.utils import ChoiceEnum
from django.utils.translation import gettext_lazy as _

# Bon
class Categories(ChoiceEnum):
    TRAINING = _("Training")
    MINI_TRAINING = _("Mini-Training")
    GROUP = _("Group")
    
# Mauvais
TRAINING = "TRAINING"
MINI_TRAINING = "MINI_TRAINING"
GROUP = "GROUP"
CATEGORIES = (
    (TRAINING, _("Training")),
    (MINI_TRAINING, _("Mini-Training")),
    (GROUP, _("Group")),
)
```

- Les signatures de fonction doivent être typées
- Éviter les **kwargs dans une fonction (+ lien vers source)
- Si utilisation, toujours valeur par défaut du kwarg=None (jamais isntancier un mutable object) - cf. formation sur les kwargs 
- Une fonction ne peut pas modifier les paramètres qu'elle reçoit (+ lien vers source)
- Privilégier l'utilisation d'objets plutôt que de dictionnaires loesqu'on implémente un code métier (+ lien vers source)
- "Let the code better than you found it" (+ lien vers source)

### Documentation du code :
- Tout objet public, exposé, service doit être documenté : templatetags, les API, les Mixins, les services (ddd), les objets du Domain (ddd)
- Pour plus tard : docString structurée pour lancer des tests
- Rédiger / rediriger vers les guidelines : https://en.wikipedia.org/wiki/Best_coding_practices et https://github.com/yetu/software-development-guidelines/blob/master/general-programming-guidelines.md
- Ajouter Django.Model.decription sur les DjangoModelFields

### Traductions :
- Voir https://github.com/uclouvain/osis/blob/dev/doc/technical-manual.adoc#internationalization
- Les "Fuzzy" doivent être supprimés si la traduction du développeur diffère de la traduction proposée (le "fuzzy" signifiant que GetText a tenté de traduire la clé en retrouvant une similitude dans une autre clé).
- Empêcher les traductions en commentaire
- Ajouter lien vers la doc Django pour l'internationalisation

### Réutilisation du code :
- Ne pas créer de fonctions qui renvoient plus d'un seul paramètre (perte de contrôle sur ce que fait la fonction et perte de réutilisation du code) -> renvoyé des NamedTuple (Cf. Eddy pour exemple)
- Ne pas faire de copier/coller ; tout code dupliqué ou faisant la même chose doit être implémenté dans une fonction documentée qui est réutilisable -> "Don't repeat yourself" (+ lien vers source cf. Eddy)
- Ne pas utiliser de 'magic number' (constante non déclarée dans une variable). (+ lien vers source)
- Ne pas utiliser de 'magic string' : utiliser des CONST ou des ChoiceEnum

### Performance :
- Attetion aux queryset et boucles for : réutiliser les prefetch_related et selec_related fournis par Django (+ lien vers source).
 
### Structure d'une App Osis
- Décrire schéma d'une app Osis (models, ddd, utils, views...) (cf. Ales)
- Chaque fichier décrivant un modèle doit se trouver dans le répertoire *'models'*
- Chaque fichier de modèle contiendra une classe du modèle, ses managers et les triggers / contraintes DB.
- Tout champs de type "ManyToMany"  doit spécifier le "trough" ; ce modèle "throug" doit être explicite (synchro, etc)

### Modèles
- Lorsqu'un nouveau modèle est créé (ou que de nouveaux champs sont ajoutés), il faut penser à mettre à jour l'admin en conséquence (raw_id_fields, search_fields, list_filter...) --> Réutiliser OsisModelAdmin ! 
- Ne pas créer de **clé étrangère** vers le modèle auth.User, mais vers **base.Person**. Cela facilite la conservation des données du modèe auth lors des écrasements des DB de Dev, Test et Qa.
- Ne pas mettre "Null" pour des valeurs textuelles (pas d'ambiguité entre chaine vide et nulle)
- Pas de blank=True pour BooleanField 
- Éviter l'héritage de modèles (+ lien ers source) (cf. Ales)
- Définir méthode str pour les modèle (obbligatoire)
- Définir un label pour les champs et classes des forms
- Ne pas utiliser de ModelForms (cf. couche "ddd")
- NE PAS définir de verbose_name pour les classes et champs des modèles
- Ne pas utiliserles GenericForeignKey
- Forcer l'utilisation de objects = models.Manager (+ lien vers source) (cf. Aless)


### DDD: 
- Les fonctions business ne peuvent pas recevoir l'argument 'request', qui est un argument propre aux views.

### Migration :
- Un fichier de migration doit toujours écrire du code Python (RunPython) et jamais du RunSQL. Ce code Python qui 
utilise des objets Model doit obligatoirement réutiliser get_model('app_name', 'model_name')
- Lors d'une phase de migration (RunPython), faire une phase de reversePython. Si pas possible, faire un RunPython.noop. (+ lien vers source)
- Les scripts doivent être écrits en python, pas en SQL.
Il faut nécessairement faire appel à la méthode 'save()', pas à la méthode 'update()' 
('update' ignore le auto_now et les signaux pre_save et post_save, utilisés pour mettre à jour le champs changed 
utilisé par la synchro et pour la sérialisation des données dans les queues vers Osis-portal).

### Dépendances entre applications : 
- Ne pas faire de références des applications principales ("base" et "reference") vers des applications satellites (Internship, assistant...)

### Vue :
- Utiliser des FilterSet dans les pages de recherche
- Privilégier la ClassBasedView à la place des Function based views (+ lien vers source)
- Différencier les POST et GET (+lien vers source)
- Ne pas envoyer de crsf_token dans les GET
- Ajouter les annotations pour sécuriser les méthodes dans les vues (user_passes_tests, login_required, require_permission)
- Dans les classBasedViews, le LoginRequiredMixin et PermissionsMixin doit se trouver en premier éritage (performance et sécurité)
- Si dispatch() est redéfini, d'abord appeler le super() avant d'override la fonction
- Pas de code métier dans les views
- Éviter d'implémenter de la logique dans les fichiers urls.py (+ lien vers source + exemple) (cf. Aless)
- Définir les namespaces pour avoir "education_group:read" à la place de "education_group_read"
- Utiliser "path" plutôt que url (+ lien vers source) (cf. Eddy)
- Slugifier les urls plutôt que les ids (+ lien vers source) (cf. Aless).

### Formulaire :
- Utiliser les objets Forms fournis par Django (https://docs.djangoproject.com/en/1.9/topics/forms/)

### Template (HTML)
- Privilégier l'utilisation Django-Bootstrap3
- Tendre un maximum vers la réutilisation des blocks ; structure :
```
[templates]templates                                  # Root structure
├── [templates/blocks/]blocks                                # Common blocks used on all 
│   ├── [templates/blocks/forms/]forms
│   ├── [templates/blocks/list/]list
│   └── [templates/blocks/modal/]modal
├── [templates/layout.html]layout.html                      # Base layout 
└── [templates/learning_unit/]learning_unit
    ├── [templates/learning_unit/blocks/]blocks                        # Block common on learning unit
    │   ├── [templates/learning_unit/blocks/forms/]forms
    │   ├── [templates/learning_unit/blocks/list/]list
    │   └── [templates/learning_unit/blocks/modal/]modal
    ├── [templates/learning_unit/layout.html]layout.html               # Layout specific for learning unit
    ├── [templates/learning_unit/proposal/]proposal
    │   ├── [templates/learning_unit/proposal/create.html]create_***.html
    │   ├── [templates/learning_unit/proposal/delete.html]delete_***.html
    │   ├── [templates/learning_unit/proposal/list.html]list.html
    │   └── [templates/learning_unit/proposal/update.html]update_***.html
    └── [templates/learning_unit/simple/]simple
        ├── [templates/learning_unit/simple/create.html]create_***.html
        ├── [templates/learning_unit/simple/delete.html]delete_***.html
        ├── [templates/learning_unit/simple/list.html]list.html
        └── [templates/learning_unit/simple/update.html]update_***.html
```

### Sécurité :
- Ne pas laisser de données sensibles/privées dans les commentaires/dans le code
- Dans les URL (url.py), on ne peut jamais passer l'id d'une personne en paramètre (par ex. '?tutor_id' ou '/score_encoding/print/34' sont à éviter! ). 
- Dans le cas d'insertion/modification des données venant de l'extérieur (typiquement fichiers excels), s'assurer que l'utilisateur qui injecte des données a bien tous les droits sur ces données qu'il désire injecter. Cela nécessite une implémentation d'un code de vérification.

### Permissions :
- Lorsqu'une view nécessite des permissions d'accès spécifiques (en dehors des permissions frounies par Django), créer un décorateur dans le dossier "perms" des "views". Le code business propre à la permission devra se trouver dans un dossier "perms" dans "business". Voir "base/views/learning_units/perms/" et "base/business/learning_units/perms/".

### Pull request :
- Ne fournir qu'un seul fichier de migration par issue/branche (fusionner tous les fichiers de migrations que vous avez en local en un seul fichier)
- Ajouter la référence au ticket Jira dans le titre de la pull request (format = "OSIS-12345")
- Utiliser un titre de pull request qui identifie son contenu (facilite la recherche de pull requests et permet aux contributeurs du projet d'avoir une idée sur son contenu)

### Pull request de màj de la référence d'un submodule :
Quand la PR correspond à la mise-à-jour de la référence pour un submodule, indiquer dans la description de la PR les références des tickets Jira du submodule qui passent dans cette mise-à-jour de référence (format : "IUFC-123").

Pour les trouver : 
1) Une fois la PR ouverte, cliquer sur l'onglet "Files Changed"
2) Cliquer sur "x files" dans le texte "Submodule xyz updated x files"
3) Cela ouvre la liste des commits qui vont passer dans la mise-à-jour de référence -> les références des tickets Jira sont indiquées dans les messages de commits.

### Ressources et dépendances :
- Ne pas faire de référence à des librairie/ressources externes ; ajouter la librairie utilisée dans le dossier 'static'

### Emails
- Utiliser la fonction d'envoi de mail décrite dans `osis_common/messaging/send_mail.py`. Exemple:
```python
from osis_common.messaging import message_config, send_message as message_service
from base.models.person import Person

def send_an_email(receiver: Person):
    receiver = message_config.create_receiver(receiver.id, receiver.email, receiver.language)
    table = message_config.create_table(
        'Table title', 
        ['column 1', 'column 2'], 
        ['content col 1', 'content col 2']
    )
    context = {
        'variable_used_in_template': 'value',
    }
    subject_context = {
        'variable_used_in_subject_context': 'value',
    }
    message_content = message_config.create_message_content(
        'template_name_as_html', 
        'template_name_as_txt', 
        [table], 
        [receiver],
        context,
        subject_context
    )
    return message_service.send_messages(message_content)

```

### PDF : 
- Utiliser WeasyPrint pour la création de documents PDF (https://weasyprint.org/).


### Tests : 
#### Vues :
Idéalement lorsqu'on teste une view, on doit vérifier :
- Le template utilisé (assertTemplateUsed)
- Les redirections en cas de succès/erreurs
- Le contenu du contexte utilisé dans le render du template
- Les éventuels ordres de listes attendus

- Lors d'un assertEqual, la première valeur doit être la valeura tendue, la 2e doit être la valeur à tester (et on l'inverse!
- Attention à la responsabilité des tests untiares : ils ne testent que la fonction 
(et ses fonction privées utilisées dans la même couche), ils ne testent pas les fonctions des autres
couches. Exemple : un test sur une View peut tester un AssertTemplateUsed, 
mais ne teste pas Un Validator. 
Autre ezxemple : un test sur un service peut tester la concaténation de messages d'error / succes, masi ne teste pas un Validator.
- Créer une classe de tests par fonction
- La structure du dossier des tests DOIT suivre la mee structure que les dossiers applicatifs.
Exemple : program_management/ddd/domain/program_tree.py -> program_management/tests/ddd/domain/test_program_tree.py
- Le nom d'une classe de test commence toujours par "Test", et est suivi du nom de la fonction testée en CamelCase.
Exemple: AuthorizedRelationshipList.is_authorized -> TestIsAuthorized dans un fichier test_authorized_relationship.
- Dans la couche ddd/Domain, Ne jamais modifier dans un test un objet créé dans le setUp (sa modification aurait un impact sur les tests suivants de la classe - à vérifier) 
(ou plutot ne jamais utiliser de setUpClass et privilégier le setUp()?)



#### Taille de PR :
- limiter le nombre de fichiers modifés par PR à 500 lignes ?

#### API / webservice
- Tous champs utilisé dans les filter doit se trouver aussi dans le serializer (tout champs "filtre" doit se trouevr dans la donnée renvoyée)
- Spécification Open API v3  (https://swagger.io/specification/)
- Schéma.yml obligatoire avant développement de l'API
- ... ?

### Template tags
- Ne peuvent pas contenir de code business
- Doivent uniquement servir à la simplification du code html

### Fonctions privées / publiques
- Les fonctions privées sont définies via un double underscore : `def __my_private_method()`
- Les fonctions privées sont destinées à l'usage interne d'une classe / d'un fichier. 
Elles ne peuvent en aucun cas être importées/appelées dans d'autres modules.


### Règles des mixins
- Quand utiliser des mixins ?

### Releases tasks
- Penser à créer une release task en cas de modification / ajout de var d'environnement

### Javascript
- Le code JS doit se trouver dans le dossier JS (et pas dans les templates)
- À définir : structure des fichiers JS...


# Thèmes généraux pour les guidelines:
## General guidelines
### Programming principles 

- ddd
- patterns + liens vers références
- comments


### Coding styles 
- PEP8 + lien
- Django coding style + lien
- Typing

### Structure d'une app Osis

### Webservices
 

## Framework Django guidelines

