from click.testing import CliRunner
from cldflex.cli import corpus, dictionary
from pycldf import Dataset
from pathlib import Path
import shutil
import pandas as pd


def check_filelist(path, checklist):
    file_list = [x.name for x in Path(path).iterdir()]
    for d in ["requirements.txt", "metadata.json", ".gitattributes", "README.md"]:
        if d in file_list:
            file_list.remove(d)
    assert sorted(checklist) == sorted(file_list)


def check_cldf(path):
    md_path = path / "cldf/metadata.json"
    assert md_path.is_file()
    ds = Dataset.from_metadata(md_path)
    assert ds.validate()
    return ds


def run_flextext(
    path, monkeypatch, data, tmp_path, config=None, lexicon=True, cldf=True
):
    monkeypatch.chdir(path)
    runner = CliRunner()
    shutil.copy(data / "output" / "senses.csv", tmp_path)
    shutil.copy(data / "output" / "morphemes.csv", tmp_path)
    commands = [
        str((data / "apalai.flextext").resolve()),
        "--output",
        str(path.resolve()),
    ]
    if lexicon:
        commands.extend(["--lexicon", str((data / "output/morphs.csv").resolve())])
    if cldf:
        commands.extend(["--cldf"])
    if config:
        commands.extend(["--conf", str((data / f"{config}.yaml"))])
    return runner.invoke(corpus, commands, catch_exceptions=False)


def test_sentences1(data, tmp_path, monkeypatch):
    result = run_flextext(tmp_path, monkeypatch, data, tmp_path, lexicon=False)
    assert result.exit_code == 0
    check_cldf(tmp_path)
    check_filelist(
        tmp_path,
        [
            "wordforms.csv",
            "sentences.csv",
            "sentence_slices.csv",
            "texts.csv",
            "morphemes.csv",
            "senses.csv",
            "cldf",
        ],
    )
    check_filelist(
        tmp_path / "cldf",
        [
            "languages.csv",
            "examples.csv",
            "forms.csv",
            "parameters.csv",
            "ExampleSlices",
            "TextTable",
        ],
    )


def test_sentences_with_lexicon_both_slices(data, tmp_path, monkeypatch):
    result = run_flextext(tmp_path, monkeypatch, data, tmp_path, config="config1")
    assert result.exit_code == 0
    check_cldf(tmp_path)
    check_filelist(
        tmp_path,
        [
            "wordforms.csv",
            "sentences.csv",
            "sentence_slices.csv",
            "texts.csv",
            "morphemes.csv",
            "senses.csv",
            "cldf",
            "form_slices.csv",
        ],
    )
    check_filelist(
        tmp_path / "cldf",
        [
            "MorphsetTable",
            "FormSlices",
            "examples.csv",
            "MorphTable",
            "forms.csv",
            "parameters.csv",
            "ExampleSlices",
            "languages.csv",
            "TextTable",
        ],
    )


def test_sentences_with_lexicon_no_example_slices(data, tmp_path, monkeypatch):
    result = run_flextext(tmp_path, monkeypatch, data, tmp_path, config="config2")
    assert result.exit_code == 0
    check_cldf(tmp_path)
    check_filelist(
        tmp_path / "cldf",
        [
            "MorphsetTable",
            "examples.csv",
            "FormSlices",
            "languages.csv",
            "MorphTable",
            "forms.csv",
            "TextTable",
            "parameters.csv",
        ],
    )


def test_sentences_with_lexicon_no_form_slices(data, tmp_path, monkeypatch):
    result = run_flextext(tmp_path, monkeypatch, data, tmp_path, "config3")
    assert result.exit_code == 0
    check_cldf(tmp_path)
    check_filelist(
        tmp_path / "cldf",
        [
            "MorphsetTable",
            "examples.csv",
            "ExampleSlices",
            "MorphTable",
            "languages.csv",
            "forms.csv",
            "TextTable",
            "parameters.csv",
        ],
    )


def test_sentences_with_lexicon_no_slices(data, tmp_path, monkeypatch):
    result = run_flextext(tmp_path, monkeypatch, data, tmp_path, "config4")
    assert result.exit_code == 0
    check_cldf(tmp_path)
    check_filelist(
        tmp_path / "cldf",
        [
            "languages.csv",
            "MorphsetTable",
            "examples.csv",
            "MorphTable",
            "forms.csv",
            "TextTable",
            "parameters.csv",
        ],
    )


def test_lift(data, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(
        dictionary,
        [str((data / "apalai.lift").resolve()), f"--output", tmp_path, "--cldf"],
    )
    assert result.exit_code == 0
    assert Path(tmp_path / "senses.csv").is_file()
    assert Path(tmp_path / "morphs.csv").is_file()
    assert Path(tmp_path / "morphemes.csv").is_file()
    md_path = Path(tmp_path / "cldf/Dictionary-metadata.json")
    assert md_path.is_file()
    ds = Dataset.from_metadata(md_path)
    assert ds.validate()
