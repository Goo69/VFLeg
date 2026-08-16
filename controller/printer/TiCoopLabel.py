import re

import zpl as zpl


class TiCoopLabel(zpl.Label):

    def write_text(self, text, char_height=None, char_width=None, font='0', orientation='N', line_width=None,
                   max_line=1, justification='L'):

        if char_height and char_width and font and orientation:
            assert orientation in 'NRIB', "invalid orientation"
            if re.match(r'^[A-Z0-9]$', font):
                self.code += "^A%c%c,%i,%i" % (font, orientation, char_height*self.dpmm,
                                               char_width*self.dpmm)
            elif re.match(r'[REBA]?:[A-Z0-9\_]+\.(FNT|TTF|TTE)', font):
                self.code += "^A@%c,%i,%i,%s" % (orientation, char_height*self.dpmm,
                                                 char_width*self.dpmm, font)
            else:
                raise ValueError("Invalid font.")
        if line_width:
            assert justification in "LCRJ", "invalid justification"

            self.code += "^TB%c,%i,%i" % (orientation, line_width*self.dpmm, char_height*max_line*self.dpmm)
        self.code += "^FD%s" % text

        if justification == 'C':
            self.code += "\\&"


