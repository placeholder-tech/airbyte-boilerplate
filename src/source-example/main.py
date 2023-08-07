import sys

from airbyte_cdk.entrypoint import launch
from source_example import ExampleSource

if __name__ == "__main__":
    source = ExampleSource()
    launch(source, sys.argv[1:])
