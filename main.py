
#!/usr/bin/python
from kivy.lang import Builder

from controller.product.ProductContainer import ProductContainer

from views.VFLegApp import VFlegApp

Builder.load_file("views/color.kv")
Builder.load_file("views/category/category.kv")
Builder.load_file("views/product/product.kv")
Builder.load_file("views/scale/scale.kv")


if __name__ == '__main__':

    product_container = ProductContainer()
    #Window.size = (1920, 1080)  # *2 pour gérer les grands écrans
    #Window.fullscreen = True # error :-(
    #Window.borderless = True
    VFlegApp().run()
