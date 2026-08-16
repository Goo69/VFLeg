#!/usr/bin/python3
"""
Version 1.0 - 2020-07-14 - Cyril CARGOU - Lib de fonctions de gestion de l'imprimante etiquette Zebra 

Info :
https://www.zebra.com/us/en/support-downloads/knowledge-articles/mac-linux-or-unix-driver-suggestions-for-zebra-printers.html
si besoin en mode raw
http://domeu.blogspot.com/2015/02/imprimante-zebra-usb-zpl-et-cups-damned.html
"""

# Import du service de gestion des chemins
import os
# Deux solutions, zpl est préféré car plus simple d'utilisation
# https://pypi.org/project/zpl/ => sudo pip3 install zpl
# https://github.com/mchobby/PythonPcl
import tempfile

import _config
import cups
from tools.Log import Log
from controller.printer.TiCoopLabel import TiCoopLabel


class Printer:

    height = None  # Hauteur de l'étiquette
    width = None  # Largeur de l'étiquette
    dpmm = None  # Résolution, 8dpmm pour 203dpi
    printerName = None  # Nom de l'imprimante, si on définie, le choix est fait automatiquement
    fontLabel = 3
    fontEmptyLine1 = 3
    fontVendor = 3
    fontEmptyLine2 = 3
    fontPrice = 3
    fontWeight = 3
    fontEmptyLine3 = 3
    fontPriceUnit = 3
    marginX = 25
    marginY = 3

    printLog = None

    # mandarin 25mm
    # Étiquette amovible
    # Transfert thermique (et non direct thermique)
    # Meilleur prix : https://www.mercurion.fr/etiquettes-zebra-thermique-enlevables-format-56-mm-x-25-mm-prd408.html

    def __init__(self, config=_config.label_config, printerName=_config.printer_name):
        """
        label_config = {"height": 34,
                "wight":64, 
                "dpmm" : 8, résolution de l'imprimante
                "printMode" : "continuous",
                "fontLabel":4,
                "fontEmptyLine1":1,
                "fontVendor":3,
                "fontEmptyLine2":3,
                "fontPrice":4,
                "fontWeight":3,
                "fontEmptyLine3":3,
                "fontPriceUnit":3
                }
        """
        self.height = config['height']
        self.width = config['weight']
        self.dpmm = config['dpmm']
        self.printerName = printerName
        self.setConfiguration(config['printMode'])
        self.fontLabel = config['fontLabel']
        self.fontEmptyLine1 = config['fontEmptyLine1']
        self.fontVendor = config['fontVendor']
        self.fontEmptyLine2 = config['fontEmptyLine2']
        self.fontPrice = config['fontPrice']
        self.fontWeight = config['fontWeight']
        self.fontEmptyLine3 = config['fontEmptyLine3']
        self.fontPriceUnit = config['fontPriceUnit']
        self.marginX = config['marginX']
        self.marginY = config['marginY']

        self.printLog = Log(folderPath=_config.engine_logPrintFolder, suffix="printedProduct", header=True, dateFormat="%Y-%m-%d")

    def setConfiguration(self, mode="continuous"):
        """
        Configuration de l'imprimante Zebra ZD220
        continuous = rouleau sans indicateur de début ou de fin, comme pour la caisse (utile pour faire les tests)
        label = rouleur d'étiquette avec indicateur de positonnement
        https://www.zebra.com/content/dam/zebra/manuals/printers/common/programming/zpl-zbi2-pm-en.pdf
        """
        assert mode in ["continuous", "label"]
        conf = ""
        # Partie 1 de la config
        conf += "^XA"  # Début de la config

        if mode == "continuous":
            conf += "^MNN"  # Media Tracking, N = continuous media
        else:
            conf += "^MNM"  # Media Tracking, M = non-continuous media mark sensing
        conf += "^LL%i" % (self.dpmm * self.height)  # Label Length en dot
        conf += "^PW%i" % (self.dpmm * self.width)  # Print Width en dot

        # Partie 2 de la config : sauvegarde
        # Conf += "^XA" # Début de la config
        conf += "^JUS"  # Configuration Update save current settings
        conf += "^XZ"  # Fin de la config
        #  self.printByZPLCode(conf) NE FONCTIONNER PAS avec la Zebra ZD220 du point d vente pk ?

    def buildLabelByProduct(self, product):
        return self.buildLabel(
                str(product.getName()),
                str(product.getVendor()),
                "Prix : "+str(product.getPrice())+" €",
                "Au Kg : "+str(product.getPriceKg())+" €/Kg",
                "Poids : "+str(product.getWeight())+" Kg",
                str(product.getBarcodeWeight())

        )

    def buildLabel(self, lineLabel="Label", lineVendor="Vendor", linePrice="Price €", linePrixUnite="€/Kg", lineWeight="Weight", barcode="000000000000"):

        data = [
                {"Text": lineLabel, "NbLigne": 2, "Height": self.fontLabel},
                {"Text": " ", "NbLigne": 1, "Height": self.fontEmptyLine1},  # saut de ligne
                {"Text": lineVendor, "NbLigne": 1, "Height": self.fontVendor},
                {"Text": " ", "NbLigne": 1, "Height": self.fontEmptyLine2},  # saut de ligne
                {"Text": linePrice, "NbLigne": 1, "Height": self.fontPrice},
                {"Text": lineWeight, "NbLigne": 1, "Height": self.fontWeight},
                {"Text": " ", "NbLigne": 1, "Height": self.fontEmptyLine3},  # saut de ligne
                {"Text": linePrixUnite, "NbLigne": 1, "Height": self.fontPriceUnit},
            ]
        # Zebra Z-Perform 1000D amovible - 64mm x 38mm : 17430 étiquettes
        # height x width
        textToPrint = TiCoopLabel(height=self.height, width=self.width, dpmm=self.dpmm)  # 12 for 300dpi, 8 for 203dpi
        textToPrint.change_international_font()  # Pour utiliser des € et é :-)
        margin = 0.5  # mm

        height = self.marginY
        for d in data:
            # Positionnement du curseur
            textToPrint.origin(self.marginX, height)
            textToPrint.write_text(d['Text'], char_height=d['Height'], char_width=d['Height'], line_width=textToPrint.width, justification='L', max_line=d['NbLigne'])
            textToPrint.endorigin()
            height += d['Height']*d['NbLigne']

        # barcode origin Y is just under the line break
        # -> loop until reach the line break and stop
        barcodeOriginY = self.marginY
        for d in data:
            barcodeOriginY += d['Height']*d['NbLigne']
            if d['Text'] == ' ':
                break

        # Placement libre de l'image
        barcodeHeight = textToPrint.height * 0.3
        textToPrint.origin(self.marginX + textToPrint.width * 0.5, barcodeOriginY)
#        textToPrint.origin(self.marginX + textToPrint.width * 0.5, barcodeOriginY + 5)
        # e=  EAN-13 Bar Code, cf zplii-pm-vol1.pdf et zpl-zbi2-pm-en.pdf (page 101)
        textToPrint.barcode_field_default(module_width=0.27, bar_width_ratio=2, height=3)
        textToPrint.barcode(code=barcode, height=int(barcodeHeight*textToPrint.dpmm), barcode_type='E', check_digit='Y')
        textToPrint.write_text(barcode)
#        textToPrint.barcode(code=barcode, height=int(barcodeHeight*textToPrint.dpmm), barcode_type='E', check_digit='Y', orientation='B)
#        textToPrint.write_text(barcode, orientation='B')
        textToPrint.endorigin()

        return textToPrint.dumpZPL()

    def printConfiguration(self):
        conf = '~WC'
        self.printByZPLCode(conf)

    def printByFile(self, strFile):
        conn = cups.Connection()
        if self.printerName is None:
            printers = conn.getPrinters()
            # print.pprint(printers)
            printer = conn.getDefault()
            # print("Default1:", printer)

            if printer is None:
                printer = list(printers.keys())[0]
                # Print("Default2:", printer)

            if printer is None:
                raise Exception("No printer found")
        else:
            printer = self.printerName

        if not _config.DEVMODE:
            conn.printFile(printer, strFile, "print", {})

    def printByZPLCode(self, strZPL):
        fd, path = tempfile.mkstemp()
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(strZPL)
            self.printByFile(path)
        finally:
            os.remove(path)

    def printSelectedProduct(self, product):
        """ Fonction appelée en thread afin de gérer l'impression de l'étiquette"""
        self.printLog.writeInfo(product.toString())
        if product.getName() is not None:
            self.printByZPLCode(self.buildLabelByProduct(product))
