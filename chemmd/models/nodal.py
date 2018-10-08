"""Compound Classes of the package.

These are classes which are composed of elemental, compound, or a combination
of the two.

"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------
import logging
import itertools
import collections
import uuid
import functools
import numpy as np
import pandas as pd
import param  # Boiler-plate for controlled class attributes.
from textwrap import dedent  # Prevent indents from percolating to the user.
from typing import Union, List, Tuple

# ----------------------------------------------------------------------------
# Local project imports.
# ----------------------------------------------------------------------------

from . import util
from .. import io
from .. transforms import INDEPENDENT_TRANSFORMS

logger = logging.getLogger(__name__)


class Node(param.Parameterized):
    """Model for a single Drupal content node.

    Much of this class is declarative, with the Param package doing all of the
    heavy-lifting in the background.

    """

    # name = param.String(
    #     allow_None=False,
    #     doc=dedent("""User supplied title of the Drupal Node or experiment.
    #
    #     This model contains all the information concerning a given
    #     Drupal Node.
    #     """)
    # )

    node_information = param.Dict(
        allow_None=True,
        default=None,
        doc=dedent("""A set of key-value pairs of information concerning 
        this experiment. 
        
        This can be any arbitrary set of key-value paris.
        """)
    )

    experiments = param.List(
        allow_None=True,
        doc=dedent("""A list of Assay models that contain all core 
        data components.
        """)
    )

    factors = param.List(
        allow_None=True,
        doc=dedent("""A list of Factor models that pertain to all 
        assays contained by this Node instance.
        """)
    )

    samples = param.List(
        allow_None=True,
        doc=dedent("""A list of Sample models that are used by all assays 
        contained by this Node instance.
        """)
    )

    comments = param.List(
        allow_None=True,
        doc=dedent(""" A list of Comment models that apply to all of the 
        assays contained by this Node instance.
        """)
    )

    @property
    def as_markdown(self):
        text = ""

        if self.node_information:
            # Create an alias for the information dictionary.
            i = self.node_information
            text = dedent(f"""\
            # {i.get("node_title")}
            
            **Description**: {i.get("node_description")}\n
            **Submission Date**: *{i.get("submission_date")}*\n
            **Public Release Date**: *{i.get("public_release_date")}*\n
            
            ---
            """)

        if self.experiments:
            text += dedent("""## Assays\n""")
            for assay in self.experiments:
                text += assay.as_markdown

        if self.samples:
            text += dedent("""## Samples\n""")
            for sample in self.samples:
                text += sample.as_markdown

        if self.factors:
            text += dedent("""### Factors\n""")
            for factor in self.factors:
                text += factor.as_markdown

        if self.comments:
            text += dedent("""### Comments\n""")
            for comment in self.comments:
                text += comment.as_markdown

        return text


class Experiment(param.Parameterized):
    """Model for single assay / experiment - contains a datafile and all
    metadata pertaining to that file.

    This model is used by the `isadream.io` module to create data frames
    and metadata dictionaries. This model should be considered the 'core'
    of this model set.

    """

    datafile = param.String(
        allow_None=True,  # There could be a single point uploaded.
        doc=dedent("""The filename of the data file which this assay 
        instance models.
        
        The base-path of where this file is actually stored is not 
        considered here.
        """)
    )

    name = param.String(
        allow_None=False,
        doc=dedent("""The user-supplied title of this assay. """))

    factors = param.List(
        allow_None=True,
        doc=dedent("""A list of Factor objects that apply to this assay. """))

    samples = param.List(
        allow_None=True,
        doc=dedent("""A list of Sample objects that are used within 
        this assay.
        """))

    comments = param.List(
        allow_None=True,
        doc=dedent(
            """A list of Comment objects that describe this assay. """))

    parental_factors = param.List(
        allow_None=True,
        doc=dedent("""A list of Factor objects from the parent Node
        of this assay.
        
        All of these factors apply to this assay.
        """))

    parental_samples = param.List(
        allow_None=True,
        doc=dedent("""A list of Sample objects from the parent Node 
        of this assay.
        
        All of these Samples are used by this assay.
        """))

    parental_info = param.Dict(
        allow_None=True,
        doc=dedent("""The metadata information of the parent Node
        of this assay.
        """))

    parental_comments = param.List(
        allow_None=True,
        doc=dedent("""A list of comments from the parent Node 
        of this assay.
        """))

    @property
    def metadata_uuid(self):
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(self)))

    # -------------------------------------------------------------------------
    # Grouping functions.
    # -------------------------------------------------------------------------
    def get_all_samples(self):
        return self.samples + self.parental_samples

    def get_all_sources(self):
        all_samples = self.get_all_samples()
        all_sources = itertools.chain.from_iterable(
            [util.get_all_elements(sample, "all_sources")
             for sample in all_samples])
        return list(all_sources)

    def get_all_factors(self):
        all_samples = self.get_all_samples()
        all_sources = self.get_all_sources()
        all_factors = itertools.chain.from_iterable(
            [util.get_all_elements(sample, "all_factors")
             for sample in all_samples + all_sources])
        return self.parental_factors + self.factors + list(all_factors)

    def get_all_species(self):
        all_samples = self.get_all_samples()
        all_sources = self.get_all_sources()
        all_species = itertools.chain.from_iterable(
            [util.get_all_elements(sample, "all_species")
             for sample in all_samples + all_sources])
        return list(all_species)

    # -------------------------------------------------------------------------
    # ChainMap creation functions.
    # -------------------------------------------------------------------------
    def build_factor_map(self):
        all_factors = self.get_all_factors()
        return collections.ChainMap(
            {"__".join(filter(None, [f.factor_type,
                                     f.unit_reference,
                                     f.reference_value,
                                     ])): f
             for f in all_factors})

    def build_species_map(self):
        all_species = self.get_all_species()
        return collections.ChainMap(
            {s.species_reference: s.stoichiometry
             for s in all_species})

    def species_group_match(self, group):
        __g_label, __g_unit_filter, g_species_filter = group
        species_map = self.build_species_map()
        if any(g_species in species_map.keys()
               for g_species in g_species_filter):
            return True

    def factor_group_match(self, group):
        __g_label, g_unit_filter, __g_species_filter = group
        all_factors = self.get_all_factors()
        if any(factor.query(g_unit_filter)
               for factor in all_factors):
            return True

    def group_species_map_matches(self, species_group):
        g_label, __g_unit_filter, g_species_filter = species_group
        all_species = self.get_all_species()
        matching_species_refs = [species
                                 for species in all_species
                                 if species.species_reference
                                 in g_species_filter]
        return {f"{g_label}__{idx}": match
                for idx, match in enumerate(matching_species_refs)}

    def group_factor_map_matches(self, group):
        g_label, g_unit_filter, g_species_filter = group
        factor_map = self.build_factor_map()
        return {f"{g_label}__{f_label}": factor
                for f_label, factor in factor_map.items()
                if factor.query(g_unit_filter)}

    def parse_factor_match(self, factor, group):
        g_label, g_unit_filter, g_species_filter = group

        if factor.is_csv_index:
            csv_data_dict = io.load_csv_as_dict(self.datafile)
            data = np.array(csv_data_dict[str(factor.csv_column_index)])

            g_species_dicts = self.group_species_map_matches(group)
            g_species_refs = [s.species_reference for s in
                              g_species_dicts.values()]



            # Now check for independent transforms that require
            # species context.
            for key, func in INDEPENDENT_TRANSFORMS.items():

                if any(unit in key for unit in g_unit_filter):
                    data = func(data, g_species_dicts[0])
                    logger.info(f"Transform {func} called for {key}.")

            return data
        else:
            return factor.value

    def parse_species_match(self, species):
        return species.species_reference

    def export_by_groups(self, groups: List):
        # TODO: Remove the need to specify a species column.
        frame_dict = {}

        for group in groups:
            # Unpack the group object.
            g_label, g_unit_filter, g_species_filter = group

            if g_unit_filter == ("Species",) \
                    and self.species_group_match(group):
                g_species_dicts = self.group_species_map_matches(group)
                g_species_data = {key: self.parse_species_match(value)
                                  for key, value in g_species_dicts.items()}
                frame_dict = {**frame_dict, **g_species_data}

            elif self.factor_group_match(group) \
                    and self.species_group_match(group):

                g_factor_dicts = self.group_factor_map_matches(group)
                g_factor_data = {key: self.parse_factor_match(value, group)
                                 for key, value in g_factor_dicts.items()}

                frame_dict = {**frame_dict, **g_factor_data}

            else:
                continue

        df = pd.DataFrame(frame_dict)
        df["metadata_uuid"] = self.metadata_uuid
        metadata = {self.metadata_uuid: self}

        return df, metadata

    @property
    def as_markdown(self):
        # TODO: Examine function for completeness.
        text = f"### {self.assay_title}\n"
        for sample in self.samples:
            text += sample.as_markdown

        for factor in self.factors:
            text += factor.as_markdown

        for comment in self.comments:
            text += comment.as_markdown

        return text


class Sample(param.Parameterized):
    """Model for a physical of simulated sample.

    A Sample object is a collection of species and factors.

    """

    name = param.String(
        allow_None=False,
        doc=dedent("""The user supplied name of this sample.
        """)
    )

    factors = param.List(
        allow_None=True,
        doc=dedent("""Factors that apply to only to this sample.
        """)
    )

    species = param.List(
        allow_None=False,  # There must at least be a reference.
        doc=dedent("""A list of species that are contained within this 
        source.
        """)
    )

    sources = param.List(
        allow_None=True,
        doc=dedent("""A list of sources that are contained within
        this sample.
        
        If supplied, factors and species from sources will apply to
        this assay instance as well. If matching factors are found,
        the highest ranking source or sample factor will take precedence.
        """)
    )

    comments = param.List(
        allow_None=True,
        doc=dedent("""A list of comment objects that pertain to this sample.
        """)
    )

    @property
    def all_factors(self) -> List:
        """Recursively find all factors of this assay.

        This includes all those factors and species within sources as well.
        See the ` utils.get_all_elements` documentation for details.

        """
        return util.get_all_elements(self, 'factors')

    @property
    def all_species(self) -> List:
        """Recursively find all species of this assay.

        This includes all those factors and species within sources as well.
        See the ` utils.get_all_elements` documentation for details.

        """
        nodes_out = list()
        for species in set(util.get_all_elements(self, 'species')):
            if species.species_reference is not None \
                    and species.stoichiometry is not None:
                nodes_out.append(species)

        return nodes_out

    @property
    def all_sources(self) -> List:
        """Get all sources contained within this assay.

        This includes nested sources.

        :return: A list of Source model objects.
        """
        return util.get_all_elements(self, 'sources')

    def query(self, query_terms) -> bool:
        """Perform a simple query on the values of this assay instance,
        returns a boolean.

        :return: `True` if a query term is found, `False` otherwise.
        """
        query_terms = util.ensure_list(query_terms)
        if any(species.query(term)
               for term in query_terms
               for species in self.all_species):
            return True

    @property
    def as_markdown(self):
        text = f"#### {self.sample_name}\n"
        for source in self.all_sources:
            text += source.as_markdown

        for factor in self.all_factors:
            text += factor.as_markdown

        for species in self.all_species:
            text += species.as_markdown

        return text


class Source(param.Parameterized):
    """Model for a single Source.

    A source is similar to a sample.

    # TODO: Consider adding nested sources.
    """

    name = param.String(
        allow_None=False,
        doc=dedent("""User given name of this source.
        """)
    )

    species = param.List(
        allow_None=False,
        doc=dedent("""A list of species objects that this source models.
        """)
    )

    factors = param.List(
        allow_None=True,
        doc=dedent("""A list of factor objects that describe this source.
        """)
    )

    comments = param.List(
        allow_None=True,
        doc=dedent("""A list of comment objects that describe this source.
        """)
    )

    @property
    def all_factors(self) -> List:
        """Get all factors associated with this source.

        This function should handle nested sources in the future with only
        minor modifications.

        """
        return util.get_all_elements(self, 'factors')

    @property
    def all_species(self) -> List:
        """Get all species associated with this source.

        This function should handle nested sources with only
        minor modifications.

        :return:
        """
        return util.get_all_elements(self, 'species')

    @property
    def as_markdown(self):
        text = ""
        for factor in self.all_factors:
            text += factor.as_markdown

        for species in self.all_species:
            text += species.as_markdown
        return text


# ----------------------------------------------------------------------------
# Define Type Hints.
# ----------------------------------------------------------------------------

NodeTypes = Union[Node, Sample, Experiment, Source]
