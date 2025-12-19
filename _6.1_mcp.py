import asyncio
import shutil
from pathlib import Path

import weave
from agents import Agent, Runner
from agents.mcp import MCPServerStdio

# Public project you created in W&B
WEAVE_PROJECT = "itprodirect/agents-course-mcp-public"


@weave.op(name="chapter_6_mcp_filesystem")
async def chapter_6_mcp():
    """
    Demonstrates using an MCP filesystem server with an agent, while logging a Weave trace.

    Returns a structured dict so the Weave trace Output is not null.
    """
    repo_dir = Path(__file__).resolve().parent
    samples_dir = (repo_dir / "sample_files").resolve()
    outputs_dir = (repo_dir / "outputs").resolve()
    outputs_dir.mkdir(exist_ok=True)

    if not samples_dir.exists():
        raise FileNotFoundError(
            f"Expected sample_files directory at:\n  {samples_dir}\n\n"
            "Create it and add:\n"
            "  - favorite_books.txt\n"
            "  - favorite_songs.txt\n"
            "  - favorite_cities.txt\n"
        )

    # Ensure `npx` exists (Node.js installed)
    npx_cmd = shutil.which("npx") or shutil.which("npx.cmd")
    if npx_cmd is None:
        raise RuntimeError(
            "npx not found.\n\n"
            "Install Node.js (LTS), then restart your terminal.\n"
            "Confirm:\n"
            "  node -v\n"
            "  npx -v\n"
        )

    # Files the model should write
    brief_path = outputs_dir / "mcp_brief.md"

    # IMPORTANT:
    # The MCP filesystem server expects allowed directories.
    # Many versions accept multiple allowed roots as separate args after the package name.
    # We'll allow BOTH sample_files (read) and outputs (write).
    async with MCPServerStdio(
        params={
            "command": npx_cmd,
            "args": [
                "-y",
                "@modelcontextprotocol/server-filesystem",
                str(samples_dir),
                str(outputs_dir),
            ],
        },
        client_session_timeout_seconds=60,
    ) as filesystem_server:
        agent = Agent(
            name="MCP Filesystem Agent",
            instructions=(
                "You MUST use filesystem tools for every task.\n"
                "- First, list available files/directories.\n"
                "- Then read any relevant file(s) before answering.\n"
                "- If asked to write output, write it under the outputs directory.\n"
                "- If you cannot read a needed file, say you cannot answer.\n"
                "Keep the response concise and follow the numbered instructions."
            ),
            mcp_servers=[filesystem_server],
        )

        prompt = (
            "1) List the files you can access.\n"
            "2) Read favorite_books.txt and tell me the #1 book (first item).\n"
            "3) Read favorite_songs.txt and suggest ONE new song I might like.\n"
            "4) Write a short markdown brief to outputs/mcp_brief.md with:\n"
            "   - the #1 book\n"
            "   - the new song suggestion\n"
            "   - which files you read\n"
        )

        print("\nRunning MCP prompt...\n")
        result = await Runner.run(agent, input=prompt)

    # After the agent run, try to read the written markdown file from disk (optional but helpful)
    brief_exists = brief_path.exists()
    brief_text = None
    if brief_exists:
        try:
            brief_text = brief_path.read_text(encoding="utf-8")
        except Exception as e:
            brief_text = f"<<could not read mcp_brief.md: {e}>>"

    # Return structured output so Weave shows something useful instead of null
    return {
        "weave_project": WEAVE_PROJECT,
        "samples_dir": str(samples_dir),
        "outputs_dir": str(outputs_dir),
        "prompt": prompt,
        "agent_final_output": result.final_output,
        "brief_path": str(brief_path),
        "brief_exists": brief_exists,
        "brief_markdown_preview": brief_text,
    }


def main():
    # IMPORTANT: init Weave BEFORE calling any @weave.op() functions
    weave.init(WEAVE_PROJECT)
    out = asyncio.run(chapter_6_mcp())

    # Optional: print a short confirmation locally
    print("\n=== Done ===")
    print(f"Brief exists: {out['brief_exists']}")
    print(f"Brief path:  {out['brief_path']}")
    print("\nAgent output:\n")
    print(out["agent_final_output"])


if __name__ == "__main__":
    main()
