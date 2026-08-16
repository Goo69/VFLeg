#!/usr/bin/python
"""
Version 1.0 - 2020-07-25 - Cyril CARGOU - Class d'interface avec l'ERP
"""

# Import du service client REST API
import requests
import os
import json
# Pour la gestion des accents
# Pour la gestion des regex
# Pour le filtre des articles modifiés
import base64
import _config

from modele.Product import Product
from modele.DatabaseProductInterface import DatabaseProductInterface


class ERP (DatabaseProductInterface):

    # https://erp.ticoop.fr/api/index.php/explorer
    apiKey = None
    baseURL = None
    pictureFolder = None  # Dossier ou stocker les images au format fichier
    weightProductsIdentification = None  # String de recherche dans l'ERP des produits VFLEG
    scaleProductsHaveNormalizedPrice = None  # ScaleProductsHaveNormalizedPrice = Bool, indique si le poid les produit à la pesée ont un prix déjà au Kg (true) ou si ce prix doit être normalisée (false)

    def __init__(self, apiKey: str, baseURL: str, pictureFolder: str = "/tmp/", weightProductsIdentification: str = '%250000', scaleProductsHaveNormalizedPrice=False):
        super().__init__()
        self.apiKey = apiKey
        self.baseURL = baseURL
        self.pictureFolder = pictureFolder
        self.scaleProductsHaveNormalizedPrice = scaleProductsHaveNormalizedPrice

        # Encode le % en %25 pour le passage en requête SQL
        self.weightProductsIdentification = weightProductsIdentification.replace('%', '%25')

    # Fonction obligatoire car demandée par l'interface
    def searchActiveWeightProducts(self):
        tmpProductList = self.getProductWithDynamicBareCode()
        return self._convertERPListToProductList(tmpProductList)

    def searchAllProducts(self):
        tmpProductList = self.getProduct()
        return self._convertERPListToProductList(tmpProductList)

    def _convertERPListToProductList(self, erpProductList):
        """ Fonction de mise ne forme pour chaque Produit """
        out = []
        for tmpP in erpProductList:

            # Création du produit
            newProduct = Product()
            newProduct.setId(tmpP['id'])
            newProduct.setName(tmpP['label'])
            newProduct.setDescription(tmpP['description'])
            newProduct.setBarcode(tmpP['barcode'])
            newProduct.setCategory(tmpP["array_options"]["options_categorie"])
            newProduct.setPrice(round(float(tmpP['price_ttc']), 2))
            newProduct.setIsScaled(self._withdrawOption(tmpP, "toweight"))
            newProduct.setVendor(self._withdrawOption(tmpP, "marque"))
            newProduct.setAccountancyCode(tmpP["accountancy_code_sell"])

            # Normalisation des données de prix et de poids/litre
            normed = self.getProductNormalized(tmpP)
            newProduct.setUnit(normed["measureNormalized_units"])
            newProduct.setUnitValue(normed["measureNormalized"])

            # Si le produit est à la pesé et que l'option est défini, le prix est déjà au Kg.
            if self.scaleProductsHaveNormalizedPrice and newProduct.getIsScaled():
                # Le prix est déjà au KG
                newProduct.setPriceKg(round(float(tmpP['price_ttc']), 2))
            else:
                # Normalisation du prix en fonction du poid du produits
                newProduct.setPriceKg(normed["priceNormalized_ttc"])

            # Récupération de l'image du produit depuis le cache car Kivy ne saisie pas gérer l'ihm en thread
            imgPath = self._getPicturePath(tmpP['id'])
            if os.path.isfile(imgPath):
                newProduct.setPicture(imgPath)
            # Récupération de l'image du produit
            """
            Utilisation d'une récupération asynchrone
            try:
                imgPath = self.getProductPictureAsFile(tmpP['id'])
                newProduct.setPicture(imgPath)
            except Exception:
                pass
                """

            out.append(newProduct)
        return out
    # Récupération de la liste des produits à partir d'un date
    # isSell : True : récupération de la liste des produit actif, False: produit inactif, None : All
    # Date de modification des produits avant datatime
    # Date de modification des produits après datatime

    def getProductWithDynamicBareCode(self):
        """creation du filtre,
        print("---------------> "+self.weightProductsIdentification)
        """
        filtre = "&sqlfilters=(t.barcode:like:'" + self.weightProductsIdentification + "')"
        filtre += "AND(t.tosell='1')"

        return self.getProduct(filtre)

    def getProduct(self, filtre="&sqlfilters=(t.tosell='1')"):
        url = '/api/index.php/products?sortfield=t.label&sortorder=ASC&limit=3000&mode=1'+filtre
        response = self._apiGet(url)
        nbArticle = len(response)
        if nbArticle < 1:
            raise Exception('Nombre d\'article inférieur à 1  : ' + str(nbArticle))
        return response

    def getProductPictureAsFile(self, productId):
        """
        Pour chaque article récupération de l'image (si existe), retourne le chemin vers l'image
        """
        imgPath = self._getPicturePath(productId)
        # Regarde si l'image existe déjà
        if not os.path.isfile(imgPath):
            # Le fichier n'existe pas, récupération
            imgObjet = self.getProductPicture(productId)
            if imgObjet is None:
                return None
            self._savePicture(imgObjet['base64'], imgPath)
        # Le fichier existe, mémorisation dans l'objet
        return imgPath

    def getProductPicture(self, productId):
        """
        Pour chaque article récupération de l'image (si existe), retourne l'image en base64
        """
        try:
            url = '/api/index.php/documents?modulepart=product&id='+productId
            # Ne sélectionne qu'un fichier qui est une image
            files = self._apiGet(url)
            selectedFile = None
            for f in files:
                if f['name'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    selectedFile = f
                    break
            if selectedFile is None:
                return None
            # Récupération de l'image
            url = '/api/index.php/documents/download?module_part=product&original_file='+selectedFile['level1name']+'%2F'+selectedFile['relativename']
            out = {
                'base64': self._apiGet(url)['content'],
                'name': selectedFile['name'],
                'relativename': selectedFile['relativename'],
            }
            return out
        except Exception:
            return None

    def _savePicture(self, imgBase64, imgPath):
        """" Fonction de création d'un fichier à partir d'une chaine base64 """
        imgdata = base64.b64decode(imgBase64)
        with open(imgPath, 'wb') as f:
            print("écriture d'une nouvelle image à " + imgPath)
            f.write(imgdata)
        return True

    def _getPicturePath(self, productId):
        return self.pictureFolder + "/" + productId

#------------------ Fonction de traitement des données

    def _withdrawOption(self, objProduit, optionName):
        """ Fonction permettant l'extraction de l'objet en fonction de l'option demandée """
        optionName = 'options_' + optionName
        if 'array_options' in objProduit and optionName in objProduit['array_options']:
            return objProduit['array_options'][optionName]
        return None

    """
    Un produit ERP est composé de 4 champs 
    ['weight']
    ['weight_units']
    ['volume']
    ['volume_units']
    A partir de ces informations il est possible d'identifier si l'article est un solide ou un liquide.
    Le weight ou volume indique la valeur saisie par les achats
    Le weight_units ou volume_units indique l'unité de cette valeur.
    L'objectif est d'uniformiser ces données afin de disposer en sortie des informations suivantes
    ['measure']  #la valeur de ['weight'] ou de ['volume']
    ['measure_units'] # la valeur ['weight_units'] ou de ['volume_units']
    ['measureNormalized'] # la valeur ['measure'] normalisé ou Kg ou L.
    ['measureNormalized_units'] # L'unité Kg ou L

    # Fait de même avec le prix TTC
    ['price_ttc'] =>  ['priceNormalized_ttc']
    """
    def getProductNormalized(self, objProduit):
        out = {
            'measure':                  None,
            'measure_units':	        None,
            'measureNormalized':	    None,
            'measureNormalized_units':	None,
            'price_ttc':	            None,
            'priceNormalized_ttc':	    None,
            }
        #Kg et L étant exclusif et traités de la même valeur, fusion ce celles-ci.
        if objProduit['volume'] is not None:
            out["measure"] = float(objProduit['volume'])
            out["measure_units"] = objProduit['volume_units']
            out["measureNormalized_units"] = "L"
        elif objProduit['weight'] is not None:
            out["measure"] = float(objProduit['weight'])
            out["measure_units"] = objProduit['weight_units']
            out["measureNormalized_units"] = "Kg"
        else:
            #c'est un objet unitaire
            out["measure"] = 1
            out["measure_units"] = "2"
            out["measureNormalized_units"] = "Kg"  # par défaut Kg

        # Puis normalisation de la valeur saisie
        # Voici la tableau de correspondance des valeurs weight_units et volume_units
        # La matrice indique par quoi mutliplier pour avec la bonne unité
        matrice = {
            '1': 1000,       # weight_units "Tonne"
            '2':    1,       # weight_units "Kg"
            '3': 0.001,      # weight_units "g"
            '4': 0.000001,   # weight_units "mg"
            '5': 0.03,       # weight_units "once"
            '6': 0.45,       # weight_units "livre"
            '19': 1000,      # volume_units "m³"
            '20':    1,      # volume_units "L"
            '21': 0.001,     # volume_units "mL"
            '22': 0.000001,  # volume_units "µl"
            '27': 4.546,     # volume_units "gallon"
            }

        # Vérification que l'unité est bien dans la matrice
        if out["measure_units"] not in matrice:
            raise "measure_units not known"
        # Calcul de la mesure normalisée
        out["measureNormalized"] = out["measure"] * float(matrice[out["measure_units"]])
        # Arrondi 2 chiffres
        out["measureNormalized"] = round(out["measureNormalized"], 2)

        # Normalisation du prix de la même façon
        # Mémorisation du prix initial
        out["price_ttc"] = float(objProduit['price_ttc'])
        # Normalisation
        if out["measureNormalized"] != 0:
            out["priceNormalized_ttc"] = out['price_ttc'] / out["measureNormalized"]
        else:
            out["priceNormalized_ttc"] = out['price_ttc']
        # Arrondi 2 chiffres
        out["priceNormalized_ttc"] = round(out["priceNormalized_ttc"], 2)

        return out

    def getCategoryFromSellCode(self, code):
        """ Fonction de mise en forme des nombres """
        if code is None or len(code) < 1:
            return "NoCodeCategory"
        if code not in _config.codeCategoryTab:
            return "NoCategoryFound"
        return _config.codeCategoryTab[code]

#------------------ Fonction API
    def _apiGet(self, URI: str):
        """Fonction privé de requêtes API GET """
        return self._api(URI, 'GET')

    def _apiPost(self, URI: str, data):
        """Fonction privé de requêtes API POST"""
        return self._api(URI, 'POST', data)

    def _apiPut(self, URI: str, data):
        """Fonction privé de requêtes API PUT """
        return self._api(URI, 'PUT', json.dumps(data))

    def _api(self, URI, webVerbType='GET', data=None):
        """Fonction privé de requêtes API"""
        headers = {'DOLAPIKEY': self.apiKey}
        url = self.baseURL + URI
        if webVerbType == 'GET':
            response = requests.get(url, headers=headers)
        elif webVerbType == 'POST':
            response = requests.post(url, headers=headers, data=data)
        elif webVerbType == 'PUT':
            headers['Accept'] = 'application/json'
            headers['Content-Type'] = 'application/json'
            response = requests.put(url, headers=headers, data=data)
        else:
            raise Exception('_api request type unknown : ' + webVerbType)
        if response.status_code == 404:  # pas de data
            return []

        if response.status_code != 200:
            raise Exception('_api status_code : ' + str(response.status_code) + " URL : " + url)

        return response.json()
