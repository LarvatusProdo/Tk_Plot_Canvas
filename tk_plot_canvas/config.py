"""Application-wide constants for the TkPlotCanvas package.

Every literal shared between modules (window sizes, style names, tab names,
default values, persisted keys...) lives here so that the rest of the code
never hard-codes them.
"""

# --- Matplotlib / figure -----------------------------------------------------
MATPLOTLIB_BACKEND = "TkAgg"
DEFAULT_DPI = 100
DEFAULT_FIGSIZE = (5.0, 4.0)
DEFAULT_BACKGROUND_COLOR = "white"

# --- Plot types and contour class modes --------------------------------------
PLOT_TYPE_2D = "2D"
PLOT_TYPE_3D = "3D"
CLASS_MODE_AUTO = "Auto"
CLASS_MODE_MANUAL = "Manuel"
CLASS_MODE_NONE = "Aucune"
CLASS_MODES = [CLASS_MODE_AUTO, CLASS_MODE_MANUAL, CLASS_MODE_NONE]

# --- Fonts -------------------------------------------------------------------
LINUX_SYSTEM_NAME = "Linux"
LINUX_DEFAULT_FONT = "DejaVu Sans"
OTHER_DEFAULT_FONT = "Arial"
FALLBACK_FONT_SIZE = "12"
FALLBACK_FONT_WEIGHT = "normal"
UI_FONT_SIZE = 10
# Matplotlib/Tk value -> name displayed in the dialogs.
FONT_STYLE_NAMES = {"normal": "Normal", "italic": "Italique", "oblique": "Oblique"}
FONT_STYLES = list(FONT_STYLE_NAMES)
FONT_SIZE_RANGE = (1, 72)
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT_COLOR = "#000000"
CARTOUCHE_LINE_SYMBOL_FONT = ("Helvetica", 15, "bold")

# --- Curves ------------------------------------------------------------------
# Matplotlib value -> name displayed in the "Courbes" tab.
LINE_STYLE_NAMES = {
    "-": "Continu",
    "--": "Tirets",
    "-.": "Tirets-points",
    ":": "Pointillés",
    "None": "Aucun",
}
MARKER_NAMES = {
    "o": "Cercle",
    "s": "Carré",
    "^": "Triangle",
    "D": "Losange",
    "x": "Croix",
    "+": "Plus",
    ".": "Point",
    "None": "Aucun",
}
LINE_STYLES = list(LINE_STYLE_NAMES)
MARKERS = list(MARKER_NAMES)
SOLID_LINE_STYLE = "-"
SOLID_LINE_SYMBOL = "―"
NO_STYLE = "None"
NO_LEGEND_LABEL = "_nolegend_"
LINE_WIDTH_RANGE = (0.5, 10.0, 0.5)
MARKER_SIZE_RANGE = (1, 20, 1)
ALPHA_RANGE = (0.0, 1.0, 0.05)
DEFAULT_ALPHA = "1.0"

# --- Axes --------------------------------------------------------------------
AXIS_SCALE_NAMES = {"linear": "Linéaire", "log": "Logarithmique"}
AXIS_SCALES = list(AXIS_SCALE_NAMES)
AXIS_LIMIT_DECIMALS = 4
VARIABLE_SEPARATOR = "---------"
GEOGRAPHIC_DIMENSIONS = ("longitude", "latitude")
COASTLINE_WIDTH = 0.5
BORDER_WIDTH = 0.3

# --- Colorbar ----------------------------------------------------------------
COLORBAR_VERTICAL = "vertical"
COLORBAR_HORIZONTAL = "horizontal"
COLORBAR_ORIENTATIONS = [COLORBAR_VERTICAL, COLORBAR_HORIZONTAL]
COLORBAR_LOCATION_NAMES = {"right": "Droite", "left": "Gauche", "top": "Haut", "bottom": "Bas"}
COLORBAR_LOCATIONS = list(COLORBAR_LOCATION_NAMES)
KEY_COLORBAR_STYLE = "colorbar_style"
# Matplotlib defaults: length (shrink), thickness (aspect = length/width),
# distance to the axes (pad), share of the axes space (fraction).
COLORBAR_STYLE_DEFAULT = {
    "location": "right",
    "shrink": 1.0,
    "aspect": 20.0,
    "pad": 0.05,
    "fraction": 0.15,
    "tick_labelsize": 10.0,
    "outline_width": 0.8,
}

# --- 3D plot kinds -----------------------------------------------------------
# Persisted kind -> name displayed in the "Graphique 3D" tab.
SURFACE_KIND_FILLED_CONTOURS = "contourf"
SURFACE_KIND_CONTOUR_LINES = "contour"
SURFACE_KIND_MESH = "pcolormesh"
SURFACE_KIND_SCATTER = "scatter"
SURFACE_KIND_NAMES = {
    SURFACE_KIND_FILLED_CONTOURS: "Contours remplis",
    SURFACE_KIND_CONTOUR_LINES: "Isolignes",
    SURFACE_KIND_MESH: "Maillage (pixels)",
    SURFACE_KIND_SCATTER: "Nuage de points",
}
SURFACE_KINDS = list(SURFACE_KIND_NAMES)
DEFAULT_SURFACE_KIND = SURFACE_KIND_FILLED_CONTOURS
KEY_SURFACE_KIND = "surface_kind"
# Number of classes Matplotlib aims at for filled contours (used by every kind).
DEFAULT_CLASS_COUNT = 7
# Size edited for the kinds that have one: line width of the contour lines
# (points), area of the scatter markers (points²). Ranges: (min, max, increment).
SURFACE_SIZE_DEFAULTS = {SURFACE_KIND_CONTOUR_LINES: 1.0, SURFACE_KIND_SCATTER: 10.0}
SURFACE_SIZE_RANGES = {
    SURFACE_KIND_CONTOUR_LINES: (0.1, 10.0, 0.1),
    SURFACE_KIND_SCATTER: (1.0, 500.0, 1.0),
}
KEY_SURFACE_SIZES = "surface_sizes"

# --- 3D plot axes ------------------------------------------------------------
KEY_SURFACE_AXES_STYLE = "axes_style"
# "aspect": None keeps the Matplotlib/cartopy default, else "equal", "auto" or a
# positive number (y/x scale ratio).
SURFACE_AXES_STYLE_DEFAULT = {
    "aspect": None,
    "grid": False,
}
ASPECT_CHOICES = {"par défaut": None, "égal": "equal", "libre": "auto"}

# --- Layout ------------------------------------------------------------------
# Tk distance in points ("75p" = 100 pixels at 100 %), so it follows the screen scale.
CARTOUCHE_HEIGHT = "75p"
SETTINGS_WINDOW_SIZE = "1000x550"
SETTINGS_WINDOW_OFFSET = (600, 50)
DIALOG_SIZE = "400x450"
VALUE_RANGE_DIALOG_SIZE = "400x500"
DIALOG_OFFSET = (50, 50)
NOTEBOOK_PADDING = (5, 5, 5, 5)
SCROLLED_FRAME_DEFAULT_HEIGHT = "7c"
SCROLLED_FRAME_INNER_OFFSET = 4
CLASS_EDITOR_WIDTH = 45
HOVER_BACKGROUND = "#e6f2ff"

# --- Settings window tab names (shown to the user, never persisted) ----------
TAB_AXES = "Axes et titre"
TAB_CARTOUCHE = "Cartouche"
TAB_CURVES = "Courbes"
TAB_LEGEND = "Légende"
TAB_3D = "Surface"

# --- Font dialog targets -----------------------------------------------------
FONT_TARGET_CARTOUCHE = "cartouche"
FONT_TARGET_TITLE = "Graphique title"
FONT_TARGET_XLABEL = "xlabel"
FONT_TARGET_YLABEL = "ylabel"
FONT_TARGET_COLORBAR = "colorbar label"
FONT_DIALOG_TITLES = {
    FONT_TARGET_CARTOUCHE: "Polices du cartouche",
    FONT_TARGET_TITLE: "Police du titre",
    FONT_TARGET_XLABEL: "Polices de l'axe X",
    FONT_TARGET_YLABEL: "Polices de l'axe Y",
    FONT_TARGET_COLORBAR: "Police du label de la colorbar",
}

# --- ttk style names ---------------------------------------------------------
STYLE_FRAME = "TkPlotCanvas.TFrame"
STYLE_NOTEBOOK = "TkPlotCanvas.TNotebook"
STYLE_NOTEBOOK_TAB = "TkPlotCanvas.TNotebook.Tab"
STYLE_LABEL = "TkPlotCanvas.TLabel"
STYLE_CHECKBUTTON = "TkPlotCanvas.TCheckbutton"
STYLE_LABELFRAME = "TkPlotCanvas.TLabelframe"
STYLE_LABELFRAME_LABEL = "TkPlotCanvas.TLabelframe.Label"
STYLE_ENTRY = "TkPlotCanvas.TEntry"
STYLE_BUTTON = "TkPlotCanvas.TButton"
STYLE_SPINBOX = "TkPlotCanvas.TSpinbox"
STYLE_COMBOBOX = "TkPlotCanvas.TCombobox"
STYLE_SECTION_TITLE = "SectionTitle.TLabel"
STYLE_COLUMN_HEADER = "ColumnHeader.TLabel"
STYLE_CARTOUCHE_HEADER = "CartoucheHeader.TLabel"
STYLE_CARTOUCHE_CELL = "CartoucheCell.TLabel"
STYLE_CARTOUCHE_FRAME = "Cartouche.TFrame"
STYLE_HOVER_FRAME = "ClassSelection.TFrame"
STYLE_HOVER_LABEL = "ClassSelection.TLabel"
STYLE_HOVER_ENTRY = "ClassSelection.TEntry"

# --- File dialogs ------------------------------------------------------------
JSON_EXTENSION = ".json"
JSON_FILE_TYPES = [("Fichiers JSON", "*.json")]
FILE_DIALOG_INITIAL_DIR = "."
EXPORT_DPI = 200
EXPORT_DEFAULT_EXTENSION = ".png"
EXPORT_FILE_TYPES = [
    ("Image PNG", "*.png"),
    ("Document PDF", "*.pdf"),
    ("Image vectorielle SVG", "*.svg"),
    ("Image JPEG", "*.jpg"),
]

# --- Keyboard shortcuts (Tk sequences; upper case covers Caps Lock) ----------
SHORTCUT_SAVE_VIEW = ("<Control-s>", "<Control-S>")
# Ctrl+G is kept for compatibility with earlier versions.
SHORTCUT_LOAD_VIEW = ("<Control-o>", "<Control-O>", "<Control-g>", "<Control-G>")
SHORTCUT_EXPORT_IMAGE = ("<Control-e>", "<Control-E>")
SHORTCUT_COPY_IMAGE = ("<Control-c>", "<Control-C>")

# --- Persisted view keys (JSON format, must never change) --------------------
KEY_PLOT_TYPE = "plot_type"
KEY_CURVES = "curves"
KEY_CURVE_TYPE = "type"
CURVE_TYPE_LINE = "line"
CURVE_TYPE_CONTOUR = "contour"
KEY_XARRAY_3D = "xarray_3D"
KEY_LEVELS_AUTO = CLASS_MODE_AUTO
KEY_LEVELS_MANUAL = CLASS_MODE_MANUAL
KEY_VALUE_RANGE = "value_range"
VALUE_RANGE_DEFAULT = "valeur par défaut"
# Figure margins and spacing edited with the toolbar "Configure subplots" dialog.
KEY_SUBPLOT_PARAMS = "subplot_params"
SUBPLOT_PARAM_NAMES = ("left", "bottom", "right", "top", "wspace", "hspace")

# --- Demo --------------------------------------------------------------------
DEMO_WINDOW_TITLE = "Tkinter + Matplotlib Plot Demo"
DEMO_XARRAY_VIEW = "vue_xarray.json"
