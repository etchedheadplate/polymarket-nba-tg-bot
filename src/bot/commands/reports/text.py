from enum import StrEnum


class ReportName(StrEnum):
    PRICE_WINDOWS = "price_windows"
    QUOTE_SERIES = "quote_series"


class ReportText:
    BUTTON_LABELS = {
        ReportName.PRICE_WINDOWS: "Price Windows",
        ReportName.QUOTE_SERIES: "Quote Series",
    }
