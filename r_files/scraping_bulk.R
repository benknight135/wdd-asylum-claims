source("./r_files/scraping_prep.R")

case_links <- as.data.table(read_feather("case_links.feather"))

first_500_links <- case_links[1:500, case_links]


#### Build dataset

case_outcomes <- data.table("case_id" = character(), 
                            "promulgation_date" = numeric(),
                            "sogi_case" = logical(), 
                            "unsuccessful" = logical(),
                            "successful" = logical(), 
                            "ambiguous" = logical(), 
                            "country" = character(), 
                            "date_of_birth" = character())


full_text_of_cases <- data.table("case_id" = character(), 
                                 "full_text" = character())


#### Loop through links to pull out information

for (i in 1:length(first_500_links)) {
  
#### Test getting relevant information

example_decision <- read_html(paste0("https://tribunalsdecisions.service.gov.uk", first_500_links[i]))

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

case_outcomes <- rbind(case_outcomes, id_dt, fill = TRUE)

case_outcomes[case_id %in% id_dt[, case_id],
              `:=` (
                sogi_case = grepl(regex_sogi, decision_text, ignore.case = TRUE),
                unsuccessful = grepl(regex_unsuccessful, decision_text, ignore.case = TRUE),
                successful = grepl(regex_successful, decision_text, ignore.case = TRUE),
                ambiguous = grepl(regex_ambiguous, decision_text, ignore.case = TRUE), 
                country = str_extract(decision_text, regex_country), 
                date_of_birth = str_extract(decision_text, regex_dob)
              )
              ]

full_text_of_cases <- rbind(full_text_of_cases, id_dt[, .(case_id)], fill = TRUE)

full_text_of_cases[case_id %in% id_dt[, case_id],
                   `:=` (
                   full_text = decision_text,
                   no_page_available = is.na(decision_text)
                   )]

}


#### Add checks to see if adequate

case_outcomes[, 
              `:=` (
                outcome_known = as.logical(unsuccessful + successful + ambiguous),
                multiple_outcomes = (unsuccessful + successful + ambiguous) > 1
                )]

case_outcomes <- merge(case_outcomes, full_text_of_cases[, .(case_id, no_page_available)], 
                         all.x = T)

cases_to_review <- case_outcomes[outcome_known == 0 & no_page_available == FALSE]

feather::write_feather(case_outcomes, "cases_to_500_outcomes.feather")
feather::write_feather(full_text_of_cases, "case_text_to_500.feather")

