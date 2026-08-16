#!/usr/bin/python
"""
 Version 1.0 - 2020-0725 - Cyril CARGOU - Interface entre l'application VFleg est la source de données contenant les produits
"""

import unicodedata
import json
from abc import ABC


class Product(ABC):
    erpId = None  # Id dans l'ERP
    name = None  # Le libellé du produit
    searchableName = None  # Le libelle du produit mis en forme pour une recherche (majuscule, sans accent ...)
    description = None
    picture = None  # Image objet contenant l'image sous forme picture base 64
    priceKg = None
    price = None
    measuredWeight = None
    tare = 0
    barcode = None
    vendor = None
    category = None
    isScaled = False  # si l'objet n'est pas à pesé, alors le prix ne tiendras pas compte du poid de la balance
    unit = "Kg"  # g,Kg,dl,L ...
    unitValue = 0
    accountancyCode = None

    def __init__(self):
        pass

    def isCategory(self, category: str) -> bool:
        isCategory = False
        if self.category is not None and category == self.category:
            isCategory = True
        return isCategory

    def getCategory(self) -> str:
        return self.category

    def setCategory(self, category: str):
        self.category = category

    def isAccountancyCode(self, accountancyCode: str) -> bool:
        if self.accountancyCode is not None:
            if accountancyCode == self.accountancyCode:
                return True
            else:
                return False
        return False

    def getAccountancyCode(self) -> str:
        return self.accountancyCode

    def setAccountancyCode(self, accountancyCode: str):
        self.accountancyCode = accountancyCode

    def getPrice(self) -> float:
        """Calcul le prix en fonction du poid si c'est un produit au poids. Sinon retour le prix à l'article"""
        if not self.getIsScaled():
            return self.price
        else:
            return round(self.getPriceKg() * self.getWeight(), 2)

    def setPrice(self, price: float):
        self.price = price

    def getWeight(self) -> float:
        if not self.getIsScaled():  # pour gestion des produits sans pese
            return self.getUnitValue()
        else:
            return round(self.getMeasuredWeight() - self.getTare(), 2)

    def getMeasuredWeight(self) -> float:
        return self.measuredWeight

    def setMeasuredWeight(self, measuredWeight: float):
        self.measuredWeight = round(measuredWeight, 2)

    def getTare(self) -> float:
        return self.tare

    def setTare(self, tare: float = float):
        self.tare = tare

    def getId(self) -> str:
        return self.erpId

    def setId(self, erpId: str):
        self.erpId = erpId

    def getIsScaled(self) -> bool:
        if self.isScaled is None or int(self.isScaled) != 1:
            return False
        return True

    def setIsScaled(self, isScaled: bool):
        if isScaled == 1 or isScaled == "1":
            isScaled = True
        self.isScaled = isScaled

    def getUnit(self) -> str:
        """Definition de l'unité Kg or L"""
        return self.unit

    def setUnit(self, unit: str):
        self.unit = unit

    def getUnitValue(self) -> float:
        """Définition de l'unité de valeur Poids ou volume"""
        if self.unitValue is None:
            return 1
        return self.unitValue

    def setUnitValue(self, unitValue: float):
        self.unitValue = unitValue

    def getName(self) -> str:
        return self.name

    def getSearchableName(self) -> str:
        """le libelle du produit mis en forme pour une recherche (majuscule, sans accent ...)"""
        return self.searchableName

    def setName(self, name: str):
        self.name = name
        self.searchableName = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode("utf-8").upper()

    def getDescription(self) -> str:
        return str(self.description)

    def setDescription(self, description: str):
        self.description = description

    def getPicture(self):
        """Retourne le chemin de l'image"""
        return self.picture

    def getPicturePath(self):
        return self.picture

    def setPicture(self, picture):
        self.picture = picture

    def getBarcode(self) -> str:
        return str(self.barcode)

    def setBarcode(self, barcode: str):
        self.barcode = barcode

    def getBarcodeWeight(self) -> str:
        """
        integration du poids dans le code barre
        le code bare doit terminer par 5 "0"
        ou 4 depuis le choix de la com achat 
        """
        assert self.getBarcode() is not None, 'empty barcode value'
        # si c'est un code barre fixe
        if not self.getIsScaled():
            return self.getBarcode()

        assert self.getWeight() is not None, 'empty weight value'

        # Convertion de KK.ggg en KKggg afin de pouvoir assurer la mise en page
        # ou en K.ggg en Kggg
        # strWeight = "{0:06.3f}".format(self.getWeight()).replace(".","")#5 x0
        strWeight = "{0:05.3f}".format(self.getWeight()).replace(".", "")  # 4 x0
        # Récupération des 8 pour ajout de 4 du poids, lle 13 sera calculé automatiquement à la génération de l'étiquette
        # Intégration dans le code barre
        return self.getBarcode()[:8] + strWeight

    def getPriceKg(self) -> float:
        """Définie le prix est au Kg ou au L"""
        return self.priceKg

    def setPriceKg(self, priceKg: float):
        self.priceKg = priceKg

    def getVendor(self) -> str:
        return self.vendor

    def setVendor(self, vendor: str):
        self.vendor = vendor

    def toString(self) -> str:
        return json.dumps(self.__dict__)
