library(data.table)
library(feather)
library(googlesheets)      # To read from google sheets
library(stringr)           # Regex value extraction

#### Data for identifying stuff

key_phrases_doc <- gs_title("Phrases used in asylum cases")

key_phrases <- as.data.table(gs_read(key_phrases_doc, ws = "simplified_phrases"))


#### Data to explore

cases_text <- as.data.table(read_feather("./data/case_text_last_6000.feather"))


# Remove annoying quirks
cases_text[, full_text := gsub("  ", " ", full_text)]
cases_text[, full_text := gsub("\n", " ", full_text, fixed = TRUE)]

# Reduce to a managebale set to manually review
# Uncomment below to get a smaller set to work with
# smaller_set <- cases_text[1:250]
smaller_set <- copy(cases_text)


#### Basic attempt to get country ----------------------------------------------

regex_country <- paste0(
  "(?<=",
  paste0(key_phrases[!is.na(country), country], collapse = " |"),
  " )\\b[A-Za-z]+\\b"
)


#### Build dataset

length_all_cases <- smaller_set[, .N]

case_outcomes <- data.table("case_id" = smaller_set[, case_id], 
                            "country" = character(length_all_cases))


#### Loop through text to pull out information

full_text_to_loop <- smaller_set[, full_text]
full_cases_to_loop <- smaller_set[, case_id]

for (i in 1:length_all_cases) {
  
  case_outcomes[case_id %in% full_cases_to_loop[i],
                  country := str_extract(full_text_to_loop[i], regex_country)
                ]
}


#### Get countries with multiple words -----------------------------------------


regex_country_2 <- paste0(
  "(?<=",
  paste0(key_phrases[!is.na(country), country], collapse = " |"),
  " )([A-Z][a-z-]*)([\\s|-][A-Z][a-z-]*)*"
)


for (i in 1:length_all_cases) {
  
  case_outcomes[case_id %in% full_cases_to_loop[i],
                country_2 := str_extract(full_text_to_loop[i], regex_country_2)
                ]
}

#### Get countries starting with the -----------------------------------------


regex_country_3 <- paste0(
  "(?<=",
  paste0(key_phrases[!is.na(country), country], collapse = " |"),
  " )(the )*([A-Z][a-z-]*)([\\s|-][A-Z][a-z-]*)*"
)


for (i in 1:length_all_cases) {
  
  case_outcomes[case_id %in% full_cases_to_loop[i],
                country_3 := str_extract(full_text_to_loop[i], regex_country_3)
                ]
}

#### Get countries with of/the/and in them or made of all caps -------------------------


regex_country_4 <- paste0(
  "(?<=",
  paste0(key_phrases[!is.na(country), country], collapse = " |"),
  " )(the )*([A-Z][A-Za-z-]*)+([\\s|-][A-Z][A-Za-z]*)*( of)?( the)?( and)?([\\s|-][A-Z][A-Za-z]*)*"
)


for (i in 1:length_all_cases) {
  
  case_outcomes[case_id %in% full_cases_to_loop[i],
                country_4 := str_extract(full_text_to_loop[i], regex_country_4)
                ]
}



#### Get nationals

regex_national <- "(?<=a )[A-Z][A-Za-z-]*(?= national)"

for (i in 1:length_all_cases) {
  case_outcomes[case_id %in% full_cases_to_loop[i],
                country_5 := ifelse(is.na(country_4), 
                                    str_extract(full_text_to_loop[i], regex_national), 
                                    country_4)
                ]
}


#### Clean trailing 'ands'

case_outcomes[, country_5 := gsub(" and\\b", "", country_5)]

#### Results

# Prop matching initially
case_outcomes[!is.na(country) & !is.na(country_2) & !country_2 %like% " ", .N]/250

# Prop matching ultimately
case_outcomes[!is.na(country_5), .N]/250







