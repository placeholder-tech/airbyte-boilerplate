# README for Airbyte Example Extractor

## Overview
This project provides a starting point for building your own data extractors using Airbyte, 
an open-source data integration platform. The extractor example demonstrates pulling data from a 
mock API, providing a hands-on way to understand how Airbyte interacts with HTTP-based data streams.

Please note, this example extractor is not a complete or fully functional solution. Instead, 
it's designed to serve as a base upon which you can build and customize your own extractors, 
tailored to your specific data sources and requirements.

Key features demonstrated in this example include:
- Interfacing with an HTTP-based data stream
- Implementing authentication for secure data access
- Managing an incrementally updating state for the data stream


## Further information 

Consult additional airbyte extractors for further implementation details 

- source-woocommerce
- source-shopify 


## Getting Started

1. Clone the repo 
2. Set up a virtual env with python 3.9 
3. Go to the src/mock-api directory and install requirements
4. Start the mock api 
5. Go to the src/source-example directory 
6. Run the extractor 


## Running the mock api: 

```
# cd src/mock-api
# flask --app api run 
```

## Running the extractor ( check )

```
# cd src/source-example 
# python main.py check --config config.json
```

## Running the extractor ( read )
```
# cd src/source-example 
# python main.py read --config config.json --catalog catalog.json
```

## Running the extractor ( from previous checkpoint )
```
# cd src/source-example 
# python main.py read --config config.json --catalog catalog.json --state state.json
```