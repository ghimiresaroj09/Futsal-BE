"""View mixins that wrap DRF generic responses into the standard envelope."""
from __future__ import annotations

from rest_framework import status as http_status
from rest_framework.response import Response


class EnvelopeMixin:
    """Wraps successful generic-view responses in {success,message,data}."""

    success_message = "Success"

    def finalize_response(self, request, response, *args, **kwargs):
        if isinstance(response, Response) and response.status_code < 400:
            # RFC 9110: a 204 response MUST have an empty body. Never attach an
            # envelope to one — doing so produces a response Postman/browsers
            # will reject as malformed. If a 204 somehow carries data, promote
            # it to 200 so the body we build is legal; otherwise leave it as a
            # true empty 204 and skip wrapping entirely.
            if response.status_code == http_status.HTTP_204_NO_CONTENT:
                if response.data is not None:
                    response.status_code = http_status.HTTP_200_OK
                else:
                    return super().finalize_response(request, response, *args, **kwargs)

            if (
                isinstance(response.data, (dict, list, type(None)))
                and not (isinstance(response.data, dict) and "success" in response.data)
            ):
                response.data = {
                    "success": True,
                    "message": getattr(self, "success_message", "Success"),
                    "data": response.data if response.data is not None else {},
                }
        return super().finalize_response(request, response, *args, **kwargs)