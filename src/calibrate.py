from datetime import datetime
from textwrap import dedent, indent
from typing import Optional
from model import EValueCalibration
import typer
from rich.console import Console
from rich.theme import Theme
from rich.prompt import Confirm

from rich.prompt import Prompt, FloatPrompt

calibrate_theme = Theme(
    {
        "step": "bold green",
        "gcode": "white on black",
    }
)

_console = Console(theme=calibrate_theme)
print = _console.print


def _calc_step_rate(
    actual_extruded: int, step_rate: float, extrude_length: int = 100
) -> float:
    steps = step_rate * extrude_length
    accurate_step_rate = steps / actual_extruded
    return accurate_step_rate


def _change_step_rate(step_rate: float) -> str:
    """Returns gcode for setting step-rate

    Args:
        step_rate (float): desired step-rate

    Returns:
        str: gcode
    """
    gcode = f"""[gcode]
		E92 {step_rate:.1f}
		M500[/gcode]"""
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
    next = None
    while next is None:
        next = Confirm.ask("Ready for next step?", console=_console)
        if not next:
            next = Confirm.ask("Really abort?", console=_console)
            if next:
                print("See you next time.")
                raise typer.Abort()
            else:
                next = None
    print("")


def _get_params(
    filament_brand: str,
    filament_type: str,
    filament_color: str,
    extruder_head_temp: float,
    evalue: float = None,
) -> EValueCalibration:
    filament = EValueCalibration(
        brand=filament_brand,
        type=filament_type,
        filament_color=filament_color,
        extruder_temp=extruder_head_temp,
        e_value=evalue,
        dt=datetime.now(),
    )

    choices = ["Continue", "Brand", "Type", "Color", "Temp"]
    choice = Prompt.ask(
        f"Continue or change params of {filament}",
        console=_console,
        choices=choices,
        default="Continue",
    )
    while choice != "Continue":
        if choice == "Brand":
            filament.brand = Prompt.ask("Enter filament brand")
        elif choice == "Type":
            filament.type = Prompt.ask(
                "Enter filament type",
                console=_console,
                choices=["PLA", "PETG", "TPU"],
                default="PLA",
            )
        elif choice == "Color":
            filament.color = Prompt.ask("Enter filament color", console=_console)
        elif choice == "Temp":
            filament.extruder_temp = FloatPrompt.ask(
                "Extruder temperature", console=_console
            )
        choice = Prompt.ask(
            f"Continue or change params of {filament}",
            console=_console,
            choices=choices,
            default="Continue",
        )

    return filament


def main(
    filament_brand: str = "AnyCubic",
    filament_type: str = "PLA",
    filament_color: str = None,
    extrude_length: float = 100,
    extra_length: float = 20,
    extruder_head_temp: float = 200,
    current_evalue: Optional[float] = None,
):
    _console.rule(
        "Let's calibrate the e-steps for the three dimensional printer!", align="left"
    )
    filament = _get_params(
        filament_brand,
        filament_type,
        filament_color,
        extruder_head_temp,
        current_evalue,
    )
    print(
        "Provide the current extruder 'e-steps' value which can be",
        "obtained by running the [gcode]M503[/gcode] command.",
        "FYI: units is steps/mm",
    )
    current_evalue = FloatPrompt.ask(
        "Current e-step Value (example: 824.7)", console=_console
    )

    print(
        f"Let's calibrate e-steps for {filament.brand} {filament.type} filament with",
        f"current e-step of [bold green]{current_evalue}[/bold green].",
        "\n",
    )

    measured_filament = extrude_length + extra_length

    _console.rule("[step]Step 1[/step]")
    print(f"Measure and mark {measured_filament} mm on filament.")
    _prompt_for_next()

    _console.rule("[step]Step 2[/step]")
    print(f"Preheat extruder head to {filament.extruder_temp} C.")
    _prompt_for_next()

    _console.rule("[step]Step 3[/step]")
    print(
        "Run the following gcode to 'enable relative mode' ([gcode]M83[/gcode])",
        f"and using toolhead ([gcode]G1[/gcode]) extrude {extrude_length} mm ([gcode]E{extrude_length}[/gcode])",
        "filament with feed rate",
        f"([gcode]F1[/gcode]) of {extrude_length} mm per minute.",
    )
    print(
        indent(
            """[gcode]
    M83 
    G1 E100 F100    
    [/gcode]
    """,
            "    ",
        )
    )
    _prompt_for_next()

    _console.rule("[step]Step 4[/step]")
    print("Measure left over filament.")
    print(f"Target is {extra_length} mm")
    _prompt_for_next()

    actual_extra = FloatPrompt.ask("What is the left over amount?", console=_console)

    actual_extruded = measured_filament - actual_extra

    filament.e_value = _calc_step_rate(
        actual_extruded, current_evalue, extrude_length=extrude_length
    )
    print(
        f"New e-step value is {filament.e_value:.1f}.   Set this new value ([gcode]E92[/gcode]) and save it",
        "to ROM ([gcode]M500[/gcode]).",
        "\n",
    )
    gcode = f"""[gcode]
            M92 E{filament.e_value:.1f}
            M500[/gcode]"""
    print(indent(gcode, "    "))

    print(f"Data: {filament}")


def _wrap():
    typer.run(main)


if __name__ == "__main__":
    _wrap()
