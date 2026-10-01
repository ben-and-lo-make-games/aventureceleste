#!/usr/bin/env python3
"""Estampille l'appel a style.css du hash de son contenu, dans chaque page.

GitHub Pages sert la feuille avec cache-control max-age=600, et un navigateur
la garde parfois plus longtemps. Si la page l'appelle toujours style.css, un
visiteur deja venu voit l'ancien style apres une mise a jour. Avec
style.css?v=<hash>, l'adresse change des que le contenu change, et le
navigateur va chercher la nouvelle.

A relancer apres chaque modification de style.css :

    python3 outils/version.py
"""
import hashlib
import pathlib
import re

racine = pathlib.Path(__file__).resolve().parent.parent
empreinte = hashlib.sha1((racine / "style.css").read_bytes()).hexdigest()[:8]

for page in sorted(racine.glob("*.html")):
    texte = page.read_text(encoding="utf-8")
    nouveau = re.sub(r'href="style\.css(\?v=[0-9a-f]+)?"', f'href="style.css?v={empreinte}"', texte)
    if nouveau != texte:
        page.write_text(nouveau, encoding="utf-8")
    print(f"{page.name:22s} style.css?v={empreinte}")
