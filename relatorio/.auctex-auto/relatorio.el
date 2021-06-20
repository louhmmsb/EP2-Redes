(TeX-add-style-hook
 "relatorio"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-class-options
                     '(("beamer" "12pt")))
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("inputenc" "utf8") ("babel" "brazil")))
   (add-to-list 'LaTeX-verbatim-environments-local "semiverbatim")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "nolinkurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperbaseurl")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperimage")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "hyperref")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "href")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "beamer"
    "beamer12"
    "inputenc"
    "amsfonts"
    "amsmath"
    "siunitx"
    "amssymb"
    "mathtools"
    "babel"
    "geometry"
    "graphicx"
    "bussproofs"
    "gensymb"
    "hyperref")
   (TeX-add-symbols
    '("code" 1)
    '("ring" 1)
    '("mytitle" 1)
    '("gsum" 3)
    '("product" 3)
    "real"))
 :latex)

