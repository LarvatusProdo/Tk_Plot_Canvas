# TkPlotCanvas

## Description

`class_TkPlotCanvas.py` est un module Python qui fournit une classe `TkPlotCanvas` pour créer des interfaces graphiques de tracé interactives en utilisant Tkinter et Matplotlib. Ce module permet d'intégrer des figures Matplotlib dans des applications Tkinter avec des fonctionnalités avancées de personnalisation, telles que la modification des axes, des courbes, des légendes et d'un cartouche de métadonnées.

Le script inclut également des classes auxiliaires comme `Window_font_parameter` pour la personnalisation des polices et `Menu_graphique` pour un menu de modification des paramètres du graphique.

## Fonctionnalités

- **Intégration Matplotlib dans Tkinter** : Crée un canevas Tkinter qui affiche une figure Matplotlib.
- **Personnalisation des axes et titres** : Modification des étiquettes, limites, échelles (linéaire/log) et polices des axes X et Y, ainsi que du titre du graphique.
- **Édition des courbes** : Changement de couleur, épaisseur de ligne, style de ligne, marqueurs et taille des marqueurs pour chaque courbe tracée.
- **Légende interactive** : Affichage/masquage de la légende, personnalisation des entrées basées sur les métadonnées, et positionnement automatique.
- **Cartouche de métadonnées** : Tableau affichant des informations supplémentaires pour chaque courbe, avec possibilité de sélectionner quelles métadonnées afficher.
- **Sauvegarde et chargement de vues** : Enregistrement des paramètres du graphique dans des fichiers JSON pour une réutilisation ultérieure.
- **Support des données xarray** : Gestion des données multidimensionnelles xarray pour les tracés.
- **Menus contextuels** : Clic droit sur le canevas pour accéder aux options de personnalisation.
- **Personnalisation des polices** : Dialogues pour modifier les polices des titres, axes et cartouches.

## Prérequis

- Python 3.x
- Tkinter (inclus dans la plupart des installations Python)
- Matplotlib
- xarray
- NumPy

Installez les dépendances via pip :

```bash
pip install matplotlib xarray numpy
```

## Utilisation

Importez la classe `TkPlotCanvas` et créez une instance dans votre application Tkinter :

```python
from class_TkPlotCanvas import TkPlotCanvas
import tkinter as tk

root = tk.Tk()
plot_canvas = TkPlotCanvas(root)
plot_canvas.pack(fill=tk.BOTH, expand=True)

# Exemple de tracé
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
plot_canvas.axes.plot(x, y, label='Sine wave')
plot_canvas._canvas.draw()

root.mainloop()
```

Pour charger une vue sauvegardée :

```python
plot_canvas = TkPlotCanvas(root, load_view='vue.json')
```

## Structure du projet

- `class_TkPlotCanvas.py` : Script principal contenant les classes `TkPlotCanvas`, `Menu_graphique` et `Window_font_parameter`.
- `vertical_frame.py` : Module auxiliaire pour des frames défilantes verticales.
- `vue.json` : Exemple de fichier de vue sauvegardée.
- `vue_xarray.json` : Exemple de vue pour données xarray.
- `__init__.py` : Fichier d'initialisation du package.

## Exemples

Consultez les fichiers `vue.json` et `vue_xarray.json` pour des exemples de configurations sauvegardées.

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre des issues ou des pull requests sur le dépôt GitHub.

## Licence

Ce projet est sous licence MIT. Consultez le fichier LICENSE pour plus de détails.