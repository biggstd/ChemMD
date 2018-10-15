"""
Core Models
###########

**Overview**

Core models are those that make up the fundamental data / metadata
blocks which model a users data. Of these, the ``Factor`` and
``SpeciesFactor`` objects are the most important. See their use
in the nodal mapping functions.

"""

# ----------------------------------------------------------------------------
# Imports -- Standard Python modules
# ----------------------------------------------------------------------------
import re  # Regular expression functions.
from textwrap import dedent  # Prevent indents from percolating to the user.
from typing import Tuple, Union, Callable, NamedTuple  # For declaring types.
from dataclasses import dataclass

# ----------------------------------------------------------------------------
# Local package imports.
# ----------------------------------------------------------------------------
from . import util


# ----------------------------------------------------------------------------
# Elemental Class Definitions
# ----------------------------------------------------------------------------
@dataclass
class Factor:
    """The factor is the fundamental storage model for an observation.

    It is designed in such a way that it should be able to store:
        + Floats / decimals
        + strings / references
        + units
        + Factor Category
        + user data reference

    This allows the factor to model / label data contained in user uploaded
    files, as well as 'single-valued' data (eg. experimental temperature).

    """
    factor_type: str
    decimal_value: float = None
    string_value: str = None
    reference_value: str = None
    unit_reference: str = None
    csv_column_index: int = None

    @property
    def label(self) -> Tuple[str]:
        """A label property. These three parameters are the categorical units or
        ontology term of this factor.

        """
        return tuple(filter(None, [self.factor_type,
                                   self.unit_reference,
                                   self.reference_value]))

    @property
    def is_csv_index(self) -> bool:
        """A boolean property. True if this factor describes a datafile column,
        and False otherwise.

        """
        if self.csv_column_index is not None:
            return True
        return False

    @property
    def value(self) -> Union[float, str]:
        """Build the values for this factor.

        The priority of return order is:
            1. decimal_value
            2. string_value
            3. ref_value

        The first one of these that is present is returned.
        """

        for item in (self.decimal_value, self.string_value,
                     self.reference_value):
            if item is not None:
                return item

    def query(self, query_terms) -> bool:
        """Query this factors properties with a list of terms.

        :param query_terms:
        :return:

        """

        # Ensure the query is a list to avoid iterating over single strings.
        query_terms = util.ensure_list(query_terms)

        # Make an tuple to handle the properties easily.
        properties = [self.factor_type, self.reference_value,
                      self.unit_reference, self.string_value]

        if any(re.match(term, str(prop))
               for term in query_terms
               for prop in properties):
            return True

    @property
    def as_markdown(self):
        return dedent(f"""\
            **{self.label}**: {self.value}\n
        """)


@dataclass
class SpeciesFactor:
    """A species factor is a pair of values. A species and a stoichiometry
    coefficient.

    Such stoichiometry coefficients are only comparable within a single
    Sample or Source object.

    """
    species_reference: str
    stoichiometry: float = 1.0

    def query(self, query_term) -> bool:
        """A boolean search function. Returns True if the query term
        is found, and False otherwise.

        """
        if re.match(query_term, self.species_reference):
            return True

    @property
    def as_markdown(self):
        return dedent(f"""\
            **{self.species_reference}** stoichiometry: {self.stoichiometry}\n
        """)


@dataclass
class Comment:
    """A node comment model.

    Holds data for a comment and functions for viewing those comment
    values as HTML.

    """

    comment_title: str
    comment_body: str = None

    @property
    def as_markdown(self):
        return dedent(f"""\
            **{self.name}**: {self.body}\n
        """)


@dataclass
class DataFile:
    """FUTURE: This class is not used or implemented.

    In the future it will may handle data file paths / objects.

    """
    filename: str


class QueryGroup(NamedTuple):
    column_name: str
    factor_filters: Tuple[str, ...]
    species_filters: Tuple[str, ...]


class DerivedGroup(NamedTuple):
    column_name: str
    source_names: Tuple[str, ...]
    callable_: Callable
