import asyncio
import shutil
from pathlib import Path

import weave
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# Change this if you want a different Weave project
WEAVE_PROJECT = "itprodirect/agents-course-live"


@weave.op()
async def chapter_6_mcp():
    # Directory containing the files the MCP filesystem server is allowed to read
    samples_dir = (Path(__file__).resolve().parent / "sample_files").resolve()

    if not samples_dir.exists():
        raise FileNotFoundError(
            f"Expected sample_files directory at:\n  {samples_dir}\n\n"
            "Create it and add:\n"
            "  - favorite_books.txt\n"
            "  - favorite_songs.txt\n"
            "  - favorite_cities.txt\n"
        )

    # Make sure npx exists (Node.js installed)
    npx_cmd = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_cmd is None:
        raise RuntimeError(
            "npx not found.\n\n"
            "Install Node.js (LTS), then restart your terminal.\n"
            "Confirm:\n"
            "  node -v\n"
            "  npx -v\n"
        )

    # NOTE:
    # First run of `npx` may download the MCP server package and can take > 5 seconds,
    # so we bump the MCP client init timeout.
    async with MCPServerStdio(
        params={
            "command": npx_cmd,
            "args": ["-y", "@modelcontextprotocol/server-filesystem", str(samples_dir)],
        },
        client_session_timeout_seconds=60,
    ) as filesystem_server:
        agent = Agent(
            name="Assistant",
            instructions=(
                "Use the filesystem tools to read files and answer questions based on those files."
            ),
            mcp_servers=[filesystem_server],
        )

        questions = [
            "What is my number one favorite book? It's the first one in the list.",
            "Look at my favorite songs and suggest one new song that I may like.",
        ]

        for q in questions:
            print(f"\nRunning: {q}")
            result = await Runner.run(agent, input=q)
            print(result.final_output)


def main():
    # IMPORTANT: init Weave BEFORE calling any @weave.op() functions
    weave.init(WEAVE_PROJECT)
    asyncio.run(chapter_6_mcp())


if __name__ == "__main__":
    main()
