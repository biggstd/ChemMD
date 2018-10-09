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
import pprint
import uuid
import numpy as np
import pandas as pd
import param  # Boiler-plate for controlled class attributes.
from textwrap import dedent  # Prevent indents from percolating to the user.
from typing import Union, List

# ----------------------------------------------------------------------------
# Local project imports.
# ----------------------------------------------------------------------------

from . import util
from .. import io
from ..transforms import INDEPENDENT_TRANSFORMS

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

    experiment_name = param.String(
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

    def data_length(self):
        csv_data_dict = io.load_csv_as_dict(self.datafile)
        return max

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

        def build_species_keys(element):
            species = sorted(util.get_all_elements(element, "all_species"),
                             key=lambda s: s.stoichiometry)
            return tuple({s.species_reference for s in species})

        def build_factor_keys(factor):
            return tuple(filter(None, [factor.factor_type,
                                       factor.unit_reference,
                                       factor.reference_value]))

        mapping = {}

        samples = self.get_all_samples()

        for sample in samples:

            sources = util.get_all_elements(sample, "all_sources")

            for source in sources:

                source_factors = util.get_all_elements(source, "all_factors")
                source_species_keys = build_species_keys(source)

                for factor in source_factors:
                    factor_keys = build_factor_keys(factor)
                    mapping[source_species_keys + factor_keys] = factor

            sample_factors = util.get_all_elements(sample, "all_factors")
            sample_species_keys = build_species_keys(sample)

            for factor in sample_factors:
                sample_factor_keys = build_factor_keys(factor)
                mapping[sample_species_keys + sample_factor_keys] = factor

        factors = self.parental_factors + self.factors
        exp_species_keys = build_species_keys(self)
        for factor in factors:
            exp_factor_keys = build_factor_keys(factor)
            mapping[exp_species_keys + exp_factor_keys] = factor

        logger.debug(f"Created mapping: {pprint.pformat(mapping)}")
        return mapping

    def build_species_map(self, species):
        return collections.ChainMap(
            {s.species_reference: s.stoichiometry
             for s in species})

    def species_group_match(self, group):
        __g_label, __g_unit_filter, g_species_filter = group
        all_species = self.get_all_species()
        species_map = self.build_species_map(all_species)
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
        checks = itertools.product(all_species, g_species_filter)

        matching_species = [species
                            for species, filter in checks
                            if species.query(filter)]

        return matching_species

    def group_factor_map_matches(self, group):
        g_label, g_unit_filter, g_species_filter = group
        # factor_map = self.build_factor_map()
        all_factors = self.get_all_factors()

        matching_factors = [factor for factor in all_factors
                            if factor.query(g_unit_filter)]
        return matching_factors

    def parse_factor_match(self, factor, group):

        g_label, g_unit_filter, g_species_filter = group

        # Pick the 'best' matching factor. For now just pick this first.
        # The list of species could be used to resolve the order.
        # Prioritize csv column factors.
        # Prioritize by factor value -- how to do for csv col factors?
        # Throw an error?

        # Get the associated species matches.
        g_species_matches = self.group_species_map_matches(group)
        sorted_species = sorted(g_species_matches, key=lambda s: s.stoichiometry,
                                reverse=True)
        species_match = sorted_species[0]

        if factor.is_csv_index:
            print(factor)
            csv_data_dict = io.load_csv_as_dict(self.datafile)
            data = np.array(csv_data_dict[str(factor.csv_column_index)])
            # Now check for independent transforms that require
            # species context.
            for key, func in INDEPENDENT_TRANSFORMS.items():
                if any(unit in key for unit in g_unit_filter):
                    data = func(data, species_match)
                    logger.info(f"Transform {func} called for {key}.")
            return data
        else:
            return [factor.value, ]

    def parse_species_match(self, species):
        return [species.species_reference, ]

    def export_by_groups(self, groups: List):
        frame_dict = {}

        for group in groups:
            logger.debug(f"{'-' * 25} Entering group: {group}")
            # Unpack the group object.
            g_label, g_unit_filter, g_species_filter = group
            # print(self.group_species_map_matches(group))
            # logger.debug(f"{self.group_species_map_matches(group)}")

            if g_unit_filter == ("Species",) \
                    and self.species_group_match(group):
                g_species_matches = list(self.group_species_map_matches(group))
                # Return the first matching species reference.
                for g_species, species in itertools.product(g_species_filter, g_species_matches):
                    if species.query(g_species):
                        frame_dict[g_label] = species.species_reference
                        logger.debug(f"Species Group match found. {species.species_reference}")
                        continue

            elif self.factor_group_match(group) \
                    and self.species_group_match(group):

                g_factor_matches = self.group_factor_map_matches(group)
                logger.debug(f"Found these matching factors: {g_factor_matches}")
                if len(g_factor_matches) > 1:
                    logger.warn(f"{len(g_factor_matches)} factor matches found."
                                " Only returning the first match.")

                g_factor_data = self.parse_factor_match(g_factor_matches[0], group)
                frame_dict[g_label] = g_factor_data

                continue

            else:
                logger.debug(f"No match found for {group}")
                continue

        factor_size = max(len(values) for values in frame_dict.values())

        for key, value in frame_dict.items():
            if len(value) == 1:
                frame_dict[key] = value * factor_size

        df = pd.DataFrame(frame_dict)
        df["metadata_uuid"] = self.metadata_uuid
        metadata = {self.metadata_uuid: self}
        logger.debug(df)
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

    sample_name = param.String(
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

    source_name = param.String(
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
