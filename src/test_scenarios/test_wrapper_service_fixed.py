"""
Modified test script for the wrapper service with mocked MQTT broker.

This class exercises the wrapper service under varying message rates
and numbers of simultaneous sensor types.  It uses a mock MQTT client
to simulate sensor messages without an external broker.  The
collected metrics include the number of messages processed, average
translation latency and the number of translation errors.
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
        # Simulate immediate reception on IEEE 1451 topic
        if self.on_message and topic.startswith("ieee1451/"):
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

# Import the wrapper service
from wrapper_service.wrapper_service import WrapperService


class WrapperServiceTest:
    """Test harness for the wrapper service."""

    def __init__(self, output_dir: str | None = None) -> None:
        """Initialise the test environment.

        Args:
            output_dir: Directory to store results.  Defaults to a
                ``results`` subdirectory.
        """
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
        os.makedirs(self.output_dir, exist_ok=True)
        # Supported sensor types
        self.sensor_types = ["temperature", "pressure", "humidity", "flow", "level", "vibration"]
        # Results storage
        self.results: dict[str, list] = {
            "messages_processed": [],
            "average_latency": [],
            "translation_errors": [],
            "test_case": [],
            "message_rate": [],
            "test_duration": [],
        }
        logger.info("Wrapper Service Test initialized")

    def run_message_rate_test(self, rates: list[int] = [1, 5, 10], duration: int = 10) -> None:
        """Run message rate tests for the wrapper service.

        Args:
            rates: Message rates to test (msg/s).
            duration: Duration of each test in seconds.
        """
        logger.info("Starting wrapper service message rate test")
        for rate in rates:
            interval = 1.0 / rate
            logger.info(f"Testing with message rate {rate} msg/s (interval: {interval:.4f}s)")
            wrapper_service = WrapperService()
            wrapper_service.start()
            time.sleep(1)
            wrapper_service.simulate_sensor_data("temperature", (20.0, 30.0), interval=interval, duration=duration)
            # Wait for simulation to complete
            time.sleep(duration + 2)
            metrics = wrapper_service.get_metrics()
            self.results["messages_processed"].append(metrics["messages_processed"])
            self.results["average_latency"].append(metrics["average_latency"])
            self.results["translation_errors"].append(metrics["translation_errors"])
            self.results["test_case"].append(f"{rate} msg/s")
            self.results["message_rate"].append(rate)
            self.results["test_duration"].append(duration)
            logger.info(
                f"Messages: {metrics['messages_processed']}, Avg Latency: {metrics['average_latency']:.6f}s, Errors: {metrics['translation_errors']}"
            )
            wrapper_service.stop()
            time.sleep(1)
        # Save results to CSV and generate plots
        self._save_results("message_rate_test")

    def run_multi_sensor_test(self, sensor_counts: list[int] = [1, 2, 3], rate: int = 5, duration: int = 10) -> None:
        """Run multi‑sensor tests for the wrapper service.

        Args:
            sensor_counts: Numbers of sensor types to test simultaneously.
            rate: Message rate per sensor type.
            duration: Duration of each test in seconds.
        """
        logger.info("Starting wrapper service multi‑sensor test")
        for count in sensor_counts:
            logger.info(f"Testing with {count} sensor types")
            wrapper_service = WrapperService()
            wrapper_service.start()
            time.sleep(1)
            # Simulate data for each sensor type
            for i in range(count):
                sensor_type = self.sensor_types[i % len(self.sensor_types)]
                if sensor_type == "temperature":
                    value_range = (20.0, 30.0)
                elif sensor_type == "pressure":
                    value_range = (95.0, 105.0)
                elif sensor_type == "humidity":
                    value_range = (40.0, 60.0)
                elif sensor_type == "flow":
                    value_range = (10.0, 50.0)
                elif sensor_type == "level":
                    value_range = (0.5, 9.5)
                else:
                    value_range = (0.0, 100.0)
                wrapper_service.simulate_sensor_data(
                    sensor_type,
                    value_range,
                    interval=1.0 / rate,
                    duration=duration,
                )
            # Wait for simulation to complete
            time.sleep(duration + 2)
            metrics = wrapper_service.get_metrics()
            self.results["messages_processed"].append(metrics["messages_processed"])
            self.results["average_latency"].append(metrics["average_latency"])
            self.results["translation_errors"].append(metrics["translation_errors"])
            self.results["test_case"].append(f"{count} sensors")
            self.results["message_rate"].append(rate)
            self.results["test_duration"].append(duration)
            logger.info(
                f"Sensors: {count}, Messages: {metrics['messages_processed']}, "
                f"Avg Latency: {metrics['average_latency']:.6f}s, Errors: {metrics['translation_errors']}"
            )
            wrapper_service.stop()
            time.sleep(1)
        # Save results
        self._save_results("multi_sensor_test")

    def _save_results(self, test_name: str) -> None:
        """Persist results and produce simple scatter plots.

        Args:
            test_name: Name of the test scenario for filenames.
        """
        df = pd.DataFrame(self.results)
        csv_path = os.path.join(self.output_dir, f"{test_name}_results.csv")
        df.to_csv(csv_path, index=False)
        # Scatter plot of latency vs. messages processed
        plt.figure(figsize=(8, 5))
        sns.scatterplot(x="messages_processed", y="average_latency", data=df)
        plt.title("Wrapper Service: Latency vs. Messages Processed")
        plt.xlabel("Messages Processed")
        plt.ylabel("Average Latency (s)")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_scatter.png"))
        plt.close()
        # Line plot of messages processed over test cases
        plt.figure(figsize=(8, 5))
        sns.lineplot(x="test_case", y="messages_processed", data=df, marker="o")
        plt.title("Wrapper Service: Messages Processed vs. Test Case")
        plt.xlabel("Test Case")
        plt.ylabel("Messages Processed")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_messages.png"))
        plt.close()
        # Line plot of latency over test cases
        plt.figure(figsize=(8, 5))
        sns.lineplot(x="test_case", y="average_latency", data=df, marker="o")
        plt.title("Wrapper Service: Average Latency vs. Test Case")
        plt.xlabel("Test Case")
        plt.ylabel("Average Latency (s)")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, f"{test_name}_latency.png"))
        plt.close()