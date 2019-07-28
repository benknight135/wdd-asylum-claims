library(rvest)             # For webscraping
library(data.table)        # For data structure
library(stringr)           # Regex value extraction
library(feather)           # Storage of files
library(textreadr)         # Reading .doc files


#### Scrape an example page

#### Test getting relevant information

example_decision <- xml2::read_html("https://tribunalsdecisions.service.gov.uk/utiac/pa-05879-2018")

decision_text <- example_decision %>%
  html_node(".decision-inner") %>%
  html_text()

#### Scrape an example page that uses a .doc

example_decision_with_doc <- xml2::read_html("https://tribunalsdecisions.service.gov.uk/utiac/2019-ukut-197")

  link_name <- example_decision_with_doc %>%
    html_nodes(".doc-file") %>%
    html_attr('href')
  
  decision_text <- link_name %>%
    download() %>%
    read_document() %>%
    paste(collapse = "\n")
  
  decision_text <- gsub("\n", " ", decision_text)

#### Create vector of links for scraper to use

# First page done individually as different address style

page <- xml2::read_html("https://tribunalsdecisions.service.gov.uk/utiac?&page=250")

case_links <- page %>%
  html_nodes("td:nth-child(1) a") %>% 
  html_attr('href')

# Loop to identify all links
# NB - the below takes several minutes and is commented to avoid running unnecessarily

# for (page_num in 1:933) {
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

# Create en empty data table to populate

full_text_of_cases <- data.table("case_id" = character(), 
                                 "full_text" = character())

#### Loop through links to pull out information

for (i in 1:length(case_links)) {
  
  example_decision <- xml2::read_html(paste0("https://tribunalsdecisions.service.gov.uk", case_links[i]))
  
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
    
    decision_text <- gsub("\n", " ", decision_text)
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

# Identify relevant cases

regex_sogi <- "sexual orientation|lgbt|lesbian|\\bgay\\b|bisexual|transgender|gender identity|homosexual"

full_text_of_cases[, sogi_case := grepl(regex_sogi, full_text, ignore.case = TRUE, perl = TRUE)]


# Identify relevant cases

full_text_of_cases[sogi_case == TRUE, .N]
