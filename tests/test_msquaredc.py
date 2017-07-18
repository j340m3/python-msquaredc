
from click.testing import CliRunner

from msquaredc.cli import main


def test_main():
    runner = CliRunner()
    result = runner.invoke(main, ["--user-interface","none"])

    # assert result.output == '()\n'
    assert result.exit_code == 0
