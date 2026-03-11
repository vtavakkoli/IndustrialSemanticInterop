"""
Wrapper Service for IEEE 1451 and IEC 61499 Integration

This module implements a wrapper service for real-time data translation between
IEEE 1451 and IEC 61499 standards. It acts as a middleware layer that facilitates
seamless data exchange between smart transducers and distributed control systems.

Based on the latest IEEE 1451.0-2024 and IEC 61499 standard specifications.
"""

import os
import json
import time
import logging
import threading
import queue
"""Handle optional import of the MQTT client.

The wrapper service relies on the paho.mqtt.client library to
communicate with an MQTT broker.  In environments where this
dependency is not available (e.g. during unit testing), we fall back
to a dummy client that implements the minimal interface used by the
service.  The fixed test scripts monkey‑patch
``paho.mqtt.client.Client`` with a mock implementation before
importing this module, so this fallback will only be activated when
no such module exists.
"""
try:
    import paho.mqtt.client as mqtt  # type: ignore
except Exception:
    import types
    class _DummyMQTTClient:
        """A minimal stand‑in for the paho.mqtt.client.Client class."""
        def __init__(self):
            self.on_connect = None
            self.on_message = None
        def connect(self, broker: str, port: int):
            if callable(self.on_connect):
                try:
                    self.on_connect(self, None, None, 0)
                except Exception:
                    pass
            return 0
        def disconnect(self):
            return 0
        def loop_start(self):
            return 0
        def loop_stop(self):
            return 0
        def publish(self, topic: str, payload: str):
            if callable(self.on_message):
                msg = types.SimpleNamespace(topic=topic, payload=payload.encode() if isinstance(payload, str) else payload)
                try:
                    self.on_message(self, None, msg)
                except Exception:
                    pass
            return 0
        def subscribe(self, topic: str):
            return 0
    mqtt = types.SimpleNamespace(Client=_DummyMQTTClient)
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WrapperService:
    """
    Class implementing the wrapper service for IEEE 1451 and IEC 61499 integration.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize the wrapper service.
        
        Args:
            config_file (str): Path to configuration file
        """
        # Default configuration
        self.config = {
            "mqtt_broker": "localhost",
            "mqtt_port": 1883,
            "ieee1451_topic_prefix": "ieee1451/",
            "iec61499_topic_prefix": "iec61499/",
            "translation_rules_file": None,
            "buffer_size": 100,
            "processing_interval": 0.1,  # seconds
            "security_enabled": True,
            "encryption_method": "AES-128",
            "log_level": "INFO"
        }
        
        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            self._load_config(config_file)
        
        # Set log level
        logging.getLogger().setLevel(getattr(logging, self.config["log_level"]))
        
        # Initialize data buffers
        self.ieee1451_buffer = queue.Queue(maxsize=self.config["buffer_size"])
        self.iec61499_buffer = queue.Queue(maxsize=self.config["buffer_size"])
        
        # Load translation rules
        # Initialise the translation rules dictionary.  The typing here is purely descriptive:
        # maps direction ("ieee1451_to_iec61499" or "iec61499_to_ieee1451") → sensor/control type → rule.
        self.translation_rules: dict[str, dict[str, dict[str, object]]] = {}
        # Load translation rules from file if provided.  If the file is missing or fails to
        # parse, fall back to default rules defined in `_set_default_translation_rules`.
        if self.config["translation_rules_file"] and os.path.exists(self.config["translation_rules_file"]):
            self._load_translation_rules(self.config["translation_rules_file"])
        else:
            self._set_default_translation_rules()
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        
        # Initialize processing threads
        self.running = False
        self.ieee1451_to_iec61499_thread = None
        self.iec61499_to_ieee1451_thread = None
        
        # Performance metrics
        self.metrics = {
            "messages_processed": 0,
            "translation_errors": 0,
            "average_latency": 0,
            "total_latency": 0,
            "start_time": None
        }
        
        logger.info("Wrapper Service initialized")
    
    def _load_config(self, config_file):
        """
        Load configuration from a JSON file.
        
        Args:
            config_file (str): Path to configuration file
        """
        try:
            with open(config_file, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            logger.info(f"Loaded configuration from {config_file}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
    
    def _load_translation_rules(self, rules_file):
        """
        Load translation rules from a JSON file.
        
        Args:
            rules_file (str): Path to translation rules file
        """
        try:
            with open(rules_file, 'r') as f:
                self.translation_rules = json.load(f)
            logger.info(f"Loaded translation rules from {rules_file}")
        except Exception as e:
            logger.error(f"Error loading translation rules: {e}")
            self._set_default_translation_rules()
    
    def _set_default_translation_rules(self):
        """Set default translation rules."""
        """Populate a sensible baseline set of translation rules.

        The service is designed to handle a variety of sensor types originating from IEEE
        1451 topics.  For commonly used sensors such as temperature, pressure and humidity
        we explicitly define translation rules to map them onto their IEC 61499 counterparts.
        To support additional sensor types (e.g. flow, level, vibration) used in the test
        scenarios and potential future extensions, we generate a generic rule that maps
        the sensor directly to the equivalent IEC 61499 topic.  These rules simply pass
        through the sensor value and include relevant metadata (timestamp, unit, accuracy)
        where present.

        For messages coming from IEC 61499 topics intended to influence IEEE 1451
        transducers (e.g. setpoints or control commands), we provide default mappings as
        well.  Additional control message types can be added in a custom translation
        rules file if needed.
        """
        # Base mappings for well‑known sensor types
        ieee_to_iec: dict[str, dict[str, object]] = {
            "temperature": {
                "target_topic": "iec61499/temperature",
                "transformation": "value",
                "metadata": ["timestamp", "unit", "accuracy"]
            },
            "pressure": {
                "target_topic": "iec61499/pressure",
                "transformation": "value",
                "metadata": ["timestamp", "unit", "accuracy"]
            },
            "humidity": {
                "target_topic": "iec61499/humidity",
                "transformation": "value",
                "metadata": ["timestamp", "unit", "accuracy"]
            }
        }
        # Additional generic sensor types used in testing
        generic_sensors = ["flow", "level", "vibration"]
        for sensor in generic_sensors:
            ieee_to_iec.setdefault(sensor, {
                "target_topic": f"iec61499/{sensor}",
                "transformation": "value",
                "metadata": ["timestamp", "unit", "accuracy"]
            })

        # Base mappings for control directions
        iec_to_ieee: dict[str, dict[str, object]] = {
            "setpoint": {
                "target_topic": "ieee1451/setpoint",
                "transformation": "value",
                "metadata": ["timestamp", "unit"]
            },
            "control": {
                "target_topic": "ieee1451/control",
                "transformation": "value",
                "metadata": ["timestamp", "command"]
            }
        }

        self.translation_rules = {
            "ieee1451_to_iec61499": ieee_to_iec,
            "iec61499_to_ieee1451": iec_to_ieee
        }
        logger.info("Set default translation rules")
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client connects to the MQTT broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            flags: Connection flags
            rc: Connection result code
        """
        if rc == 0:
            logger.info("Connected to MQTT broker")
            
            # Subscribe to IEEE 1451 topics
            client.subscribe(f"{self.config['ieee1451_topic_prefix']}+")
            
            # Subscribe to IEC 61499 topics
            client.subscribe(f"{self.config['iec61499_topic_prefix']}+")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback for when a message is received from the MQTT broker.
        
        Args:
            client: MQTT client instance
            userdata: User data
            msg: Received message
        """
        try:
            # Attempt to decode JSON payload.  If decoding fails we log and drop the message.
            try:
                decoded = json.loads(msg.payload.decode())
            except Exception:
                logger.error("Failed to decode JSON payload on topic %s", msg.topic)
                return

            # Ignore messages that have already been translated.  We mark translated messages
            # with a `_translation` key in their payload to prevent them from being
            # reprocessed.  Without this guard, translated messages would bounce between
            # IEEE 1451 and IEC 61499 processors indefinitely, causing a feedback loop and
            # artificially inflating metrics.
            if isinstance(decoded, dict) and decoded.get("_translation") is not None:
                logger.debug("Dropping translated message on topic %s", msg.topic)
                return

            # Construct message object with arrival timestamp for latency calculation
            message = {
                "topic": msg.topic,
                "payload": decoded,
                "received_time": time.time()
            }
            
            # Route message to appropriate buffer
            if msg.topic.startswith(self.config["ieee1451_topic_prefix"]):
                if not self.ieee1451_buffer.full():
                    self.ieee1451_buffer.put(message)
                else:
                    logger.warning("IEEE 1451 buffer full, dropping message")
            
            elif msg.topic.startswith(self.config["iec61499_topic_prefix"]):
                if not self.iec61499_buffer.full():
                    self.iec61499_buffer.put(message)
                else:
                    logger.warning("IEC 61499 buffer full, dropping message")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _ieee1451_to_iec61499_processor(self):
        """Process messages from IEEE 1451 to IEC 61499."""
        logger.info("Started IEEE 1451 to IEC 61499 processor thread")
        
        while self.running:
            try:
                if not self.ieee1451_buffer.empty():
                    message = self.ieee1451_buffer.get()
                    
                    # Extract sensor type from topic
                    topic_parts = message["topic"].split('/')
                    if len(topic_parts) < 2:
                        logger.warning(f"Invalid topic format: {message['topic']}")
                        continue
                    
                    sensor_type = topic_parts[-1]
                    
                    # Check if we have translation rules for this sensor type
                    if sensor_type in self.translation_rules["ieee1451_to_iec61499"]:
                        rule = self.translation_rules["ieee1451_to_iec61499"][sensor_type]
                        
                        # Apply transformation
                        transformed_payload = self._transform_payload(
                            message["payload"], 
                            rule["transformation"],
                            rule["metadata"]
                        )
                        
                        # Add translation metadata
                        transformed_payload["_translation"] = {
                            "source": message["topic"],
                            "timestamp": time.time()
                        }
                        
                        # Publish to IEC 61499 topic
                        self.mqtt_client.publish(
                            rule["target_topic"],
                            json.dumps(transformed_payload)
                        )
                        
                        # Update metrics
                        latency = time.time() - message["received_time"]
                        self.metrics["messages_processed"] += 1
                        self.metrics["total_latency"] += latency
                        self.metrics["average_latency"] = self.metrics["total_latency"] / self.metrics["messages_processed"]
                        
                        logger.debug(f"Translated IEEE 1451 message: {sensor_type}, latency: {latency:.3f}s")
                    else:
                        logger.warning(f"No translation rule for sensor type: {sensor_type}")
                
                # Sleep to avoid high CPU usage
                time.sleep(self.config["processing_interval"])
                
            except Exception as e:
                logger.error(f"Error in IEEE 1451 to IEC 61499 processor: {e}")
                self.metrics["translation_errors"] += 1
    
    def _iec61499_to_ieee1451_processor(self):
        """Process messages from IEC 61499 to IEEE 1451."""
        logger.info("Started IEC 61499 to IEEE 1451 processor thread")
        
        while self.running:
            try:
                if not self.iec61499_buffer.empty():
                    message = self.iec61499_buffer.get()
                    
                    # Extract control type from topic
                    topic_parts = message["topic"].split('/')
                    if len(topic_parts) < 2:
                        logger.warning(f"Invalid topic format: {message['topic']}")
                        continue
                    
                    control_type = topic_parts[-1]
                    
                    # Check if we have translation rules for this control type
                    if control_type in self.translation_rules["iec61499_to_ieee1451"]:
                        rule = self.translation_rules["iec61499_to_ieee1451"][control_type]
                        
                        # Apply transformation
                        transformed_payload = self._transform_payload(
                            message["payload"], 
                            rule["transformation"],
                            rule["metadata"]
                        )
                        
                        # Add translation metadata
                        transformed_payload["_translation"] = {
                            "source": message["topic"],
                            "timestamp": time.time()
                        }
                        
                        # Publish to IEEE 1451 topic
                        self.mqtt_client.publish(
                            rule["target_topic"],
                            json.dumps(transformed_payload)
                        )
                        
                        # Update metrics
                        latency = time.time() - message["received_time"]
                        self.metrics["messages_processed"] += 1
                        self.metrics["total_latency"] += latency
                        self.metrics["average_latency"] = self.metrics["total_latency"] / self.metrics["messages_processed"]
                        
                        logger.debug(f"Translated IEC 61499 message: {control_type}, latency: {latency:.3f}s")
                    else:
                        logger.warning(f"No translation rule for control type: {control_type}")
                
                # Sleep to avoid high CPU usage
                time.sleep(self.config["processing_interval"])
                
            except Exception as e:
                logger.error(f"Error in IEC 61499 to IEEE 1451 processor: {e}")
                self.metrics["translation_errors"] += 1
    
    def _transform_payload(self, payload, transformation, metadata_fields):
        """
        Transform payload according to the specified transformation rule.
        
        Args:
            payload (dict): Original payload
            transformation (str): Transformation rule
            metadata_fields (list): Metadata fields to include
            
        Returns:
            dict: Transformed payload
        """
        result = {}
        
        # Apply transformation
        if transformation == "value" and "value" in payload:
            result["value"] = payload["value"]
        elif transformation == "scale" and "value" in payload:
            result["value"] = payload["value"] * 2  # Example scaling
        elif transformation == "convert_c_to_f" and "value" in payload:
            result["value"] = (payload["value"] * 9/5) + 32
        elif transformation == "convert_f_to_c" and "value" in payload:
            result["value"] = (payload["value"] - 32) * 5/9
        else:
            # Default: copy the value as is
            if "value" in payload:
                result["value"] = payload["value"]
        
        # Include specified metadata
        for field in metadata_fields:
            if field in payload:
                result[field] = payload[field]
        
        # Always include timestamp if not already present
        if "timestamp" not in result:
            result["timestamp"] = datetime.now().isoformat()
        
        return result
    
    def start(self):
        """Start the wrapper service."""
        if self.running:
            logger.warning("Wrapper Service is already running")
            return
        
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(self.config["mqtt_broker"], self.config["mqtt_port"])
            self.mqtt_client.loop_start()
            
            # Start processing threads
            self.running = True
            self.metrics["start_time"] = time.time()
            
            self.ieee1451_to_iec61499_thread = threading.Thread(
                target=self._ieee1451_to_iec61499_processor
            )
            self.ieee1451_to_iec61499_thread.daemon = True
            self.ieee1451_to_iec61499_thread.start()
            
            self.iec61499_to_ieee1451_thread = threading.Thread(
                target=self._iec61499_to_ieee1451_processor
            )
            self.iec61499_to_ieee1451_thread.daemon = True
            self.iec61499_to_ieee1451_thread.start()
            
            logger.info("Wrapper Service started")
            
        except Exception as e:
            logger.error(f"Error starting Wrapper Service: {e}")
            self.stop()
    
    def stop(self):
        """Stop the wrapper service."""
        if not self.running:
            logger.warning("Wrapper Service is not running")
            return
        
        try:
            # Stop processing threads
            self.running = False
            
            if self.ieee1451_to_iec61499_thread:
                self.ieee1451_to_iec61499_thread.join(timeout=2.0)
            
            if self.iec61499_to_ieee1451_thread:
                self.iec61499_to_ieee1451_thread.join(timeout=2.0)
            
            # Disconnect MQTT client
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            
            logger.info("Wrapper Service stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Wrapper Service: {e}")
    
    def get_metrics(self):
        """
        Get performance metrics.
        
        Returns:
            dict: Performance metrics
        """
        # Calculate uptime
        if self.metrics["start_time"]:
            uptime = time.time() - self.metrics["start_time"]
            self.metrics["uptime"] = uptime
        
        return self.metrics
    
    def simulate_sensor_data(self, sensor_type, value_range, interval=1.0, duration=60):
        """
        Simulate sensor data for testing.
        
        Args:
            sensor_type (str): Type of sensor (temperature, pressure, etc.)
            value_range (tuple): Range of values (min, max)
            interval (float): Interval between messages in seconds
            duration (int): Duration of simulation in seconds
        """
        if not self.running:
            logger.warning("Wrapper Service is not running")
            return
        
        def _sensor_simulator():
            start_time = time.time()
            count = 0
            
            while self.running and (time.time() - start_time) < duration:
                # Generate random value within range
                value = np.random.uniform(value_range[0], value_range[1])
                
                # Create payload
                payload = {
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "unit": "C" if sensor_type == "temperature" else 
                           "kPa" if sensor_type == "pressure" else 
                           "%" if sensor_type == "humidity" else 
                           "unit",
                    "accuracy": 0.1,
                    "sensor_id": f"{sensor_type}_sim_{count}"
                }
                
                # Publish to IEEE 1451 topic
                topic = f"{self.config['ieee1451_topic_prefix']}{sensor_type}"
                self.mqtt_client.publish(topic, json.dumps(payload))
                
                logger.debug(f"Published simulated {sensor_type} data: {value}")
                
                count += 1
                time.sleep(interval)
            
            logger.info(f"Sensor simulation completed: {count} messages published")
        
        simulator_thread = threading.Thread(target=_sensor_simulator)
        simulator_thread.daemon = True
        simulator_thread.start()
        
        logger.info(f"Started sensor simulation for {sensor_type}")

# Example usage
if __name__ == "__main__":
    # Create wrapper service
    wrapper_service = WrapperService()
    
    # Start the service
    wrapper_service.start()
    
    try:
        # Simulate temperature sensor data
        wrapper_service.simulate_sensor_data("temperature", (20.0, 30.0), interval=0.5, duration=30)
        
        # Simulate pressure sensor data
        wrapper_service.simulate_sensor_data("pressure", (95.0, 105.0), interval=0.7, duration=30)
        
        # Run for a while
        time.sleep(35)
        
        # Get and print metrics
        metrics = wrapper_service.get_metrics()
        print(f"Performance Metrics:")
        print(f"  Messages Processed: {metrics['messages_processed']}")
        print(f"  Translation Errors: {metrics['translation_errors']}")
        print(f"  Average Latency: {metrics['average_latency']:.3f} seconds")
        print(f"  Uptime: {metrics.get('uptime', 0):.1f} seconds")
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    finally:
        # Stop the service
        wrapper_service.stop()
