#!/usr/bin/env python3
"""Versionne les adresses internes du site par l'empreinte de son contenu.

GitHub Pages sert les pages et la feuille de style avec cache-control
max-age=600, et l'en-tete ne se regle pas. Un visiteur deja venu garde donc
dix minutes, parfois plus, l'ancienne version d'une page, et l'ancienne feuille
qu'elle appelle.

Le script calcule une empreinte unique du site, style.css et pages confondus,
et l'ajoute a chaque adresse interne : style.css?v=..., index.html?v=..., etc.
Des que quelque chose change, toutes les adresses changent, et un navigateur
qui suit un lien depuis une page fraiche ne trouve plus rien de perime en cache.

L'empreinte se calcule sur les pages debarrassees de leurs propres ?v=, ce qui
la rend stable : relancer le script sans rien changer ne modifie aucun fichier.

A relancer apres chaque modification du site :

    python3 outils/version.py
"""
import hashlib
import pathlib
import re

racine = pathlib.Path(__file__).resolve().parent.parent
pages = sorted(racine.glob("*.html"))
internes = ["style.css"] + [p.name for p in pages]
motif = re.compile(r'href="(' + "|".join(re.escape(n) for n in internes) + r')(\?v=[0-9a-f]+)?"')

def sans_version(texte):
    return motif.sub(lambda m: f'href="{m.group(1)}"', texte)

h = hashlib.sha1((racine / "style.css").read_bytes())
for page in pages:
    h.update(sans_version(page.read_text(encoding="utf-8")).encode("utf-8"))
empreinte = h.hexdigest()[:8]

for page in pages:
    texte = page.read_text(encoding="utf-8")
    nouveau = motif.sub(lambda m: f'href="{m.group(1)}?v={empreinte}"', texte)
    if nouveau != texte:
        page.write_text(nouveau, encoding="utf-8")
    print(f"{page.name:22s} {len(motif.findall(nouveau)):2d} adresses internes en ?v={empreinte}")
