# ----------------------------------------------------------------------------
# Transform Functions
# ----------------------------------------------------------------------------
def apply_stoichiometry_coefficient(data, species):
    stoichiometry = species.stoichiometry
    return data * stoichiometry

# ----------------------------------------------------------------------------
# Global Definitions
# ----------------------------------------------------------------------------
TRANSFORMS = {
    ("Molar"): apply_stoichiometry_coefficient,
}
