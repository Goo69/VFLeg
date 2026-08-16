import os
import pickle

import _config
from tools.Log import Log
from modele.GetProductFromERP import GetProductFromERP


class LoadProduct:

	printLog = None
	productDb = None
	products_list = None

	def __init__(self):
		self.productDb = GetProductFromERP(pictureFolder=_config.engine_cachePictureFolder,
											weightProductsIdentification=_config.erp_weightProductsIdentification)
		self.printLog = Log(folderPath=_config.engine_logPrintFolder, suffix="printedProduct",
							header=True, dateFormat="%Y-%m-%d")

	def load_all_products(self, use_cache=_config.engine_useCache, product_type=_config.engine_productType):
		"""Charge les produits depuis l'ERP """
		assert use_cache in [True, False, "auto"], "useCache value are [True,False,'auto']"
		assert product_type in ["All", "ActiveWeightProducts"], "productType value are ['All','ActiveWeightProducts']"

		# Gestion du cache
		if use_cache is True:
			self.printLog.writeInfo("Forçage de l'utilisation du cache")
			# Utilisation unique du cache
			self._loadProductFromCache()
		else:
			try:
				# Récupération des produits depuis l'ERP
				if product_type == "ActiveWeightProducts":
					self.printLog.writeInfo("Récupération des produits de pesée")
					self.products_list = self.productDb.searchActiveWeightProducts()
				elif product_type == "All":
					self.printLog.writeInfo("Récupération de l'ensemble des produits")
					self.products_list = self.productDb.searchAllProducts()
				else:
					self.printLog.writeError("Erreur de configuration")
				# Mise en cache des produit
				self.printLog.writeInfo("Mise en cache des produits")
				self._saveProductToCache()
			except Exception as e:
				self.printLog.writeError(e)
				self.products_list = None
				if use_cache == "auto":
					self.printLog.writeWarning("Aucun produit trouvé, utilisation du cache")
					self._loadProductFromCache()
				else:
					self.printLog.writeError("Aucun produit trouvé")
					raise Exception("Aucun produit trouvé")
			self.printLog.writeInfo("Nombre de produit : " + str(len(self.products_list)))
		# Tri des produits par catégorie ou code comptable
		# self.sort_products_by_category()
		return self.products_list

	def _loadProductFromCache(self):
		if os.path.isfile(_config.engine_cacheFileName) is False:
			raise FileNotFoundError("Il n'existe pas de cache de produit")
		# Read that file
		self.products_list = pickle.load(open(_config.engine_cacheFileName, "rb"))

	def _saveProductToCache(self):
		"""Écriture dans le cacheFileName"""
		pickle.dump(self.products_list, open(_config.engine_cacheFileName, "wb"))

	def sort_products_by_category(self):
		products_list_creation = []
		for category in _config.categoriesSelectionne:
			if self.is_code_category(category):
				products_list_creation[category] = self.get_all_products_from_category(category)
			elif self.is_code_accountancy_table(category):
				products_list_creation[category] = self.get_all_products_from_accountancy_table(category)
		self.products_list = products_list_creation

	@staticmethod
	def is_code_category(category):
		is_from_category = False
		for config_category in _config.codeCategoryTab.items():
			if category == config_category:
				is_from_category = True
		return is_from_category

	@staticmethod
	def is_code_accountancy_table(accountancy_table):
		is_from_accountancy_table = False
		for config_accountancy_table in _config.codeComptableTab.items():
			if config_accountancy_table == accountancy_table:
				is_from_accountancy_table = True
		return is_from_accountancy_table

	def get_all_products_from_category(self, category):
		list_to_return = []
		for product in self.products_list:
			if product.getCategory() == category:
				list_to_return.append(product)
		return list_to_return

	def get_all_products_from_accountancy_table(self, accountancy_table):
		list_to_return = []
		for product in self.products_list:
			if product.getAccountancyCode() == accountancy_table:
				list_to_return.append(product)
		return list_to_return

	def getProductPicture(self, picture_id):
		return self.productDb.getProductPictureAsFile(picture_id)
