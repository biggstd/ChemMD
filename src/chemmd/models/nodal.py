"""Compound Classes of the package.

These are classes which are composed of elemental, compound, or a combination
of the two.

"""

# ----------------------------------------------------------------------------
# Imports -- Standard Python modules
# ----------------------------------------------------------------------------
import logging
import uuid

from textwrap import dedent  # Prevent indents from percolating to the user.
from typing import List, Dict
from dataclasses import dataclass

# ----------------------------------------------------------------------------
# Local package imports.
# ----------------------------------------------------------------------------
from . import util
from .core import Factor, Comment, SpeciesFactor
from .. import io

logger = logging.getLogger(__name__)


@dataclass
class Source:
    """Model for a single Source.

    A source is similar to a sample.

    # TODO: Consider adding nested sources.
    """

    source_name: str
    species: List[SpeciesFactor]
    factors: List[Factor] = None
    comments: List[Comment] = None

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

    def species_map(self):
        species = util.get_all_elements(self, "all_species")
        species_map = {s.species_reference: s.stoichiometry
                       for s in species}
        return species_map

    def mapping(self, applied_factors=None):
        # Set to an empty list if no applied factors are given.
        # It is bad form to use a 'mutable' default argument,
        # such as an emtpy list. This is an ad-hoc way around that.
        if applied_factors is None:
            applied_factors = []

        # The applied factors should be a higher priority than the contained
        # factors.
        factors = util.get_all_elements(self, "all_factors") + applied_factors
        mapping = {}

        # Build the basic species map.
        species_map = self.species_map()

        # Construct the basic mapping and add it to the output mapping.
        for factor in factors:
            factor_mapping = {"factor": factor,
                              "source": self,
                              "species_map": species_map}
            mapping[tuple(species_map.keys()), factor.label] = factor_mapping

        return mapping

    @property
    def as_markdown(self):
        text = ""
        for factor in self.all_factors:
            text += factor.as_markdown

        for species in self.all_species:
            text += species.as_markdown
        return text


@dataclass
class Sample:
    """Model for a physical of simulated sample.

    A Sample object is a collection of species and factors.

    """
    sample_name: str
    factors: List[Factor]
    species: List[SpeciesFactor]
    sources: List[Source]
    comments: List[Comment]

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
        for species in util.get_all_elements(self, 'species'):
            if species.species_reference is not None \
                    and species.stoichiometry is not None:
                nodes_out.append(species)

        return nodes_out

    def species_map(self):
        species = util.get_all_elements(self, "all_species")
        species_map = {s.species_reference: s.stoichiometry
                       for s in species}
        return species_map

    def mapping(self, applied_factors=None):
        # Set to an empty list if no applied factors are given.
        # It is bad form to use a 'mutable' default argument,
        # such as an emtpy list. This is an ad-hoc way around that.
        if applied_factors is None:
            applied_factors = []

        # The applied factors should be a higher priority than the contained
        # factors.
        factors = util.get_all_elements(self, "all_factors") + applied_factors
        mapping = {}

        # Build the basic species map.
        species_map = self.species_map()

        # Construct the basic mapping and add it to the output mapping.
        for factor in factors:
            factor_mapping = {"factor": factor,
                              "sample": self,
                              "species_map": species_map}
            mapping[tuple(species_map.keys()), factor.label] = factor_mapping

        return mapping

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


@dataclass
class Experiment:
    """Model for single assay / experiment - contains a datafile and all
    metadata pertaining to that file.

    This model is used by the `chemmd.io` module to create data frames
    and metadata dictionaries. This model should be considered the 'core'
    of this model set.

    """
    name: str
    datafile: str = None
    factors: List[Factor] = None
    samples: List[Sample] = None
    comments: List[Comment] = None
    parental_factors: List[Factor] = None
    parental_info: dict = None
    parental_comments: List[Comment] = None

    @property
    def metadata_uuid(self):
        """Creates and returns a unique universal identifier
        for this object."""
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, str(self)))

    def parse_factor_value(self, factor: Factor) -> List:
        """Parses a factor value.

        :param factor: A `chemmd.models.Factor` object.
        :returns: A sized list of that factors value.
        """
        csv_data_dict = io.input.load_csv_as_dict(self.datafile)
        factor_size = max(len(values) for values in csv_data_dict.values())

        if factor.is_csv_index:
            data = csv_data_dict[str(factor.csv_column_index)]
            return data
        elif factor.value:
            return [factor.value, ] * factor_size

    # -------------------------------------------------------------------------
    # ChainMap creation functions.
    # -------------------------------------------------------------------------
    def species_factor_mapping(self, parent_node) -> Dict:
        """Create a species - factor label mapping of this Experiment object.

        This function creates a dictionary of `{(species_keys, factor_keys):
        factors}` for each factor associated with this object. The order
        of examination is setup so that lower priority factors will be
        overwritten by higher priority factors.

        :param parent_node: The parent `chemmd.models.Node` object.
        :return: A dictionary mapping of species and factor keys to their
            matching factors.

        """
        # Create dictionaries to be output.
        source_mapping = {}
        sample_mapping = {}

        # Oder the samples and factors of this experiment.
        # Parental factors (those with a higher priority) are added at the
        # end so that they overwrite lower priority factors.
        samples = self.samples + self.parental_samples
        factors = self.factors + self.parental_factors

        for sample in samples:

            # Get all source objects associated with this sample.
            sources = util.get_all_elements(sample, "all_sources")

            for source in sources:

                # Create the basic source mapping, then add associated
                # metadata objects.
                source_maps = source.mapping()
                for source_map in source_maps.values():
                    source_map["factor_data"] = self.parse_factor_value(
                        source_map["factor"])
                    source_map["sample"] = sample
                    source_map["experiment"] = self
                    source_map["parent_node"] = parent_node

                # Update the output mapping dictionary, Call the
                # original dictionary first so that the new values
                # overwrite the old.
                source_mapping = {**source_maps, **source_mapping}

            # Create the basic sample mapping and update it with
            # associated metadata objects.
            sample_maps = sample.mapping(factors)
            for sample_map in sample_maps.values():
                sample_map["factor_data"] = self.parse_factor_value(
                    sample_map["factor"])
                sample_map["experiment"] = self
                sample_map["parent_node"] = parent_node

            # Update the output mapping. Call the original mapping
            # first so that new values overwrite the old values.
            sample_mapping = {**sample_maps, **sample_mapping}

        # Combine the source and sample mappings. Samples have a higher
        # priority, so they are called last so that those values
        # overwrite any matching keys in the source mapping.
        mapping = {**source_mapping, **sample_mapping}
        return mapping

    @property
    def as_markdown(self):
        text = f"### {self.assay_title}\n"
        for sample in self.samples:
            text += sample.as_markdown

        for factor in self.factors:
            text += factor.as_markdown

        for comment in self.comments:
            text += comment.as_markdown

        return text


@dataclass
class Node:
    """Model for a single Drupal content node.

    Much of this class is declarative, with the Param package doing all of the
    heavy-lifting in the background.

    """
    experiments: List
    node_information: dict = None
    factors: List[Factor] = None
    samples: List = None
    comments: List = None

    def mapping(self):
        mapping = {"node": self}
        return mapping

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
