# POST - /upload
upload_docs = {
    "summary": "Upload a DOCX file",
    "responses": {

        200: {
            "description": "Successful upload",
            "content": {
                "application/json": {
                    "example": {
                        "task_id": "a129690f-5281-4ca4-860d-637fd5fbcd7a",
                        "status": "queued",
                        "success": True
                    }
                }
            }
        },

        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Invalid or expired token"
                    }
                }
            }
        },  

        422: {
            "description": "Invalid File Format",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid file format. Only DOCX files are supported."}
                }
            }
        }
    },
}

# GET - /upload
upload_list = {
    "summary": "List the Upload History",
    "responses": {

        200: {
            "description": "Successful request",
            "content": {
                "application/json": {
                    "example": {
                        "status": True,
                        "data": [
                            {
                                "created_at": "2025-05-12T09:38:28.244000+00:00",
                                "task_id": "a129690f-5281-4ca4-860d-637fd5fbcd7a",
                                "authors": "First Author 1) , Second Author 2) , Third Author 3)",
                                "title": "Title of the Paper",
                                "user_id": "681beef34cd243503a669f3e",
                                "status": "processed",
                                "updated_at": "2025-05-12T09:38:51.135000+00:00"
                            },]
                    }
                }
            }
        },

        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Invalid or expired token"
                    }
                }
            }
        },  

        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Error fetching history"
                    }
                }
            }
        }
    },
}

# GET - /download/{task_id}
download = {
    "summary": "Downloads Report",
    "description": "Downloads the PDF report using the Task ID",
    "responses": {

        200: {
            "description": "Successful Download",
            "content": {
                "application/pdf": {
                    "schema": {
                        "type": "string",
                        "format": "binary",
                        "description": "A downloadable PDF report"
                    },
                    "example": "<< report pdf file >>"
                },
                 "application/json": {
                    "example": "null > returns pdf file"
                }
            }
        },

        423: {
            "description": "Not Found or Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Item not found or unauthorized access"
                    }
                }
            }
        }, 

        404: {
            "description": "Still processing",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Item is not finished processing"
                    }
                }
            }
        }, 

        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Invalid or expired token"
                    }
                }
            }
        },  

        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "status": False,
                        "message": "Download failed"
                    }
                }
            }
        }
    },
}