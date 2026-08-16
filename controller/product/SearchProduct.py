import re
import unicodedata

import _config

from controller.product.ProductContainer import ProductContainer
from modele.enum.TypeDeCategorie import TypeDeCategorie


class SearchProduct:

	categoryType = None
	products_list = None
	product_container = None

	def __init__(self):
		self.categoryType = None
		self.product_container = ProductContainer()
		self.products_list = self.product_container.get_all_products()

	def getProductList(self, categoryFilter=None, strFilter=None):
		"""
			En fonction du texte de recherche, filtre les produits sur le label,
			non sensible à la casse et aux accents
		"""

		self.categoryType = TypeDeCategorie.toutesCategories

		if categoryFilter in _config.codeCategoryTab.keys() and categoryFilter != "99":
			self.categoryType = TypeDeCategorie.codeCategorie
		elif categoryFilter in _config.codeComptableTab.keys():
			self.categoryType = TypeDeCategorie.codeComptable

		# Si pas de filtre retourne directement les produits
		if strFilter is None and categoryFilter is None:
			return self.products_list

		plist = []
		for product in self.products_list:
			if self.categoryType is TypeDeCategorie.codeCategorie:
				if product.isCategory(categoryFilter):
					plist.append(product)
			elif self.categoryType is TypeDeCategorie.codeComptable:
				if product.isAccountancyCode(categoryFilter):
					plist.append(product)
			elif self.categoryType is TypeDeCategorie.toutesCategories:
				if product.getCategory() in _config.categoriesSelectionne or \
						product.getAccountancyCode() in _config.categoriesSelectionne:
					plist.append(product)

		searchList = self._removeAccent(self._CleanStringForSearch(strFilter)).upper().split(" ")

		for searchWord in searchList:
			out = []
			for product in plist:
				# Comparatif sans accents et case
				if re.search(searchWord, product.getSearchableName()):
					out.append(product)
			plist = out.copy()  # Car par défaut c'est un pointeur, et donc l'ajout de produit se fait sur la liste source :-(
		return plist

	@staticmethod
	def _CleanStringForSearch(strToClean: str):
		if strToClean is not None:
			return re.sub("[^a-zA-Z1-9éèà ]", "", strToClean)
		else:
			return ""

	@staticmethod
	def _removeAccent(string: str):
		""" import unicodedata """
		out = unicodedata.normalize('NFD', string).encode('ascii', 'ignore').decode("utf-8")
		return out
