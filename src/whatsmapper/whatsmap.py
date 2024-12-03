"""Whatsmapper application to convert a whatsapp chat to simple HTML.
"""

# pylint: disable=C0103, R0903, R0914, W0511, R0915, R0912

import argparse
import asyncio
import logging
import pathlib
import re
import sys
import time
from dataclasses import dataclass, field
from typing import Final, Union

# Set up logging.
logging.basicConfig(
    format="%(asctime)-15s %(levelname)s :: %(filename)s:%(lineno)s:%(funcName)s() :: %(message)s",  # noqa: E501
    datefmt="%Y-%m-%d %H:%M:%S",
    level="INFO",
    handlers=[
        logging.StreamHandler(),
    ],
)

# Format logs using UTC time.
logging.Formatter.converter = time.gmtime


logger = logging.getLogger(__name__)

TITLE_TEMPLATE = "{{ EXPORT_TITLE }}"

html_header: Final[
    str
] = """
<!DOCTYPE html>
<html>
   <head>
      <title>{{ EXPORT_TITLE }}</title>
      <link href="https://fonts.googleapis.com/css?family=Press+Start+2P" rel="stylesheet">
      <link href="https://unpkg.com/nes.css/css/nes.css" rel="stylesheet" />
      <link href="https://cdnjs.cloudflare.com/ajax/libs/skeleton/2.0.4/skeleton.css" rel="stylesheet" />
      <link href="custom.css" rel="stylesheet" />
      <style>
            html, body, pre, code, kbd, samp {
                font-family: "Press Start 2P";
                background-color: #212529;
            }
            body { margin-top: 10rem; }
            div.bottom-margin { margin-top: 10rem; }
      </style>

      <meta charset="UTF-8">
      <meta name="description" content="Whatsmapper Whatsapp export formatter by Ross Spencer (@beet_keeper)">
      <meta name="keywords" content="Digital Preservation, HTML, Migration">
      <meta name="author" content="Ross Spencer">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">

   </head>
   <body>
    <div class="container">
        <div class="nes-container is-rounded is-dark">
         <section class="message-list">
            <h1>{{ EXPORT_TITLE }}</h1>
"""

html_footer: Final[
    str
] = """
            </section>
        </div></div>
    <div class=\"bottom-margin\"><br></div>
</body>
"""

file_image: Final[
    str
] = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAAB7CAMAAAC8V3VSAAAAY1BMVEX///8AAABbW1tsbGwxMTF+fn6goKDj4+PY2Nitra01NTWnp6c9PT05OTnf39+Tk5P29vbu7u5JSUm9vb2amposLCwMDAxRUVGKiorDw8PKyspkZGRxcXEVFRUmJibS0tIcHBzyOjX6AAADQ0lEQVRoge2a6ZKrIBCFwWg0u0vW0cT7/k95k0xYhAYa0JqpKc+vjDLnC0QaWpoQSbdjezpTL92zkiCVZ37WXBXKvrwG2lOaYvpQPIL9Ka3dhCbC/qlkYn9KF3b/faw/pZkVcBINz5cFUl09IFwt/gfear3CPXJvrYZ9WBobVuJboOfMSxtllFamhnwCbHzsdQBtDA0xo4gC0C+wXf+5e/IaHwlwE4TC1s5zgMQ/5oUg5EC7zHIPBdiTLw44A8Nw+b5V+/pLACkSPPR26fcdZzixAaQ5sZ4GQI6coA3FOAAiVqt2GgDpOKGbBkBaThhO2dEARITXQeAbD1BuOUEOfOMBSJVyghT4RgSQ/M4JIvAFA9j07aVrUljil4MBLAINFpqeA+6sZ8EA9m2H670IfI8qElCyvcLwsgh8nx1fMIDFYXWpFIFvGwlgTmqIVgJfOCBnPuq+TgS+JApAFsxHCW/DwBcBEFvO0214RwS+JgYgjQVND30lLcgJu95GAciaynrUSdu2yUvsCXs+SVGA3JnRRQJI4SLEAki1mxgg7/4nAtjz3zEAz3HaJNMCnir7zbVrL2/VL91HBmhKZsAMmAEMsPvJHhSHDKkDkIG7AUtT/IKkp/FOQG92g6T1wQnwfMmpvUpxAhZmM0jq3ssNWJnNIGmvo5yAcm1207XV3oK4n6KyM/up6vS3LHOomAEzYAaMA8ibJUoNeOjgBuDj9fkWAijMhjoB6IMT4LVkAqcfTkBrttMFHG44AfoBh0XAj+AElCeznyrobMD9FFXGzFFVC53OYCZalaMEH/78hpk8A2YADrCeATGAslk5BC+WWACqFsJ8ku8E5GZXWfApOAaArHVRTy7xAOSSCRwgIwHIRF9LX9GA6h8KsIfMUQBS1GZbptT4G6Mm2r5wyVIq8Rtm8gz4I4CU7KYF7NgH/9oWh2r2xYOrc+xi0T4Lry+yS9iyXMy7Qsoqnl0U4TVeVvHlioRXqdnE868DCa+zs0gcDpbDP1OfSkGTqkYcbx7fV8qgWkeTEmkl3H2YPkm9l/h6Gl1vCkvKnichDLLzwiPtxilV9hsRVcuggGkbXHcN2Rse99ux3XpWjqs6bxdHuaSJ/Ads3C/5Z6OwGwAAAABJRU5ErkJggg=="


video_image: Final[
    str
] = "data:image/png;base64,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"


class Attachment:
    file_path = ""
    extension = ""

    def attachment_as_href(self) -> str:
        """Return a html snippet for the attachment."""
        if self.extension in ("mp4",):
            logger.info("todo: need to process video effectively")
            return f"""
                <video controls autoplay>
                <source src="{self.file_path}" type="video/mp4">
                </video>
            """

        if self.extension in ("jpg", "png"):
            return f"""
                <div class=\"nes-container is-rounded is-dark\">
                        <img src='{self.file_path}' width=\"800px\" />\n
                </div>
                    """
        return f"""
            <div class=\"nes-container is-rounded is-dark\">
            <a href='{self.file_path}'><img src='{file_image}' /></a>\n
            </div>
        """


@dataclass(slots=True)
class ChatEntry:
    chat_date: str = ""
    individual: str = ""
    text: str = ""
    primary: str = ""

    def chat_as_html(self) -> str:
        """Return a html snippet for the entry."""
        person = self.individual
        date = self.chat_date
        text = self.text
        if self.primary == self.individual:
            return f"""<section class=\"message -right\">
\t<div class=\"nes-balloon from-right is-dark\">\n\t\t<p>{date}: {person}</p>\n
\t\t<p>{text}</p></div>\n\t<i class=\"nes-bcrikko\"></i>
</section>\n"""
        return f"""<section class=\"message -left\">
\t<i class=\"nes-bcrikko\"></i>\n\t<div class=\"nes-balloon from-left is-dark\">
\t\t<p>{date}: {person}</p>\n\t\t<p>{text}</p></div>\n</section>\n"""


@dataclass
class TranscriptData:
    individuals: list = field(default_factory=lambda: [])
    transcript: list[ChatEntry] = field(default_factory=lambda: [])
    extensions: list = field(default_factory=lambda: [])


async def _strip_chars(input_: str) -> str:
    """Replace poorly encoded characters with alternatives.

    NB. be careful with early encoding here. <> for example are needed
    for file attachments to be matched correctly.
    """
    input_ = input_.replace("<", "&lt;").replace(">", "&gt;")
    input_ = input_.replace("~", "", 1)
    input_ = (
        input_.strip().replace("\u200E", "").replace("\u202A", "").replace("\u202C", "")
    )
    input_ = input_.encode().replace(b"\xc2\xa0", b"\x20").replace(b"\xe2\x80\xaF", b"")
    input_ = input_.replace(b"\xE2\x80\x99", b"\x27")
    return input_.decode()


async def data_to_html(transcript_data: TranscriptData) -> str:
    """Output the chat data as HTML."""
    output = ""
    for chat in transcript_data.transcript:
        logger.info(chat)
        if not isinstance(chat, Attachment):
            output = f"{output}{chat.chat_as_html()}"
            continue
        output = f"{output}{chat.attachment_as_href()}"
    return output


def whatsapp_to_stats(transcript_data: TranscriptData) -> str:
    """Output the chat data as HTML."""
    attachments = 0
    chats = 0
    for chat in transcript_data.transcript:
        if isinstance(chat, Attachment):
            attachments += 1
            continue
        chats += 1

    return (
        "<ul>\n"
        f"   <li>attachments: {attachments}</li>\n"
        f"   <li>individuals: {len(transcript_data.individuals)}</li>\n"
        f"   <li>entries: {chats}</li>\n"
        f"   <li>file extensions: {len(transcript_data.extensions)}</li>\n"
        "</ul>\n"
    )


async def whatsmap_to_data(transcript: pathlib.Path) -> TranscriptData:
    """Map a chat transcript to internal data structures."""
    transcript_data = TranscriptData()
    parent_folder = transcript.parents[0]
    attachment: Final[str] = "attached:"
    http_link: Final[str] = "http"
    https_link: Final[str] = "https"
    individuals = []
    file_extensions = []
    chat = ""
    with transcript.open() as chat_log:
        chat = chat_log.read()
    chat_entry = None
    for line in chat.splitlines():
        line = await _strip_chars(line)
        if line == "":
            # TODO: HTML does not have to be an output of this script,
            # is there another way to signal a line break here?
            chat_entry.text = f"{chat_entry.text}<br>"
            continue
        logger.info(line)
        chat_date = ""
        if not chat_entry:
            chat_entry = ChatEntry()
            chat_date = f"{line.split(']', 1)[0].replace(']', '')}]"
        elif chat_entry and line.startswith("["):
            transcript_data.transcript.append(chat_entry)
            chat_entry = ChatEntry()
            chat_date = ""
            individual = ""
            chat_text = ""
            chat_date = f"{line.split(']', 1)[0].replace(']', '')}]"
        # Check for attachment.
        if attachment in line:
            # Generate entry for the attachment.
            if line.startswith("["):
                individual = line.split("] ")[1].split(": ", 1)[0]
                if individual not in individuals:
                    individuals.append(individual)
            chat_text = "".join(line.split(individual)[1:])
            chat_entry.chat_date = chat_date.strip()
            chat_entry.individual = individual.strip()
            chat_entry.text = chat_text.replace(":", "", 1).strip()
            transcript_data.transcript.append(chat_entry)
            chat_entry = None
            # process the attachment.
            file_attachment = Attachment()
            logger.info("handling attachment: %s", line)
            file_name = line.split(attachment, 1)[1].strip().replace("&gt;", "")
            try:
                ext = file_name.split(".")[1]
                file_attachment.extension = ext
                file_extensions.append(ext)
            except IndexError:
                logger.info("cannot parse extension: %s", line)
            file_path = parent_folder / pathlib.Path(file_name)
            if not file_path.exists():
                logger.warning("attachment path: '%s', doesn't exist", file_path)
                continue
            file_attachment.file_path = str(file_path)
            transcript_data.transcript.append(file_attachment)
            continue
        # Otherwise process the chat entry.
        if http_link in line or https_link in line:
            # TODO: regex can probably be combined into one, but this is
            # just a quick and dirty PoC.
            http_links = re.findall(r"(http?://\S+)", line)
            https_links = re.findall(r"(https?://\S+)", line)
            for http_link in http_links:
                line = line.replace(http_link, f'<a href="{http_link}">{http_link}</a>')
            for http_link in https_links:
                line = line.replace(http_link, f'<a href="{http_link}">{http_link}</a>')
        try:
            if line.startswith("["):
                individual = line.replace(f"{chat_date}", "").strip().split(":", 1)[0]
                date_name = f"{chat_date}\x20{individual}:"
                chat_text = line.replace(date_name, "").strip()
                if individual not in individuals:
                    individuals.append(individual)
            else:
                chat_text = line
        except IndexError:
            chat_text = line
        if not chat_entry.chat_date:
            # Not part of a multi-line entry.
            chat_entry.chat_date = chat_date.strip()
        chat_entry.individual = individual.strip()
        # TODO: HTML does not have to be an output of this script,
        # is there another way to signal a line break here?
        chat_entry.text = f"{chat_entry.text}<br>{chat_text.strip()}".replace(
            ":", "", 1
        )  # Colon is still present after separating the string from the
        # metadata. We replace it here. TODO: write test for.
        chat_entry.primary = None
    logger.info("individuals: %s", list(set(individuals)))
    transcript_data.individuals = list(set(individuals))
    transcript_data.extensions = list(set(file_extensions))
    return transcript_data


def check_path(transcript: str) -> Union[pathlib.Path, bool]:
    """Make sure the chat transcript path exists."""
    path = pathlib.Path(transcript)
    if not path.exists():
        return False
    return path


async def whatsmap() -> None:
    """Primary runner."""
    parser = argparse.ArgumentParser(
        prog="whatsmap",
        description="utility to map a whatsmap chat transcript to HTML",
        epilog="for more information visit https://github.com/ross-spencer/whatsmapper",
    )
    parser.add_argument(
        "-t",
        "--transcript",
        help="location of the whatsapp transcript file",
        required=False,
    )
    parser.add_argument(
        "-e",
        "--export_title",
        help="export title",
        default="Whatsmapper Demo",
    )
    args = parser.parse_args()
    if len(sys.argv) <= 1:
        parser.print_help(sys.stderr)
        return
    if args.transcript:
        transcript_path = check_path(args.transcript)
        if not transcript_path:
            logger.info("transcript path '%s' does not exist", args.transcript)
            sys.exit(1)
        data = await whatsmap_to_data(transcript_path)
        stats = whatsapp_to_stats(data)
        processed = await data_to_html(data)
        output = f"{html_header.replace(TITLE_TEMPLATE, args.export_title)}{stats}{processed}{html_footer}"
        print(output)


def main():
    """Primary entry point for this script."""
    asyncio.run(whatsmap())


if __name__ == "__main__":
    main()
