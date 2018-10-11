
import logging

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------
# Transform Functions
# ----------------------------------------------------------------------------
def apply_stoichiometry_coefficient(data, species):
    stoichiometry = species.stoichiometry
    return data * stoichiometry


# ----------------------------------------------------------------------------
# Global Definitions
# ----------------------------------------------------------------------------
INDEPENDENT_TRANSFORMS = {
    ("Molar", ): apply_stoichiometry_coefficient,
}


def apply_transform(group_dict):
    for group, metadata_dict in group_dict.items():
        g_label, g_unit_filter, g_species_filter = group

        for key, func in INDEPENDENT_TRANSFORMS.items():
            if any(unit in key for unit in g_unit_filter):
                logger.info(f"Transform {func} called for {key}.")
                data = func(metadata_dict.get("factor_data"),
                            metadata_dict.get("species"))
                metadata_dict["factor_data"] = data
                # return metadata_dict
            # else:
            #     return metadata_dict
    return group_dict

