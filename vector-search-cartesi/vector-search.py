# Copyright 2022 Cartesi Pte. Ltd.
#
# SPDX-License-Identifier: Apache-2.0
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use
# this file except in compliance with the License. You may obtain a copy of the
# License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.

from os import environ
import traceback
import logging
import requests

from qdrant_client import QdrantClient
from qdrant_client.http.models.models import Filter
from sentence_transformers import SentenceTransformer
from typing import List

class NeuralSearcher:

    def __init__(self, collection_name: str, cursor=None):
        self.collection_name = collection_name
        self.model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens', device='cpu')
        # self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant_client = QdrantClient(
            host=environ.get("QDRANT_HOST", "b8be5dab-08a0-43ec-ae4a-ed92bbd23805.us-east-1-0.aws.cloud.qdrant.io"),
            api_key=environ.get("QDRANT_API_KEY", "Ws4dvr1f4ULm0QUp3Pbvzt4AYaL5Eits6WWi8MbW0fQlub7pP0T6Ew"),
        )

    def search(self, text: str, filter_: dict = None) -> List[dict]:
        vector = self.model.encode(text).tolist()
        payloads = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=vector,
            query_filter=Filter(**filter_) if filter_ else None,
            with_payload=True,
            limit=10
        )
        return payloads



logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")


logger.info(f"HTTP rollup_server url is {rollup_server}")

collection_name="lens_posts_4"
logger.info(f"Creating a NeuralSearcher for collection {collection_name}")
n = NeuralSearcher(collection_name=collection_name)


def hex2str(hex):
    """
    Decodes a hex string into a regular string
    """
    return bytes.fromhex(hex[2:]).decode("utf-8")


def str2hex(str):
    """
    Encodes a string as a hex string
    """
    return "0x" + str.encode("utf-8").hex()


def handle_advance(data):
    """
    An advance request may be processed as follows:

    1. A notice may be generated, if appropriate:

    response = requests.post(rollup_server + "/notice", json={"payload": data["payload"]})
    logger.info(f"Received notice status {response.status_code} body {response.content}")

    2. During processing, any exception must be handled accordingly:

    try:
        # Execute sensible operation
        op.execute(params)

    except Exception as e:
        # status must be "reject"
        status = "reject"
        msg = "Error executing operation"
        logger.error(msg)
        response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})

    finally:
        # Close any resource, if necessary
        res.close()

    3. Finish processing

    return status
    """

    """
    The sample code from the Echo DApp simply generates a notice with the payload of the
    request and print some log messages.
    """

    logger.info(f"Received advance request data {data}")

    status = "accept"
    try:
        payload = hex2str(data["payload"])
        logger.info(f"Payload is {payload}")

        result = n.search(payload)
        logger.info(f"Result is {result}")

        result_hex = str2hex(str(result))

        logger.info("Adding notice")
        response = requests.post(
            rollup_server + "/notice", json={"payload": result_hex})
        logger.info(
            f"Received notice status {response.status_code} body {response.content}")

    except Exception as e:
        status = "reject"
        msg = f"Error processing data {data}\n{traceback.format_exc()}"
        logger.error(msg)
        response = requests.post(
            rollup_server + "/report", json={"payload": str2hex(msg)})
        logger.info(
            f"Received report status {response.status_code} body {response.content}")

    return status


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    logger.info("Adding report")
    response = requests.post(rollup_server + "/report",
                             json={"payload": data["payload"]})
    logger.info(f"Received report status {response.status_code}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}
rollup_address = None

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        if "metadata" in data:
            metadata = data["metadata"]
            if metadata["epoch_index"] == 0 and metadata["input_index"] == 0:
                rollup_address = metadata["msg_sender"]
                logger.info(f"Captured rollup address: {rollup_address}")
                continue
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
