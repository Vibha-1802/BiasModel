from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Bias-Tools")

@mcp.tool()
def calculate_disparate_impact(favorable_outcome_ratio_a: float, favorable_outcome_ratio_b: float):
    """Calculates bias ratio between two demographic groups."""
    return favorable_outcome_ratio_a / favorable_outcome_ratio_b

if __name__ == "__main__":
    mcp.run()
