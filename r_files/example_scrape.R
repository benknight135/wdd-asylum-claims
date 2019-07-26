source("./r_files/scraping_prep.R")

#### Test getting relevant information

example_decision <- read_html("https://tribunalsdecisions.service.gov.uk/utiac/2019-ukut-216")

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

full_text_of_cases <- data.table("case_id" = character(), 
                            "full_text" = character())

full_text_of_cases <- rbind(full_text_of_cases, id_dt[, .(case_id)], fill = TRUE)

full_text_of_cases[case_id %in% id_dt[, case_id],
                   full_text := decision_text]


# All in one vs no text vs separate text
## 0.580 secs vs 0.266 secs vs 0.332 secs
## 14.3kb vs 3.1kb vs 3.1kb/12.6kb