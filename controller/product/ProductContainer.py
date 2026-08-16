from abc import ABC

from controller.product.LoadProduct import LoadProduct


class SingletonMeta(ABC, type):
	"""
	The Singleton class can be implemented in different ways in Python. Some
	possible methods include: base class, decorator, metaclass. We will use the
	metaclass because it is best suited for this purpose.
	"""

	_instances = {}

	def __call__(cls, *args, **kwargs):
		"""
		Possible changes to the value of the `__init__` argument do not affect
		the returned instance.
		"""
		if cls not in cls._instances:
			instance = super().__call__(*args, **kwargs)
			cls._instances[cls] = instance
		return cls._instances[cls]


class ProductContainer(metaclass=SingletonMeta):

	products_list = None
	products_picture = None
	load_product = None

	def __init__(self):
		self.load_product = LoadProduct()
		self.load_products_list()

	def get_all_products(self):
		return self.products_list

	def get_products_by_category(self, category):
		return self.products_list[category]

	def get_products_picture(self, pictureId):
		self.products_picture = self.load_product.getProductPicture(pictureId)

	def load_products_list(self):
		self.products_list = self.load_product.load_all_products()
