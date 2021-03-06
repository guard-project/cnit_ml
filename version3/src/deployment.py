import ast
import json
import logging
import os
import signal
import ssl
import sys
import time
import warnings

import numpy as np
import pandas as pd
from about import project, title, version  # noqa: E402
from dynaconf import Dynaconf
from joblib import load
from kafka import KafkaConsumer, KafkaProducer
from rich import print
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel  # noqa: E402


class Data:
    producer = None
    consumer = None
    log = None

    kafka_bootstrap_servers = None
    kafka_client_id = None
    kafka_topic = None
    kafka_group_id = None
    kafka_security_protocol = 'PLAINTEXT'
    kafka_ssl_cafile = None
    kafka_ssl_certfile = None
    log_level = None
    log_format = None

    @classmethod
    def init(cls):
        output_filename = "/proc/1/fd/1"
        if (os.path.exists(output_filename)):
            output_file = open(output_filename, "wt")
            cls.console = Console(file=output_file)
        else:
            cls.console = Console(file=sys.stdout)

    @classmethod
    def read(cls):
        data = Dynaconf(settings_files=["config.yaml"])
        cls.kafka_bootstrap_servers = data.kafka.bootstrap_servers
        if isinstance(cls.kafka_bootstrap_servers, list):
            cls.kafka_bootstrap_servers = ",".join(cls.kafka_bootstrap_servers)
        cls.kafka_client_id = data.kafka.client_id
        cls.kafka_security_protocol = data.kafka.security_protocol
        if 'ssl' in cls.kafka_security_protocol.lower():
            cls.kafka_ssl_cafile = data.kafka.ssl_cafile
            cls.kafka_ssl_certfile = data.kafka.ssl_certfile
        cls.kafka_topic = data.kafka.topic
        cls.kafka_group_id = data.kafka.group_id
        cls.log_level = data.log.level
        cls.log_format = data.log.format
        cls.version = data.version
        cls.sources = data.get('sources', [])
        cls.report_time = data.get('report-time', 60)

    @classmethod
    def print(cls):
        cls.console.print(f"Kafka Bootstrap Servers: {cls.kafka_bootstrap_servers}")
        cls.console.print(f"Kafka Client ID: {cls.kafka_client_id}")
        cls.console.print(f"Kafka Security Protocol: {cls.kafka_security_protocol}")
        if 'ssl' in cls.kafka_security_protocol.lower():
            cls.console.print(f"Kafka CAfile: {cls.kafka_ssl_cafile}")
            cls.console.print(f"Kafka Certfile: {cls.kafka_ssl_certfile}")
        cls.console.print(f"Kafka Topic: {cls.kafka_topic}")
        cls.console.print(f"Kafka Group ID: {cls.kafka_group_id}")
        cls.console.print(f"LOG Format: {cls.log_format}")
        cls.console.print(f"LOG Level: {cls.log_level}")
        cls.console.print(f"Version: {cls.version}")
        cls.console.print(f"Report Time: {cls.report_time}")

    @classmethod
    def set(cls):
        logging.basicConfig(level=cls.log_level, format=cls.log_format,
                            datefmt="[%X]",
                            handlers=[RichHandler(console=cls.console,
                                                  rich_tracebacks=True,
                                                  omit_repeated_times=False,
                                                  markup=True)]
                            )
        cls.log = logging.getLogger("rich")

        if Data.version not in ["v3", "v3b"]:
            Data.log.error(f"Version {Data.version} is not supported")
            signal_stop()

        ssl_ctx = None
        if 'ssl' in cls.kafka_security_protocol.lower() \
            and cls.kafka_ssl_cafile is not None        \
                and cls.kafka_ssl_certfile is not None:
            ssl_ctx = ssl.create_default_context(cafile=cls.kafka_ssl_cafile)
            ssl_ctx.load_cert_chain(cls.kafka_ssl_certfile)
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

        cls.producer = KafkaProducer(
            bootstrap_servers=cls.kafka_bootstrap_servers,
            client_id=cls.kafka_client_id,
            security_protocol=cls.kafka_security_protocol,
            ssl_context=ssl_ctx
        )
        cls.consumer = KafkaConsumer(
            cls.kafka_topic,
            group_id=cls.kafka_group_id,
            bootstrap_servers=cls.kafka_bootstrap_servers,
            auto_offset_reset="earliest",
            security_protocol=cls.kafka_security_protocol,
            client_id=cls.kafka_client_id,
            ssl_context=ssl_ctx
        )


def signal_stop(sig=None, frame=None):
    if os.path.exists('.pidfile'):
        os.remove('.pidfile')
    if os.path.exists(f'.pidfile.{pid}'):
        os.remove(f'.pidfile.{pid}')
    Data.console.rule('Stopping')
    if Data.producer:
        Data.producer.close()
    if Data.consumer:
        Data.consumer.close()
    exit(1)


def signal_restart(sig=None, frame=None):
    Data.console.rule('Restarting')
    Data.log.error("Restarting not yet available")
    # if Data.consumer:
    #     Data.consumer.close()
    # if Data.producer:
    #     Data.producer.close()
    # time.sleep(20)


signal.signal(signal.SIGINT, signal_stop)
signal.signal(signal.SIGTERM, signal_stop)
signal.signal(signal.SIGHUP, signal_restart)

Data.init()
Data.console.print(Panel.fit(f"{project} - {title} v:{version}"))

try:
    pid = str(os.getpid())
    with open(".pidfile", "w") as f:
        f.write(pid)
    with open(f".pidfile.{pid}", "w") as f:
        f.write(pid)

    while True:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=UserWarning)
            scaler = load("joblib/scaler.joblib")
            cols = load("joblib/columns.joblib")
            class_names = load("joblib/class_names.joblib")
            grid_clf_acc = load("joblib/rfmodel_multiclass_new.joblib")

            Data.read()
            Data.console.rule('Options')
            Data.print()
            Data.console.rule('Logging')
            Data.set()

            rep_time = Data.report_time
            time_to_report = time.time() + rep_time
            attackers = {}
            for msg in Data.consumer:
                message = msg.value.decode("utf-8")
                message2 = ast.literal_eval(message)

                testing = [float(message2[i]) for i in cols]
                # test = pd.DataFrame([testing], columns = cols)
                test = pd.DataFrame(
                    scaler.transform(np.asarray(testing).reshape(1, -1)),
                    columns=cols
                )
                test_preds = grid_clf_acc.predict(test)
                class_name_test_preds = class_names[test_preds[0]]
                Data.log.info(f'Flow ID: [red]{message2["FLOW_ID"]}[/ red] - '
                              f'Result Class: [red]{class_name_test_preds}[/ red]')

                ipv4_src_addr = message2["IPV4_SRC_ADDR"]
                if (Data.version == "v3" and test_preds[0] != 0) or \
                        (Data.version == "v3b" and test_preds[0] != 0 and
                            ipv4_src_addr in Data.sources):
                    if ipv4_src_addr not in attackers:
                        attackers[ipv4_src_addr] = {}

                    class_name_test_preds = class_names[test_preds[0]]
                    if class_name_test_preds not in attackers[ipv4_src_addr]:
                        attackers[ipv4_src_addr][class_name_test_preds] = 1
                    else:
                        attackers[ipv4_src_addr][class_name_test_preds] = \
                            attackers[ipv4_src_addr][class_name_test_preds] + 1

                if time.time() >= time_to_report:
                    if attackers:
                        output = {
                            "SOURCE": "ALGO112_v3",
                            "SEVERITY": "10",
                            "DESCRIPTION": "DDoS Attack(s)",
                            "DATA": attackers,
                            "TIMESTAMP": time.time(),
                        }
                        Data.producer.send("detection-results",
                                           json.dumps(output).encode("utf-8"))
                        Data.log.warning(f'Attackers: {attackers}')
                        attackers = {}
                    time_to_report = time.time() + rep_time
except Exception as e:
    if Data.log:
        Data.log.exception(e)
    else:
        print(e)
    signal_stop()
