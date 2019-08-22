#!/usr/bin/env python
# coding: utf-8

# In[1]:


import re
import pandas as pd
from itertools import product
from difflib import SequenceMatcher as sm

## For POS-tagging and/or tokenization
import nltk
from nltk.corpus import stopwords

## For dependency parsing
import spacy
## Configure spaCy English-pretrained model
nlp = spacy.load('C:\\Users\\gn633dt\\AppData\\Local\\Continuum\\anaconda3\\Lib\\en_core_web_sm\\en_core_web_sm-2.1.0')

# ## Testing to get time/day/money
# import duckling
# from datetime import datetime

## Initiate duckling-wrapper: takes few seconds to complete
# duck = duckling.DucklingWrapper()


# ### Helper Functions

# In[2]:


def checkATE(input_sent):
    """
    Check if it's ATE.
    """
    input_sent = [sent.lower() for sent in input_sent]
    ATE = 'ATE not found!'
    
    for ele in input_sent:
        if 'additional termination events' in ele:
            ATE = 'Additional Termination Event'
            return ATE
        else:
            continue
            
    return ATE


# In[3]:


########################################-----------------ERISA-----------------########################################
# def checkEventType(input_sent):
#     """
#     Check what type of event it is.
#     """
    
#     input_sent = [sent.lower() for sent in input_sent]
    
#     for ele in input_sent:
#         if 'net asset value' in ele:       
#             return 'net asset value'
#         elif 'erisa' in ele:
#             return 'erisa'
#         elif 'key person' in ele:
#             return 'Key Person'
#         elif 'investment manager' in ele:
#             return 'investment manager'        
#         elif 'financials' in ele:
#             return 'financials'
#         elif 'other optional termination' in ele:
#             return 'other optional early termination'
#         elif 'regulatory authority' in ele:
#             return 'regulatory authority'
#         elif 'material change' in ele:
#             return 'material change'
        
#         else:
#             continue
            
#     return None


def checkEventType_temp(input_sent):
    """
    Check what type of event it is.
    """
    
    ## Possible input phrases
    phrases = ['additional termination event', 'erisa', 'net asset value', 'investment manager', 'financials', 
               'material change', 'regulatory authority', 'other optional termination', 'key person', 'rating']    
    
    identified_events = []
    
    for p in phrases:
        if p in input_sent.lower():       
            identified_events.append(p)
            
    return identified_events


def checkElectiveTermination(input_sent):
    """
    
    """
    if type(input_sent) == list:
        input_sent = [sent.lower() for sent in input_sent]
        elective_termination = 'No indication found!'
        
        for sent in input_sent:
            if 'optional' in sent:
                elective_termination = 'Elective'
                return elective_termination
            else:
                continue
                
        return elective_termination
    
    
def getAffectedParty(input_sent):
    """
    
    """
    regex_party = 'Party\s*[A-Z]'
    affected_party_identifiers = ['Affected']  ## Try with spacy/nltk lemmatizer

    for ele in affected_party_identifiers:
        if ele in input_sent: 
            affected_party = list(set(re.findall(regex_party, input_sent)))

    if len(affected_party) == 1:
        affected_party = affected_party[0].split(' ')[1]
        return affected_party
    elif len(affected_party) > 1:
        affected_party = [p.split(' ')[1] for p in affected_party]
        return affected_party
    else:
        return 'Party not found!'

# def checkElectingParty(electing_party = None, affected_party = None):
#     """
    
#     """
    
#     notification = False
#     notified_parties = []
    
#     if affected_party == 'B' and electing_party == 'A':
#         notification = True
#         notified_parties.append('A')
#         notified_parties.append('B')
#         return notification, notified_parties
    
#     elif affected_party == 'B' and electing_party == 'B':
#         return notification, notified_parties
    
#     elif affected_party not in ['A', 'B'] or electing_party not in ['A', 'B']:
#         notification = 'Indication not available!'
#         notified_parties.append('Indication not available!')
        
#         return notification, notified_parties

def retokenizeCorpus(input_sent):
    """
    For following specific case:
    Re-tokenize the corpus to catch 'the other party' which is an indication of one of the parties involved in the context. We 
    can then consider that phrase as whole noun and re-train spacy to catch dependencies or modify tagging.
    
    """
    
    doc = nlp(input_sent)
    start = 0
    ind_ls = []
    for i, token in enumerate(doc):    
        if str(token) == 'the':
            start = i
            if str(doc[start+1]) in ['Other', 'other'] and str(doc[start+2]) in ['Party', 'party']:
                end = start + 3
                ind_ls.append((start, end))

    with doc.retokenize() as retokenizer:    
        for i in ind_ls:
            retokenizer.merge(doc[i[0]:i[1]])
            
    return doc

# doc = retokenizeCorpus(input_sent)
def checkNotification(doc, notify_party = 'No Party'):
    """
    This indication is only available in ERISA-paragraph. For NAV and/or others, it's not there.    
    """


    notification_flag = False
    notifying_parties = []
    doc_len = len(doc)

    for i, token in enumerate(doc):
        if str(token.text) in ['notifies', 'notify', 'notification', 'notice']:      
            start = i

            ## Proximity-range: +/- 5 words. Can be tuned if more data available
            before = i - 5   
            if before < 0:
                before = 0

            after = i + 5    
            if after > doc_len:
                after = doc_len

            proximity_list = [str(doc[t_id]).lower() for t_id in range(before, after)]
            if 'party' in proximity_list:
                notification_flag = True
                notifying_parties.extend(notify_party)
                break
            else:
                continue

    return notification_flag, notifying_parties
    

# def checkAffectedParty(affected_party = None, event_type = None):
#     """
#     event_type = ['ERISA', 'NAV']
    
#     """
#     written_bases_determination_c1 = False
#     written_bases_determination_c2 = False
#     if affected_party == 'B':
#         if event_type in ['ERISA', 'erisa']:
#             written_bases_determination_c1 = True
#             written_bases_determination_c2 = True            
#             return (written_bases_determination_c1, written_bases_determination_c2)
#         elif event_type == 'NAV':
#             return (written_bases_determination_c1, written_bases_determination_c2)
        
#     else:
#         ## DON'T KNOW WHAT PATH TO FOLLOW AS IT'S NOT AVAILABLE IN DECISION-TREE
#         return (written_bases_determination_c1, written_bases_determination_c2)

def checkWrittenNotification(doc):
    """
    
    """
    
    ## Written-notification-of-determination
    written_notification = False
    written_basis = False
        
    ## For written-notification
    child_ls = []
    for token in doc:
        if str(token.dep_) == 'prep':
            if str(token.head.text) in ['notifies', 'provides']:
                child_ls = list(set([str(child) for child in token.children]))

    if child_ls:
        if 'writing' in child_ls:
            written_notification = True
            
    ## For written-basis-of-determination
    child_ls_2 = []
    for token in doc:
        if str(token.head.text) == 'basis':
            child_ls_2.extend([str(child) for child in token.children])
    
    if child_ls_2:
        if set(['determination', 'determines']) & set(child_ls_2):
            written_basis = True

    return written_notification, written_basis
  
    
def prohibitedTransaction(affected_party = None, event_type = None):
    """
    
    """
    
    prohibited_transaction = 'Indication not available!'
#     conditions = checkAffectedParty(affected_party = affected_party, event_type = event_type)
    if affected_party == 'B' and event_type in ['ERISA', 'erisa']:    
        prohibited_transaction = True
        return prohibited_transaction
    else:
        return prohibited_transaction


# def exemptTransaction(affected_party = None, event_type = None):
#     """
    
#     """
#     exempt = False
#     if prohibitedTransaction(affected_party = affected_party, event_type = event_type):
#         return exempt
#     else:
#         exempt = 'Indication not available!'
#         return exempt
    
def checkExemptTransaction(doc):
    """
    
    """
    
    exempt_transaction = False
    for i, token in enumerate(doc):    
        if str(token.head.text) == 'exemption':        
            if str(token.text) == 'no':
                return exempt_transaction


# In[4]:


########################################-----------------NAV-----------------########################################
## Use above functions: checkElectiveTermination, checkElectingParty, checkAffectedParty

def getValuedParty(input_sent):
    """
    Valued Party
    """ 
    valued_party = None
    children = []
    doc = nlp(input_sent)
    for token in doc:
        if str(token) in ['of']:
            if str(token.head.text) == 'Value':
                children.extend([str(child) for child in token.children if len(child) == 1])
                valued_party = list(set(children))[0]
    
    return 'Party '+valued_party

            
def getChangeDirection(input_sent):
    """
    NAV_Trigger
    """
    
    doc = nlp(input_sent[0])
    change_directions = []
    for token in doc:
        if str(token) == 'Value':
            if str(token.head.pos_) == 'VERB':
                change_directions.append(token.head.text)
                
    NAV_Trigger = list((set(change_directions)))
    return NAV_Trigger



def getValuationAmount(input_sent):
    """
    
    """

    regex_p = '\d+\%'  ## To get PERCENT values
    regex_d = 'USD+[0-9].+\.'  ## To get DOLLAR amount

    result_p = re.findall(regex_p, input_sent, flags = re.IGNORECASE)
    result_d = re.findall(regex_d, input_sent, flags = re.IGNORECASE)
    
    non_below_valuation_amounts = []
    for i,j in enumerate(result_p):
        temp = 'valuation_amount_'+str(i)
        non_below_valuation_amounts.append((temp, j))

    below_valuation_amounts = []
    for i,j in enumerate(result_d):
        temp = 'valuation_amount_below_'+str(i)
        below_valuation_amounts.append((temp, j))
        
    if not non_below_valuation_amounts:
        non_below_valuation_amounts.append('Empty List. Values not found!')
    if not below_valuation_amounts:
        below_valuation_amounts.append('Empty List. Values not found!')
        
    
    return non_below_valuation_amounts, below_valuation_amounts


def getValuationDayMonth(input_sent):
    """
    
    """

    doc = nlp(input_sent)
        
    if doc:
        valuation_days = []
        valuation_months = []

        for chunk in doc.noun_chunks:
            if str(chunk.root.text) in ['Day', 'Days']:
                valuation_days.append(chunk.text)
            elif str(chunk.root.text) == 'month':
                valuation_months.append(chunk.text)            

        return valuation_days, valuation_months
    
    else:
        return 'Something is wrong in valuation-day-month-func!'
    

def getValuationDayMonth_temp(input_sent):
    """
    
    """

    doc = nlp(input_sent)
        
    valuation_days = []
    valuation_months = []

    for chunk in doc.noun_chunks:
        if str(chunk.root.text) in ['Day', 'Days']:
            valuation_days.append(chunk.text)
        if str(chunk.root.text) == 'month':
            valuation_months.append(chunk.text)            
        
    try:
        valuation_day = list(set(valuation_days))
        if len(valuation_day) == 1:
            day_doc = nlp(valuation_day[0])
            for token in day_doc:
                if str(token.head.text) in ['Day', 'Days']:
                    if str(token.pos_) == 'NUM':
                        num_days = str(token.text)
        if num_days:                        
            return valuation_days, valuation_months, num_days
    except:
        return valuation_days, valuation_months
    
    
def getCreditRatingInfo(input_sent):
    """
    
    """
    
    doc = nlp(input_sent)
    
    credit_rating_info = []
    credit_rating_codes = []
    credit_rating_agencies = []
    
    for chunk in doc.noun_chunks:
        if str(chunk.root.head.text) in ['above']:
            credit_rating_codes.append(str(chunk.text))
        if str(chunk.root.head.text) in ['by']:
            credit_rating_agencies.append(str(chunk.text))    
    
    for code, agency in zip(credit_rating_codes, credit_rating_agencies):
        credit_rating_info.append((code, agency))
        
    return credit_rating_info


# In[5]:


#######################-----------------KeyPerson, InvestmentManager, Financials-----------------########################
def getMiniBranchFields(input_sent, mini_branches, eve_cat = None, elec_term = None, party_affected = None, ATE = None):
    """
    Function for small branches such as: Key-person, Investment Manager, Financials, Other Optional Early Termination, 
    Regulatory Authority, Material Change
    
    """
    
    branch_name = 'Not available in pre-defined phrases!'
        
    input_sent = input_sent.lower()    
    for branch in mini_branches:
        if branch in input_sent:
            branch_name = branch
            break
            
    branch_dict = {'Event Type': branch_name, 'Event Category': eve_cat, 'Type of Termination': elec_term, 
                   'Affected Party': party_affected, 'ATE': ATE}
    
    return branch_dict


# In[6]:


def getMajorBranchFields(ATE = None, eve_typ = None, elec_term = None, eve_cat = None, party_affected = None, 
                         party_elected = None, notif_req = None, notif_party = None, party_valued = None, nav = None, 
                         eqaul_more = None, below = None, written_clause_1 = None, written_clause_2 = None, 
                         prohibit_tran = None, exem_tran = None, event = None, value_days = None, value_months = None, 
                         num_days = None, unit_time = None, cred_rat_info = None):
    """
    Function to make a fields:values dictionary for ERISA and NAV
    """
    
    
    if event == 'Net Asset Value' or event == 'net asset value':
        ## Dict of NAV-fields
        NAV_fields_dict = {'ATE': ATE, 'Event Type': eve_typ, 'Type of Termination': elec_term, 'Event_Category': eve_cat,
                           'Affected Party': party_affected, 'Electing Party': party_elected, 
                           'Notification Required': notif_req, 'Notified Party': notif_party, 
                           'Valued Party': party_valued, 'NAV_Trigger': nav, 'Equal or More': eqaul_more, 'Below': below, 
                          }
        
        return NAV_fields_dict

    elif event == 'ERISA' or event == 'erisa':
        ## Dict of ERISA-fields
        ERISA_fields_dict = {'ATE': ATE, 'Event Type': eve_typ, 'Type of Termination': elec_term, 'Event_Category': eve_cat,
                             'Affected Party': party_affected, 'Electing Party': party_elected, 
                             'Notification Required': notif_req, 'Notified Party': notif_party, 
                             'Written Basis Determination - 1': written_clause_1, 
                             'Written Basis Determination - 2': written_clause_2, 
                             'Prohibited Transaction': prohibit_tran, 'Exempt Transaction': exem_tran}    
        return ERISA_fields_dict
    
    elif event == 'rating':
        ## Dict of Rating-fields
        Rating_fields_dict = {'ATE': ATE, 'Event_Type': eve_typ, 'Type of Termination': elec_term, 'Event_Category': eve_cat,
                              'Affected Party': party_affected, 'Electing Party': party_elected, 
#                               'Notification Required': notif_req, 'Notified Party': notif_party,
                              'Notification Number': num_days, 'Notification Units': unit_time,
                              'Credit Rating Info': cred_rat_info}
        return Rating_fields_dict
        
    else:
        return None


# In[ ]:





# ### Execution

# ### Input Data

# In[9]:


# ## Input data: Provide sentences as per order described in power-point and utilize decision-tree to creare logic
# ip_1 = ["Additional Termination Event. The following Additional Termination Events will apply:"]
# ip_2_3_6_23 = ["Optional Early Termination1. Both Party A and Party B shall have the right, as long as no \
#                Termination Event or Event of Default shall have occurred, and upon three (3) \
#                 Local Business Day's prior written notice to terminate any Transaction with immediate effect. "]
# ip_4 = ["Party B, in each such instance, shall be the sole Affected Party5"]
# ip_7_to_14 = ["Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of \
#               Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month; \
#               or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the \
#               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month; \
#               or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000."]

# ip_15_to_17_21_22_24 = [' Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other \
# Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is \
# likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited \
# transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to \
# have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with \
# clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification.']

# ip_19 = ["Key Person4. XXX ceases to be responsible for the day-to-day portfolio management of Party B and a successor reasonably acceptable to Party A is not appointed within a reasonable time thereafter "]
# ip_20 = ["Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement."]
# ip_21 = [ "Financials4. Party B shall fail to deliver (i) any financial information pursuant to Part 3(b)(i) of this Schedule within five (5) calendar days of Party A's notice to Party B of Party B's failure to provide such information, or (ii) any financial statements or financial information pursuant to Party 3(b)(ii) of this Schedule within two (2) calendar days of Party A's notice to Party B of Party B's failure to provide such information"]
# ip_24 = ["Regulatory Authority4. The Regulator's authorisation of Party B or approval is withdrawn or subjected to conditions that would have a material adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement."]
# ip_25 = ["Material Change4. Any of the constitutive documents or the Prospectus relating to Party B (in the case of the Prospectus) from time to time are materially amended or modified in a manner which would have a material, adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement or any Transaction hereunder."]


# ### With whole ATE-data: Identify paragraphs in all ATE-text and return appropriate fields to be populated in data model

# In[7]:


# def getData(input_text):
#     """
    
#     """

# #     with open('ATE_raw_text.txt', 'r') as ate:
# #         all_ATE = ate.read()

#     ## Making two lists of same text data: If I keep raw text in original form then it's easy to catch langauge dependencies with spaCy
#     all_ATE_elements_original = re.split('\n{2} \n{2}', input_text)
#     all_ATE_elements = [ele.lower() for ele in all_ATE_elements_original]
    
#     return all_ATE_elements_original, all_ATE_elements


def getData_temp(input_text):
    """
    
    """
    
    ## Making two lists of same text data: If I keep raw text in original form then it's easy to catch langauge dependencies with spaCy
    all_ATE_elements = re.split('\n', input_text)
    
    return all_ATE_elements


def searchParagraph(keyword, all_elements):
    """
    Use key-words and/or phrases to look for a relevant sentence/paragraph in the ATE-text (all_elements). ATE-text is split 
    into list of paragraphs for this process.
    """
    matched_elements = []
    for ele in all_elements:
        if keyword in ele.lower():
            matched_elements.append(ele)
        
    return matched_elements


def dictValuesToList(input_dict):
    """
    Convert all values of a dictionary into list.
    """
    
    for i,j in input_dict.items():
        if type(j) == list:
            pass
        elif type(j) == str:
            j = [j]
            input_dict[i] = j
        elif type(j) == bool:
            j = [j]
            input_dict[i] = j
        elif j is None:
            j = 'Value not available!'
            input_dict[i] = [j]
        else:
            continue
        
    return input_dict


def convertDictToDf(input_dict):
    """
    Convert dictionary to dataframe when values of dictionary are lists of varying lengths.
    """
    
    input_dict = dictValuesToList(input_dict)
    
    flat = [[(k, v) for v in vs] for k, vs in input_dict.items()]
    df_ls = [dict(items) for items in product(*flat)]
    
    return pd.DataFrame(df_ls)

def getGlobalFields(ATE = 'None', party_affected = 'None', elec_term = 'None'):
    """
    Pre-defined set of fields to return if input-clause is same as one of the global statements.
    """
    global_var_dict = {}
    global_var_dict['ATE'] = ATE
    global_var_dict['Affected_Party'] = party_affected
    global_var_dict['Elective Termination'] = elec_term
    
    return global_var_dict


def checkSimilarity(input_clause, global_sents):
    """
    
    """
    sim = 0
    match = None
    threshold = 0.90

    for ind, sent in enumerate(global_sents):
        sim_temp = sm(None, sent, input_clause).ratio()
        if sim_temp > sim and sim_temp >= threshold:
            sim = sim_temp
            match = sent
            return ind
        else:
            continue
            
    return False


# ## Example-0 (Take user-input and get relevant o/p)

# In[8]:


# ## Only NAV
# ip_test = ["Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of \
#               Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month; \
#               or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the \
#               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month; \
#               or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000. "]

# # ## Only ERISA
# ip_test = [' Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other \
# Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is \
# likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited \
# transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to \
# have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with \
# clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification.']

# # ## For others
# ip_test = ["Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement."]
# ip_test = [ "Financials4. Party B shall fail to deliver (i) any financial information pursuant to Part 3(b)(i) of this Schedule within five (5) calendar days of Party A's notice to Party B of Party B's failure to provide such information, or (ii) any financial statements or financial information pursuant to Party 3(b)(ii) of this Schedule within two (2) calendar days of Party A's notice to Party B of Party B's failure to provide such information"]
# ip_test = ["Regulatory Authority4. The Regulator's authorisation of Party B or approval is withdrawn or subjected to conditions that would have a material adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement."]
# ip_test = ["Material Change4. Any of the constitutive documents or the Prospectus relating to Party B (in the case of the Prospectus) from time to time are materially amended or modified in a manner which would have a material, adverse effect on the ability of Party B to perform its obligations, or Party A's ability to exercise its rights, under this Agreement or any Transaction hereunder."]


# In[9]:


# def execute(input_clause):
#     """
    
#     """

#     ## Possible input phrases
#     phrases = ['additional termination event', 'erisa', 'net asset value', 'investment manager', 'financials', 
#                'material change', 'regulatory authority', 'other optional termination', 'key person']
    

#     ## Extract information from GLOBAL STATEMENTS
#     global_statements = ["Additional Termination Event. The following Additional Termination Events will apply:", 
#                          "Party B, in each such instance, shall be the sole Affected Party5", 
#                          "Optional Early Termination1. Both Party A and Party B shall have the right, as long as no \
#                              Termination Event or Event of Default shall have occurred, and upon three (3) \
#                              Local Business Day's printor written notice to terminate any Transaction with immediate effect. "]
    
#     ate_statement = [global_statements[0]]
#     ate_input_keyword = phrases[0]
#     matched_elements = searchParagraph(ate_input_keyword, ate_statement)
#     ATE = checkATE(matched_elements)

#     affected_party_statement = [global_statements[1]]
#     affected_party = getAffectedParty(affected_party_statement)    

#     termination_statement = [global_statements[2]]
#     EVENT_CATEGORY = 'termination'
#     matched_elements = searchParagraph(EVENT_CATEGORY, termination_statement)
#     elective_termination = checkElectiveTermination(matched_elements)

#     ## Check if input_clause is similar to one of the global statements.
#     value = checkSimilarity(input_clause, global_statements)
    
#     if value is not False:
#         if ATE in global_statements[value]:
#             global_dict = getGlobalFields(ATE = ATE)
#             global_dict_df = convertDictToDf(global_dict)    
#             return global_dict_df
#         elif 'Affected Party' in global_statements[value]:
#             global_dict = getGlobalFields(party_affected = affected_party)
#             global_dict_df = convertDictToDf(global_dict)    
#             return global_dict_df
#         elif 'Termination' in global_statements[value]:
#             global_dict = getGlobalFields(elec_term = elective_termination)
#             global_dict_df = convertDictToDf(global_dict)    
#             return global_dict_df
#         else:
#             return 'False Alarm!'
                
#     else:
    
#         ## Get event-type
#         event_type = checkEventType(input_clause)

#         ## For Net Asset Value
#         if  event_type in phrases and event_type == 'net asset value':
#             print ('Done-1', event_type)

#             NAV_Trigger = getChangeDirection(input_clause)
#             non_below, below = getValuationAmount(input_clause[0])   
#             valuation_days, valuation_months = getValuationDayMonth(input_clause)
#             valuation_info_non_below = []
#             for n,d,m in zip(non_below, valuation_days, valuation_months):
#                 n = n + (d,) + (m,)
#                 valuation_info_non_below.append(n)
            
#             print ('Done-2')

#             if len(ip_test) > 1:
#                 matched_elements = ' '.join(matched_elements)     
#                 matched_elements = re.sub(pattern = '(\\n)', string = matched_elements, repl = '')
#                 valued_party = getValuedParty(input_sent = matched_elements)
#             else:
#                 valued_party = getValuedParty(input_sent = input_clause[0])

#             print ('Done-3')

#             electing_party = 'A'
#             notification_required, notified_party = checkElectingParty(affected_party = affected_party, electing_party = electing_party)
#             print ('Done-4')

#             major_branch = getMajorBranchFields(ATE = ATE, eve_typ = event_type, elec_term = elective_termination, 
#                                                 eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
#                                                 party_elected = electing_party, notif_req = notification_required, 
#                                                 notif_party = notified_party, party_valued = valued_party, nav = NAV_Trigger, 
#                                                 eqaul_more = valuation_info_non_below, below = below, 
#                                                 written_clause_1 = None, written_clause_2 = None, prohibit_tran = None, 
#                                                 exem_tran = None, event = event_type)

#             major_branch_df = convertDictToDf(major_branch)

            
#             ## Split columns as per excel-data-model: order of following lines matter!
#             major_branch_df['Valuation Month'] = list(map(lambda ele: ele[3], major_branch_df['Equal or More']))
#             major_branch_df['Valuation Day'] = list(map(lambda ele: ele[2], major_branch_df['Equal or More']))
#             major_branch_df['Equal or More'] = list(map(lambda ele: ele[1], major_branch_df['Equal or More']))
#             major_branch_df['Below'] = list(map(lambda ele: ele[1], major_branch_df['Below']))
            
#             return major_branch_df
        
#         ## For ERISA
#         elif event_type in phrases and event_type == 'erisa':

#             print ('Done-1')

#             electing_party = 'A'
#             notification_required, notified_party = checkElectingParty(affected_party = affected_party, electing_party = electing_party)
#             written_bases_determination_c1, written_bases_determination_c2 = checkAffectedParty(affected_party = affected_party, 
#                                                                                                         event_type = event_type)
#             print ('Done-2')

#             prohibited_transact = prohibitedTransaction(affected_party = affected_party, event_type = event_type)
#             exempt_transact = exemptTransaction(affected_party = affected_party, event_type = event_type)

#             major_branch = getMajorBranchFields(ATE = ATE, eve_typ = event_type, elec_term = elective_termination, 
#                                                 eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
#                                                 party_elected = electing_party, notif_req = notification_required, 
#                                                 notif_party = notified_party, party_valued = None, nav = None, 
#                                                 eqaul_more = None, below = None, written_clause_1 = written_bases_determination_c1, 
#                                                 written_clause_2 = written_bases_determination_c1, 
#                                                 prohibit_tran = prohibited_transact, exem_tran = exempt_transact, 
#                                                 event = event_type)

#             major_branch_df = convertDictToDf(major_branch)

#             return major_branch_df

#         ## For mini-branches    
#         elif event_type in phrases and event_type not in ['erisa', 'net asset value']:
#             input_matched_elements = searchParagraph(event_type, input_clause)
#             input_matched_elements = ' '.join(input_matched_elements)

#             print ('Done-1')

#             mini_branch = getMiniBranchFields(input_sent = input_matched_elements, mini_branches = phrases, 
#                                               eve_cat = EVENT_CATEGORY, elec_term = elective_termination, 
#                                               party_affected = affected_party, ATE = ATE)

#             mini_branch_df = convertDictToDf(mini_branch)  

#             return mini_branch_df

#         else:
#             message = 'Event_type not found in pre-defined phrases/keywords!'
#             return message


# In[ ]:





# ## Example-1: When identifies more than one event type

# In[8]:


## Only NAV+ERISA+minibranches
ip_test = ['Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month; or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month;             or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000. \n Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification. \n             Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement. \n              Key Person4. XXX ceases to be responsible for the day-to-day portfolio management of Party B and a successor reasonably acceptable to Party A is not appointed within a reasonable time thereafter'
]

# ip_test = ['Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification. \n             Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement. \n              Key Person4. XXX ceases to be responsible for the day-to-day portfolio management of Party B and a successor reasonably acceptable to Party A is not appointed within a reasonable time thereafter \n Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month; or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month;             or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000. '
# ]


# mini_ip_test = ['Investment Manager4. ABC ceases to act at any time as investment manager on behalf of Party B in the same or similar capacity as on the date of this Agreement. \n              Key Person4. XXX ceases to be responsible for the day-to-day portfolio management of Party B and a successor reasonably acceptable to Party A is not appointed within a reasonable time thereafter']

# with open('./ATE_raw_text.txt', 'r') as ate:
#     ip_test = ate.read()

# ip_test = ['Net Asset Value Decline4. On the last Local Business Day of any calendar month, the Net Asset Value of \
#               Party B, as reported in writing as a final Net Asset Value declines: (A) by forty percent (40%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the twelfth prior calendar month; \
#               or (B) by thirty percent (30%) or more compared to the Net Asset Value of Party B on the \
#               last Local Business Day of the third prior calendar month; or (C) by twenty percent (20%) or more \
#               compared to the Net Asset Value of Party B on the last Local Business Day of the prior calendar month; \
#               or (D) as of any day the Net Asset Value of Party B declines below USD30,000,000.']


# In[9]:


def execute(input_clause):
    """
    
    """
    
    ## Store all dataframes that are being created
    return_list_df = []

    ## Possible input phrases
    phrases = ['additional termination event', 'erisa', 'net asset value', 'investment manager', 'financials', 
               'material change', 'regulatory authority', 'other optional termination', 'key person', 'rating']    
    
    ## Dict of matched phrases
    phrases_flag = {}
    for p in phrases:
        phrases_flag[p] = False

    event_type = checkEventType_temp(input_clause)  ######
    
    for e in event_type:
        phrases_flag[e] = True
        
    ## Split data into elements
    all_elements = getData_temp(input_clause)    

    ## Extract information from GLOBAL STATEMENTS
    global_statements = ["Additional Termination Event. The following Additional Termination Events will apply:", 
                         "Party B, in each such instance, shall be the sole Affected Party5", 
                         "Optional Early Termination1. Both Party A and Party B shall have the right, as long as no \
                             Termination Event or Event of Default shall have occurred, and upon three (3) \
                             Local Business Day's printor written notice to terminate any Transaction with immediate effect. "]
    
    ate_statement = [global_statements[0]]
    ate_input_keyword = phrases[0]
    matched_elements = searchParagraph(ate_input_keyword, ate_statement)
    ATE = checkATE(matched_elements)

    affected_party_statement = global_statements[1]
    affected_party = getAffectedParty(affected_party_statement)    

    termination_statement = [global_statements[2]]
    EVENT_CATEGORY = 'termination'
    matched_elements = searchParagraph(EVENT_CATEGORY, termination_statement)
    elective_termination = checkElectiveTermination(matched_elements)

    ## Check if input_clause is similar to one of the global statements.
    value = checkSimilarity(input_clause, global_statements)
    if value is not False:
        if ATE in global_statements[value]:
            global_dict = getGlobalFields(ATE = ATE)
            global_dict_df = convertDictToDf(global_dict)    
            return_list_df.append(global_dict_df)

        elif 'Affected Party' in global_statements[value]:
            global_dict = getGlobalFields(party_affected = affected_party)
            global_dict_df = convertDictToDf(global_dict)    
            return_list_df.append(global_dict_df)

        elif 'Termination' in global_statements[value]:
            global_dict = getGlobalFields(elec_term = elective_termination)
            global_dict_df = convertDictToDf(global_dict)    
            return_list_df.append(global_dict_df)

    ## For Net Asset Value
    if  phrases_flag['net asset value']:
        matched_elements = searchParagraph('net asset value', all_elements)
        print ('Done-1')

        NAV_Trigger = getChangeDirection(matched_elements)   ## Need to check if input-text needs to be split (in case of multiple events)
        non_below, below = getValuationAmount(matched_elements[0])   
        valuation_days, valuation_months = getValuationDayMonth_temp(matched_elements[0])
        valuation_info_non_below = []
        for n,d,m in zip(non_below, valuation_days, valuation_months):
            n = n + (d,) + (m,)
            valuation_info_non_below.append(n)

        print ('Done-2')

        if len(ip_test) > 1:
            matched_elements = ' '.join(matched_elements)     
            matched_elements = re.sub(pattern = '(\\n)', string = matched_elements, repl = '')
            valued_party = getValuedParty(input_sent = matched_elements)
        else:
            valued_party = getValuedParty(input_sent = matched_elements[0])

        print ('Done-3')

        electing_party = 'A'
        doc = nlp(matched_elements[0])
        
        ## Need to hard-code since NAV-data actually does not provide any info on Notification
        notification_required = True
        notified_party = ['A', 'B']
        
        print ('Done-4')

        major_branch = getMajorBranchFields(ATE = ATE, eve_typ = 'Net Asset Value', elec_term = elective_termination, 
                                            eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
                                            party_elected = electing_party, notif_req = notification_required, 
                                            notif_party = notified_party, party_valued = valued_party, nav = NAV_Trigger, 
                                            eqaul_more = valuation_info_non_below, below = below, 
                                            written_clause_1 = None, written_clause_2 = None, prohibit_tran = None, 
                                            exem_tran = None, event = 'Net Asset Value')

        major_branch_nav_df = convertDictToDf(major_branch)
        
        ## Split columns as per excel-data-model: order of following lines matter!
        major_branch_nav_df['Valuation Month'] = list(map(lambda ele: ele[3], major_branch_nav_df['Equal or More']))
        major_branch_nav_df['Valuation Day'] = list(map(lambda ele: ele[2], major_branch_nav_df['Equal or More']))
        major_branch_nav_df['Equal or More'] = list(map(lambda ele: ele[1], major_branch_nav_df['Equal or More']))
        major_branch_nav_df['Below'] = list(map(lambda ele: ele[1], major_branch_nav_df['Below']))

        return_list_df.append(major_branch_nav_df)

    ## For ERISA
    if  phrases_flag['erisa']:
        matched_elements = searchParagraph('erisa', all_elements)
        print ('Done-1')

        
        doc = nlp(matched_elements[0])

        electing_party = 'A'
        notification_required, notified_party = checkNotification(doc, notify_party = ['None'])
        notified_party = ['A', 'B']
        written_notification_determination_c2, written_basis_determination_c1 = checkWrittenNotification(doc)

        
        print ('Done-2')

        prohibited_transact = prohibitedTransaction(affected_party = affected_party, event_type = 'erisa')
        exempt_transact = checkExemptTransaction(doc)

        major_branch = getMajorBranchFields(ATE = ATE, eve_typ = 'ERISA', elec_term = elective_termination, 
                                            eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
                                            party_elected = electing_party, notif_req = notification_required, 
                                            notif_party = notified_party, party_valued = None, nav = None, 
                                            eqaul_more = None, below = None, written_clause_1 = written_basis_determination_c1, 
                                            written_clause_2 = written_notification_determination_c2, 
                                            prohibit_tran = prohibited_transact, exem_tran = exempt_transact, 
                                            event = 'ERISA')

        major_branch_erisa_df = convertDictToDf(major_branch)
        return_list_df.append(major_branch_erisa_df)

        
    ## For Rating-event
    if phrases_flag['rating']:
        matched_elements = searchParagraph('rating', all_elements)
        results = getValuationDayMonth_temp(matched_elements[0])
        if len(results) == 3:
            valuation_days = results[0]
            valuation_months = results[1]
            num_days = results[2]
        else:
            valuation_days = results[0]
            valuation_months = results[1]
            num_days = None

        affected_party = getAffectedParty(matched_elements[0])
        credit_rating_info = getCreditRatingInfo(matched_elements[0])
        
        doc = nlp(matched_elements[0])
        notification_required, notified_party = checkNotification(doc, notify_party = 'None')
        
        major_branch = getMajorBranchFields(ATE = ATE, eve_typ = 'rating', elec_term = elective_termination, 
                                            eve_cat = EVENT_CATEGORY, party_affected = affected_party, 
                                            party_elected = 'A', 
                                            notif_req = notification_required, 
                                            notif_party = notified_party, party_valued = None, nav = None, 
                                            event = 'rating', num_days = num_days, unit_time = valuation_days, 
                                            cred_rat_info = credit_rating_info)

        major_branch_rating_df = convertDictToDf(major_branch)
        return_list_df.append(major_branch_rating_df)

        
    ## For mini-branches    
    for mini_event in event_type: 
        if phrases_flag[mini_event]:
            if mini_event not in ['erisa', 'net asset value', 'rating', 'additional termination event']:
                matched_elements = searchParagraph(mini_event, all_elements)
                print (mini_event)
                input_matched_elements = ' '.join(matched_elements)

                mini_branch = getMiniBranchFields(input_sent = input_matched_elements, mini_branches = phrases, 
                                                  eve_cat = EVENT_CATEGORY, elec_term = elective_termination, 
                                                  party_affected = affected_party, ATE = ATE)

                mini_branch_df = convertDictToDf(mini_branch)  
                return_list_df.append(mini_branch_df)
                

    try:
        ## Concatenate all the generated data-frames
        final_df = pd.DataFrame()
        for df in return_list_df:
            final_df = pd.concat([df, final_df])

        final_df.reset_index(inplace = True, drop = True)

        return final_df
    
    except:
        return 'Something is wrong!'


# In[ ]:





# ### Working towards more robust logic

# In[158]:


# ## Only ERISA
# ip_test = [' Prohibited Transaction3. If either Party2 reasonably determines, and (1) notifies the other party in writing of such determination, and (2) promptly provides to the other \
# Party (in writing , if promptly requested by the other Party) the basis for the determination, that this Agreement or any Transaction contemplated hereby constitutes or is \
# likely to constitute a "prohibited transaction" under ERISA (as defined in Part 5) and/or the Code (as defined in Part 5) and that no exemption from the "prohibited \
# transaction" provisions of ERISA and the Code is available with respect to this Agreement and/or such Transaction. Such Additional Termination Event shall be deemed to \
# have occurred when the condition of clause (1) has been satisfied, if clause (2) is eventually satisfied. If the required basis is provided to the other Party in accordance with \
# clause (2) along with the initial notification, the Additional Termination Event occurs at the time of the initial notification.']


# In[88]:


########-----------------------------INCOMPLETE----------------############
# ## For Prohibited-transaction
# doc = retokenizeCorpus(ip_test[0])
# start = 0
# ind_ls = []
# for i, token in enumerate(doc):    
#     if str(token) in ['prohibited', 'Prohibited']:
#         start = i
#         if str(doc[start+1]) in ['transaction', 'Transaction3']:
#             end = start + 2
#             ind_ls.append((start, end))

# with doc.retokenize() as retokenizer:    
#     for i in ind_ls:
#         retokenizer.merge(doc[i[0]:i[1]])

# for i, token in enumerate(doc):
#     print (i, token.text, token.pos_, token.dep_, token.head.text, token.head.pos_, [child for child in token.children])


# In[ ]:





# ## Exmple-3

# In[10]:


# with open('./ATE_EX_3.txt', 'r') as ate:
#     ex_3 = ate.read()
    
# ## Replace '\n' with ''.
# ex_3 = re.sub(pattern = '\\n', string = ex_3, repl = '')
# ex_3


# In[ ]:




