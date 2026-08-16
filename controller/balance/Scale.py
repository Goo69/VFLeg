#!/usr/bin/python
from controller.balance.BalanceConnection import BalanceConnection
from serial import SerialException


class Scale:

    def scaleSelectedProduct(self, product, tare: float = 0):
        """ Gestion de la tare saisie par l'utilisateur afin de calculer le poids produits"""
        assert tare >= 0, "tare can't be negative : " + str(tare)
        assert product is not None, "No selected product"
        # Mise à jour du poids produit
        product.setMeasuredWeight(self.readScale())
        # Gestion des tares trop importante
        if tare > product.getMeasuredWeight():
            tare = product.getMeasuredWeight()
        # Définition de la tare dans le produit
        product.setTare(tare)
        return product

    @staticmethod
    def readScale() -> float:
        try:

            scale = BalanceConnection()
            measureWeight = scale.read_balance_value()

        # Si la connection à la balance n'est pas possible, pour des tests en local ou pour l'impression d'étiquette
        # devant les produits par exemple, on affiche un poids égale à 1.
        except SerialException:
            measureWeight = 1

        if measureWeight is None or not (isinstance(measureWeight, float) or isinstance(measureWeight, int)) or measureWeight < 0:
            measureWeight = 0

        return measureWeight
