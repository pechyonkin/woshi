"""
Find out the number of ridings where the combined votes of the CPC (Conservative Party of Canada) and PPC (People’s
Party of Canada) exceeded that riding’s winner’s vote total, where the eventual winner was neither of these two parties.
"""
import re
from dataclasses import dataclass, fields
from typing import List
from urllib.request import urlopen

from bs4 import BeautifulSoup, Tag
from urllib3 import HTTPResponse

LINK = "https://en.wikipedia.org/wiki/Results_of_the_2019_Canadian_federal_election"
NROWS_HEADER = 5


PARTIES = frozenset(
    {
        "Lib",
        "Con",
        "NDP",
        "BQ",
        "Grn",
        "PPC",
        "Ind",
        "Other",
    }
)


@dataclass
class VotesByParty:
    LIB: int = 0
    CON: int = 0
    NDP: int = 0
    BQ: int = 0
    GREEN: int = 0
    PPC: int = 0
    IND: int = 0
    OTHER: int = 0

    @classmethod
    def field_names(cls):
        return ["votes_" + field.name.lower() for field in fields(cls)]


@dataclass
class ParsedRow:
    riding: str
    province: str
    winning_party: str
    winning_votes: int
    winning_share: float
    winning_margin_num: int
    winning_margin_percent: float
    turnout: float
    votes_total: int
    votes: VotesByParty

    def __repr__(self):
        return f"{self.riding} - {self.province}"

    @classmethod
    def field_names(cls):
        return [field.name for field in fields(cls)]


def parse_riding(row_data: List[Tag]) -> str:
    riding = row_data[0].contents[0].contents[0]
    return riding


def parse_province(row_data: List[Tag]) -> str:
    province = row_data[1].contents[0]
    return province


def parse_winning_party(row_data: List[Tag]) -> str:
    winning_party = row_data[5].contents[0]
    assert winning_party in PARTIES, f"{winning_party} not in {PARTIES}!"
    return winning_party


def parse_votes(votes_tag: Tag) -> int:
    if not votes_tag.contents:  # edge case with empty table cell
        return 0
    votes_str: str = votes_tag.contents[0]
    if votes_str == "–":
        return 0
    num_str = re.sub(r"[^\w\s]", "", votes_str)  # drop punctuation
    num_votes = int(num_str)
    return num_votes


def parse_percent(percent_str: str) -> float:
    percent = float(percent_str[:-1])
    return percent


def parse_row(row: Tag) -> ParsedRow:
    row_datas: List[Tag] = row.find_all("td")
    assert len(row_datas) == 20

    return ParsedRow(
        riding=parse_riding(row_datas),
        province=parse_province(row_datas),
        winning_party=parse_winning_party(row_datas),
        winning_votes=parse_votes(row_datas[6]),
        winning_share=parse_percent(row_datas[7].contents[0]),
        winning_margin_num=parse_votes(row_datas[8]),
        winning_margin_percent=parse_percent(row_datas[9].contents[0]),
        turnout=parse_percent(row_datas[10].contents[0]),
        votes_total=parse_votes(row_datas[19]),
        votes=VotesByParty(
            LIB=parse_votes(row_datas[11]),
            CON=parse_votes(row_datas[12]),
            NDP=parse_votes(row_datas[13]),
            BQ=parse_votes(row_datas[14]),
            GREEN=parse_votes(row_datas[15]),
            PPC=parse_votes(row_datas[16]),
            IND=parse_votes(row_datas[17]),
            OTHER=parse_votes(row_datas[18]),
        ),
    )


def column_names() -> List[str]:
    """Return table column names to be used in Pandas dataframe."""
    return ParsedRow.field_names()[:-1] + VotesByParty.field_names()


def get_page():
    html: HTTPResponse = urlopen(LINK)
    soup = BeautifulSoup(html, "html.parser")
    tables: List[Tag] = soup.find_all("table")
    table: Tag = tables[4]
    rows = table.find_all("tr")
    data_rows = rows[NROWS_HEADER:]
    parsed_rows = [parse_row(row) for row in data_rows]
    for i, pr in enumerate(parsed_rows):
        print(i + 1, pr)
    return soup
