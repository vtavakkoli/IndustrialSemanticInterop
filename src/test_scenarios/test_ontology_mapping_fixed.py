"""
Modified test script for ontology mapping tool that handles import paths correctly.

This class provides methods to generate test sensors, execute mapping
across different sensor counts and evaluate accuracy and mapping time.
It is a lightly edited version of the original unit test provided in
the project.  Plotting and result saving have been retained but
downstream consumers (such as ``compute_metrics``) only rely on the
in‑memory results.
"""

import os
import sys
import time
import json
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the modules with correct paths
from ontology_mapping.ieee1451_ontology import IEEE1451Ontology
from ontology_mapping.iec61499_ontology import IEC61499Ontology
from ontology_mapping.ontology_mapping_tool import OntologyMappingTool


class OntologyMappingTest:
    """Class for testing the ontology mapping tool."""

    def __init__(self, output_dir: str | None = None) -> None:
        """
        Initialise the test environment.

        Args:
            output_dir: Directory to save test results.  If not provided
                results are stored in a ``results`` subdirectory relative
                to this file.
        """
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        # Define possible sensor types and manufacturers
        self.sensor_types = ["temperature", "pressure", "humidity", "flow", "level", "vibration"]
        self.manufacturers = ["Acme Sensors", "TechMeasure", "SensorTech", "DataSense", "PrecisionSensors"]
        self.model_prefixes = ["TS", "PS", "HS", "FS", "LS", "VS"]
        # Storage for results
        self.results: dict[str, list] = {
            "accuracy": [],
            "mapping_time": [],
            "sensor_count": [],
            "test_case": [],
        }
        logger.info("Ontology Mapping Test initialized")

    def generate_test_sensors(self, count: int, sensor_type: str | None = None) -> list[dict[str, str]]:
        """Generate test sensors for the IEEE 1451 ontology.

        Args:
            count: Number of sensors to generate.
            sensor_type: Optional specific sensor type to generate.

        Returns:
            A list of dictionaries containing sensor metadata.
        """
        sensors: list[dict[str, str]] = []
        for i in range(count):
            if sensor_type:
                s_type = sensor_type
                type_index = self.sensor_types.index(s_type) if s_type in self.sensor_types else 0
            else:
                type_index = i % len(self.sensor_types)
                s_type = self.sensor_types[type_index]
            manufacturer = self.manufacturers[i % len(self.manufacturers)]
            model_prefix = self.model_prefixes[type_index]
            model_number = f"{model_prefix}-{100 + i}"
            if s_type == "temperature":
                measurement_range = f"-40°C to {100 + i % 50}°C"
                unit = "°C"
            elif s_type == "pressure":
                measurement_range = f"0-{100 + i % 900} kPa"
                unit = "kPa"
            elif s_type == "humidity":
                measurement_range = "0-100%"
                unit = "%"
            elif s_type == "flow":
                measurement_range = f"0-{50 + i % 200} L/min"
                unit = "L/min"
            elif s_type == "level":
                measurement_range = f"0-{10 + i % 90} m"
                unit = "m"
            else:  # vibration
                measurement_range = f"0-{100 + i % 900} Hz"
                unit = "Hz"
            sensor = {
                "id": f"{s_type.upper()}{i:03d}",
                "type": s_type,
                "manufacturer": manufacturer,
                "model_number": model_number,
                "serial_number": f"SN{10000 + i}",
                "measurement_range": measurement_range,
                "accuracy": round(0.1 + (i % 10) / 100, 2),
                "sensitivity": round(0.01 + (i % 20) / 1000, 3),
                "security_level": i % 4,
                "unit": unit,
            }
            sensors.append(sensor)
        return sensors

    def run_accuracy_test(self, sensor_counts: list[int] = [10, 50, 100]) -> None:
        """Run mapping accuracy and timing tests for various sensor counts.

        Args:
            sensor_counts: Numbers of sensors to test with.  Default values
                are 10, 50 and 100.
        """
        logger.info("Starting ontology mapping accuracy test")
        for count in sensor_counts:
            logger.info(f"Testing with {count} sensors")
            test_sensors = self.generate_test_sensors(count)
            ieee1451_ontology = IEEE1451Ontology()
            iec61499_ontology = IEC61499Ontology()
            # Populate the IEEE 1451 ontology
            for sensor in test_sensors:
                ieee1451_ontology.add_sensor(
                    sensor_id=sensor["id"],
                    manufacturer=sensor["manufacturer"],
                    model_number=sensor["model_number"],
                    serial_number=sensor["serial_number"],
                    measurement_range=sensor["measurement_range"],
                    accuracy=sensor["accuracy"],
                    sensitivity=sensor["sensitivity"],
                    security_level=sensor["security_level"],
                )
            mapping_tool = OntologyMappingTool(ieee1451_ontology, iec61499_ontology)
            start_time = time.time()
            for sensor in test_sensors:
                mapping_tool.map_sensor_to_function_block(sensor["id"])
            mapping_time = time.time() - start_time
            accuracy = mapping_tool.evaluate_mapping_accuracy()
            # Store results
            self.results["accuracy"].append(accuracy)
            self.results["mapping_time"].append(mapping_time)
            self.results["sensor_count"].append(count)
            self.results["test_case"].append(f"{count} sensors")
            logger.info(
                f"Accuracy: {accuracy:.4f}, Mapping Time: {mapping_time:.4f}s"
            )
        # Save results to CSV for reference
        self._save_results("accuracy_test")

    def _save_results(self, test_name: str) -> None:
        """Persist results to CSV and generate plots.

        Args:
            test_name: Name of the test scenario used for filenames.
        """
        df = pd.DataFrame(self.results)
        csv_path = os.path.join(self.output_dir, f"{test_name}_results.csv")
        df.to_csv(csv_path, index=False)
        # Accuracy plot
        plt.figure(figsize=(8, 5))
        sns.lineplot(x="sensor_count", y="accuracy", data=df, marker="o")
        plt.title("Ontology Mapping Accuracy vs. Sensor Count")
        plt.xlabel("Number of Sensors")
        plt.ylabel("Mapping Accuracy")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_accuracy.png"))
        plt.close()
        # Mapping time plot
        plt.figure(figsize=(8, 5))
        sns.lineplot(x="sensor_count", y="mapping_time", data=df, marker="o")
        plt.title("Ontology Mapping Time vs. Sensor Count")
        plt.xlabel("Number of Sensors")
        plt.ylabel("Mapping Time (s)")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_time.png"))
        plt.close()