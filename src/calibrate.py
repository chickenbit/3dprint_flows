from textwrap import dedent, indent
from typing import Optional
import typer
from rich import print


def _calc_step_rate(
    actual_extruded: int, step_rate: float, extrude_length: int = 100
) -> float:
    steps = step_rate * extrude_length
    accurate_step_rate = steps / actual_extruded
    return accurate_step_rate


def _change_step_rate(step_rate: float) -> str:
    gcode = f"""
		E92 {step_rate:.1f}
		M500"""
    return dedent(gcode)


def _get_step_rate_gcode(
    actual_extruded: int, step_rate: float, extrude_length: int = 100
):
    step_rate = _calc_step_rate(actual_extruded, step_rate, extrude_length)
    print(_change_step_rate(step_rate))


# TODO configure defaults via pydantic config
# TODO if matching, Congratulations
# TODO save stuff to disk/honor reading last one in


def _prompt_for_next():
    next = typer.confirm("Ready for next step?")
    if not next:
        next = typer.confirm("Really abort?")
        if not next:
            print("See you next time.")
            raise typer.Abort()
    print("")


def main(
    filament_brand: str = typer.Option(..., prompt="What is the filament brand?"),
    filament_type: str = typer.Option(..., prompt="What type of filament?  (PLA|PETG)"),
    extrude_length: float = 100,
    extra_length: float = 20,
    extruder_head_temp: float = 200,
    current_evalue: Optional[float] = None,
):
    if current_evalue is None:
        print(
            "Provide the current extruder 'e-steps' value which can be",
            "obtained by running the [bold]M503[/bold] command.",
            "FYI: units is steps/mm",
        )
        current_evalue = typer.prompt("Current e-step Value (example: 824.7)")
        current_evalue = float(current_evalue)

    print(
        f"Let's calibrate e-steps for {filament_brand} {filament_type} filament with",
        f"current e-step of [bold green]{current_evalue}[/bold green].",
        "\n",
    )

    measured_filament = extrude_length + extra_length

    print(f"[bold]Step 1[/bold]: Measure and mark {measured_filament} mm on filament.")
    _prompt_for_next()

    print(f"[bold]Step 2[/bold]: Preheat extruder head to {extruder_head_temp} C.")
    _prompt_for_next()

    print(
        "[bold]Step 3[/bold]: Run the folowing gcode to 'enable relative mode' (M83)",
        f"and using toolhead (G1) extrude {extrude_length} mm (E{extrude_length})",
        "filament with feed rate",
        f"(F1) of {extrude_length} mm per minute.",
    )
    print(
        indent(
            """
    M83 
    G1 E100 F100    
    """,
            "    ",
        )
    )
    _prompt_for_next()

    print("[bold]Step 4[/bold]: Measure left over filament.")
    print(f"Target is {extra_length} mm")
    _prompt_for_next()

    actual_extra = typer.prompt("What is the left over amount?")

    actual_extruded = measured_filament - float(actual_extra)

    new_evalue = _calc_step_rate(
        actual_extruded, current_evalue, extrude_length=extrude_length
    )
    print(
        f"New e-step value is {new_evalue:.1f}.   Set this new value (E92) and save it",
        "to ROM (M500).",
        "\n",
    )
    gcode = f"""
            M92 E{new_evalue:.1f}
            M500"""

    print(indent(gcode, "    "))


def _wrap():
    typer.run(main)


if __name__ == "__main__":
    _wrap()
