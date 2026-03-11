"""
Modified test script for the semantic reasoner with mocked MQTT broker.

This class defines several test scenarios for the semantic reasoner
component.  It uses a mock implementation of the paho MQTT client to
avoid the need for a running broker.  Data rate tests send sensor
messages at different rates and measure the processing performance of
the reasoner.
"""

import os
import sys
import time
import logging
from unittest.mock import MagicMock

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Create a mock for paho.mqtt.client
class MockMQTTClient:
    def __init__(self) -> None:
        self.on_connect = None
        self.on_message = None
        self.connected = False
        self.messages: list[tuple[str, str]] = []
    def connect(self, broker: str, port: int) -> int:
        self.connected = True
        if self.on_connect:
            self.on_connect(self, None, None, 0)
        return 0
    def disconnect(self) -> int:
        self.connected = False
        return 0
    def loop_start(self) -> int:
        return 0
    def loop_stop(self) -> int:
        return 0
    def publish(self, topic: str, payload: str) -> int:
        self.messages.append((topic, payload))
        # Simulate immediate message reception
        if self.on_message and topic.startswith("data/"):
            msg = MagicMock()
            msg.topic = topic
            msg.payload = payload
            self.on_message(self, None, msg)
        return 0
    def subscribe(self, topic: str) -> int:
        return 0

# Mock the mqtt.Client
sys.modules['paho.mqtt.client'] = MagicMock()
sys.modules['paho.mqtt.client'].Client = MockMQTTClient

# Now import the semantic reasoner
from semantic_reasoner.semantic_reasoner import SemanticReasoner


class SemanticReasonerTest:
    """Test harness for the semantic reasoner."""

    def __init__(self, output_dir: str | None = None) -> None:
        """Initialise the test environment.

        Args:
            output_dir: Directory to save test results.  If omitted,
                results are stored in a ``results`` subdirectory.
        """
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        # Data patterns for pattern test (not used by compute_metrics)
        self.data_patterns = ["random", "sine", "step", "spike"]
        # Results storage
        self.results: dict[str, list] = {
            "messages_processed": [],
            "rules_triggered": [],
            "alerts_generated": [],
            "average_processing_time": [],
            "test_case": [],
            "data_rate": [],
            "test_duration": [],
        }
        logger.info("Semantic Reasoner Test initialized")

    def run_data_rate_test(self, rates: list[int] = [1, 5, 10], duration: int = 5) -> None:
        """Run a data rate test for the semantic reasoner.

        Args:
            rates: List of message rates to test (messages per second).
            duration: Duration of each test in seconds.
        """
        logger.info("Starting semantic reasoner data rate test")
        for rate in rates:
            interval = 1.0 / rate
            logger.info(f"Testing with data rate {rate} msg/s (interval: {interval:.4f}s)")
            reasoner = SemanticReasoner()
            reasoner.start()
            time.sleep(1)  # allow initialisation
            # Simulate sensor data at the specified rate
            reasoner.simulate_sensor_data("temperature", pattern="spike", interval=interval, duration=duration)
            # Wait for simulation to finish
            time.sleep(duration + 2)
            metrics = reasoner.get_metrics()
            # Collect results
            self.results["messages_processed"].append(metrics["messages_processed"])
            self.results["rules_triggered"].append(metrics["rules_triggered"])
            self.results["alerts_generated"].append(metrics["alerts_generated"])
            self.results["average_processing_time"].append(metrics["average_processing_time"])
            self.results["test_case"].append(f"{rate} msg/s")
            self.results["data_rate"].append(rate)
            self.results["test_duration"].append(duration)
            logger.info(
                f"Messages: {metrics['messages_processed']}, Rules: {metrics['rules_triggered']}, "
                f"Alerts: {metrics['alerts_generated']}, Avg Time: {metrics['average_processing_time']:.6f}s"
            )
            reasoner.stop()
            time.sleep(1)
        # Save results to CSV for reference
        self._save_results("data_rate_test")

    def _save_results(self, test_name: str) -> None:
        """Persist collected results and produce simple plots.

        Args:
            test_name: Test scenario name used for filenames.
        """
        df = pd.DataFrame(self.results)
        csv_path = os.path.join(self.output_dir, f"{test_name}_results.csv")
        df.to_csv(csv_path, index=False)
        # Plot messages processed
        plt.figure(figsize=(8, 5))
        sns.lineplot(x="data_rate", y="messages_processed", data=df, marker="o")
        plt.title("Semantic Reasoner: Messages Processed vs. Data Rate")
        plt.xlabel("Data Rate (msg/s)")
        plt.ylabel("Messages Processed")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_messages.png"))
        plt.close()
        # Plot processing time
        plt.figure(figsize=(8, 5))
        sns.lineplot(x="data_rate", y="average_processing_time", data=df, marker="o")
        plt.title("Semantic Reasoner: Avg Processing Time vs. Data Rate")
        plt.xlabel("Data Rate (msg/s)")
        plt.ylabel("Average Processing Time (s)")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_processing_time.png"))
        plt.close()