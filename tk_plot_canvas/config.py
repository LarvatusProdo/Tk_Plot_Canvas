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
FONT_STYLES = ["normal", "italic", "oblique"]
FONT_SIZE_RANGE = (0, 20)
DEFAULT_FONT_SIZE = 10
DEFAULT_FONT_COLOR = "#000000"
CARTOUCHE_LINE_SYMBOL_FONT = ("Helvetica", 15, "bold")

# --- Curves ------------------------------------------------------------------
LINE_STYLES = ["-", "--", "-.", "None"]
MARKERS = ["o", "s", "^", "x", "None"]
SOLID_LINE_STYLE = "-"
SOLID_LINE_SYMBOL = "―"
NO_STYLE = "None"
NO_LEGEND_LABEL = "_nolegend_"
LINE_WIDTH_RANGE = (0.5, 10.0, 0.5)
MARKER_SIZE_RANGE = (1, 20, 1)
ALPHA_RANGE = (0.0, 1.0, 0.05)
DEFAULT_ALPHA = "1.0"

# --- Axes --------------------------------------------------------------------
AXIS_SCALES = ["linear", "log"]
AXIS_LIMIT_DECIMALS = 4
VARIABLE_SEPARATOR = "---------"
GEOGRAPHIC_DIMENSIONS = ("longitude", "latitude")
COASTLINE_WIDTH = 0.5
BORDER_WIDTH = 0.3

# --- Colorbar ----------------------------------------------------------------
COLORBAR_VERTICAL = "vertical"
COLORBAR_HORIZONTAL = "horizontal"
COLORBAR_ORIENTATIONS = [COLORBAR_VERTICAL, COLORBAR_HORIZONTAL]

# --- Layout ------------------------------------------------------------------
CARTOUCHE_HEIGHT = 100
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

# --- Settings window tab names (also persisted as "selected tab") ------------
TAB_AXES = "Axes et titre"
TAB_CARTOUCHE = "Cartouche"
TAB_CURVES = "Courbes"
TAB_LEGEND = "Légende"
TAB_3D = "Graphique 3D"

# --- Font dialog targets -----------------------------------------------------
FONT_TARGET_CARTOUCHE = "cartouche"
FONT_TARGET_TITLE = "Graphique title"
FONT_TARGET_XLABEL = "xlabel"
FONT_TARGET_YLABEL = "ylabel"
FONT_TARGET_COLORBAR = "colorbar label"

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
JSON_FILE_TYPES = [("JSON files", "*.json")]
FILE_DIALOG_INITIAL_DIR = "."

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

# --- Demo --------------------------------------------------------------------
DEMO_WINDOW_TITLE = "Tkinter + Matplotlib Plot Demo"
DEMO_XARRAY_VIEW = "vue_xarray.json"
