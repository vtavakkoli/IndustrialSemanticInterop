"""
Simplified IEC 61499 Ontology Model
===================================

This module provides a lightweight stand‑in for the IEC 61499
ontology used in the original implementation.  The goal of this
reimplementation is to support the test suite without requiring
external dependencies such as ``rdflib``.  The full IEC 61499
standard defines a rich set of concepts around function blocks,
events, data inputs/outputs and execution control charts.  For the
purposes of these tests we only need to model enough of that
structure to create and inspect function blocks; there is no need
for RDF graphs or formal ontologies.

Function blocks are stored internally as dictionaries containing
their identifier, type, name and interface definitions.  The
``add_function_block`` method mirrors the API of the original
``IEC61499Ontology`` class so that higher‑level code can operate
unchanged.

The simplified model uses the following keys for each function block:

``id``:               The identifier assigned to the function block.
``type``:             The type of the block (e.g. ``"BasicFB"``).
``name``:             A human readable name.
``event_inputs``:     A list of event input names.
``event_outputs``:    A list of event output names.
``data_inputs``:      A list of 2‑tuples ``(name, data_type)``.
``data_outputs``:     A list of 2‑tuples ``(name, data_type)``.
``security_level``:   Security level (integer).
``supports_reconfiguration``: Boolean flag indicating dynamic reconfiguration support.

Additional fields can be added as needed; they are not used by the
tests.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

# Configure a module‑level logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IEC61499Ontology:
    """A lightweight container for IEC 61499 function blocks.

    This simplified implementation stores function block definitions
    in an in‑memory dictionary keyed by the function block identifier.
    It intentionally omits RDF/OWL semantics and instead provides a
    minimal API surface that matches the expectations of the mapping
    tool and test suite.  Each function block can define event
    interfaces, data interfaces, security level and reconfiguration
    support.  The contents of a function block are not interpreted
    beyond being stored for inspection.
    """

    def __init__(self) -> None:
        # Internal storage for function blocks keyed by their identifier.
        self.function_blocks: Dict[str, Dict[str, object]] = {}
        logger.info("Initialized simplified IEC61499 ontology")

    def add_function_block(
        self,
        fb_id: str,
        fb_type: str = "BasicFB",
        name: Optional[str] = None,
        event_inputs: Optional[List[str]] = None,
        event_outputs: Optional[List[str]] = None,
        data_inputs: Optional[List[Tuple[str, str]]] = None,
        data_outputs: Optional[List[Tuple[str, str]]] = None,
        security_level: int = 0,
        supports_reconfiguration: bool = False,
    ) -> str:
        """Add a function block definition to the ontology.

        Args:
            fb_id: Unique identifier for the function block.
            fb_type: Type of function block (e.g. ``"BasicFB"``).
            name: Human readable name (optional).
            event_inputs: List of event input names.
            event_outputs: List of event output names.
            data_inputs: List of ``(name, data_type)`` tuples for inputs.
            data_outputs: List of ``(name, data_type)`` tuples for outputs.
            security_level: Security level (0–3).
            supports_reconfiguration: Whether the block supports dynamic
                reconfiguration.

        Returns:
            The identifier of the newly added function block.
        """
        block = {
            "id": fb_id,
            "type": fb_type,
            "name": name or fb_id,
            "event_inputs": list(event_inputs or []),
            "event_outputs": list(event_outputs or []),
            "data_inputs": list(data_inputs or []),
            "data_outputs": list(data_outputs or []),
            "security_level": int(security_level),
            "supports_reconfiguration": bool(supports_reconfiguration),
        }
        self.function_blocks[fb_id] = block
        logger.debug(f"Added function block {fb_id}: {block}")
        return fb_id

    def query_function_blocks(self) -> List[Dict[str, object]]:
        """Return a list of all function blocks currently stored."""
        return list(self.function_blocks.values())

    # These methods are no‑ops provided for API compatibility.
    def export_to_file(self, file_path: str, format: str = "turtle") -> None:
        """Export function block definitions to a file.

        Only JSON format is supported in this simplified implementation.
        Attempting to write in a different format will result in a
        warning.  The JSON export contains the list of function blocks.
        """
        if format.lower() == "json":
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(self.query_function_blocks(), f, indent=2)
                logger.info(f"Exported function block data to {file_path}")
            except Exception as exc:
                logger.error(f"Failed to export function blocks to {file_path}: {exc}")
        else:
            logger.warning(f"Export format '{format}' is not supported in the simplified IEC61499 ontology")

    def import_from_file(self, file_path: str, format: str = "turtle") -> None:
        """Import function block definitions from a file.

        Only JSON format is supported in this simplified implementation.
        If ``format`` is not 'json' a warning is logged and nothing is
        imported.
        """
        if format.lower() == "json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    blocks = json.load(f)
                if isinstance(blocks, list):
                    for block in blocks:
                        self.add_function_block(
                            fb_id=block.get("id"),
                            fb_type=block.get("type", "BasicFB"),
                            name=block.get("name"),
                            event_inputs=block.get("event_inputs", []),
                            event_outputs=block.get("event_outputs", []),
                            data_inputs=[tuple(di) for di in block.get("data_inputs", [])],
                            data_outputs=[tuple(do) for do in block.get("data_outputs", [])],
                            security_level=block.get("security_level", 0),
                            supports_reconfiguration=block.get("supports_reconfiguration", False),
                        )
                logger.info(f"Imported function block data from {file_path}")
            except Exception as exc:
                logger.error(f"Failed to import function blocks from {file_path}: {exc}")
        else:
            logger.warning(f"Import format '{format}' is not supported in the simplified IEC61499 ontology")


__all__ = ["IEC61499Ontology"]