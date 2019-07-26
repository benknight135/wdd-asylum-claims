source("./r_files/scraping_prep.R")


full_text_of_cases <- data.table("case_id" = character(), 
                                 "full_text" = character())

link_number_start <- 20000
link_number_end <- 25922

case_links <- as.data.table(read_feather("case_links.feather"))
focus_links <- case_links[link_number_start:link_number_end, case_links]

#### Loop through links to pull out information
start <- Sys.time()

for (i in 1:length(focus_links)) {
  
  #### Test getting relevant information

  example_decision <- xml2::read_html(paste0("https://tribunalsdecisions.service.gov.uk", focus_links[i]))
  
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
  
  if (is.na(decision_text)) {

    link_name <- example_decision %>%
      html_nodes(".doc-file") %>%
      html_attr('href')

    decision_text <- link_name %>%
      download() %>%
      read_document() %>%
      paste(collapse = "\n")
  }
  
  id_dt <- data.table("case_id" = case_id, 
                      "promulgation_date" = prom_date)
  
  full_text_of_cases <- rbind(full_text_of_cases, id_dt[, .(case_id, promulgation_date)], fill = TRUE)
  
  full_text_of_cases[case_id %in% id_dt[, case_id],
                     `:=` (
                       full_text = decision_text,
                       no_page_available = is.na(decision_text)
                     )]
}

end <- Sys.time()

end - start

feather::write_feather(full_text_of_cases, "data/case_text_last_6000.feather")


#### Build dataset

length_all_cases <- full_text_of_cases[, .N]

case_outcomes <- data.table("case_id" = full_text_of_cases[, case_id], 
                            "promulgation_date" = full_text_of_cases[, promulgation_date],
                            "heard_at" = character(length_all_cases),
                            "so_case" = logical(length_all_cases), 
                            "gi_case" = logical(length_all_cases), 
                            "other_sogi_case" = logical(length_all_cases), 
                            "unsuccessful" = logical(length_all_cases),
                            "successful" = logical(length_all_cases), 
                            "ambiguous" = logical(length_all_cases), 
                            "country" = character(length_all_cases), 
                            "date_of_birth" = character(length_all_cases))


#### Loop through text to pull out information

full_text_to_loop <- full_text_of_cases[, full_text]
full_cases_to_loop <- full_text_of_cases[, case_id]

start <- Sys.time()

for (i in 1:length_all_cases) {
  
  case_outcomes[case_id %in% full_cases_to_loop[i],
                `:=` (
                  heard_at = str_extract(full_text_to_loop[i], regex_heard),
                  so_case = grepl(regex_so, 
                                    full_text_to_loop[i], ignore.case = TRUE),
                  gi_case = grepl(regex_gi, 
                                    full_text_to_loop[i], ignore.case = TRUE),
                  other_sogi_case = grepl(regex_sogi_other, 
                                    full_text_to_loop[i], ignore.case = TRUE),
                  unsuccessful = grepl(regex_unsuccessful, 
                                       full_text_to_loop[i], ignore.case = TRUE),
                  successful = grepl(regex_successful, 
                                     full_text_to_loop[i], ignore.case = TRUE),
                  ambiguous = grepl(regex_ambiguous, 
                                    full_text_to_loop[i], ignore.case = TRUE), 
                  country = str_extract(full_text_to_loop[i], regex_country), 
                  date_of_birth = str_extract(full_text_to_loop[i], regex_dob)
                )
                ]
}

end <- Sys.time()

end-start


#### Add checks to see if adequate

case_outcomes[, 
              `:=` (
                outcome_known = as.logical(unsuccessful + successful + ambiguous),
                multiple_outcomes = (unsuccessful + successful + ambiguous) > 1
                )]

case_outcomes <- merge(case_outcomes, full_text_of_cases[, .(case_id, no_page_available)], 
                         all.x = T)

cases_to_review <- case_outcomes[outcome_known == 0 & no_page_available == FALSE]

feather::write_feather(case_outcomes, "data/last_6000_outcomes.feather")
# feather::write_feather(full_text_of_cases, "case_text_to_500.feather")

