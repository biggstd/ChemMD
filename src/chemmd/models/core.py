"""

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

    Types:
        + Measurement
        + Reference

    """

    factor_type: str
    """The type of factor represented by this instance. This should be one of:
    Measurement, Condition"""
    decimal_value: float = None
    """The optional decimal value of this instance."""
    string_value: str = None
    """The optional string value of this instance."""
    reference_value: str = None
    """The optional reference string value of this instance."""
    unit_reference: str = None
    """The unit in which this data of this instance is described."""
    csv_column_index: int = None
    """The column index (if applicable) of this instance (if applicable)."""

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
    """The user-given string representation of this species."""
    stoichiometry: float = 1.0
    """The user-supplied stoichiometry coefficient for this species.
    This value only references stoichiometry within the same
    ``Sample`` or ``Source`` object."""

    def query(self, query_term) -> bool:
        """A boolean search function. Returns True if the query term
        is found, and False otherwise.

        Args:
            query_term (str): A single string to check against this
            object's ``species_reference``.

        Returns:
            bool: True if ``query_term`` is found, False otherwise.

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

    Holds data for a comment and functions for viewing those
    comment values as HTML.

    """

    comment_title: str
    """A user-given name or title of the comment."""
    comment_body: str = None
    """The body of the comment."""

    @property
    def as_markdown(self):
        """Formats the contents of this comment as Markdown."""
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
    """The user-given name of the column this group will create."""
    factor_filters: Tuple[str, ...]
    """The filters to be applied to ``Factor`` instances."""
    species_filters: Tuple[str, ...]
    """The filters to be applied to ``SpeciesFactor`` instances."""


class DerivedGroup(NamedTuple):
    column_name: str
    """The user-given name of the column this group will create."""
    source_names: Tuple[str, ...]
    """The existing columns that make up the values used by
    ``callable_``."""
    callable_: Callable
    """The function to be applied to those values pulled from
    ``source_names``."""
