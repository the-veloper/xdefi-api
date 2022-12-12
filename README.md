# Optimal exchange route between assets

This is a simple asyncronous FAST API that returns the optimal exchange route between assets using a graphql endpoint.

## Prerequisites

- Docker (obviously)
- Docker Compose

## Setup

```bash
docker-compose up -d
```

## Usage

To get the most optimal route between two assets, run the following query:

1. Go to http://localhost:8000/graphql
2. Run the following query:
```graphql
{
  bestRoute(routeInput: {
    fromToken: "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    toToken: "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
  }) {
    path {
        id
    }
  }
}
```

Expected response:
```json
{
  "data": {
    "bestRoute": {
      "path": [
        {
          "id": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
        },
        {
          "id": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
        }
      ]
    }
  }
}
```

## Tests
(TODO)
```bash
docker-compose exec app pytest
```