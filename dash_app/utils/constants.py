VALID_ATTRIBUTE_TYPES = ["category", "color", "fabric"]

# These are potential values for dropdowns, derived from gtrends columns primarily.
# Actual filtering/matching in make_bar_chart will depend on existing columns in gtrends_cleaned.csv
UNIQUE_CATEGORIES = sorted(list(set([
    "long sleeve", "culottes", "miniskirt", "short sleeves", "printed shirt", 
    "short cardigan", "solid color top", "trapeze dress", "sleeveless", 
    "long cardigan", "sheath dress", "short coat", "medium coat", "doll dress", 
    "long dress", "shorts", "long coat", "jumpsuit", "drop sleeve", 
    "patterned top", "kimono dress", "medium cardigan", "shirt dress", "maxi", 
    "capris", "gitana skirt", "long duster"
])))

UNIQUE_COLORS = sorted(list(set([
    "yellow", "brown", "blue", "grey", "green", "black", "red", "white", "orange", "violet"
])))

UNIQUE_FABRICS = sorted(list(set([
    "acrylic", "scuba crepe", "tulle", "angora", "faux leather", "georgette", 
    "lurex", "crepe", "satin cotton", "silky satin", "fur", "matte jersey", 
    "plisse", "velvet", "lace", "cotton", "piquet", "plush", "bengaline", 
    "jacquard", "frise", "technical", "cady", "dark jeans", "light jeans", 
    "ity", "plumetis", "polyviscous", "dainetto", "webbing", "foam rubber", 
    "chanel", "marocain", "macrame", "embossed", "heavy jeans", "nylon", 
    "tencel", "paillettes", "chambree", "chine crepe", "muslin cotton or silk", 
    "linen", "tactel", "viscose twill", "cloth", "mohair", "mutton", 
    "scottish", "milano stitch", "devore", "ottoman",
    "fluid", "flamed", "fluid polyviscous", "shiny jersey", "goose"
])))

DEFAULT_PRODUCT_IMAGE = "default_product_placeholder.png"