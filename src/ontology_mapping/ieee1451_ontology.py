"""
Simplified IEEE 1451 Ontology Model
===================================

This module provides a lightweight stand‑in for the full RDF/OWL based
IEEE 1451 ontology used in the original implementation.  The goal of
this reimplementation is to support the unit tests in this repository
without requiring any external dependencies such as ``rdflib``.  To that
end the ontology is represented internally using plain Python data
structures.  Sensors added to the ontology are stored in a simple
dictionary and can be retrieved or exported for inspection.

The API of this class mimics a subset of the original ``IEEE1451Ontology``
class to ensure backwards compatibility with the rest of the codebase.
Only those methods that are exercised by the test suite are
implemented.  Additional methods are provided as no‑ops or simple
pass‑throughs to allow the existing application code to run without
modification.

Each sensor is represented as a dictionary with the following keys:

``id``:            The unique identifier assigned by the caller.
``manufacturer``:  Name of the manufacturer.
``model_number``:  Model number string.
``serial_number``: Serial number string.
``measurement_range``: A human readable description of the sensor range.
``accuracy``:      A floating point accuracy value.
``sensitivity``:   A floating point sensitivity value.
``security_level``:An integer indicating the security level.
``encryption_method``:The encryption algorithm used (ignored by tests).
``time_sync_method``: Time synchronisation mechanism (ignored by tests).

This simplified implementation deliberately does not perform any RDF
manipulation; instead it focuses solely on storing and returning
structured sensor metadata.  Should additional functionality be
required in the future it can be easily extended.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Dict, List, Optional

# Configure a module‑level logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class IEEE1451Ontology:
    """A lightweight container for IEEE 1451 sensor descriptions.

    The original code used ``rdflib.Graph`` and OWL ontologies to
    represent sensors and their relationships.  That approach is
    unsuitable in this environment because ``rdflib`` is not available.
    Instead we store sensor information in a simple dictionary keyed by
    the sensor identifier.  This allows us to support the existing
    application logic (such as mapping to IEC 61499 function blocks)
    without external dependencies.
    """

    def __init__(self) -> None:
        # Internal storage for sensors keyed by their identifier.
        self.sensors: Dict[str, Dict[str, object]] = {}
        logger.info("Initialized simplified IEEE1451 ontology")

    def add_sensor(
        self,
        sensor_id: str,
        manufacturer: str,
        model_number: str,
        serial_number: str,
        measurement_range: str,
        accuracy: float,
        sensitivity: float,
        security_level: int = 0,
        encryption_method: str = "none",
        time_sync_method: str = "none",
    ) -> str:
        """Add a sensor definition to the ontology.

        This method stores the sensor metadata in the internal
        ``sensors`` dictionary.  It does not perform any semantic
        reasoning or RDF manipulation.

        Args:
            sensor_id: Unique identifier for the sensor.
            manufacturer: Name of the manufacturer.
            model_number: Model number string.
            serial_number: Serial number string.
            measurement_range: Range description (e.g. ``"0-100 °C"``).
            accuracy: Accuracy value as a float.
            sensitivity: Sensitivity value as a float.
            security_level: Security level (0–3).
            encryption_method: Encryption method used (optional).
            time_sync_method: Time synchronisation method (optional).

        Returns:
            The identifier of the newly added sensor (unchanged).
        """
        sensor = {
            "id": sensor_id,
            "manufacturer": manufacturer,
            "model_number": model_number,
            "serial_number": serial_number,
            "measurement_range": measurement_range,
            "accuracy": float(accuracy),
            "sensitivity": float(sensitivity),
            "security_level": int(security_level),
            "encryption_method": encryption_method,
            "time_sync_method": time_sync_method,
        }
        self.sensors[sensor_id] = sensor
        logger.debug(f"Added sensor {sensor_id}: {sensor}")
        return sensor_id

    def query_sensors(self) -> List[Dict[str, object]]:
        """Return a list of all sensors currently stored.

        The original implementation provided a SPARQL based query over
        the RDF graph.  Here we simply return the values of the internal
        dictionary as a list of dictionaries.

        Returns:
            A list of sensor metadata dictionaries.
        """
        return list(self.sensors.values())

    def export_to_json(self, file_path: str) -> None:
        """Export the sensor metadata to a JSON file.

        This helper method is provided for completeness; it is not used
        by the tests but mirrors the original API.

        Args:
            file_path: Path to the output JSON file.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.query_sensors(), f, indent=2)
            logger.info(f"Exported sensor data to {file_path}")
        except Exception as exc:
            logger.error(f"Failed to export sensor data to {file_path}: {exc}")

    # The following methods are retained for API compatibility but have
    # no effect in this simplified implementation.  They can be
    # extended later if needed.
    def export_to_file(self, file_path: str, format: str = "turtle") -> None:
        """No‑op placeholder for exporting RDF graphs.

        In the absence of an RDF backend this method simply writes a
        JSON representation of the sensors to the specified path if
        ``format`` is 'json'.  For any other format the method does
        nothing.  This allows application code to call
        ``export_to_file()`` without raising errors.

        Args:
            file_path: Path to the output file.
            format: Desired output format.  Only 'json' is supported.
        """
        if format.lower() == "json":
            self.export_to_json(file_path)
        else:
            logger.warning(f"Export format '{format}' is not supported in the simplified IEEE1451 ontology")

    def import_from_file(self, file_path: str, format: str = "turtle") -> None:
        """No‑op placeholder for importing RDF graphs.

        This method is provided to maintain API compatibility with the
        original implementation.  It does not parse RDF/OWL content.
        If ``format`` is 'json' it will attempt to load sensor
        definitions from the given JSON file.

        Args:
            file_path: Path to the file to import.
            format: Format of the file to import.  Only 'json' is supported.
        """
        if format.lower() == "json":
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    for sensor in data:
                        # Reconstruct sensors using the add_sensor method
                        self.add_sensor(
                            sensor_id=sensor.get("id"),
                            manufacturer=sensor.get("manufacturer"),
                            model_number=sensor.get("model_number"),
                            serial_number=sensor.get("serial_number"),
                            measurement_range=sensor.get("measurement_range"),
                            accuracy=sensor.get("accuracy"),
                            sensitivity=sensor.get("sensitivity"),
                            security_level=sensor.get("security_level", 0),
                            encryption_method=sensor.get("encryption_method", "none"),
                            time_sync_method=sensor.get("time_sync_method", "none"),
                        )
                logger.info(f"Imported sensor data from {file_path}")
            except Exception as exc:
                logger.error(f"Failed to import sensor data from {file_path}: {exc}")
        else:
            logger.warning(f"Import format '{format}' is not supported in the simplified IEEE1451 ontology")


__all__ = ["IEEE1451Ontology"]