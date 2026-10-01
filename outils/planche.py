#!/usr/bin/env python3
"""Trace une planche celeste en SVG depuis les donnees du jeu.

Lit assets/stars.bin et assets/figures.bin du projet rive/star (depot
avent-ure-celeste) : directions unitaires equatoriales J2000, magnitudes, et
les polylignes des figures. Projette en stereographique autour de la visee de
la constellation demandee, et donne a chaque etoile un rayon tire de sa
magnitude, comme sur une planche gravee.

    python3 outils/planche.py <chemin/vers/rive/star> [code IAU] > planche.svg

Le code IAU vaut Ori par defaut. Donnees sous licence CC BY-SA : HYG v4.4 de
David Nash pour les etoiles, sky culture western_rey de Stellarium pour les
figures. L'attribution doit accompagner toute reutilisation de la planche.
"""
import math
import struct
import sys


# Etiquettes posees sur la planche, par constellation. Coordonnees J2000 lues
# dans le catalogue HYG v4.4 (colonnes ra en heures, dec en degres). Chaque
# entree : texte, ra, dec, decalage x, decalage y, alignement du texte.
ETIQUETTES = {
    "Ori": [
        ("B\u00e9telgeuse", 5.9195, +7.4071, -11.5, 3.5, "end"),
        ("Rigel",           5.2423, -8.2016,  11.5, 3.5, "start"),
        ("les Trois Rois",  5.6036, -1.2019, -14.0, 14.0, "end"),
    ],
}


def lire_etoiles(chemin):
    b = open(chemin, "rb").read()
    magic, _version, n, taille = struct.unpack_from("<4sIII", b, 0)
    if magic != b"RSTR" or taille != 24:
        raise SystemExit("stars.bin : en-tete inattendu")
    return [struct.unpack_from("<ffff", b, 16 + i * 24) for i in range(n)]


def lire_figures(chemin):
    b = open(chemin, "rb").read()
    magic, _v, nfig, npoly, nidx, _ntn, ncons, _ = struct.unpack_from("<4sIIIIIII", b, 0)
    if magic != b"RFIG":
        raise SystemExit("figures.bin : en-tete inattendu")
    o = 32
    figs = [struct.unpack_from("<HHHH4sffffI", b, o + i * 32) for i in range(nfig)]
    o += nfig * 32
    cons = [struct.unpack_from("<4sffffIHHHH", b, o + i * 32) for i in range(ncons)]
    o += ncons * 32
    polys = [struct.unpack_from("<HH", b, o + i * 4) for i in range(npoly)]
    o += npoly * 4
    idx = [struct.unpack_from("<H", b, o + i * 2)[0] for i in range(nidx)]
    return figs, cons, polys, idx


def main():
    racine = sys.argv[1] if len(sys.argv) > 1 else "rive/star"
    code = (sys.argv[2] if len(sys.argv) > 2 else "Ori")

    etoiles = lire_etoiles(f"{racine}/assets/stars.bin")
    figs, cons, polys, idx = lire_figures(f"{racine}/assets/figures.bin")

    cible = next((c for c in cons if c[0].decode().strip() == code), None)
    if cible is None:
        raise SystemExit(f"constellation inconnue : {code}")
    _, fx, fy, fz, rayon, _, prem_fig, nb_fig, _, _ = cible

    forward = (fx, fy, fz)
    nord = (0.0, 0.0, 1.0)
    cross = lambda a, c: (a[1]*c[2]-a[2]*c[1], a[2]*c[0]-a[0]*c[2], a[0]*c[1]-a[1]*c[0])
    dot = lambda a, c: a[0]*c[0] + a[1]*c[1] + a[2]*c[2]
    m = math.sqrt(dot(cross(nord, forward), cross(nord, forward)))
    droite = tuple(v / m for v in cross(nord, forward))
    haut = cross(forward, droite)

    largeur, hauteur = 340.0, 300.0
    cx, cy = largeur / 2, hauteur / 2
    # Un peu plus large que la constellation, pour lui laisser de l'air.
    champ = min(math.radians(60.0), rayon * 2.0 + math.radians(9.0))
    echelle = (min(largeur, hauteur) / 2 - 16) / (2 * math.tan(champ / 2) / (1 + math.cos(champ / 2)))

    def projette(s):
        d = dot(s, forward)
        if d <= 0.2:
            return None
        k = 2.0 / (1.0 + d)
        return (cx - k * dot(s, droite) * echelle, cy - k * dot(s, haut) * echelle)

    lignes, sommets = [], set()
    for fi in range(prem_fig, prem_fig + nb_fig):
        premiere, combien = figs[fi][0], figs[fi][1]
        for pi in range(premiere, premiere + combien):
            debut, compte = polys[pi]
            points = []
            for k in range(compte):
                si = idx[debut + k]
                sommets.add(si)
                points.append(projette(etoiles[si][:3]))
            lignes += [(a, c) for a, c in zip(points, points[1:]) if a and c]

    champ_visible = []
    for i, (x, y, z, mag) in enumerate(etoiles):
        if mag > 5.2:
            continue
        p = projette((x, y, z))
        if p and 6 <= p[0] <= largeur - 6 and 6 <= p[1] <= hauteur - 6:
            champ_visible.append((p, mag, i in sommets))

    rayon_mag = lambda m: max(0.7, 3.0 - 0.42 * m)
    ecrire = sys.stdout.write

    ecrire(f'<svg class="planche" viewBox="0 0 {largeur:.0f} {hauteur:.0f}" '
           f'xmlns="http://www.w3.org/2000/svg" role="img" '
           f'aria-label="Planche celeste : {code}">\n')
    ecrire('  <g class="figure">\n')
    for a, c in lignes:
        ecrire(f'    <line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{c[0]:.1f}" y2="{c[1]:.1f}"/>\n')
    ecrire('  </g>\n  <g class="champ">\n')
    for p, mag, som in sorted(champ_visible, key=lambda e: -e[1]):
        if not som:
            ecrire(f'    <circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{rayon_mag(mag):.2f}"/>\n')
    ecrire('  </g>\n  <g class="sommets">\n')
    for p, mag, som in sorted(champ_visible, key=lambda e: -e[1]):
        if som:
            r = rayon_mag(mag)
            ecrire(f'    <circle cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r:.2f}"/>\n')
            if mag < 1.0:
                ecrire(f'    <circle class="halo" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="{r + 3.4:.2f}"/>\n')
    ecrire('  </g>\n')
    etiquettes = ETIQUETTES.get(code, [])
    if etiquettes:
        ecrire('  <g class="noms">\n')
        for texte, ra_h, dec_d, dx, dy, ancre_txt in etiquettes:
            ra, dec = math.radians(ra_h * 15.0), math.radians(dec_d)
            s = (math.cos(dec) * math.cos(ra), math.cos(dec) * math.sin(ra), math.sin(dec))
            p = projette(s)
            if p:
                ecrire(f'    <text x="{p[0] + dx:.1f}" y="{p[1] + dy:.1f}" text-anchor="{ancre_txt}">{texte}</text>\n')
        ecrire('  </g>\n')
    ecrire('</svg>\n')


if __name__ == "__main__":
    main()
