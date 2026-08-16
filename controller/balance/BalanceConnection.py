import glob
import re
import sys

import _config
import serial


# Le modèle XFOC+ renvoi des bytes et non pas une chaîne humainement interprêtable :
# b'W'      = W pour Weight ?
# b'\xff'   = ?
# b'\x..'   = .. représente le poids
# b'\x..'   = .. représente le poids
# b'0'      = EOF
#
# Le poids est représenté par 2 hexa :
#   la valeur d'un hexa est de 255 maximum
#   pour représenter une valeur supérieure, on utilise le 2e comme "dizaine"
#   Par exemple en base 10, on peut représenter un nombre de 0 à 9.
#   Pour aller au-delà on utilise un 2e nombre pour la dizaine :
#   0x10+5 =  5
#   2x10+5 = 25
#
#   Ici c'est le même principe mais sur une base 256
#
# Cette classe est là pour interprêter les données de la balance
class SerialScaleXFOC2(serial.Serial):
	def readline(self):
		weight = 0
		self.read()  # 'W'
		self.read()  # 0xff
		weight += int.from_bytes(self.read(), byteorder='big') * 256  # La "dizaine"
		weight += int.from_bytes(self.read(), byteorder='big')        # "L'unité"
		self.read()  # EOF

		# On redivise par 1000 pour obtenir un poids au Kg et non au g
		return float(weight) / 1000


class BalanceConnection:

	portSerie = None  # Objet de communication Série avec la Balance

	def __init__(self):
		super(BalanceConnection, self).__init__()
		model = _config.scale_model
		port = _config.scale_portName
		if model == "XFOC":
			self.portSerie = serial.Serial(port,
			                               baudrate=9600,
			                               bytesize=serial.SEVENBITS,
			                               parity=serial.PARITY_ODD,
			                               stopbits=serial.STOPBITS_ONE,
			                               timeout=1,
			                               writeTimeout=1)
		else:
			self.portSerie = SerialScaleXFOC2(port)

	def read(self):
		""" Exemple de lecture de la balance
		"b'ST,GS,+  1.045kg\r\n'
		"b'US,GS,+  4.515kg\r\n'
		None
		"b'S,GS,+  7.190kg\r\n'
		"b'345kg\r\n'
		"b'S,GS,+  2.090kg\r\n'
		"b'US,NT,+  0.000kg\r\n'
		"b'S,NT,+  0.020kg\r\n'
		"""
		if self.portSerie.isOpen():
			line = self.portSerie.readline()
			return line
		else:
			# Fin du script : ERREUR -> SerialException(13, "could not open port /dev/ttyUSB0: [Errno 13] Permission denied: '/dev/ttyUSB0'")
			# https://websistent.com/fix-serial-port-permission-denied-errors-linux/
			# ls -l /dev/ttyUSB*
			# id -Gn $LOGNAME
			# sudo usermod -a -G dialout cyril
			# crw-rw---- 1 root dialout 188, 0 19 juil. 12:24 /dev/ttyUSB0
			raise serial.SerialException("Serial Port closed")

	def read_balance_value(self):
		"""
		Retourne le poids de l'article posé sur la balance en Kg, nombre flottant avec précisions au millième
			Ex :
			1.045
			4.515
			7.19
			2.09
			0.0
			0.02
		"""
		try:
			readStr = str(self.read())
			#print(readStr)
			if readStr is None:
				return None
			readFloat = re.findall(r"\d+\.\d+", readStr)

			# 1 et 1 seul nombre doit être trouvé, sinon la chaine n'est pas correcte.
			if len(readFloat) == 1:
				out = float(readFloat[0])
				return out
			return None
		except Exception:
			return None

	@staticmethod
	def getPortList():
		""" Lists serial port names
			:raises EnvironmentError:
				On unsupported or unknown platforms
			:returns:
				A list of the serial ports available of USB Serial Converter support the system
		"""
		if sys.platform.startswith('win'):
			ports = ['COM%s' % (i + 1) for i in range(256)]
		elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
			# this excludes your current terminal "/dev/tty"
			ports = glob.glob('/dev/tty[A-Za-z]*')
		elif sys.platform.startswith('darwin'):
			ports = glob.glob('/dev/tty.*')
		else:
			raise EnvironmentError('Unsupported platform')

		result = []
		for port in ports:

			try:
				s = serial.Serial(port)
				s.close()
				result.append(port)
			except (OSError, serial.SerialException):
				pass
		return result
