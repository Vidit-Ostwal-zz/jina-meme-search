import sys
import os
from jina import Flow, Document
from config import WORKSPACE_DIR, NUM_DOCS, DATA_DIR, REQUEST_SIZE, PORT
from executors import ImageNormalizer
from helper import print_result, generate_docs

flow = (
    Flow()
    .add(name="image_normalizer", uses=ImageNormalizer)
    .add(
        name="meme_image_encoder",
        uses="jinahub://CLIPImageEncoder/v0.3",
        uses_metas={"workspace": WORKSPACE_DIR},
        volumes="./data:/encoder/data",
        install_requirements=True
    )
    .add(
        name="meme_image_indexer",
        uses="jinahub://SimpleIndexer/v0.11",
        uses_with={"index_file_name": "index"},
        uses_metas={"workspace": WORKSPACE_DIR},
        volumes=f"./{WORKSPACE_DIR}:/workspace/workspace",
        install_requirements=True
    )
)


def index():
    if os.path.exists(WORKSPACE_DIR):
        print(f"'{WORKSPACE_DIR}' folder exists. Please delete")
        sys.exit()

    docs = generate_docs(DATA_DIR, NUM_DOCS)

    with flow:
        flow.index(inputs=docs, show_progress=True, request_size=REQUEST_SIZE)


def search():

    with flow:
        flow.protocol = "http"
        flow.port_expose = PORT
        flow.block()


def search_grpc():
    filename = sys.argv[2]
    query = Document(uri=filename)

    with flow:
        flow.search(
            query,
            on_done=print_result,
            parameters={"top_k": 5},
            show_progress=True,
        )


if len(sys.argv) < 1:
    print("Supported arguments: index, search, search_grpc")
if sys.argv[1] == "index":
    index()
elif sys.argv[1] == "search":
    search()
elif sys.argv[1] == "search_grpc":
    search_grpc()
else:
    print("Supported arguments: index, search, search_grpc")
