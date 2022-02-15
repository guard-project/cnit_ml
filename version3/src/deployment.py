import ast
import json
import logging
import os
import signal
import sys
import time
import warnings

import numpy as np
import pandas as pd
from about import project, title, version  # noqa: E402
from dynaconf import Dynaconf
from joblib import load
from kafka import KafkaConsumer, KafkaProducer
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel  # noqa: E402


def signal_stop(sig=None, frame=None):
    if os.path.exists('.pidfile'):
        os.remove('.pidfile')
    if os.path.exists(f'.pidfile.{pid}'):
        os.remove(f'.pidfile.{pid}')
    log.warning('Stopping...')
    exit(1)


def signal_restart(sig=None, frame=None):
    log.warning('Restarting...')


signal.signal(signal.SIGINT, signal_stop)
signal.signal(signal.SIGTERM, signal_stop)
signal.signal(signal.SIGHUP, signal_restart)

config = Dynaconf(settings_files=["config.yaml"])

log_data = config.get('log', {})
log_level = log_data.get('level', 'NOTSET')
log_format = log_data.get('format', '%(message)s')

output_filename = "/proc/1/fd/1"
if (os.path.exists(output_filename)):
    output_file = open(output_filename, "wt")
    console = Console(file=output_file)
else:
    console = Console(file=sys.stdout)

logging.basicConfig(level=log_level, format=log_format,
                    datefmt="[%X]",
                    handlers=[RichHandler(console=console,
                                          rich_tracebacks=True,
                                          omit_repeated_times=False,
                                          markup=True)]
                    )
log = logging.getLogger("rich")

try:
    pid = str(os.getpid())
    with open(".pidfile", "w") as f:
        f.write(pid)
    with open(f".pidfile.{pid}", "w") as f:
        f.write(pid)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=UserWarning)
        scaler = load("joblib/scaler.joblib")
        cols = load("joblib/columns.joblib")
        class_names = load("joblib/class_names.joblib")
        grid_clf_acc = load("joblib/rfmodel_multiclass_new.joblib")

        kafka_bootstrap_servers = config.kafka.bootstrap_servers
        if isinstance(kafka_bootstrap_servers, list):
            kafka_bootstrap_servers = ",".join(kafka_bootstrap_servers)
        kafka_topic = config.kafka.topic
        kafka_group_id = config.kafka.group_id

        ident = f"{project} - {title} v:{version}"

        console.print("")
        console.print(Panel.fit(ident))

        console.rule('Options')
        console.print(f"Kafka Bootstrap Servers: {kafka_bootstrap_servers}")
        console.print(f"Kafka Topic: {kafka_topic}")
        console.print(f"Kafka Group ID: {kafka_group_id}")
        console.print(f"LOG Format: {log_format}")
        console.print(f"LOG Level: {log_level}")

        console.rule('Logging')

        producer = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
        consumer = KafkaConsumer(
            kafka_topic,
            group_id=kafka_group_id,
            bootstrap_servers=kafka_bootstrap_servers,
            auto_offset_reset="earliest",
        )

        rep_time = 60
        time_to_report = time.time() + rep_time
        attackers = {}
        for msg in consumer:
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
            log.info(f'Flow ID: [red]{message2["FLOW_ID"]}[/red] - Result Class: [red]{class_name_test_preds}[/red]')

            if test_preds[0] != 0:
                ipv4_src_addr = message2["IPV4_SRC_ADDR"]
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
                    producer.send("detection-results",
                                  json.dumps(output).encode("utf-8"))
                    log.warning(f'Attackers: {attackers}')
                    attackers = {}
                time_to_report = time.time() + rep_time
except Exception as e:
    log.exception(e)
    signal_stop()
