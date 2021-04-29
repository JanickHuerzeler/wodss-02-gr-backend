template = {
    "swagger": "2.0",
    "info": {
        "title": "WODSS Gruppe 02 Backend API",
        "description": "API for WODSS Gruppe 02 Backend",
        "contact": {
            "responsibleOrganization": "FHNW",
            "url": "https://corona-navigator.ch",
        },
        "version": "0.0.1"
    },
    #   "host": "mysite.com",  # overrides localhost:500
    "basePath": "/",  # base bash for blueprint registration
    "schemes": [
        "http",
        "https"
    ],
    "operationId": "getmyData",
    "definitions": {
        "coordinateDTO": {
            "properties": {
                "lat": {
                    "type": "number"
                },
                "lng": {
                    "type": "number"
                }
            },
            "type": "object"
        },
        "municipalityDTO": {
            "properties": {
                "bfs_nr": {
                    "type": "integer"
                },
                "canton": {
                    "type": "string"
                },
                "geo_shapes": {
                    "items": {
                        "items": {
                            "$ref": "#/definitions/coordinateDTO"
                        },
                        "type": "array"
                    },
                    "type": "array"
                },
                "incidence": {
                    "type": "number",
                    "format": "float"
                },
                "incidence_color": {
                    "type": "string"
                },
                "incidence_date": {
                    "format": "date",
                    "type": "string"
                },
                "name": {
                    "type": "string"
                },
                "plz": {
                    "type": "integer"
                }
            },
            "type": "object"
        },
        "incidenceDTO": {
            "properties": {
                "bfsNr": {
                    "type": "number"
                },
                "date": {
                    "format": "date",
                    "type": "string"
                },
                "incidence": {
                    "type": "number",
                    "format": "float"
                },
            },
            "type": "object"
        },
        "municipalityMetadataDTO": {
            "properties": {
                "bfs_nr": {
                    "type": "integer"
                },
                "name": {
                    "type": "string"
                },
                "canton": {
                    "type": "string"
                },
                "area": {
                    "type": "number",
                    "format": "float"
                },
                "population": {
                    "type": "number"
                },
            }
        }
    }
}
