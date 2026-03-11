"""
Lightweight Ontology Mapping Tool
================================

This module implements a simplified ontology mapping tool for
integrating IEEE 1451 sensors with IEC 61499 function blocks.  The
original implementation relied on the ``rdflib`` library and OWL
ontologies to define concept, property and instance mappings.  This
reimplementation avoids all external dependencies and instead uses
plain Python data structures to represent sensors, function blocks and
mapping metadata.  The goal is to provide enough functionality for
the accompanying unit tests without sacrificing clarity or requiring
complex RDF processing.

Key Design Decisions
--------------------

* **No RDF graph**: All sensor and function block data are stored in
  in‑memory dictionaries provided by the simplified ontology classes.
  Mapping relationships are tracked in a list of mapping entries
  rather than as triples in an RDF graph.

* **Mapping entries**: Each concept, property or instance mapping is
  recorded as a dictionary containing its type and confidence level.
  This allows the mapping tool to compute an average confidence
  score, which serves as a proxy for mapping accuracy in the tests.

* **Default mapping rules**: The tool populates a set of concept and
  property mapping entries at initialization time.  These rules are
  based on the integration guidelines described in the accompanying
  paper and are sufficient for the tests to assess mapping
  completeness.

* **Sensor to function block mapping**: When mapping a sensor to a
  function block the tool constructs a human readable name and
  determines appropriate data outputs based on the sensor's
  measurement range.  The created function block is added to the
  simplified IEC 61499 ontology.

* **Accuracy calculation**: The ``evaluate_mapping_accuracy`` method
  computes the average confidence of all concept, property and
  instance mappings that have been recorded.  If no mappings exist the
  method returns zero.

This module intentionally avoids any dependency on MQTT or other
networking libraries; those are handled in separate modules.  The
primary objective here is to provide a deterministic, side‑effect
free mapping that can be easily tested.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

from .ieee1451_ontology import IEEE1451Ontology
from .iec61499_ontology import IEC61499Ontology

# Configure a module‑level logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OntologyMappingTool:
    """A minimal ontology mapping tool for IEEE 1451 and IEC 61499.

    This class maintains references to simplified IEEE 1451 and
    IEC 61499 ontologies and a list of mapping entries.  Each mapping
    entry is a dictionary with the following keys:

    ``type``: One of ``"ConceptMapping"``, ``"PropertyMapping"`` or
        ``"InstanceMapping"``.
    ``source``: The source concept, property or instance identifier.
    ``target``: The target concept, property or instance identifier.
    ``confidence``: A floating point value between 0 and 1 representing
        the confidence in the correctness of the mapping.

    The mapping tool provides methods to add concept and property
    mappings, map sensors to function blocks and evaluate the overall
    mapping accuracy.
    """

    def __init__(self, ieee1451_ontology: Optional[IEEE1451Ontology] = None, iec61499_ontology: Optional[IEC61499Ontology] = None) -> None:
        # Use provided ontologies or create new ones
        self.ieee1451_ontology = ieee1451_ontology or IEEE1451Ontology()
        self.iec61499_ontology = iec61499_ontology or IEC61499Ontology()

        # Internal list of mapping entries (concept, property and instance)
        self._mappings: List[Dict[str, object]] = []

        # Populate default mapping rules
        self._load_default_mapping_rules()
        logger.info("Ontology Mapping Tool initialised with default mapping rules")

    # ------------------------------------------------------------------
    # Mapping rule definitions
    # ------------------------------------------------------------------
    def _add_concept_mapping(self, source_concept: str, target_concept: str, description: str, confidence: float) -> None:
        """Record a concept mapping entry.

        Args:
            source_concept: Identifier for the source concept.
            target_concept: Identifier for the target concept.
            description: Human readable description of the mapping (unused).
            confidence: Confidence level of the mapping (0.0–1.0).
        """
        entry = {
            "type": "ConceptMapping",
            "source": source_concept,
            "target": target_concept,
            "confidence": float(confidence),
        }
        self._mappings.append(entry)
        logger.debug(f"Added concept mapping: {entry}")

    def _add_property_mapping(self, source_property: str, target_property: str, description: str, confidence: float, transformation: Optional[str] = None) -> None:
        """Record a property mapping entry.

        Args:
            source_property: Identifier for the source property.
            target_property: Identifier for the target property.
            description: Description of the mapping (unused).
            confidence: Confidence level of the mapping.
            transformation: Optional transformation expression (unused).
        """
        entry = {
            "type": "PropertyMapping",
            "source": source_property,
            "target": target_property,
            "confidence": float(confidence),
        }
        # Transformation is not used in this simplified implementation but
        # retained for completeness
        if transformation:
            entry["transformation"] = transformation
        self._mappings.append(entry)
        logger.debug(f"Added property mapping: {entry}")

    def _add_instance_mapping(self, source_instance: str, target_instance: str, description: str, confidence: float) -> None:
        """Record an instance mapping entry.

        Args:
            source_instance: Source instance identifier.
            target_instance: Target instance identifier.
            description: Description of the mapping (unused).
            confidence: Confidence level of the mapping.
        """
        entry = {
            "type": "InstanceMapping",
            "source": source_instance,
            "target": target_instance,
            "confidence": float(confidence),
        }
        self._mappings.append(entry)
        logger.debug(f"Added instance mapping: {entry}")

    def _load_default_mapping_rules(self) -> None:
        """Populate the internal mapping list with default concept and property mappings.

        The confidence levels reflect heuristic assessments of how
        strongly concepts and properties correspond between the two
        standards.  These rules are intentionally simplified and
        directly mirror the original implementation's default rules.
        """
        # Concept mappings
        self._add_concept_mapping(
            "IEEE1451:Sensor", "IEC61499:FunctionBlock",
            "Direct mapping from IEEE 1451 Sensor to IEC 61499 Function Block",
            0.9,
        )
        self._add_concept_mapping(
            "IEEE1451:Actuator", "IEC61499:FunctionBlock",
            "Direct mapping from IEEE 1451 Actuator to IEC 61499 Function Block",
            0.9,
        )
        self._add_concept_mapping(
            "IEEE1451:TEDS", "IEC61499:DataInput",
            "Mapping from IEEE 1451 TEDS to IEC 61499 Data Input",
            0.8,
        )
        # Property mappings
        self._add_property_mapping(
            "IEEE1451:hasIdentifier", "IEC61499:hasIdentifier",
            "Direct mapping of identifiers", 1.0,
        )
        self._add_property_mapping(
            "IEEE1451:hasManufacturer", "IEC61499:hasName",
            "Map manufacturer to name with prefix", 0.7, "concat('Manufacturer:', value)",
        )
        self._add_property_mapping(
            "IEEE1451:hasMeasurementRange", "IEC61499:hasDataType",
            "Map measurement range to appropriate data type", 0.6,
            "if contains(value, 'temperature') then 'REAL' else 'STRING'",
        )
        self._add_property_mapping(
            "IEEE1451:hasSecurityLevel", "IEC61499:hasSecurityLevel",
            "Direct mapping of security levels", 1.0,
        )

    # ------------------------------------------------------------------
    # Sensor to function block mapping
    # ------------------------------------------------------------------
    def map_sensor_to_function_block(self, sensor_id: str, fb_id: Optional[str] = None, fb_type: str = "BasicFB") -> Optional[str]:
        """Create a new IEC 61499 function block corresponding to a sensor.

        This method looks up the sensor metadata from the IEEE 1451
        ontology, determines appropriate interface definitions for the
        function block and then adds it to the IEC 61499 ontology.  An
        instance mapping with a confidence of 1.0 is recorded to
        capture the relationship between the source sensor instance
        and the target function block.

        Args:
            sensor_id: Identifier of the IEEE 1451 sensor to map.
            fb_id: Optional explicit identifier for the function block.  If
                omitted a default of ``FB_<sensor_id>`` will be used.
            fb_type: Type of function block to create (default ``"BasicFB"``).

        Returns:
            The identifier of the created function block, or ``None`` if
            the sensor cannot be found.
        """
        sensor = self.ieee1451_ontology.sensors.get(sensor_id)
        if not sensor:
            logger.error(f"Sensor with ID {sensor_id} not found in IEEE1451 ontology")
            return None

        # Determine function block identifier
        if not fb_id:
            fb_id = f"FB_{sensor_id}"

        manufacturer = sensor.get("manufacturer", "")
        model = sensor.get("model_number", "")
        fb_name = f"{manufacturer} {model} Sensor".strip()

        # Define event and data interfaces
        event_inputs = ["INIT", "REQ"]
        event_outputs = ["INITO", "CNF"]
        data_inputs = [("ENABLE", "BOOL")]
        data_outputs = []

        # Determine appropriate data outputs based on measurement range
        range_str = sensor.get("measurement_range", "")
        lower_range = range_str.lower()
        if any(x in lower_range for x in ["temperature", "°c", "°f"]):
            data_outputs.append(("TEMPERATURE", "REAL"))
        elif any(x in lower_range for x in ["pressure", "kpa", "bar"]):
            data_outputs.append(("PRESSURE", "REAL"))
        elif any(x in lower_range for x in ["humidity", "%"]):
            data_outputs.append(("HUMIDITY", "REAL"))
        elif any(x in lower_range for x in ["flow", "l/min"]):
            data_outputs.append(("FLOW", "REAL"))
        elif any(x in lower_range for x in ["level", "m"]):
            data_outputs.append(("LEVEL", "REAL"))
        elif any(x in lower_range for x in ["vibration", "hz"]):
            data_outputs.append(("VIBRATION", "REAL"))
        else:
            data_outputs.append(("VALUE", "REAL"))

        # Add additional status and accuracy outputs
        data_outputs.append(("STATUS", "STRING"))
        data_outputs.append(("ACCURACY", "REAL"))

        # Security level mapping
        security_level = sensor.get("security_level", 0)

        # Create the function block
        self.iec61499_ontology.add_function_block(
            fb_id=fb_id,
            fb_type=fb_type,
            name=fb_name,
            event_inputs=event_inputs,
            event_outputs=event_outputs,
            data_inputs=data_inputs,
            data_outputs=data_outputs,
            security_level=security_level,
            supports_reconfiguration=True,
        )

        # Record the instance mapping with full confidence
        self._add_instance_mapping(sensor_id, fb_id, f"Mapping from sensor {sensor_id} to function block {fb_id}", 1.0)

        logger.debug(f"Mapped sensor {sensor_id} to function block {fb_id}")
        return fb_id

    # ------------------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------------------
    def evaluate_mapping_accuracy(self) -> float:
        """Compute the average confidence across all recorded mappings.

        The mapping accuracy is defined as the arithmetic mean of the
        confidence values for concept, property and instance mappings.
        If no mappings have been recorded the method returns 0.0.

        Returns:
            A float representing the mapping accuracy in the range
            ``[0.0, 1.0]``.
        """
        if not self._mappings:
            logger.debug("No mappings available to evaluate")
            return 0.0
        total_confidence = sum(entry.get("confidence", 0.0) for entry in self._mappings)
        accuracy = total_confidence / len(self._mappings)
        logger.info(f"Evaluated mapping accuracy: {accuracy:.4f}")
        return accuracy

    # ------------------------------------------------------------------
    # Stub methods for API compatibility
    # ------------------------------------------------------------------
    def export_mapping(self, file_path: str, format: str = "turtle") -> None:
        """Export mappings to a file (not implemented).

        This method is provided to maintain API compatibility with the
        original implementation.  In the simplified version the
        mappings are not persisted to disk.
        """
        logger.warning("export_mapping is not implemented in the simplified mapping tool")

    def import_mapping(self, file_path: str, format: str = "turtle") -> None:
        """Import mappings from a file (not implemented).

        Provided for API compatibility; does nothing in this simplified
        implementation.
        """
        logger.warning("import_mapping is not implemented in the simplified mapping tool")


__all__ = ["OntologyMappingTool"]