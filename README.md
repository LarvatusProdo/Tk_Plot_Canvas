# TkPlotCanvas

## Description

`class_TkPlotCanvas.py` fournit un point d'entrée compatible vers la classe `TkPlotCanvas`, implémentée dans le sous-dossier `plot/`. Le projet permet d'intégrer des figures Matplotlib dans des applications Tkinter avec des fonctionnalités avancées de personnalisation, telles que la modification des axes, des courbes, des légendes et d'un cartouche de métadonnées.

Les panneaux de réglages et leurs dialogues sont regroupés dans `menu/`. Les modules de tracé et le canevas sont regroupés dans `plot/`.

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

Importez la classe `TkPlotCanvas` depuis son nouveau module et créez une instance dans votre application Tkinter :

```python
from plot.class_TkPlotCanvas import TkPlotCanvas
import tkinter as tk

root = tk.Tk()
plot_canvas = TkPlotCanvas(root)
plot_canvas.pack(fill=tk.BOTH, expand=True)

# Exemple de tracé
import numpy as np
x = np.linspace(0, 10, 100)
y = np.sin(x)
z = np.cos(x)

plot_canvas.plot(x, y, label={'curve' : 'Sine wave', "comment" : ""})
plot_canvas.plot(x, z, label={'curve' : 'Cosine wave', "comment" : ""}, clear=False)

root.mainloop()
```

Pour charger une vue sauvegardée :

```python
plot_canvas = TkPlotCanvas(root, load_view='vue.json')
```

![Exemple avec le fichier "vue.json"](https://github.com/LarvatusProdo/Tk_Plot_Canvas/blob/main/image/Exemple_la_vue_json.jpg)

## Structure du projet

- `plot/` : Implémentation du canevas et modules de tracé standard, xarray, colorbar, métadonnées et paramètres de vue.
- `menu/` : Fenêtre de réglages, panneaux de configuration et dialogues associés.
- `class_TkPlotCanvas.py` : Façade conservant l'import historique `from class_TkPlotCanvas import TkPlotCanvas`.
- `class_menu_graphique.py` : Façade conservant les imports historiques du menu et des dialogues 3D.
- `vertical_frame.py` : Module auxiliaire pour des frames défilantes verticales.
- `vue.json` : Exemple de fichier de vue sauvegardée.
- `vue_xarray.json` : Exemple de vue pour données xarray.
- `__init__.py` : Fichier d'initialisation du package.

## Exemples

Consultez les fichiers `vue.json` et `vue_xarray.json` pour des exemples de configurations sauvegardées.

## Contribution

Les contributions sont les bienvenues ! Veuillez soumettre des issues ou des pull requests sur le dépôt GitHub.
