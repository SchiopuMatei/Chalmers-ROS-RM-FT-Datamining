library(ggplot2)  
library(extrafont)  
require(reshape2) 
library(dplyr)  
library(tidyr)  
library(forcats)  
library(likert) 
library(stringr)  
library(stringi)  
library(R.utils)  
setwd('.')  
loadfonts() 
options(max.print=100)  
fontSize = 10 
cv <- function(data, percentage){ 
  sd <- sd(data, na.rm=TRUE)  
  mean <- mean(data, na.rm=TRUE)  
  result <- sd/mean 
  if(percentage) {  
    result <- result * 100  
  } 
  return(result)  
} 
repos = read.csv(here("dataset", "repos_dataset_selected.csv"), na.strings=c("","NA"))  
survey_responses = read.csv(here("online_questionnaire", "online_questionnaire_responses_raw.csv"), na.strings=c("","NA"))  
guidelines = read.csv(here("data_analysis", "guidelines_definitions.csv"), na.strings=c("","NA")) 
survey_responses_coded = read.csv(here("online_questionnaire", "online_questionnaire_responses.csv"), na.strings=c("","NA"))  
survey_responses_coded = read.csv(here("data_analysis", "repos_sa_analysis.csv"), na.strings=c("","NA"))  
# We rename the columns of Repos_SA_ANALYSIS to more meaningful names 
repos_sa_analysis = repos_sa_analysis %>%   
  rename( 
    Nodes = SA.View.Elements, 
    Topics = X, 
    Messages = X.1, 
    Services = X.2, 
    Parameters = X.3, 
    Packages = X.4, 
    ExternalSystemElements = X.5, 
    ROSLibraries = X.6, 
    OtherSoftwareComponents = X.7 
  ) 
# We remove the all rows of Repos_SA_ANALYSIS without a repo ID because they does not contain any specific information (e.g., they contain only partial counts we checked in GDrive)  
# repos_sa_analysis = repos_sa_analysis[-1,]  
repos_sa_analysis = repos_sa_analysis[!is.na(repos_sa_analysis$ID),]  
# Reshape the part of dataframe related to the View elements  
repos_sa_analysis_long = repos_sa_analysis %>% gather(ViewElements, value, Nodes, Topics, Messages, Services, Parameters, Packages, ExternalSystemElements, ROSLibraries, OtherSoftwareComponents)  
repos_sa_analysis_long = repos_sa_analysis_long[repos_sa_analysis_long$value == TRUE,] %>% select(-value) 
repos_sa_analysis_long$ViewElements = gsub("OtherSoftwareComponents", "Other Software\nComponents", repos_sa_analysis_long$ViewElements)  
repos_sa_analysis_long$ViewElements = gsub("ExternalSystemElements", "External System\nElements", repos_sa_analysis_long$ViewElements)  
repos_sa_analysis_long$ViewElements = gsub("ROSLibraries", "ROS Libraries", repos_sa_analysis_long$ViewElements)  
# We separate the guidelines column into multiple columns and then transform the df into the long format  
guidelines = guidelines %>%   
  rename( 
    quality_attributes = Quality.requirements..comma.separated. 
  ) 
quality_attributes = gsub(",", ", ", guidelines$quality_attributes) 
quality_attributes = gsub("Compatibility", "COMP", quality_attributes)  
quality_attributes = gsub("Performance", "PERF", quality_attributes)  
quality_attributes = gsub("Reliability", "REL", quality_attributes) 
quality_attributes = gsub("Maintainability", "MAINT", quality_attributes) 
quality_attributes = gsub("Portability", "PORT", quality_attributes)  
quality_attributes = gsub("Usability", "USAB", quality_attributes)  
quality_attributes = gsub("Energy", "EN", quality_attributes) 
quality_attributes = gsub("Safety", "SAFE", quality_attributes) 
quality_attributes = gsub("Security", "SEC", quality_attributes)  
guidelines = guidelines %>% 
  separate(quality_attributes, c("quality_attributes_1", "quality_attributes_2", "quality_attributes_3"), ",") %>% mutate(quality_attributes = quality_attributes)  
# We do the same for quality attributes in the survey responses 
# We separate the guidelines column into multiple columns and then transform the df into the long format  
survey_responses_coded = survey_responses_coded %>% 
  separate(Quality_attributes_coded, c("quality_attributes_1", "quality_attributes_2", "quality_attributes_3"), ",")  
# We also separate the No_documentation_codes column into separate columns  
survey_responses_coded = survey_responses_coded %>% 
  separate(No_documentation_codes, c("no_documentation_codes_1", "no_documentation_codes_2", "no_documentation_codes_3"), ",")  
# Transform the groups columns related to the same feature into one column (the df becomes in the long format now)  
repos_long_system_type <- repos %>% gather(Column_name, System.type, System.type.1, System.type.2, System.type.3) %>% select(-Column_name)  
repos_long_capabilities <- repos %>% gather(Column_name, Capability, Capability.1, Capability.2, Capability.3) %>% select(-Column_name) 
guidelines_long <- guidelines %>% gather(Column_name, quality_attributes, quality_attributes_1, quality_attributes_2, quality_attributes_3) %>% select(-Column_name)  
survey_responses_coded_long <- survey_responses_coded %>% gather(Column_name, quality_attributes, quality_attributes_1, quality_attributes_2, quality_attributes_3) %>% select(-Column_name)  
survey_responses_coded_long <- survey_responses_coded %>% gather(Column_name, no_documentation_codes, no_documentation_codes_1, no_documentation_codes_2, no_documentation_codes_3) %>% select(-Column_name)  
# Rename values so that they are more meaningful in the plots 
repos_long_system_type = repos_long_system_type %>% mutate(System.type = fct_recode(System.type, "Generic" = "GEN", "Manipulation" = "Manu", "Service" = "Service", "Self-driving\nvehicle" = "Selfdriving_car")) 
repos = repos %>% mutate(Scope = fct_recode(Scope, "Full system" = "FULL_SYSTEM", "Subsystem" = "SUBSYSTEM")) 
repos_long_capabilities = repos_long_capabilities %>% mutate(Capability = fct_recode(Capability, "Infrastructure" = "Infrastructural", "Dev. support" = "DevSupport", "SLAM" = "Slam")) %>% subset(Capability != "FULL")  
repos = repos %>% mutate(SA.documented = fct_recode(SA.documented, "No" = "NO", "Partially" = "PARTIALLY", "Yes" = "YES"))  
# rename the names of the columns with the guidelines so that we show only Gx 
# Assumption: all columns are within the start and end indexes  
start_index = 5 
end_index = 43  
colname <- names(survey_responses)  
desired.order <- ordered(c("Absolutely NOT useful", "NOT useful","Don't know", "Useful", "Absolutely useful"))  
for (i in c(start_index:end_index)) { 
    colname[i] = paste("G", i-start_index + 1, sep="")  
    survey_responses[[i]] = as.ordered(survey_responses[[i]]) 
    survey_responses[[i]] = ordered(survey_responses[[i]], levels=desired.order)  
} 
colnames(survey_responses) <- colname 
plot = function(df, var_name, file_name, highlighted_var, max_scale, width, height) { 
    
  df_local = df %>% drop_na(var_name) 
  df_local = df_local %>% mutate(highlight_flag = ifelse(df_local[[var_name]] == highlighted_var, T, F))  
    
  ggplot(data=df_local, aes(x=fct_infreq(factor(df_local[[var_name]])))) +  
    geom_bar(width = 0.7, aes(fill = highlight_flag)) + 
    scale_fill_manual(values = c('#595959', 'firebrick2')) +  
    xlab("") + ylab("") + 
    ylim(0, max_scale) +  
    geom_text(aes( label = ..count.., 
                   y= ..count.. ), stat= "count", vjust = -.3, position = position_dodge(1), size=3) +  
    theme_bw() +  
    theme(legend.position="none") +   
    theme(axis.text.x = element_text(angle = 60, hjust = 1)) +  
    theme(axis.text=element_text(size=fontSize), axis.title=element_text(size=fontSize)) +  
    theme(plot.margin=grid::unit(c(1, 1, 1, -4), "mm")) 
    
  ggsave(file_name, scale = 0.55, width = width, height = height, unit = "cm")  
} 
plot_stacked = function(df, var1_name, var2_name, file_name, max_scale, width, height) {  
    
  df_local = df 
    
  ggplot(repos_sa_analysis, aes(df_local[[var1_name]], fill = df_local[[var2_name]])) + geom_bar() +  
    xlab("") + ylab("") + 
    ylim(0, max_scale) +  
    annotate("text", x = 1, y=25, label = "23") + 
    annotate("text", x = 2, y=27, label = "25") + 
    annotate("text", x = 3, y=22, label = "20") + 
    theme_bw() +  
    theme(legend.direction="vertical", legend.title = element_blank(), legend.text=element_text(size=8), legend.position = "right", legend.background = element_rect(fill=alpha('blue', 0))) +  
    theme(axis.text.x = element_text(angle = 60, hjust = 1)) +  
    theme(axis.text=element_text(size=fontSize), axis.title=element_text(size=fontSize)) +  
    # geom_text(aes( label = ..count.., 
    #                y= ..count.. ), stat= "count", position = position_stack(vjust = 0.5), size=2) + 
    theme(plot.margin=grid::unit(c(1, 1, 1, -4), "mm")) 
    
  ggsave(file_name, scale = 0.55, width = width, height = height, unit = "cm")  
} 
plot_responses = function(file_name, data) {  
    likert.bar.plot(likert(data), type="bar", group.order=names(data), legend="", legend.position='bottom', plot.percents=FALSE, include.center=TRUE, centered=TRUE, plot.percent.low = FALSE, plot.percent.high = FALSE, plot.percent.neutral = FALSE) + 
    scale_y_continuous(labels = likert:::abs_formatter, lim = c(-100, 100), 
                       breaks = seq(-100, 100, 20)) + 
    theme_bw() +  
    labs(y = "") +  
    theme(plot.margin=grid::unit(c(1, 0, 1, 1), "mm")) +  
    theme(legend.direction="vertical", legend.text=element_text(size=8), legend.position = c(0.2, 0.33), legend.background = element_rect(fill=alpha('blue', 0))) + 
    guides(fill=guide_legend(nrow=5,byrow=TRUE, reverse = TRUE, keyheight=unit(0.1,"cm"))) +  
    theme(axis.text=element_text(size=fontSize), axis.title=element_text(size=fontSize))  
      
  ggsave(file_name, scale = 1.5, width = 8, unit = "cm")  
} 
add_zero = function(x) {  
  if(!is.na(x) && str_detect(as.character(x), "[A-Z][1-9]$")) { 
    splitted = unlist(strsplit(x, ""))  
    splitted <- unlist(insert(splitted, ats=2, values='0')) 
    x = str_c(splitted, collapse='')    
  } 
  return(x) 
} 
gen_guidelines_table = function() { 
  guidelines$Final.ID = as.character(guidelines$Final.ID) 
  guidelines$Final.ID = sapply(guidelines$Final.ID, add_zero)   
  order <- c('C', 'N', 'B', 'I', 'H', 'S', 'P') 
  to_print = '' 
  for(i in order) { 
    current_group = guidelines %>% subset(Resolved == i)  
    current_group = current_group %>% arrange_at("Final.ID")  
    to_print = paste(current_group$Final.ID, current_group$Guideline, current_group$quality_attributes, current_group$Provenance, current_group$Occurrences.in.repos, '\\\\ \n', sep=" & ") 
    to_print = stri_replace_last_fixed(to_print, '&', '') 
    cat(to_print) 
  } 
} 
plot(repos_long_system_type, 'System.type', './output/SystemType.pdf', 'Generic', 100, 15, 13)  
plot(repos, 'Scope', './output/Scope.pdf', '', 250, 4, 13)  
plot(repos_long_capabilities, 'Capability', './output/Capabilities.pdf', '', 55, 15, 13)  
plot(repos, 'SA.documented', './output/SA_documented.pdf', '', 250, 6, 13)  
plot(guidelines_long, 'quality_attributes', './output/quality_attribute_mentioned.pdf', '', 25, 15, 13) 
plot(survey_responses_coded_long, 'quality_attributes', './output/quality_attribute_considered.pdf', '', 55, 15, 13)  
plot(survey_responses_coded_long, 'no_documentation_codes', './output/no_documentation_codes.pdf', '', 10, 15, 13)  
data = survey_responses %>% select(matches("G[1-9]+"))  
# Let's rename the guidelines according to the final IDs  
pairs = guidelines %>% subset(Usefulness != "-") %>% select(ID, Final.ID) 
renamer = function(old_names) { 
  result = c()  
  for (e in old_names) {  
    entry = pairs %>% filter(ID == e) 
    result = c(result, entry$Final.ID)  
  } 
  return(result)  
} 
data <- data %>% rename_with(renamer) 
# Add the clusters of guidelines  
col_order <- c('C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'B1', 'B2', 'B3', 'B4', 'I1', 'I2', 'I3', 'I4', 'I5', 'H1', 'H2', 'H3', 'H4', 'H5', 'S1', 'S2', 'S3', 'S4', 'P1', 'P2', 'P3') 
data <- data[, col_order] 
data[is.na(data)] = "Don't know"  
# gen_guidelines_table()  
plot(repos_sa_analysis, 'SA.View.Depiction', './output/SA_View_Depiction.pdf', '', max(summary(repos_sa_analysis$SA.View.Depiction)) + 5, 7, 13)  
plot(repos_sa_analysis, 'SA.View.Type', './output/SA_View_Type.pdf', '', max(summary(repos_sa_analysis$SA.View.Type)) + 5, 12, 13)  
plot(repos_sa_analysis_long, 'ViewElements', './output/SA_View_Elements.pdf', '', max(summary(as.factor(repos_sa_analysis_long$ViewElements))) + 5, 15, 13) 
plot_stacked(repos_sa_analysis, 'SA.View.Depiction', 'SA.View.Type', './output/SA_Stacked.pdf', max(summary(repos_sa_analysis$SA.View.Depiction)) + 5, 20, 13)  
