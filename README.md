# whatsmapper

Convert Whatsapp to other file formats, starting with HTML you can style
yourself.

![whatsmapp image using NES.css](static/images/whatsmapper-nes.png)

> The excellent NES CSS is available [here][nes-1].

[nes-1]: https://nostalgic-css.github.io/NES.css/

## Whatsapp exports

This proof of concept currently only works with ~2024 exports. It can easily be
extended with more sample data. The coding standards will improve with samples
and usage.

### 2014 and before

> NB. I don't know when this format stopped being the norm for Whatsapp. My
last exports from this era are 2014.

Example message: `12/10/14, 00:59:54: NAME: MSG_DATA`

* I don't know if it could consist of newlines or not.

### 2024

> NB. I don't know when this format started.

Example message: `[9/12/24, 08:54:43] ~ NAME: MSG_DATA`

* I do know this format can consist of new lines.
* If you know the individual, the tilde is omitted.

## Output formats

Whatsapp data is parsed into a dataclass which currently only has a mapping to
HTML but the data class has been written so that it can easily be extended into
other formats if any other make sense.

## Usage

```text
python whatsmap.py
usage: whatsmap [-h] [-t TRANSCRIPT]

utility to map a whatsmap chat transcript to HTML

options:
  -h, --help            show this help message and exit
  -t TRANSCRIPT, --transcript TRANSCRIPT
                        location of the whatsapp transcript file

for more information visit https://github.com/ross-spencer/whatsmapper/
```

## Whatsapp folder structure

An export (with media) should output a zip folder, e.g.

```text
'WhatsApp Chat - Digipres Chat.zip'
```

Extract the zip. It should should have a structure along the lines of:

```text
WhatsApp Chat - Digipres Chat/
├── 00000002-PHOTO-2017-05-24-06-15-02.jpg
├── 00000006-PHOTO-2017-05-29-03-35-35.mp4
└── _chat.txt
```

To convert this to html run:

```text
whatsmap -t "/path/to/WhatsApp Chat - Digipres Chat/_chat.txt"
```

Or:

```text
python3 -m whatsmap.py -t "/path/to/WhatsApp Chat - Digipres Chat/_chat.txt"
```

And to output to a html file, simply add:

```text
 > whatsapp_chat.html
```

Providing a custom filename as required, e.g.

```text
whatsmap -t "/path/to/WhatsApp Chat - Digipres Chat/_chat.txt" > my_whatsapp_chat.html
```

## Developer install

### pip

Setup a virtual environment `venv` and install the local development
requirements as follows:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements/local.txt
```

### tox

#### Run tests (all)

```bash
python -m tox
```

#### Run tests-only

```bash
python -m tox -e py3
```

#### Run linting-only

```bash
python -m tox -e linting
```

### pre-commit

Pre-commit can be used to provide more feedback before committing code. This
reduces reduces the number of commits you might want to make when working on
code, it's also an alternative to running tox manually.

To set up pre-commit, providing `pip install` has been run above:

* `pre-commit install`

This repository contains a default number of pre-commit hooks, but there may
be others suited to different projects. A list of other pre-commit hooks can be
found [here][pre-commit-1].

[pre-commit-1]: https://pre-commit.com/hooks.html

## Packaging

The `justfile` contains helper functions for packaging and release.

Makefile functions can be reviewed by calling `just`  from the root of this
repository:

```just
Available recipes:
    all-checks          # All checks
    clean               # Clean the package directory
    docs                # Generate documentation
    help                # Help
    package-check       # Check the distribution is valid
    package-deps        # Upgrade dependencies for packaging
    package-source      # Package the source code
    package-upload      # Upload package to pypi
    package-upload-test # Upload package to test.pypi
    pre-commit-checks   # Run pre-commit-checks.
    serve-docs          # Serve the documentation
    tar-source          # Package repository as tar for easy distribution
    upgrade             # Upgrade project dependencies
```

> [`just`][just-1] can be installed via cargo which can be installed via rust.
Install rust following the commands [here][rust-1] and then run
`cargo install just`.

[just-1]: https://github.com/casey/just
[rust-1]: https://doc.rust-lang.org/cargo/getting-started/installation.html

### pyproject.toml

Packaging consumes the metadata in `pyproject.toml` which helps to describe
the project on the official [pypi.org][pypi-2] repository. Have a look at the
documentation and comments there to help you create a suitably descriptive
metadata file.

### Local packaging

To create a python wheel for testing locally, or distributing to colleagues
run:

* `just package-source`

A `tar` and `whl` file will be stored in a `dist/` directory. The `whl` file
can be installed as follows:

* `pip install <your-package>.whl`

### Publishing

Publishing for public use can be achieved with:

* `just package-upload-test` or `just package-upload`

`just-package-upload-test` will upload the package to [test.pypi.org][pypi-1]
which provides a way to look at package metadata and documentation and ensure
that it is correct before uploading to the official [pypi.org][pypi-2]
repository using `just package-upload`.

[pypi-1]: https://test.pypi.org
[pypi-2]: https://pypi.org
