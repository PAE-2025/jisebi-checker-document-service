# POST - /upload
upload_docs = {
    "summary": "Upload a DOCX file",
    "responses": {

        200: {
            "description": "Successful upload",
            "content": {
                "application/json": {
                    "example": {
                        "status": "true",
                        "data": {
                            "user_id": "681beef34cd243503a669f3e",
                            "task_id": "0b4eb629-f435-430c-994b-710e05fd1988",
                            "title": "Title of the Paper",
                            "authors": {
                                "text": "First Author 1) , Second Author 2) , Third Author 3)",
                                "first_author": {
                                    "first_name": "First",
                                    "last_name": "Author"
                                }
                            },
                            "status": "awaiting",
                            "url": "https://storage.googleapis.com/jisebi_documents/0b4eb629-f435-430c-994b-710e05fd1988/input.docx?Expires=1747838168&GoogleAccessId=1086217609371-compute%40developer.gserviceaccount.com&Signature=PQSNLhUuVsVr%2BSwntxUNnEnzyLxg3wBTEl6LQDRNOHvUivIIIyE%2BHjteB%2FCmyMweX3sh43gzhb%2FYDWuWFfr3iyz8%2BPnugLXCNvz3jpZ7Rv%2BJOy8dBxHivxXTRrfT7RTzNi53T%2FhA%2BXUPvgestVvg4Q%2FX6nyed1DLmouVh4IteGKvWlcfpHEmQ5RvGvKv0UhtEy270bV%2BfTF9zyQ6knvSdlDJi6OveyP27rxerAOC%2BxDk3L6FcIZAFc6dKxaWGMxPB0Ci%2Bgl9xQhCvo2j6%2BWkMR%2B21Eq%2BQEBGFx3XJ3vzNi1m4Xl1UvTYgedtIMhnff5VptNzweIWM5nHzNHsm6fa9A%3D%3D",
                            "success": "true"
                        }
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
                        "data": 
                            {
                                "created_at": "2025-05-12T09:38:28.244000+00:00",
                                "task_id": "a129690f-5281-4ca4-860d-637fd5fbcd7a",
                                "authors": "First Author 1) , Second Author 2) , Third Author 3)",
                                "title": "Title of the Paper",
                                "user_id": "681beef34cd243503a669f3e",
                                "status": "processed",
                                "updated_at": "2025-05-12T09:38:51.135000+00:00"
                            }
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

# PUT - /upload/{task_id}
update_upload = {
    "summary": "Puts the Document into Queue for Processing",
    "description": "Updates the status of the upload and adds it to the queue",
    "responses": {

        200: {
            "description": "Successful Enqueue",
            "content": {
                "application/json": {
                    "example": {
                        "status": "true"
                    }
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
                        "message": "Error processing document: Error message"
                    }
                }
            }
        }
    },
}

# DELETE - /upload/{task_id}
delete_upload = {
    "summary": "Deletes the Upload",
    "description": "Deletes the entry on the database and deletes the item on storage",
    "responses": {

        200: {
            "description": "Successful Enqueue",
            "content": {
                "application/json": {
                    "example": {
                        "status": "true"
                    }
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
                        "message": "Error processing document: Error message"
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