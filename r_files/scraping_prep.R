library(rvest)             # For webscraping
library(data.table)        # For data structure
library(googlesheets)      # To read from google sheets
library(stringr)           # Regex value extraction
library(feather)           # Storage of files
library(textreadr)         # Reading .doc files


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

regex_so <- paste0(key_phrases[!is.na(sexual_orientation_case), sexual_orientation_case], collapse = "|")

regex_gi <- paste0(key_phrases[!is.na(gender_identity_case), gender_identity_case], collapse = "|")

regex_sogi_other <- paste0(key_phrases[!is.na(unknown_sogi_case), unknown_sogi_case], collapse = "|")

regex_heard <- "(?<=Heard at )\\b.*?(?=\\s)"


