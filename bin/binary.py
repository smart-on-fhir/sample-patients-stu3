
def Binary(data):
    """Builds and returns the Binary JSON"""

    return {
        "request": {
            "method": "PUT",
            "url"   : data["id"]
        },
        "resource": {
            "id"          : data["id"],
            "resourceType": "Binary",
            "contentType" : data["mime_type"],
            "content"     : data["content"]
        }
    }
