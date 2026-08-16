import os

from modele.object.Product import Product
from modele.NormalizeProduct import NormalizeProduct
import _config


class ProductMapper:

	normalize_product = None
	scale_products_have_normalized_price = None
	picture_folder = None

	def __init__(self):
		super(ProductMapper, self).__init__()

		self.normalize_product = NormalizeProduct()
		self.scale_products_have_normalized_price = _config.erp_scaleProductsHaveNormalizedPrice
		self.picture_folder = "/tmp/"

	def convertERPListToProductList(self, erpProductList):
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
			newProduct.setIsScaled(self.normalize_product.withdrawOption(tmpP, "toweight"))
			newProduct.setVendor(self.normalize_product.withdrawOption(tmpP, "marque"))
			newProduct.setAccountancyCode(tmpP["accountancy_code_sell"])

			# Normalisation des données de prix et de poids/litre
			normed = self.normalize_product.getProductNormalized(tmpP)
			newProduct.setUnit(normed["measureNormalized_units"])
			newProduct.setUnitValue(normed["measureNormalized"])

			# Si le produit est à la pesé et que l'option est défini, le prix est déjà au Kg.
			if self.scale_products_have_normalized_price and newProduct.getIsScaled():
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

	def _getPicturePath(self, productId):
		return self.picture_folder + "/" + productId
