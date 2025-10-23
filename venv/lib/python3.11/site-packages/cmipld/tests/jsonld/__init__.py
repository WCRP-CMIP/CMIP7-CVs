# from .components import *
from pydantic import BaseModel, field_validator
from cmipld.utils import git
from pydantic import ValidationError
from rich.console import Console
from rich.table import Table

from . import experiment


def field_test(extended_class):
    # dynamic class
    return type(extended_class.__name__, (BaseModel, extended_class), {})


def multi_field_test(args):
    assert isinstance(args, list)
    return type('multi_field_test', (BaseModel, *args), {})


def table2md(table: Table) -> str:
    # Extract headers

    md = f"#### {table.title}\n"
    headers = [
        f"<span style=\'color:{col.style}\'>{col.header}</span>" for col in table.columns]
    md += "| " + " | ".join(headers) + " |\n"
    md += "| " + " | ".join(["---"] * len(headers)) + " |\n"

    # Extract rows
    for row in range(len(table.columns[0]._cells)):
        # Iterate over the row directly
        md += "| " + " | ".join(c._cells[row] for c in table.columns) + " |\n"

    return md


def handle_pydantic_errors(e: ValidationError):
    """Format and display Pydantic errors with rich."""
    console = Console()

    # Create a table to display errors
    table = Table(title="Validation Errors", show_lines=True)
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Error Message", style="red")
    table.add_column("Error Type", style="yellow")

    # Populate table with error details
    for err in e.errors():
        field = ".".join(str(part)
                         for part in err['loc'])  # Handle nested fields
        message = err['msg']
        err_type = err['type']
        table.add_row(field, message, err_type)

    # Print the table
    console.print(table)
    mdtable = table2md(table)
    # git.update_summary(f"### Validation Errors\n{mdtable}")
    git.update_issue(
        f"### Validation failed:\n {len(e.errors())} issues found.\n{mdtable}")


def run_checks(pydclass, args):
    # Usage in your run function
    try:
        pydclass(**args)  # Your Pydantic validation
    except ValidationError as e:
        handle_pydantic_errors(e)
        git.close_issue(f"Validation failed: {len(e.errors())} issues found.")
    except Exception as e:
        git.close_issue(f"Unexpected error: {str(e)}")
