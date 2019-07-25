library(rvest)             # For webscraping
library(data.table)        # For data structure
library(googlesheets)      # To read from google sheets
library(stringr)           # Regex value extraction
library(feather)           # Storage of files


#### Data for identifying stuff

key_phrases_doc <- gs_title("Phrases used in asylum cases")

key_phrases <- as.data.table(gs_read(key_phrases_doc, ws = "simplified_phrases"))

#### Regex using key phrases

regex_unsuccessful <- paste0(key_phrases[!is.na(unsuccessful), unsuccessful], collapse = "|")

regex_successful <- paste0(key_phrases[!is.na(successful), successful], collapse = "|")

regex_ambiguous <- paste0(key_phrases[!is.na(ambiguous_outcome), ambiguous_outcome], collapse = "|")

regex_country <- paste0(
  "(?<=",
  paste0(key_phrases[!is.na(country), country], collapse = " |"),
  " )\\b[A-Za-z]+\\b"
)

regex_dob <- paste0(
  "(?<=",
  paste0(key_phrases[!is.na(dob), dob], collapse = " |"),
  " ).*?\\d{4}"
)

regex_sogi <- "sexual orientation|lgbt|LGBT|lesbian|\\bgay\\b|bisexual|transgender|gender identity"


