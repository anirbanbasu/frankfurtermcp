import logging

from fastmcp.server.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

logger = logging.getLogger(__name__)


class StripUnknownArgumentsMiddleware(Middleware):
    """Middleware to strip unknown arguments from tool calls."""

    async def on_call_tool(self, context, call_next):
        """Filter out unknown arguments from tool calls."""
        try:
            # Only proceed if this is a tool call with non-zero arguments
            if context.fastmcp_context and context.message.arguments and len(context.message.arguments) > 0:
                tool = await context.fastmcp_context.fastmcp.get_tool(context.message.name)
                tool_args = tool.parameters.get("properties", None)
                expected_args_names = set(tool_args.keys()) if tool_args else set()
                filtered_args = {k: v for k, v in context.message.arguments.items() if k in expected_args_names}
                unknown_args = set(context.message.arguments.keys()).difference(expected_args_names)
                if unknown_args:
                    logger.info(f"Unknown arguments for tool '{context.message.name}': {list(unknown_args)}")
                context.message.arguments = filtered_args  # modify in place
        except Exception as e:  # pragma: no cover
            logger.error(f"Error in {StripUnknownArgumentsMiddleware.__name__}: {e}", exc_info=True)
        return await call_next(context)


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to limit the size of HTTP request bodies."""

    def __init__(self, app, max_body_size: int = 0):
        super().__init__(app)
        self.max_body_size = max_body_size

    async def dispatch(self, request, call_next):
        if request.headers.get("content-length"):
            content_length = int(request.headers["content-length"])
            if self.max_body_size > 0 and content_length > self.max_body_size:
                return Response(
                    content=f"Request body is too large. Allowed maximum size is {self.max_body_size} bytes.",
                    status_code=413,
                )
        return await call_next(request)
