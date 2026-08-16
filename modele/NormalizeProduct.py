import _config


class NormalizeProduct:

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

	@staticmethod
	def withdrawOption(obj_produit, option_name):
		""" Fonction permettant l'extraction de l'objet en fonction de l'option demandée """
		option_name = 'options_' + option_name
		if 'array_options' in obj_produit and option_name in obj_produit['array_options']:
			return obj_produit['array_options'][option_name]
		return None
