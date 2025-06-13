import asyncio
import sys
from fastmcp import Client
from typer import Typer
from rich import print as print
from rich.console import Console
from rich.table import Table
from frankfurtermcp.common import (
    get_nonstdio_mcp_client,
    get_nonstdio_transport_endpoint,
    package_metadata,
)

from llama_index.tools.mcp import (
    # get_tools_from_mcp_url,
    aget_tools_from_mcp_url,
    BasicMCPClient,
)

# from frankfurtermcp.common import ic

app = Typer(
    name=f"{package_metadata['Name']}-cli",
    no_args_is_help=True,
    add_completion=False,
    help="A command-line test interface for the Frankfurter MCP server.",
)


def _print_header():
    print(
        f"[bold yellow]{package_metadata['Name']}-cli[/bold yellow] {package_metadata['Version']}: a command line interface to a{package_metadata['Summary'][1:]}"
    )


@app.command()
def version():
    """
    Print the version of the Frankfurter MCP CLI.
    """
    _print_header()
    print(
        f"[bold blue]Author(s)[/bold blue]: [cyan]{package_metadata['Author-email']}[/cyan]"
    )
    print(
        f"[bold blue]License[/bold blue]: [cyan]{package_metadata['License-Expression']}[/cyan]"
    )
    print(
        f"[bold blue]Required Python[/bold blue]: [cyan]{package_metadata['Requires-Python']}[/cyan]"
    )


async def _retrieve_tools_metadata(client: Client):
    async with client:
        tools = await client.list_tools()
        return tools


@app.command()
def tools_info():
    """
    Print information about the available tools in the Frankfurter MCP server.
    """
    _print_header()
    client = get_nonstdio_mcp_client()
    tools_list = asyncio.run(_retrieve_tools_metadata(client))
    if not tools_list:
        print("[bold red]No tools found.[/bold red]")
    else:
        table = Table(
            caption="List of available tools using FastMCP client",
            caption_justify="right",
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Description and schema", style="yellow")
        for tool in tools_list:
            table.add_row(tool.name, tool.description)
            table.add_row(None, None)
            table.add_row(None, tool.model_dump_json(indent=2))
            table.add_section()
        console = Console()
        console.print(table)


@app.command()
def llamaindex_tools_list():
    """
    List tools from the MCP server using LlamaIndex's MCP client.
    """
    _print_header()
    transport_endpoint = get_nonstdio_transport_endpoint()
    llamaindex_client = BasicMCPClient(transport_endpoint)
    tools_list = asyncio.run(
        aget_tools_from_mcp_url(transport_endpoint, llamaindex_client)
    )
    if not tools_list:
        print("[bold red]No tools found.[/bold red]")
    else:
        table = Table(
            caption="List of available tools using LlamaIndex MCP client",
            caption_justify="right",
        )
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column(
            ("Description"),
            style="yellow",
        )
        for tool in tools_list:
            tool_metadata = tool.__dict__["_metadata"]
            table.add_row(tool_metadata.name, tool_metadata.description)
            table.add_section()
        console = Console()
        console.print(table)


def main():
    try:
        app()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
