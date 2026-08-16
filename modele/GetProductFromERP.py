import base64
import os

from modele.VerbAPI import VerbAPI
from modele.NormalizeProduct import NormalizeProduct
from modele.ProductMapper import ProductMapper


class GetProductFromERP:

	verb_api = None
	normalize_product = None
	product_mapper = None
	pictureFolder = None

	def __init__(self, pictureFolder: str = "/tmp/", weightProductsIdentification: str = '%250000'):
		super().__init__()

		self.verb_api = VerbAPI()
		self.normalize_product = NormalizeProduct()
		self.product_mapper = ProductMapper()
		self.pictureFolder = pictureFolder

		# Encode le % en %25 pour le passage en requête SQL
		self.weightProductsIdentification = weightProductsIdentification.replace('%', '%25')

	# Fonction obligatoire car demandée par l'interface
	def searchActiveWeightProducts(self):
		tmpProductList = self.getProductWithDynamicBareCode()
		return self.product_mapper.convertERPListToProductList(tmpProductList)

	def searchAllProducts(self):
		tmpProductList = self.getProduct()
		return self.product_mapper.convertERPListToProductList(tmpProductList)

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
		response = self.verb_api.apiGet(url)
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
			files = self.verb_api.apiGet(url)
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
				'base64': self.verb_api.apiGet(url)['content'],
				'name': selectedFile['name'],
				'relativename': selectedFile['relativename'],
			}
			return out
		except Exception:
			return None

	@staticmethod
	def _savePicture(imgBase64, imgPath):
		"""" Fonction de création d'un fichier à partir d'une chaine base64 """
		imgdata = base64.b64decode(imgBase64)
		with open(imgPath, 'wb') as f:
			print("écriture d'une nouvelle image à " + imgPath)
			f.write(imgdata)
		return True

	def _getPicturePath(self, productId):
		return self.pictureFolder + "/" + productId
