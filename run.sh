#!/bin/bash
set -e
set -x
set -o pipefail

SCRIPTPATH="$(dirname -- "$0")"
(
   cd "$SCRIPTPATH"
   source "venv/bin/activate"

   "./templater.py" template.tex.jinja2 | sponge "display.tex"
   latexmk -pdf --xelatex -f -silent display.tex
   pdftocairo -png -mono -singlefile -antialias none display.pdf display
   convert -rotate 180 display.png display.png
   python "$HOME/RaspberryPi/python3/display.py" "display.png"
) 2>&1 | tee "${SCRIPTPATH}/log"
