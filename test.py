from class_TkPlotCanvas import TkPlotCanvas
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