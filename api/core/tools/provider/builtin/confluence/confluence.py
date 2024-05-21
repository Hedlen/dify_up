from core.tools.errors import ToolProviderCredentialValidationError
from core.tools.provider.builtin.confluence.tools.confluence_search import ConfluenceSearchTool
from core.tools.provider.builtin_tool_provider import BuiltinToolProviderController


class ConfluenceProvider(BuiltinToolProviderController):
    def _validate_credentials(self, credentials: dict) -> None:
        try:
            ConfluenceSearchTool().fork_tool_runtime(
                meta={
                    "credentials": credentials,
                }
            ).invoke(
                user_id='',
                tool_parameters={
                    "query": "",
                    "top_n": 5
                },
            )
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))