# TkPlotCanvas

## Description

`tk_plot_canvas` intègre des figures Matplotlib dans des applications Tkinter et ajoute une
personnalisation interactive : axes, titres, courbes, légende, cartouche de métadonnées,
cartes 3D (contours remplis, colorbar, classes) et sauvegarde/chargement de vues au format JSON.

## Fonctionnalités

- **Intégration Matplotlib dans Tkinter** : canevas Tkinter avec la barre d'outils Matplotlib.
- **Axes et titres** : étiquettes, limites, échelles (linéaire/log), inversion, polices.
- **Courbes** : couleur, épaisseur, style de ligne, marqueurs et taille des marqueurs.
- **Légende** : affichage/masquage, choix des métadonnées affichées, position automatique.
- **Cartouche** : tableau des métadonnées de chaque courbe, colonnes et polices configurables.
- **Données xarray** : courbes (1 dimension) et cartes en contours remplis (2 dimensions),
  avec côtes et frontières si `cartopy` est installé.
- **Vues** : enregistrement/chargement des réglages dans des fichiers JSON.
- **Menu contextuel** (clic droit sur la figure) : vues, accès direct à chaque onglet de
  réglages, affichage de la légende / du cartouche / de la colorbar, réinitialisation du zoom,
  copie et export de l'image.
- **Raccourcis** : Ctrl+S enregistrer la vue, Ctrl+O charger une vue (Ctrl+G reste accepté),
  Ctrl+E exporter l'image (PNG, PDF, SVG, JPEG), Ctrl+C copier l'image (Windows).
- **Double-clic** : sur le titre, un libellé d'axe ou celui de la colorbar pour le modifier sur
  place ; sur la légende, une courbe, les graduations ou la colorbar pour ouvrir l'onglet
  correspondant.
- **Réglages appliqués immédiatement** : dans les onglets, chaque modification est visible tout
  de suite. Les dialogues (polices, colorbar) montrent un aperçu en direct, avec « Annuler »
  (ou Échap) pour revenir à l'état d'ouverture et « Fermer » pour garder les changements. Seul le
  dialogue des classes demande « Appliquer » / « OK », car il valide une liste entière.

## Prérequis

- Python 3.9+ avec Tkinter
- Matplotlib, NumPy, xarray
- Optionnel : cartopy (fonds de carte), h5netcdf (lecture/écriture des fichiers NetCDF)

```bash
pip install matplotlib numpy xarray
pip install cartopy h5netcdf   # optionnel
```

## Utilisation

```python
import tkinter as tk

import numpy as np

from tk_plot_canvas import TkPlotCanvas

root = tk.Tk()
plot_canvas = TkPlotCanvas(root)              # ou TkPlotCanvas(root, load_view="vue.json")
plot_canvas.pack(fill=tk.BOTH, expand=True)

x = np.linspace(0, 10, 100)
plot_canvas.plot(x, np.sin(x), label={"curve": "Sine wave", "comment": ""})
plot_canvas.plot(x, np.cos(x), label={"curve": "Cosine wave", "comment": ""}, clear=False)

root.mainloop()
```

Sans vue chargée, le titre et les libellés passés à `plot()` sont affichés, le cartouche
montre toutes les métadonnées et `legend=True` affiche la légende avec la première clé.
Une vue JSON, si elle en définit, impose ses propres choix (polices, clés, visibilité).

Sous Windows, l'import de `tk_plot_canvas` rend l'application nette sur les écrans mis à
l'échelle (125 %, 150 %...) : importez le package **avant** de créer `tk.Tk()`.

L'ancien import `from class_TkPlotCanvas import TkPlotCanvas` reste valide.

![Exemple avec le fichier "vue.json"](https://github.com/LarvatusProdo/Tk_Plot_Canvas/blob/main/image/Exemple_la_vue_json.jpg)

### Démonstrations et exemples

Depuis la racine du projet :

```bash
python -m tk_plot_canvas                      # démo xarray (par défaut)
python -m tk_plot_canvas standard             # démo courbes x/y
python -m tk_plot_canvas class-selection      # sélecteur de classes de contours
python -m tk_plot_canvas scrolled-frame       # cadre défilant

python -m examples.example_numpy_curves       # courbes NumPy
python -m examples.example_xarray_timeseries  # série temporelle + vue JSON
python -m examples.example_xarray_map         # carte 3D + vue JSON
```

Les exemples xarray lisent les fichiers `2024_temperature_2m_*.nc` placés dans le dossier
parent du projet ; `tools/create_temporal_netcdf.py` génère la série temporelle.

## Structure du projet

```
tk_plot_canvas/                 Package principal
├── __init__.py                 API publique : TkPlotCanvas, VerticalScrolledFrame, ClassSelectionFrame
├── __main__.py                 Point d'entrée des démos (python -m tk_plot_canvas)
├── config.py                   Constantes (tailles, styles, noms d'onglets, clés JSON...)
├── compat.py                   Compatibilité Matplotlib/Tk (couleurs, colormaps)
├── fonts.py                    Analyse et sécurisation des polices Tk
├── dpi.py                      Netteté sur écrans mis à l'échelle (Windows)
├── clipboard.py                Copie d'une image dans le presse-papiers (Windows)
├── demos.py                    Démonstrations interactives
├── canvas/                     Le widget TkPlotCanvas
│   ├── plot_canvas.py          Classe TkPlotCanvas (mise en page, menu, fenêtre de réglages)
│   ├── styles.py               Styles ttk
│   ├── plot_helpers.py         Étapes communes aux tracés
│   ├── standard_plotting.py    plot(x, y)
│   ├── xarray_curves.py        plot_xarray() et courbes 1D
│   ├── xarray_surfaces.py      Cartes 2D (contours remplis, cartopy)
│   ├── legend.py               Légende
│   ├── cartouche.py            Cartouche de métadonnées
│   ├── colorbar.py             Colorbar et niveaux de contours
│   ├── context_menu.py         Menu contextuel et raccourcis clavier
│   ├── double_click.py         Actions du double-clic sur la figure
│   ├── figure_export.py        Export et copie de l'image
│   └── view_persistence.py     Sauvegarde/chargement de vues
├── view/                       Format des vues JSON
│   ├── capture.py              État du canevas -> dictionnaire
│   ├── restore.py              Dictionnaire -> état du canevas
│   └── storage.py              Lecture/écriture JSON
├── settings/                   Fenêtre de réglages
│   ├── settings_window.py      Fenêtre à onglets
│   ├── base_tab.py             Classe de base des onglets
│   ├── axes_tab.py, axis_frame.py   Onglet « Axes et titre »
│   ├── cartouche_tab.py        Onglet « Cartouche »
│   ├── curves_tab.py           Onglet « Courbes »
│   ├── legend_tab.py           Onglet « Légende »
│   ├── surface_tab.py, surface_axes_frame.py   Onglet « Surface » et aspect des cartes
│   ├── font_controls.py, font_dialogs.py   Dialogues de police
│   ├── colorbar_dialog.py      Dialogue colorbar
│   ├── value_range_dialog.py   Dialogue plage de valeurs / classes
│   ├── dialog_manager.py       Un seul dialogue ouvert par élément édité
│   ├── choices.py              Noms français des choix (styles, échelles, positions)
│   └── window_placement.py     Positionnement et comportement des fenêtres
└── widgets/                    Widgets réutilisables
    ├── scrolled_frame.py       VerticalScrolledFrame
    ├── class_selection.py      ClassSelectionFrame (classes Auto/Manuel/Aucune)
    ├── manual_classes.py       Éditeur des classes manuelles
    ├── tooltip.py              Infobulles
    └── inline_text_editor.py   Édition d'un texte de la figure sur place
examples/                       Exemples exécutables
tools/create_temporal_netcdf.py Génération du NetCDF de série temporelle
Exemples de vues json/          Vues JSON d'exemple
class_TkPlotCanvas.py           Compatibilité avec l'ancien import
```

## Qualité du code

Le code suit PEP 8 (formaté avec `black`, lignes de 99 caractères), avec annotations de type
et docstrings au format Google. Vérifications :

```bash
black -l 99 --check tk_plot_canvas examples tools
flake8 tk_plot_canvas examples tools
pydocstyle --convention=google tk_plot_canvas examples tools
```

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre des issues ou des pull requests sur le dépôt GitHub.
