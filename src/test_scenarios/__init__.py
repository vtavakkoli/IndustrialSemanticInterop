"""Test scenarios package for performance evaluation.

This package provides three classes used to exercise the ontology
mapping, semantic reasoner and wrapper service components.  They are
adapted versions of the original test scripts provided with the
project and have been modified to run without external dependencies
such as an MQTT broker.  Each class defines methods for executing
specific test scenarios and saving results to disk.

The tests are intended for internal use by ``compute_metrics.py`` and
should not be executed directly by end users.
"""

# Expose renamed test scenario modules for external import.  The ``_fixed``
# suffix has been removed to reflect the stable nature of these tests.
__all__ = [
    'test_ontology_mapping',
    'test_semantic_reasoner',
    'test_wrapper_service',
]