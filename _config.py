#!/usr/bin/python
import os
import sys

#------------------- Moteur -------------------------------------

DEVMODE = False

#------- engine
#fiche conservant la liste des produits en local
appFolder = os.path.abspath(os.path.dirname(os.path.abspath(sys.argv[0])))
#appFolder = Path.home()
engine_cacheFileName = appFolder+"/data/cache/products.cache.dat"
#dossier conservant las photos des produits
engine_cachePictureFolder = appFolder+"/data/cache/images"
#fichier d'export des impressions d'étiquettes effecutées
engine_logPrintFolder = appFolder+"/log/"

# Indique comment utiliser le cache
# True : force l'utilisation du cache, pas de connexion au serveur
# False : interdit l'utilisation du cache, toujours une connexion au serveur
# Auto : connexion au serveur si possible, sinon utilisation du cache. Si les photos existe, utilisation de celles locales.

engine_useCache = "auto"

# Indique quels type de produits afficher
# All :touts les produits actif, en vente
# ActiveWeightProducts, que les produits en vente type pesée (qui termine par 00000)
#engine_productType = "ActiveWeightProducts"
engine_productType="All"

#------------- Identifiant de connexion ERP 
# Token de connexion à Dolibarr avec le compte de service export Data
# Pour générer le jeton (ou depuis l'interface web du compte utilisateur): https://erp.ticoop.fr/api/index.php/login?login=ser&password=TODO[&reset=1]
# https://erp.ticoop.fr/api/index.php/explorer
# accès en lecture uniquement
erp_apiKeyProduction = ''
erp_baseUrlProduction = ''

#Chaine de recherche des produits à code dynamique
#mode SQL LIKE
# les codes barre dynamiques commencent par 21
# _ = 1 caractére, représente les 6 caractéres d'identification du fournisseur et du produit
# 0 = le poids est inscrit sur 4 caractéres
# % = 0 ou x caractéres (si la clef est présente ou pas)
#erp_weightProductsIdentification = '21______0000%'
erp_weightProductsIdentification ='%0000%'

#normalemenProductsHaveNormalizedPrice = Bool, indique si le poids les produit à la pesée ont un prix déjà au Kg (true) ou si ce prix doit être normalisée (false)
erp_scaleProductsHaveNormalizedPrice = True

#------------------- Balance
#port USB de connexion du convertisseur RS232 /USB de la balance
scale_portName = "/dev/ttyUSB0"
scale_model = "XFOC"

#------------------- Imprimante
#SI None, sera détecté automatiquement
printer_name = "Zebra_ZD220_788"
#"continuous" si rouleau type ticket de caisse
#"label", si rouleau étiquette avec séparateur
#etiquette autocollante pour coller sur produits
label_config = {"height": 40,
                "weight": 56,
                # résolution de l'imprimante
                "dpmm": 8,
                "printMode": "label",
                #"printMode" : "continuous",
                "fontLabel":4,
                "fontEmptyLine1":1,
                "fontVendor":3,
                "fontEmptyLine2":3,
                "fontPrice":4,
                "fontWeight":3,
                "fontEmptyLine3":3,
                "fontPriceUnit":3,
                "marginX": 2,
                "marginY": 3
                }
#label_config = [
 #   ("height", 40),
 #   ("weight", 56),
 #   ("dpmm", 8),
 #   ("printMode", "label"),
 #   ("fontLabel", 4.5),
 #   ("fontEmptyLine", 2),
 #   ("fontVendor", 3.5),
 #   ("fontEmptyLine", 2),
 #   ("fontPrice", 4),
 #   ("fontWeight", 3),
 #   ("fontEmptyLine", 3),
 #   ("fontPriceUnit", 3),
 #   ("marginX", 2),
 #   ("marginY", 3)
#]
printer_etiquette_magasin = False
#------------------- Interface -------------------------------------
gui_categoryImage = appFolder + "/data/images/"
# Image par défaut pour les produits
gui_defaultImage = appFolder + "/data/images/logo.png"
# Nombre d'accordéon max avant une fusion en 1 seul accordéon
gui_nombreAccordionMax = 7
# Limite le nombre de produit à afficher afin de ne pas saturer l'application
gui_nombreProduitMax = 100

# Liste des catégories pour Perceval et Karadoc. Les catégories sont des chiffres auxquelles chaques chiffres
# correspond à une catégorie comme ci-dessous:

categoriesSelectionne = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

codeCategoryTab = {'1': "BOISSONS",
                   '2': "DROGUERIE ET HYGIÈNE",
                   '3': "ÉPICERIE SALÉE",
                   '4': "ÉPICERIE SUCRÉE",
                   '5': "FRAIS",
                   '6': "PAINS",
                   '7': "LÉGUMES",
                   '8': "FRUITS",
                   '9': "AUTRES",
                   '99': "TOUS PRODUITS"
                   }
#
# Pour Karadoc, on fait aussi une distinction pour le frais avec le code comptable. On trie via le code comptable
# fromage pour faire deux catégories distinctes à partir d'un seul code de catégories.

# Source :https://wiki.ticoop.fr/bin/view/Documentation/Informatique/Application/Dolibarr/Comptabilite/
codeComptableTab = {'70710001': "LÉGUMES",
                    '70710002':	"FRUITS",
                    '70720001':	"FROMAGES",
                    '70720002':	"PRODUITS LAITIERS ET ASSIMILÉS",
                    '70720003':	"FROMAGES À LA COUPE",
                    '70730001':	"VIANDES",
                    '70730002':	"VOLAILLES",
                    '70730003':	"CHARCUTERIES",
                    '70740001':	"ÉPICERIE SALÉES",
                    '70740002': "ÉPICERIE SUCRÉES",
                    '70740012': "CHOCOLATS",
                    '70740003':	"PAINS",
                    '70750001':	"PRODUITS FRAIS",
                    '70760001':	"BOISSONS NON ALCOLISÉES",
                    '70760002':	"BOISSONS ALCOLISÉES",
                    '70780001': "PRODUITS D'HYGIÈNE",
                    '70780011': "PRODUITS PÉRIODIQUES FÉMININ",
                    '70780002':	"PRODUITS D'ENTRETIEN",
                    '70780003':	"DROGUERIES",
                    '70790001':	"VRAC SALÉS",
                    '70790002':	"VRAC SUCRÉS",
                    }
