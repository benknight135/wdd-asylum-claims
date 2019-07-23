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


#### Test getting relevant information

example_decision <- read_html("https://tribunalsdecisions.service.gov.uk/utiac/pa-13874-2018")

decision_text <- example_decision %>%
  html_node(".decision-inner") %>%
  html_text()

case_id <- example_decision %>%
  html_node("h1") %>%
  html_text()

prom_date <- example_decision %>%
  html_node("li:nth-child(5) time") %>%
  html_text()

prom_date <- as.Date(prom_date, format = "%d %B %Y")

id_dt <- data.table("case_id" = case_id,
                    "promulgation_date" = prom_date)


#### Build dataset

case_outcomes <- data.table("case_id" = character(), 
                            "promulgation_date" = numeric(),
                            "sogi_case" = logical(), 
                            "unsuccessful" = logical(),
                            "successful" = logical(), 
                            "ambiguous" = logical(), 
                            "country" = character(), 
                            "date_of_birth" = character())

case_outcomes <- rbind(case_outcomes, id_dt, fill = TRUE)

case_outcomes[case_id %in% id_dt[, case_id],
              `:=` (
                sogi_case = decision_text %like% regex_sogi,
                unsuccessful = decision_text %like% regex_unsuccessful,
                successful = decision_text %like% regex_successful,
                ambiguous = decision_text %like% regex_ambiguous, 
                country = str_extract(decision_text, regex_country), 
                date_of_birth = str_extract(decision_text, regex_dob)
              )
                ]

#### Scrape multiple

first_page <- read_html("https://tribunalsdecisions.service.gov.uk/utiac?utf8=%E2%9C%93&search%5Bquery%5D=&search%5Breported%5D=all&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=0&search%5Bjudge%5D=&search%5Bclaimant%5D=")

# Vector of links to click

case_links <- first_page %>%
  html_nodes("td:nth-child(1) a") %>% 
  html_attr('href')

# Second page onward has page=2 etc, so replicable pattern
# NB - the below takes several minutes - recommend using the case_links.feather file that exists

# for (page_num in 2:933) {
#   
#   # Link for each new page
#   page <- read_html(paste0("https://tribunalsdecisions.service.gov.uk/utiac?page=", 
#                            page_num, 
#                            "&search%5Bclaimant%5D=&search%5Bcountry%5D=&search%5Bcountry_guideline%5D=&search%5Bjudge%5D=&search%5Bquery%5D=&search%5Breported%5D=all&utf8=%E2%9C%93"))
#   
#   # Get links of cases from page
#   new_links <- page %>%
#     html_nodes(".unreported a") %>% 
#     html_attr('href')
#   
#   
#   case_links <- c(case_links, new_links)
# }
# 
# case_links_table <- as.data.table(case_links)
# 
# feather::write_feather(case_links_table, "case_links.feather")

case_links <- as.data.table(read_feather("case_links.feather"))


