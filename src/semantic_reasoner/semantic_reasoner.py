"""
Lightweight Semantic Reasoner for IEEE 1451 and IEC 61499 Integration

This module implements a lightweight semantic reasoner for real-time processing
of data at the fog computing layer. It enhances decision-making capabilities by
applying semantic reasoning to data exchanged between IEEE 1451 sensors and
IEC 61499 function blocks.

Based on the latest IEEE 1451.0-2024 and IEC 61499 standard specifications.
"""

import os
import json
import time
import logging
import threading
import queue
"""Handle optional import of the MQTT client.

The semantic reasoner relies on the paho.mqtt.client library to
communicate with an MQTT broker.  In environments where this
dependency is not available (e.g. during unit testing), we fall back
to a dummy client that implements the minimal interface used by the
reasoner.  The fixed test scripts monkey‑patch
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
            # Callbacks to be assigned by the caller
            self.on_connect = None
            self.on_message = None
        def connect(self, broker: str, port: int):
            # Immediately invoke on_connect callback with rc=0
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
            # Immediately invoke on_message callback if subscribed topic matches
            if callable(self.on_message):
                # Create a simple object with topic and payload attributes
                msg = types.SimpleNamespace(topic=topic, payload=payload.encode() if isinstance(payload, str) else payload)
                try:
                    self.on_message(self, None, msg)
                except Exception:
                    pass
            return 0
        def subscribe(self, topic: str):
            return 0
    # Expose a namespace with a Client attribute
    mqtt = types.SimpleNamespace(Client=_DummyMQTTClient)
import numpy as np
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SemanticReasoner:
    """
    Class implementing a lightweight semantic reasoner for IEEE 1451 and IEC 61499 integration.
    """
    
    def __init__(self, config_file=None):
        """
        Initialize the semantic reasoner.
        
        Args:
            config_file (str): Path to configuration file
        """
        # Default configuration
        self.config = {
            "mqtt_broker": "localhost",
            "mqtt_port": 1883,
            "input_topic_prefix": "data/",
            "output_topic_prefix": "reasoning/",
            "rules_file": None,
            "buffer_size": 1000,
            "processing_interval": 0.05,  # seconds
            "window_size": 10,  # number of data points for temporal reasoning
            "log_level": "INFO"
        }
        
        # Load configuration from file if provided
        if config_file and os.path.exists(config_file):
            self._load_config(config_file)
        
        # Set log level
        logging.getLogger().setLevel(getattr(logging, self.config["log_level"]))
        
        # Initialize data buffer
        self.data_buffer = queue.Queue(maxsize=self.config["buffer_size"])
        
        # Initialize data store for temporal reasoning
        self.data_store = defaultdict(lambda: {
            "values": [],
            "timestamps": [],
            "last_update": None
        })
        
        # Load reasoning rules
        self.rules = []
        if self.config["rules_file"] and os.path.exists(self.config["rules_file"]):
            self._load_rules(self.config["rules_file"])
        else:
            self._set_default_rules()
        
        # Initialize MQTT client
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message
        
        # Initialize processing thread
        self.running = False
        self.processing_thread = None
        
        # Performance metrics
        self.metrics = {
            "messages_processed": 0,
            "rules_triggered": 0,
            "alerts_generated": 0,
            "average_processing_time": 0,
            "total_processing_time": 0,
            "start_time": None
        }
        
        logger.info("Semantic Reasoner initialized")
    
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
    
    def _load_rules(self, rules_file):
        """
        Load reasoning rules from a JSON file.
        
        Args:
            rules_file (str): Path to rules file
        """
        try:
            with open(rules_file, 'r') as f:
                self.rules = json.load(f)
            logger.info(f"Loaded {len(self.rules)} rules from {rules_file}")
        except Exception as e:
            logger.error(f"Error loading rules: {e}")
            self._set_default_rules()
    
    def _set_default_rules(self):
        """Set default reasoning rules."""
        self.rules = [
            {
                "id": "high_temperature_alert",
                "description": "Alert when temperature exceeds threshold",
                "conditions": [
                    {"type": "value", "sensor": "temperature", "operator": ">", "threshold": 30.0}
                ],
                "actions": [
                    {"type": "alert", "level": "warning", "message": "High temperature detected"}
                ]
            },
            {
                "id": "rapid_temperature_rise",
                "description": "Alert when temperature rises rapidly",
                "conditions": [
                    {"type": "rate_of_change", "sensor": "temperature", "operator": ">", "threshold": 2.0, "time_window": 5}
                ],
                "actions": [
                    {"type": "alert", "level": "warning", "message": "Rapid temperature rise detected"}
                ]
            },
            {
                "id": "pressure_anomaly",
                "description": "Alert when pressure deviates significantly from moving average",
                "conditions": [
                    {"type": "deviation", "sensor": "pressure", "operator": ">", "threshold": 5.0, "window_size": 10}
                ],
                "actions": [
                    {"type": "alert", "level": "warning", "message": "Pressure anomaly detected"}
                ]
            },
            {
                "id": "temperature_pressure_correlation",
                "description": "Alert when temperature and pressure show abnormal correlation",
                "conditions": [
                    {"type": "correlation", "sensors": ["temperature", "pressure"], "operator": "<", "threshold": 0.5, "window_size": 10}
                ],
                "actions": [
                    {"type": "alert", "level": "warning", "message": "Abnormal temperature-pressure correlation detected"}
                ]
            },
            {
                "id": "system_status",
                "description": "Publish system status based on sensor values",
                "conditions": [
                    {"type": "always"}
                ],
                "actions": [
                    {"type": "status", "message": "System operating normally"}
                ]
            }
        ]
        logger.info(f"Set {len(self.rules)} default rules")
    
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
            
            # Subscribe to input topics
            client.subscribe(f"{self.config['input_topic_prefix']}+")
            logger.info(f"Subscribed to {self.config['input_topic_prefix']}+")
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
            # Add timestamp for processing time calculation
            message = {
                "topic": msg.topic,
                "payload": json.loads(msg.payload.decode()),
                "received_time": time.time()
            }
            
            # Extract sensor type from topic
            topic_parts = msg.topic.split('/')
            if len(topic_parts) >= 2:
                message["sensor_type"] = topic_parts[-1]
            
            # Add to buffer
            if not self.data_buffer.full():
                self.data_buffer.put(message)
            else:
                logger.warning("Data buffer full, dropping message")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
    
    def _data_processor(self):
        """Process data and apply reasoning rules."""
        logger.info("Started data processing thread")
        
        while self.running:
            try:
                if not self.data_buffer.empty():
                    message = self.data_buffer.get()
                    processing_start = time.time()
                    
                    # Update data store
                    if "sensor_type" in message and "payload" in message and "value" in message["payload"]:
                        sensor_type = message["sensor_type"]
                        value = message["payload"]["value"]
                        timestamp = message["payload"].get("timestamp", datetime.now().isoformat())
                        
                        # Add to data store
                        self._update_data_store(sensor_type, value, timestamp)
                    
                    # Apply reasoning rules
                    self._apply_rules(message)
                    
                    # Update metrics
                    processing_time = time.time() - processing_start
                    self.metrics["messages_processed"] += 1
                    self.metrics["total_processing_time"] += processing_time
                    self.metrics["average_processing_time"] = (
                        self.metrics["total_processing_time"] / self.metrics["messages_processed"]
                    )
                
                # Sleep to avoid high CPU usage
                time.sleep(self.config["processing_interval"])
                
            except Exception as e:
                logger.error(f"Error in data processor: {e}")
    
    def _update_data_store(self, sensor_type, value, timestamp):
        """
        Update the data store with new sensor data.
        
        Args:
            sensor_type (str): Type of sensor
            value (float): Sensor value
            timestamp (str): Timestamp of the reading
        """
        # Convert timestamp to float for calculations
        if isinstance(timestamp, str):
            try:
                dt = datetime.fromisoformat(timestamp)
                timestamp_float = dt.timestamp()
            except ValueError:
                timestamp_float = time.time()
        else:
            timestamp_float = time.time()
        
        # Add to data store
        self.data_store[sensor_type]["values"].append(float(value))
        self.data_store[sensor_type]["timestamps"].append(timestamp_float)
        self.data_store[sensor_type]["last_update"] = time.time()
        
        # Limit the size of stored data
        window_size = self.config["window_size"]
        if len(self.data_store[sensor_type]["values"]) > window_size:
            self.data_store[sensor_type]["values"] = self.data_store[sensor_type]["values"][-window_size:]
            self.data_store[sensor_type]["timestamps"] = self.data_store[sensor_type]["timestamps"][-window_size:]
    
    def _apply_rules(self, message):
        """
        Apply reasoning rules to the message.
        
        Args:
            message (dict): Message to process
        """
        for rule in self.rules:
            if self._evaluate_conditions(rule["conditions"], message):
                self._execute_actions(rule["actions"], message, rule["id"])
                self.metrics["rules_triggered"] += 1
    
    def _evaluate_conditions(self, conditions, message):
        """
        Evaluate rule conditions.
        
        Args:
            conditions (list): List of conditions to evaluate
            message (dict): Message to evaluate against
            
        Returns:
            bool: True if all conditions are met, False otherwise
        """
        if not conditions:
            return False
        
        for condition in conditions:
            condition_type = condition.get("type")
            
            # Always true condition
            if condition_type == "always":
                continue
            
            # Value threshold condition
            elif condition_type == "value":
                sensor = condition.get("sensor")
                operator = condition.get("operator")
                threshold = condition.get("threshold")
                
                # Check if this message is for the specified sensor
                if ("sensor_type" in message and message["sensor_type"] == sensor and 
                    "payload" in message and "value" in message["payload"]):
                    
                    value = float(message["payload"]["value"])
                    
                    if not self._compare_values(value, operator, threshold):
                        return False
                else:
                    # If this message is not for the specified sensor, check the data store
                    if sensor in self.data_store and self.data_store[sensor]["values"]:
                        value = self.data_store[sensor]["values"][-1]
                        
                        if not self._compare_values(value, operator, threshold):
                            return False
                    else:
                        # Can't evaluate this condition
                        return False
            
            # Rate of change condition
            elif condition_type == "rate_of_change":
                sensor = condition.get("sensor")
                operator = condition.get("operator")
                threshold = condition.get("threshold")
                time_window = condition.get("time_window", 5)
                
                if sensor in self.data_store:
                    values = self.data_store[sensor]["values"]
                    timestamps = self.data_store[sensor]["timestamps"]
                    
                    if len(values) >= 2:
                        # Calculate rate of change
                        recent_values = values[-time_window:] if len(values) >= time_window else values
                        recent_timestamps = timestamps[-time_window:] if len(timestamps) >= time_window else timestamps
                        
                        if len(recent_values) >= 2:
                            value_change = recent_values[-1] - recent_values[0]
                            time_change = recent_timestamps[-1] - recent_timestamps[0]
                            
                            if time_change > 0:
                                rate = value_change / time_change
                                
                                if not self._compare_values(rate, operator, threshold):
                                    return False
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            
            # Deviation from moving average condition
            elif condition_type == "deviation":
                sensor = condition.get("sensor")
                operator = condition.get("operator")
                threshold = condition.get("threshold")
                window_size = condition.get("window_size", self.config["window_size"])
                
                if sensor in self.data_store:
                    values = self.data_store[sensor]["values"]
                    
                    if len(values) >= window_size:
                        # Calculate moving average
                        moving_avg = sum(values[-window_size:]) / window_size
                        current_value = values[-1]
                        deviation = abs(current_value - moving_avg)
                        
                        if not self._compare_values(deviation, operator, threshold):
                            return False
                    else:
                        return False
                else:
                    return False
            
            # Correlation between sensors condition
            elif condition_type == "correlation":
                sensors = condition.get("sensors", [])
                operator = condition.get("operator")
                threshold = condition.get("threshold")
                window_size = condition.get("window_size", self.config["window_size"])
                
                if len(sensors) == 2 and sensors[0] in self.data_store and sensors[1] in self.data_store:
                    values1 = self.data_store[sensors[0]]["values"]
                    values2 = self.data_store[sensors[1]]["values"]
                    
                    if len(values1) >= window_size and len(values2) >= window_size:
                        # Calculate correlation coefficient
                        recent_values1 = values1[-window_size:]
                        recent_values2 = values2[-window_size:]
                        
                        if len(recent_values1) == len(recent_values2) and len(recent_values1) > 1:
                            correlation = self._calculate_correlation(recent_values1, recent_values2)
                            
                            if not self._compare_values(correlation, operator, threshold):
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            
            else:
                logger.warning(f"Unknown condition type: {condition_type}")
                return False
        
        # All conditions passed
        return True
    
    def _compare_values(self, value, operator, threshold):
        """
        Compare values using the specified operator.
        
        Args:
            value (float): Value to compare
            operator (str): Comparison operator (>, <, >=, <=, ==, !=)
            threshold (float): Threshold value
            
        Returns:
            bool: Result of the comparison
        """
        if operator == ">":
            return value > threshold
        elif operator == "<":
            return value < threshold
        elif operator == ">=":
            return value >= threshold
        elif operator == "<=":
            return value <= threshold
        elif operator == "==":
            return value == threshold
        elif operator == "!=":
            return value != threshold
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _calculate_correlation(self, values1, values2):
        """
        Calculate Pearson correlation coefficient between two lists of values.
        
        Args:
            values1 (list): First list of values
            values2 (list): Second list of values
            
        Returns:
            float: Correlation coefficient
        """
        try:
            return np.corrcoef(values1, values2)[0, 1]
        except Exception as e:
            logger.error(f"Error calculating correlation: {e}")
            return 0.0
    
    def _execute_actions(self, actions, message, rule_id):
        """
        Execute rule actions.
        
        Args:
            actions (list): List of actions to execute
            message (dict): Message that triggered the rule
            rule_id (str): ID of the rule that was triggered
        """
        for action in actions:
            action_type = action.get("type")
            
            # Alert action
            if action_type == "alert":
                level = action.get("level", "info")
                action_message = action.get("message", "Alert triggered")
                
                # Create alert payload
                alert_payload = {
                    "rule_id": rule_id,
                    "level": level,
                    "message": action_message,
                    "timestamp": datetime.now().isoformat(),
                    "trigger": {
                        "sensor_type": message.get("sensor_type"),
                        "value": message.get("payload", {}).get("value"),
                        "timestamp": message.get("payload", {}).get("timestamp")
                    }
                }
                
                # Publish alert
                self.mqtt_client.publish(
                    f"{self.config['output_topic_prefix']}alert",
                    json.dumps(alert_payload)
                )
                
                logger.info(f"Published alert: {action_message}")
                self.metrics["alerts_generated"] += 1
            
            # Status action
            elif action_type == "status":
                action_message = action.get("message", "Status update")
                
                # Create status payload
                status_payload = {
                    "message": action_message,
                    "timestamp": datetime.now().isoformat(),
                    "sensors": {}
                }
                
                # Add latest values for all sensors
                for sensor_type, data in self.data_store.items():
                    if data["values"]:
                        status_payload["sensors"][sensor_type] = {
                            "value": data["values"][-1],
                            "timestamp": datetime.fromtimestamp(data["timestamps"][-1]).isoformat() 
                                        if data["timestamps"] else None
                        }
                
                # Publish status
                self.mqtt_client.publish(
                    f"{self.config['output_topic_prefix']}status",
                    json.dumps(status_payload)
                )
                
                logger.debug(f"Published status update")
            
            # Control action
            elif action_type == "control":
                target = action.get("target")
                command = action.get("command")
                
                # Create control payload
                control_payload = {
                    "command": command,
                    "timestamp": datetime.now().isoformat(),
                    "source_rule": rule_id
                }
                
                # Publish control command
                self.mqtt_client.publish(
                    f"{self.config['output_topic_prefix']}control/{target}",
                    json.dumps(control_payload)
                )
                
                logger.info(f"Published control command to {target}: {command}")
            
            else:
                logger.warning(f"Unknown action type: {action_type}")
    
    def start(self):
        """Start the semantic reasoner."""
        if self.running:
            logger.warning("Semantic Reasoner is already running")
            return
        
        try:
            # Connect to MQTT broker
            self.mqtt_client.connect(self.config["mqtt_broker"], self.config["mqtt_port"])
            self.mqtt_client.loop_start()
            
            # Start processing thread
            self.running = True
            self.metrics["start_time"] = time.time()
            
            self.processing_thread = threading.Thread(target=self._data_processor)
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            logger.info("Semantic Reasoner started")
            
        except Exception as e:
            logger.error(f"Error starting Semantic Reasoner: {e}")
            self.stop()
    
    def stop(self):
        """Stop the semantic reasoner."""
        if not self.running:
            logger.warning("Semantic Reasoner is not running")
            return
        
        try:
            # Stop processing thread
            self.running = False
            
            if self.processing_thread:
                self.processing_thread.join(timeout=2.0)
            
            # Disconnect MQTT client
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            
            logger.info("Semantic Reasoner stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Semantic Reasoner: {e}")
    
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
    
    def add_rule(self, rule):
        """
        Add a new reasoning rule.
        
        Args:
            rule (dict): Rule to add
        """
        if "id" not in rule:
            rule["id"] = f"rule_{len(self.rules)}"
        
        self.rules.append(rule)
        logger.info(f"Added rule: {rule['id']}")
    
    def remove_rule(self, rule_id):
        """
        Remove a reasoning rule.
        
        Args:
            rule_id (str): ID of the rule to remove
            
        Returns:
            bool: True if rule was removed, False otherwise
        """
        for i, rule in enumerate(self.rules):
            if rule.get("id") == rule_id:
                self.rules.pop(i)
                logger.info(f"Removed rule: {rule_id}")
                return True
        
        logger.warning(f"Rule not found: {rule_id}")
        return False
    
    def simulate_sensor_data(self, sensor_type, pattern="random", interval=1.0, duration=60):
        """
        Simulate sensor data for testing.
        
        Args:
            sensor_type (str): Type of sensor (temperature, pressure, etc.)
            pattern (str): Data pattern (random, sine, step, spike)
            interval (float): Interval between messages in seconds
            duration (int): Duration of simulation in seconds
        """
        if not self.running:
            logger.warning("Semantic Reasoner is not running")
            return
        
        def _sensor_simulator():
            start_time = time.time()
            count = 0
            
            # Initial value and parameters
            if sensor_type == "temperature":
                base_value = 25.0
                amplitude = 5.0
                unit = "C"
            elif sensor_type == "pressure":
                base_value = 100.0
                amplitude = 10.0
                unit = "kPa"
            elif sensor_type == "humidity":
                base_value = 50.0
                amplitude = 20.0
                unit = "%"
            else:
                base_value = 50.0
                amplitude = 10.0
                unit = "unit"
            
            while self.running and (time.time() - start_time) < duration:
                # Generate value based on pattern
                if pattern == "random":
                    value = base_value + np.random.uniform(-amplitude, amplitude)
                elif pattern == "sine":
                    value = base_value + amplitude * np.sin(count * 0.1)
                elif pattern == "step":
                    value = base_value + (amplitude if count % 20 < 10 else 0)
                elif pattern == "spike":
                    value = base_value + (amplitude * 3 if count % 30 == 0 else np.random.uniform(-amplitude/5, amplitude/5))
                else:
                    value = base_value
                
                # Create payload
                payload = {
                    "value": value,
                    "timestamp": datetime.now().isoformat(),
                    "unit": unit,
                    "sensor_id": f"{sensor_type}_sim_{count}"
                }
                
                # Publish to input topic
                topic = f"{self.config['input_topic_prefix']}{sensor_type}"
                self.mqtt_client.publish(topic, json.dumps(payload))
                
                logger.debug(f"Published simulated {sensor_type} data: {value}")
                
                count += 1
                time.sleep(interval)
            
            logger.info(f"Sensor simulation completed: {count} messages published")
        
        simulator_thread = threading.Thread(target=_sensor_simulator)
        simulator_thread.daemon = True
        simulator_thread.start()
        
        logger.info(f"Started sensor simulation for {sensor_type} with {pattern} pattern")

# Example usage
if __name__ == "__main__":
    # Create semantic reasoner
    reasoner = SemanticReasoner()
    
    # Start the reasoner
    reasoner.start()
    
    try:
        # Simulate temperature sensor data with spike pattern
        reasoner.simulate_sensor_data("temperature", pattern="spike", interval=0.5, duration=60)
        
        # Simulate pressure sensor data with sine pattern
        reasoner.simulate_sensor_data("pressure", pattern="sine", interval=0.7, duration=60)
        
        # Run for a while
        time.sleep(65)
        
        # Get and print metrics
        metrics = reasoner.get_metrics()
        print(f"Performance Metrics:")
        print(f"  Messages Processed: {metrics['messages_processed']}")
        print(f"  Rules Triggered: {metrics['rules_triggered']}")
        print(f"  Alerts Generated: {metrics['alerts_generated']}")
        print(f"  Average Processing Time: {metrics['average_processing_time']:.6f} seconds")
        print(f"  Uptime: {metrics.get('uptime', 0):.1f} seconds")
        
    except KeyboardInterrupt:
        print("Interrupted by user")
    
    finally:
        # Stop the reasoner
        reasoner.stop()
